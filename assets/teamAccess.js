const TEAM_HOME = '/team/'
const TEAM_LOGIN = '/team/login?redirect=%2F'
const TOKEN_KEY = 'mathteam_token'
const VALIDATION_URL = '/team/api/v1/auth/me'

let navigationPending = false

function redirectToLogin() {
  window.location.assign(TEAM_LOGIN)
}

export async function enterTeam() {
  if (navigationPending) return
  const token = localStorage.getItem(TOKEN_KEY)
  if (!token) {
    redirectToLogin()
    return
  }

  navigationPending = true
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 5000)
  try {
    const response = await fetch(VALIDATION_URL, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
      signal: controller.signal,
    })
    if (!response.ok) {
      localStorage.removeItem(TOKEN_KEY)
      redirectToLogin()
      return
    }
    window.location.assign(TEAM_HOME)
  } catch {
    localStorage.removeItem(TOKEN_KEY)
    redirectToLogin()
  } finally {
    window.clearTimeout(timeout)
    navigationPending = false
  }
}

export function installTeamNavigation() {
  const onClick = (event) => {
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return
    }
    const anchor = event.target.closest?.('a[href]')
    if (!anchor) return

    const url = new URL(anchor.href, window.location.href)
    const path = url.pathname.replace(/\/+$/, '') || '/'
    if (url.origin !== window.location.origin || path !== '/team') return

    event.preventDefault()
    event.stopPropagation()
    void enterTeam()
  }

  document.addEventListener('click', onClick, true)
  return () => document.removeEventListener('click', onClick, true)
}
