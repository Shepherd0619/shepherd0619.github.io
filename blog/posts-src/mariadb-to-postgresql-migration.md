---
title: "记一次从 MariaDB 迁移到 PostgreSQL 的踩坑经历"
date: 2026-07-11
source: https://blog.csdn.net/u012587406/article/details/162787412
categories: IT 运维
tags: [MariaDB, PostgreSQL, 数据库迁移, 运维]
---
## 记一次从 MariaDB 迁移到 PostgreSQL 的踩坑经历

### 背景

上周末把自托管 Gitea 的数据库从本地 MariaDB 10.3 迁移到了云 RDS PostgreSQL 16。整个过程从评估到完成大约一小时，但中间踩了几个坑，导致服务出现了几分钟的不可用。本文记录一下遇到的问题和经验，希望能帮到有同样需求的同学。

### 环境概况

| 组件 | 迁移前 | 迁移后 |
| --- | --- | --- |
| 数据库引擎 | MariaDB 10.3 | PostgreSQL 16 |
| 数据量 | ~120 MB，110 张表 | 不变 |
| 部署方式 | 本地自建 | 云 RDS 托管 |
| 数据库名 | gitea | gitea（不变） |

### 迁移方案选择

摆在我面前的有几条路：

1. **Gitea 自带的 dump-restore 命令** — `gitea dump` 导出 + `gitea restore` 导入，但跨数据库引擎的支持不明确
2. **pgloader** — 专门做 MySQL→PG 迁移的工具，理论上是最佳选择
3. **手动迁移** — Gitea 自动建表 + Python 脚本搬数据

我一开始选了 pgloader，结果连踩两个坑后发现它在这种场景下根本跑不通。

### 坑 1：云 RDS PostgreSQL 的 Schema 创建限制

pgloader 的迁移流程是先创建 schema（默认以数据库名命名），再创建表、导数据。但云 RDS PostgreSQL 的数据库 owner 是云厂商的系统账户（如 AWS RDS 的 `rdsadmin`、
阿里云
的 `aurora`），即使用 Super 账号登录，也无法在非自己所有的数据库中 `CREATE SCHEMA`。

```
ERROR: permission denied for database gitea
```

pgloader 即使设置 `create no tables`，仍然会在迁移开始前查找与数据库同名的 schema，找不到就报错。这个行为没有参数可以跳过。

**教训**：使用云 RDS 时，pgloader 的跨引擎自动迁移基本不可行。要么先用 pg\_dump/pg\_restore 手动建 schema，要么换其他方案。

### 坑 2（重大）：PostgreSQL Sequence 未同步

这是本次迁移最核心的故障。

#### 现象

Gitea 启动后 Web UI 正常显示（200 OK），仓库列表、代码浏览都没问题。但当我 push 一个 feature branch 时，post-receive hook 返回 **500 Internal Server Error**，branch 创建失败。

#### 排查

查看 Gitea 日志，报错是：

```
duplicate key value violates unique constraint "branch_pkey"
ERROR: duplicate key value violates unique constraint "branch_pkey"
DETAIL: Key (id)=(4) already exists.
```

一看就明白了：`branch_id_seq` 的当前值是 3，但 `branch` 表中 `MAX(id)` 已经是 1413。`nextval('branch_id_seq')` 返回 4 → 主键冲突。

#### 根因

从 MariaDB 批量迁移数据时，行数据（含自增 ID）被原样复制过来了，但 PostgreSQL 的 **sequences 没有被同步**。

MariaDB 的 `AUTO_INCREMENT` 是表级别的属性，MySQL dump 时会自动带上当前值。而 PostgreSQL 的 `SERIAL`/`BIGSERIAL` 是 sequence 对象，独立于表数据。用 Python 脚本、pgloader 等手动迁移工具时，如果不显式调用 `setval()`，所有的 sequences 都会停留在初始值。

我一开始只修了 `branch_id_seq`，push 测试通过了就没管其他的。结果用户在网页上创建 Pull Request 时又 500 了——因为 **100 个 sequences 全都没同步**，不只是 `branch`。

#### 修复

**教训**：

- `pg_dump`/`pg_restore` 会自动处理 sequence 同步，但手动迁移工具（Python 脚本、pgloader）不会
- 跨引擎迁移后，**必须验证所有 sequences**，不能只修第一个报错的
- 可以用 `SELECT * FROM pg_sequences WHERE schemaname = 'public'` 查看所有 sequence 状态

### 坑 3：迁移期间的外部因素叠加

修复 sequences 时，服务器突然变得完全无响应（
Cloudflare 
 返回 502 Bad Gateway）。SSH 连上去一看，load average **28.83**（2 核机器），iowait **82%**。

元凶是一个卡死的进程（`D` 状态，不可中断睡眠），占满了磁盘 I/O。这个进程跟数据库迁移完全无关——是之前某个 
Jenkins 
 job 残留的 `terraform` 进程。修复 sequences 触发了额外的数据库写操作，叠加原有的 I/O 饱和，直接把服务打挂了。

`kill -9` 之后，load 在 5 分钟内从 28 降到 3.5，服务恢复。

**教训**：

- 维护操作前检查服务器状态（`top`、`iostat`），确认没有异常进程
- 迁移数据库的同时产生大量 DB 写操作，会放大已有的 I/O 问题
- 业务操作和运维操作在同一台机器上时，故障会相互放大

### 经验总结

#### 迁移流程建议

跨引擎数据迁移的正确姿势：

1. **在目标库建好 schema** — 让 Gitea（或目标应用）自己在 PG 上跑 migration，保证 DDL 与代码版本一致。不要手动翻译 MySQL DDL
2. **只搬数据，不搬 schema** — 用 Python/Go 脚本逐表 `INSERT INTO ... SELECT * FROM ...`
3. **修正 sequences** — 数据迁移后立即用 `setval()` 同步所有 sequences
4. **验证读写** — 不只是看列表页，要测创建（INSERT）、编辑（UPDATE）、删除（DELETE）等写操作
5. **监控服务器状态** — 维护期间持续关注 CPU、内存、磁盘 I/O

#### 为什么不能让 Gitea 直接用 pgloader 迁移

| 条件 | pgloader 预期 | 云 RDS 实际情况 |
| --- | --- | --- |
| CREATE SCHEMA | 需要 | 禁止（非 owner） |
| 数据库 owner | 迁移用户 | 云厂商系统账户 |
| 表结构翻译 | pgloader 自动 | Gitea 的 DDL 更准确 |

让 Gitea 自己在 PG 上建表，保证了字段类型、默认值、索引都与 Gitea 版本精确匹配，比任何自动翻译工具都靠谱。

#### 最重要的一个提醒

> **跨数据库引擎迁移后，一定要同步 sequences！**

这个坑不限于 Gitea，任何使用自增主键的 PostgreSQL 数据库，只要经历了手动数据批量导入，都必须做这一步。记住了能省很多排查时间。

---

*迁移日期：2026-07-11 | 目标引擎：PostgreSQL 16（云 RDS） | 源引擎：MariaDB 10.3*