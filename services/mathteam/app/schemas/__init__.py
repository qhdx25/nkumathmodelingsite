"""Pydantic Schema 集合。

约定：
- XxxCreate / XxxUpdate  → 请求体（入参）
- XxxOut / XxxCard       → 响应（出参），用 response_model 声明
- 所有 Out 类都带 model_config = ConfigDict(from_attributes=True)，
  这样才能直接把 SQLAlchemy 对象交给 FastAPI 序列化。
"""
