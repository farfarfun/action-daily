# daily-action

farfarfun 组织的定时任务集合，参考 [farfarfun-skills/daily-action](https://github.com/farfarfun-skills/daily-action)。

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

配置好后，Gitee 侧需已存在 `farfarfun` 组织（个人无法在他人组织下自动建仓）。
