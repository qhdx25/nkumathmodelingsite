#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$RUN_DIR/logs"
BACKEND_SESSION="mathteam-backend"
FRONTEND_SESSION="mathteam-frontend"

POSTGRES_SERVICE="${POSTGRES_SERVICE:-postgresql@16}"
DB_NAME="${DB_NAME:-mathteam}"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

BREW_BIN="${BREW_BIN:-$(command -v brew || true)}"
PG_BIN="${PG_BIN:-/opt/homebrew/opt/postgresql@16/bin}"

mkdir -p "$LOG_DIR"

log() {
  print "[services] $*"
}

fail() {
  print -u2 "[services] ERROR: $*"
  exit 1
}

pid_alive() {
  local pid="${1:-}"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

port_busy() {
  local port="$1"
  [[ -n "$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)" ]]
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-40}"
  local i
  for ((i = 1; i <= attempts; i++)); do
    if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

postgres_state() {
  if [[ -z "$BREW_BIN" ]]; then
    print "unavailable"
    return
  fi
  "$BREW_BIN" services list 2>/dev/null |
    awk -v service="$POSTGRES_SERVICE" '$1 == service { print $2; found=1 } END { if (!found) print "unavailable" }'
}

wait_for_postgres() {
  local i
  for ((i = 1; i <= 80; i++)); do
    if "$PG_BIN/pg_isready" -h "$BACKEND_HOST" -p 5432 >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  return 1
}

ensure_database() {
  local exists
  exists="$("$PG_BIN/psql" -h "$BACKEND_HOST" -d postgres -Atqc \
    "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'")"
  if [[ "$exists" != "1" ]]; then
    "$PG_BIN/createdb" -h "$BACKEND_HOST" "$DB_NAME"
  fi
}

start_database() {
  [[ -n "$BREW_BIN" ]] || fail "未找到 Homebrew"
  [[ -x "$PG_BIN/pg_isready" ]] || fail "未找到 PostgreSQL：$PG_BIN"

  if [[ "$(postgres_state)" != "started" ]]; then
    nohup "$BREW_BIN" services start "$POSTGRES_SERVICE" \
      >>"$LOG_DIR/postgres.log" 2>&1 </dev/null
  fi
  wait_for_postgres || fail "PostgreSQL 未能按时启动，请查看 $LOG_DIR/postgres.log"

  ensure_database
  (
    cd "$ROOT_DIR"
    "$ROOT_DIR/.venv/bin/alembic" upgrade head \
      >>"$LOG_DIR/migrate.log" 2>&1
  )
  log "PostgreSQL 已启动，数据库：$DB_NAME"
}

screen_job_pid() {
  local session="$1"
  screen -ls 2>/dev/null |
    awk -v session="$session" '$1 ~ ("\\." session "$") { split($1, parts, "."); print parts[1] }' \
    || true
}

start_screen_service() {
  local name="$1"
  local session="$2"
  local port="$3"
  local health_url="$4"
  local command="$5"
  local pid

  pid="$(screen_job_pid "$session")"
  if [[ -n "$pid" ]]; then
    if wait_for_http "$health_url" 4; then
      log "$name 已在运行，PID $pid"
      return
    fi
    screen -S "$session" -X quit >/dev/null 2>&1 || true
    sleep 0.5
  fi

  if port_busy "$port"; then
    fail "$name 端口 $port 已被其他进程占用"
  fi

  screen -dmS "$session" /bin/zsh -lc \
    "$command >>'$LOG_DIR/$name.log' 2>&1"

  if ! wait_for_http "$health_url"; then
    tail -n 30 "$LOG_DIR/$name.log" >&2 || true
    screen -S "$session" -X quit >/dev/null 2>&1 || true
    fail "$name 未能按时启动"
  fi
  pid="$(screen_job_pid "$session")"
  log "$name 已启动，PID $pid"
}

stop_screen_service() {
  local name="$1"
  local session="$2"
  local port="$3"
  local process_match="$4"
  local pid
  local listener_pid
  local i

  pid="$(screen_job_pid "$session")"
  if [[ -z "$pid" ]] && ! port_busy "$port"; then
    screen -S "$session" -X quit >/dev/null 2>&1 || true
    log "$name 未运行"
    return
  fi

  if [[ -n "$pid" ]]; then
    screen -S "$session" -X quit >/dev/null 2>&1 || true
  fi
  for ((i = 1; i <= 40; i++)); do
    if ! port_busy "$port"; then
      break
    fi
    sleep 0.25
  done
  if port_busy "$port"; then
    listener_pid="$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null | head -n 1)"
    if [[ -n "$listener_pid" ]]; then
      local listener_command
      listener_command="$(ps -p "$listener_pid" -o command= 2>/dev/null || true)"
      if [[ "$listener_command" == *"$process_match"* ]]; then
        kill "$listener_pid" 2>/dev/null || true
        sleep 0.5
        kill -KILL "$listener_pid" 2>/dev/null || true
      else
        fail "$name 端口 $port 被未知进程占用，拒绝自动终止"
      fi
    fi
  fi
  log "$name 已停止"
}

start_backend() {
  start_screen_service \
    "backend" \
    "$BACKEND_SESSION" \
    "$BACKEND_PORT" \
    "http://$BACKEND_HOST:$BACKEND_PORT/health" \
    "cd '$ROOT_DIR'; exec '$ROOT_DIR/.venv/bin/uvicorn' main:app --host '$BACKEND_HOST' --port $BACKEND_PORT"
}

start_frontend() {
  start_screen_service \
    "frontend" \
    "$FRONTEND_SESSION" \
    "$FRONTEND_PORT" \
    "http://$FRONTEND_HOST:$FRONTEND_PORT/" \
    "export PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin'; cd '$ROOT_DIR/web'; exec '$ROOT_DIR/web/node_modules/.bin/vite' --host '$FRONTEND_HOST' --port $FRONTEND_PORT"
}

start_all() {
  start_database
  start_backend
  start_frontend
  log "全部服务已静默启动"
  log "前端：http://$FRONTEND_HOST:$FRONTEND_PORT"
  log "后端：http://$BACKEND_HOST:$BACKEND_PORT"
  log "日志：$LOG_DIR"
}

stop_all() {
  stop_screen_service \
    "frontend" "$FRONTEND_SESSION" "$FRONTEND_PORT" "vite"
  stop_screen_service \
    "backend" "$BACKEND_SESSION" "$BACKEND_PORT" "uvicorn"

  if [[ -n "$BREW_BIN" ]] && [[ "$(postgres_state)" == "started" ]]; then
    nohup "$BREW_BIN" services stop "$POSTGRES_SERVICE" \
      >>"$LOG_DIR/postgres.log" 2>&1 </dev/null
    log "PostgreSQL 已停止"
  else
    log "PostgreSQL 未运行"
  fi
}

status_all() {
  local backend_pid frontend_pid
  backend_pid="$(screen_job_pid "$BACKEND_SESSION")"
  frontend_pid="$(screen_job_pid "$FRONTEND_SESSION")"

  print "PostgreSQL：$(postgres_state)"
  if pid_alive "$backend_pid"; then
    print "后端：运行中 PID=$backend_pid http://$BACKEND_HOST:$BACKEND_PORT"
  else
    print "后端：停止"
  fi
  if pid_alive "$frontend_pid"; then
    print "前端：运行中 PID=$frontend_pid http://$FRONTEND_HOST:$FRONTEND_PORT"
  else
    print "前端：停止"
  fi
}

case "${1:-}" in
  start|run)
    start_all
    ;;
  stop)
    stop_all
    ;;
  restart)
    stop_all
    start_all
    ;;
  status)
    status_all
    ;;
  *)
    print "用法：$0 {start|stop|restart|status}"
    exit 2
    ;;
esac
