# TRIAXUS 数据库迁移指南（PostgreSQL）

本项目内置基于 Alembic 的数据库版本管理工具，仅支持 PostgreSQL。用于在生产环境进行安全的数据库版本升级与回退。

- 迁移目录：`db_migrations/`
- 迁移运行器：`scripts/db_migrate.py`
- 目标元数据：`triaxus.database.models.Base`（即本项目内的 OceanographicData、DataSource 等表）

## 前置条件

- 已安装并可访问 PostgreSQL 实例
- Python 依赖：`alembic`、`SQLAlchemy`、`psycopg2-binary`
- 环境变量配置数据库连接（推荐）：
  - `export DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<db>`

如未设置 `DATABASE_URL`，迁移程序会尝试从 `SecureDatabaseConfigManager` 获取连接串，否则回退至默认 `postgresql://user:password@localhost:5432/triaxus_db`。

## 快速上手

1) 查看当前数据库所处版本

```
python3 scripts/db_migrate.py current
```

2) 初始化生产数据库的版本标记（不变更结构）

- 如果生产库已经手工建表或通过应用初始化完成，建议直接“盖章”为基线版本：
```
python3 scripts/db_migrate.py stamp 0001_initial_baseline
```
- 若是全新数据库，建议先运行应用的初始化流程或编写首个“创建表”的迁移，再执行升级（见下文）。

3) 升级到最新版本

```
python3 scripts/db_migrate.py upgrade head
```

4) 回退一个版本（示例）

```
python3 scripts/db_migrate.py downgrade -1
```

5) 查看历史

```
python3 scripts/db_migrate.py history
```

## 创建新迁移

当模型（`triaxus.database.models`）发生变化时：

- 自动生成迁移（推荐）：
```
python3 scripts/db_migrate.py revision -m "add new column" --autogenerate
```
Alembic 会根据模型元数据与当前数据库差异生成迁移脚本（位于 `db_migrations/versions/`）。请务必审阅生成的 `upgrade()` 与 `downgrade()`，确保只包含预期变更且适配生产数据（必要时加入数据迁移、安全检查等逻辑）。

- 手工创建迁移：
```
python3 scripts/db_migrate.py revision -m "custom migration"
```
随后在生成的文件中手写 `upgrade()`/`downgrade()`。

完成后，执行升级：
```
python3 scripts/db_migrate.py upgrade head
```

## 使用建议（生产环境）

- 在维护窗口执行迁移，提前备份数据库。
- 对潜在破坏性操作（如列类型变更、列删除）进行灰度或分步迁移：
  - 新增列 → 双写 → 回填数据 → 切换读取 → 下线旧列。
- 始终实现可回退的 `downgrade()`，并在预生产环境演练升级与回退。
- 对长时间锁表操作（如大型索引重建）评估影响，考虑 `CONCURRENTLY`（注意 Alembic/事务限制）。

## 常见问题

- 无法连接数据库：确认 `DATABASE_URL` 正确、网络连通性与权限。
- 模型与库结构差异太大自动生成不准确：改为手工编辑迁移脚本。
- 多环境管理：通过设置不同环境的 `DATABASE_URL` 执行同一套迁移。

## 目录结构

```
db_migrations/
  alembic.ini         # Alembic 配置
  env.py              # 迁移环境，指向 triaxus.database.models.Base
  script.py.mako      # 迁移模板
  versions/
    0001_initial_baseline.py  # 基线（无操作）的初始版本
scripts/
  db_migrate.py       # 迁移运行器 CLI
```

## 附录：示例命令

- 标记现有库为基线：
```
python3 scripts/db_migrate.py stamp 0001_initial_baseline
```
- 生成并应用迁移：
```
python3 scripts/db_migrate.py revision -m "add index on oceanographic_data" --autogenerate
python3 scripts/db_migrate.py upgrade head
```
- 回退到指定版本：
```
python3 scripts/db_migrate.py downgrade 0001_initial_baseline
```

> 提示：本迁移系统独立于 `triaxus_backend` 的 Alembic 配置，仅管理 `triaxus` 应用自身的数据模型。
