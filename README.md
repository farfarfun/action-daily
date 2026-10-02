# action-daily

farfarfun 组织的定时任务集合：把公开仓库镜像同步到 Gitee，并对照组织开发规范
（[farfarfun/todo-list](https://github.com/farfarfun/todo-list) 的 `SPEC.md`）
滚动做合规审计、自动提交修复。

本仓库只有 GitHub Actions workflow 和配套的 Python 脚本，不是可安装的包，没有 PyPI 发布。

## Mirror to Gitee

`Mirror to Gitee` 每 2 小时增量运行一次，每天额外跑一次全量（Asia/Shanghai 凌晨），
也可手动触发（`workflow_dispatch`，可强制全量）。它会把 `farfarfun` 组织下所有**公开**
仓库（含 fork）镜像同步到 Gitee 的 `farfarfun` 组织，不会同步私有仓库。

镜像本身由 [`farfarfun-action/mirror-repo`](https://github.com/farfarfun-action/mirror-repo)
完成——我们自己写的 Action，底层调用 [`farfarfun/funmirror`](https://github.com/farfarfun/funmirror)
这个两阶段（detect 高并发探测 commit sha → sync 低并发 clone+push）镜像流水线，
详细架构图见该仓库的 README。增量档只查 GitHub 一侧的 commit sha，命中
`.mirror-state/gitee.json` 里记录的状态就跳过；全量档同时查询 GitHub 和 Gitee 两侧，
忽略状态文件，自愈任何漂移（例如有人手动改动了 Gitee 上的仓库）。状态文件每次运行后
都会提交回本仓库，以便在无状态的 runner 之间延续。

需要在本仓库的 Actions secrets 中配置：

- `GITEE_TOKEN`：Gitee 私人令牌，需要有 `projects` 权限，用于在 `farfarfun` 组织下创建/更新仓库。
- `GITEE_RSA_PRIVATE_KEY`：用于推送代码的 SSH 私钥，对应公钥需添加到该 Gitee 账号的 SSH 公钥中。
- `ACTION_GITHUB_TOKEN`：org 级 GitHub token，用于列举组织仓库。

配置好后，Gitee 侧需已存在 `farfarfun` 组织（个人无法在他人组织下自动建仓）。

## Codex 规范审计

两条 workflow 配合，一条找问题、一条修问题，issue 统一建在 `farfarfun/todo-list`：

| workflow | 定时 | 做什么 |
| --- | --- | --- |
| `codex-find-issues.yml` | 每 5 小时一批 | 按游标滚动选一批仓库，用 Codex CLI 对照 `SPEC.md` 做只读审计，命中就建 issue（label `codex-audit`） |
| `codex-fix-issues.yml` | 每小时 5 条 | 取最旧的 open `codex-audit` issue，clone 目标仓库交给 Codex CLI 修复，直接提交到默认分支并关闭 issue |

脚本分工：

- `scripts/codex_audit_cursor.py`：算本轮批次，游标存 `scripts/codex_audit_cursor.json`（跨运行保留，会提交回本仓库）
- `scripts/run_codex_audit.py`：逐仓库 clone + 跑 Codex，发现写 `scripts/codex_audit_findings.json`
- `scripts/file_codex_audit_issues.py`：按仓库聚合、过滤 low 置信度、去重后建 issue
- `scripts/codex_audit_schema.json`：Codex 输出的 JSON schema

需要的 Actions secrets：`ACTION_GITHUB_TOKEN`（跨仓库读写 issue 与 clone 私有仓库）、
`OPENAI_API_KEY`、`OPENAI_BASE_URL`（走自定义/代理的 OpenAI 兼容端点）。

### 本地运行

脚本只用 Python 3.12 标准库，不需要安装依赖，但需要本机已有
[`gh`](https://cli.github.com/)（已登录）和 [`codex`](https://github.com/openai/codex) CLI：

```bash
# 准备：SPEC.md / mapping.json 来自 todo-list，克隆一份供脚本读取
git clone --depth 1 https://github.com/farfarfun/todo-list.git todo-list-ref
export TODO_LIST_DIR="$PWD/todo-list-ref"

# 1) 选本轮批次（会推进 scripts/codex_audit_cursor.json 里的游标）
python3 scripts/codex_audit_cursor.py

# 只想扫指定仓库时跳过上一步，手写批次文件即可
echo '["funfile", "funget"]' > scripts/codex_audit_batch.json

# 2) 跑审计（结果写 scripts/codex_audit_findings.json）
export ORG_PAT="<github token>"           # clone 目标仓库用，含私有仓库
export OPENAI_API_KEY="<key>"
export OPENAI_BASE_URL="<endpoint>"       # 可选，留空则走官方 OpenAI 端点
export PYTHON_STANDARDS_PATH="<lang-spec-hub>/skills/python-development-standards/SKILL.md"
python3 scripts/run_codex_audit.py

# 3) 建 issue（默认直接写到 farfarfun/todo-list，先看 findings 再执行）
python3 scripts/file_codex_audit_issues.py
```

`ORG_PAT` 只通过环境变量传入，clone 时用 `http.extraheader` 认证，不会写进命令行参数
或目标仓库的 `.git/config`。

Gitee 镜像没有本地入口，逻辑都在 `farfarfun-action/mirror-repo` 里，本地复现请直接用
`farfarfun/funmirror`。

---

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
