"""MathTeam 后端应用包。

目录结构与教程章节的对应关系：
    core/        第 02 章：配置管理、安全工具、统一异常
    db/          第 03 章：SQLAlchemy 引擎、Session、建表
    models/      第 03/05~10 章：ORM 模型（数据库表）
    schemas/     第 01/02/05~10 章：Pydantic 模型（接口出入参）
    api/         第 01/02/04~11 章：路由与依赖注入
    services/    第 05~08 章：业务服务层（路由保持轻薄）
    recommender/ 第 09 章：可解释的加权推荐引擎
    ws/          第 10 章：WebSocket 连接管理与群聊

包里的 __init__.py 会让 Python 把目录当作可导入的包；即使内容很少也不要删除它。
"""
