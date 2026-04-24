# CrossReview Reviewer Prompt Template (product/v0.1)

You are an independent code reviewer. You have NO access to the original development session, conversation history, or the author's reasoning process. You are seeing this code change for the first time.

## Your Input

**Task Intent** (background claim — NOT verified truth):
add wiki command

**Task Description** (background claim — NOT verified truth):
(no task file provided)

**Focus Areas** (author's suggestion — verify independently):
(no focus specified)

**Context Files**:
(no context files provided)

**Changed Files**:
- .claude-plugin/marketplace.json (json)
- .claude-plugin/plugin.json (json)
- .codex-plugin/plugin.json (json)
- README.md (markdown)
- README_CN.md (markdown)
- bootstrap-lite.md (markdown)
- bootstrap.md (markdown)
- gemini-extension.json (json)
- package.json (json)
- scripts/cli-messages.mjs (javascript)
- scripts/notify.mjs (javascript)
- skills/commands/help/SKILL.md (markdown)
- skills/commands/wiki/SKILL.md (markdown)
- tests/runtime-chain.test.mjs (javascript)

**Evidence** (deterministic tool output):
[]

**Code Diff**:
```diff
diff --git a/.claude-plugin/marketplace.json b/.claude-plugin/marketplace.json
index f5b0c14..13bee97 100644
--- a/.claude-plugin/marketplace.json
+++ b/.claude-plugin/marketplace.json
@@ -9,7 +9,7 @@
     {
       "name": "helloagents",
       "description": "Quality-driven orchestration kernel for AI CLIs: intelligent routing, quality verification, safety guards, and notifications",
-      "version": "3.0.2",
+      "version": "3.0.3",
       "source": "./",
       "author": {
         "name": "HelloWind",
diff --git a/.claude-plugin/plugin.json b/.claude-plugin/plugin.json
index cefc428..00ecf39 100644
--- a/.claude-plugin/plugin.json
+++ b/.claude-plugin/plugin.json
@@ -1,6 +1,6 @@
 {
   "name": "helloagents",
-  "version": "3.0.2",
+  "version": "3.0.3",
   "description": "HelloAGENTS — The orchestration kernel that makes any AI CLI smarter. Adds intelligent routing, quality verification (Ralph Loop), safety guards, and notifications.",
   "author": "HelloWind",
   "license": "Apache-2.0",
diff --git a/.codex-plugin/plugin.json b/.codex-plugin/plugin.json
index 250972b..7c048b6 100644
--- a/.codex-plugin/plugin.json
+++ b/.codex-plugin/plugin.json
@@ -1,6 +1,6 @@
 {
   "name": "helloagents",
-  "version": "3.0.2",
+  "version": "3.0.3",
   "description": "HelloAGENTS — Quality-driven orchestration kernel for AI CLIs with intelligent routing, quality verification (Ralph Loop), safety guards, and notifications.",
   "author": {
     "name": "HelloWind",
diff --git a/README.md b/README.md
index 9ca700c..27fa44a 100644
--- a/README.md
+++ b/README.md
@@ -226,7 +226,7 @@ Codex CLI does not need a manual plugin command. `helloagents --global` now inst
 ```
 💡【HelloAGENTS】- Help
 
-Available commands: ~auto, ~design, ~prd, ~loop, ~init, ~test, ~verify, ~review, ~commit, ~clean, ~help
+Available commands: ~auto, ~design, ~prd, ~loop, ~wiki, ~init, ~test, ~verify, ~review, ~commit, ~clean, ~help
 
 Auto-activated skills (14): hello-ui, hello-api, hello-security, hello-test, hello-verify, hello-errors, hello-perf, hello-data, hello-arch, hello-debug, hello-subagent, hello-review, hello-write, hello-reflect
 ```
@@ -297,7 +297,8 @@ All commands run inside AI chat with the `~` prefix:
 
 | Command | Purpose |
 |---------|---------|
-| `~init` | Initialize project knowledge base (`.helloagents/`) |
+| `~wiki` | Create or sync the project knowledge base only (`.helloagents/`) |
+| `~init` | Full project bootstrap: KB + project-local carrier files |
 | `~commit` | Generate conventional commit message + KB sync |
 | `~clean` | Archive completed plans, clean temp files |
 | `~help` | Show all commands and current config |
@@ -328,7 +329,7 @@ Only include keys you want to override — missing keys use defaults.
 | `notify_level` | `0` | `0`=off, `1`=desktop, `2`=sound, `3`=both |
 | `ralph_loop_enabled` | `true` | Auto-run verification after task completion |
 | `guard_enabled` | `true` | Block dangerous commands |
-| `kb_create_mode` | `1` | `0`=off, `1`=auto on coding tasks, `2`=always |
+| `kb_create_mode` | `1` | `0`=off, `1`=auto on coding tasks in activated projects or global mode, `2`=always in activated projects or global mode |
 | `commit_attribution` | `""` | Empty = no attribution. Set text to append to commit messages |
 | `install_mode` | `"standby"` | `"standby"` = per-project activation (lite rules), `"global"` = full rules for all projects |
 
@@ -394,7 +395,7 @@ HelloAGENTS supports two installation modes with different installation methods:
 
 | Mode | Install Method | Rules | Skills | Best For |
 |------|---------------|-------|--------|----------|
-| **Standby** (default) | `helloagents install <target> --standby` or `helloagents install --all --standby` | `bootstrap-lite.md` (lite rules) | `~command` on demand, `~init` for full activation | Selective use, keeping other projects unaffected |
+| **Standby** (default) | `helloagents install <target> --standby` or `helloagents install --all --standby` | `bootstrap-lite.md` (lite rules) | `~command` on demand, project activation via `.helloagents/` (`~wiki` or `~init`) | Selective use, keeping other projects unaffected |
 | **Global** | Manual plugins for Claude/Gemini; native local-plugin auto-install for Codex | `bootstrap.md` (full rules) | 14 skills auto-activate | All-in on HelloAGENTS across every project |
 
 Standby mode injects rules into `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md`, and `~/.codex/AGENTS.md`; Codex then loads that local merged file via `developer_instructions` in `~/.codex/config.toml`. Each CLI also gets a `helloagents` package-root symlink. Claude Code and Gemini still use hooks where their host surfaces support quiet injection well. Codex deliberately does **not** enable HelloAGENTS hooks by default: the latest pre-source shows hook lifecycle output in TUI and does not honor `suppressOutput` as a true silent injection path, so Codex relies on the injected rules file plus the local symlink/native plugin layout instead. In global mode, Claude Code uses plugin hooks from `.claude-plugin/plugin.json`, Gemini loads `bootstrap.md` via `contextFileName` plus extension hooks, and Codex uses the native local-plugin chain (marketplace + local plugin root + cache + plugin enablement in `config.toml`) without plugin hooks.
@@ -424,9 +425,9 @@ After every task, Ralph Loop auto-runs your project's verification commands:
 
 ### Knowledge Base (`.helloagents/`)
 
-`~init` creates a project-local knowledge base. `STATE.md` is a project-level recovery snapshot, not a universal memory file for every interaction.
+`~wiki` creates or syncs the project-local knowledge base only. `~init` is the fuller bootstrap: it also writes project-local carrier files (`AGENTS.md`, `CLAUDE.md`, `.gemini/GEMINI.md`), refreshes the project `skills/helloagents` link, and appends the related ignore rules. In standby mode, the presence of `.helloagents/` is what promotes the current project into the full project workflow; project-local carrier files are optional.
 
-It is created and continuously updated for long-running project workflows such as `~init`, `~design`, `~auto`, `~prd`, and `~loop`; updated when already present for verification/review style tasks; and intentionally not created for one-off read-only interactions such as `~help`.
+`STATE.md` is a project-level recovery snapshot, not a universal memory file for every interaction. It is created and continuously updated for long-running project workflows such as `~wiki`, `~init`, `~design`, `~auto`, `~prd`, and `~loop`; updated when already present for verification/review style tasks; and intentionally not created for one-off read-only interactions such as `~help`.
 
 | File | Purpose |
 |------|---------|
@@ -483,7 +484,7 @@ The test suite validates:
 
 **A:** Everything. The v3 line is a complete rewrite:
 - Python package → pure Node.js/Markdown architecture
-- 15 commands → 11 commands + 14 auto-activated quality skills
+- 15 commands → 12 commands + 14 auto-activated quality skills
 - 6 CLI targets → 3 (Claude Code + Codex CLI + Gemini CLI)
 - New: checklist gate control, guard system, ~prd, ~loop, ~verify, design system generation
 - See [Version History](#-version-history) for full details.
@@ -520,13 +521,13 @@ Subagents may skip workflow packaging such as routing, interaction flow, and out
 <details>
 <summary><strong>Q: What is standby vs global mode?</strong></summary>
 
-**A:** Standby mode (default) deploys lite rules to the targets you choose, typically with `helloagents install <target> --standby` or `helloagents install --all --standby`. Projects need `~init` to activate full features. Global mode uses each CLI's native plugin/extension system for full rules everywhere; deploy it with `helloagents install <target> --global`, `helloagents install --all --global`, or bulk-switch with `helloagents --global`.
+**A:** Standby mode (default) deploys lite rules to the targets you choose, typically with `helloagents install <target> --standby` or `helloagents install --all --standby`. A project enters the full project flow once it has `.helloagents/`, usually via `~wiki` (KB only) or `~init` (full bootstrap). Global mode uses each CLI's native plugin/extension system for full rules everywhere; deploy it with `helloagents install <target> --global`, `helloagents install --all --global`, or bulk-switch with `helloagents --global`.
 </details>
 
 <details>
 <summary><strong>Q: Where does project knowledge go?</strong></summary>
 
-**A:** In the project-local `.helloagents/` directory. Created by `~init`, auto-synced on code changes (controlled by `kb_create_mode`). `STATE.md` is used as a concise recovery snapshot for long-running workflows, not as a catch-all memory file for every interaction.
+**A:** In the project-local `.helloagents/` directory. It can be created by `~wiki` (KB only) or `~init` (full project bootstrap), then auto-synced on code changes according to `kb_create_mode`. `STATE.md` is used as a concise recovery snapshot for long-running workflows, not as a catch-all memory file for every interaction.
 </details>
 
 <details>
@@ -643,7 +644,15 @@ Subagents may skip workflow packaging such as routing, interaction flow, and out
 
 ## 📈 Version History
 
-### v3.0.2 (current)
+### v3.0.3 (current)
+
+**Workflow and KB activation:**
+- ✨ Added `~wiki` for creating or syncing `.helloagents/` without writing project-local carrier files
+- 🔧 Clarified the activation boundary: in standby mode, `.helloagents/` is the actual project activation signal; project-local carrier files remain optional and belong to `~init`
+- 🔧 Refined `kb_create_mode` wording across bootstrap, help text, and README so it only describes sync timing inside activated projects or global mode
+- 🧪 Added routing coverage for `~wiki` and kept standby `.helloagents/` activation behavior under test
+
+### v3.0.2
 
 **Fixes and verification:**
 - 🔧 Removed the Codex-only static runtime-context block that had been reintroduced into generated `AGENTS.md` carriers in standby/global installs
diff --git a/README_CN.md b/README_CN.md
index 7dfd5fd..609a23c 100644
--- a/README_CN.md
+++ b/README_CN.md
@@ -226,7 +226,7 @@ Codex CLI 无需手动执行插件命令。`helloagents --global` 会自动走
 ```
 💡【HelloAGENTS】- 帮助
 
-可用命令: ~auto, ~design, ~prd, ~loop, ~init, ~test, ~verify, ~review, ~commit, ~clean, ~help
+可用命令: ~auto, ~design, ~prd, ~loop, ~wiki, ~init, ~test, ~verify, ~review, ~commit, ~clean, ~help
 
 自动激活技能 (14): hello-ui, hello-api, hello-security, hello-test, hello-verify, hello-errors, hello-perf, hello-data, hello-arch, hello-debug, hello-subagent, hello-review, hello-write, hello-reflect
 ```
@@ -297,7 +297,8 @@ HelloAGENTS 在不同模式下会写入不同文件，但写入/恢复/清理都
 
 | 命令 | 说明 |
 |------|------|
-| `~init` | 初始化项目知识库（`.helloagents/`） |
+| `~wiki` | 仅创建/同步项目知识库（`.helloagents/`） |
+| `~init` | 完整初始化项目：知识库 + 项目级载体文件 |
 | `~commit` | 生成规范化提交信息 + 知识库同步 |
 | `~clean` | 归档已完成方案，清理临时文件 |
 | `~help` | 显示所有命令和当前配置 |
@@ -328,7 +329,7 @@ HelloAGENTS 在不同模式下会写入不同文件，但写入/恢复/清理都
 | `notify_level` | `0` | `0`=关闭，`1`=桌面通知，`2`=声音，`3`=两者 |
 | `ralph_loop_enabled` | `true` | 任务完成时自动运行验证 |
 | `guard_enabled` | `true` | 拦截危险命令 |
-| `kb_create_mode` | `1` | `0`=关闭，`1`=编码任务自动，`2`=始终 |
+| `kb_create_mode` | `1` | `0`=关闭，`1`=已激活项目或全局模式中的编码任务自动，`2`=已激活项目或全局模式中始终 |
 | `commit_attribution` | `""` | 空=不添加，填写内容则追加到 commit message |
 | `install_mode` | `"standby"` | `"standby"`=按项目激活（精简规则），`"global"`=所有项目启用完整规则 |
 
@@ -394,7 +395,7 @@ HelloAGENTS 支持两种安装模式，采用不同的安装方式：
 
 | 模式 | 安装方式 | 规则 | 技能 | 适用场景 |
 |------|---------|------|------|----------|
-| **标准模式** (默认) | `helloagents install <target> --standby` 或 `helloagents install --all --standby` | `bootstrap-lite.md`（精简规则） | `~command` 按需使用，`~init` 激活完整功能 | 按需使用，不影响其他项目 |
+| **标准模式** (默认) | `helloagents install <target> --standby` 或 `helloagents install --all --standby` | `bootstrap-lite.md`（精简规则） | `~command` 按需使用，通过 `.helloagents/` 激活项目（`~wiki` 或 `~init`） | 按需使用，不影响其他项目 |
 | **全局模式** | Claude/Gemini 手动装插件；Codex 自动装原生本地插件 | `bootstrap.md`（完整规则） | 14 个技能自动激活 | 全面使用 HelloAGENTS |
 
 标准模式会把规则注入到 `~/.claude/CLAUDE.md`、`~/.gemini/GEMINI.md`、`~/.codex/AGENTS.md`；其中 Codex 再通过 `~/.codex/config.toml` 中的 `developer_instructions` 加载这个本地合并后的文件。每个 CLI 还会创建 `helloagents` 包根目录符号链接。Claude Code 和 Gemini 仍使用 hooks，因为宿主可以较安静地承载这类注入；Codex 默认**不启用** HelloAGENTS hooks：最新 pre 源码里 hook 生命周期会在 TUI 中可见显示，且 `suppressOutput` 不能作为真正的静默注入通道，所以 Codex 改为依赖注入后的规则文件，以及本地符号链接 / 原生本地插件目录结构。全局模式下，Claude Code 通过 `.claude-plugin/plugin.json` 中声明的 hooks 工作，Gemini 通过 `contextFileName=bootstrap.md` 和扩展 hooks 工作；Codex 仍使用原生本地插件安装链路（marketplace + 本地插件目录 + cache + `config.toml` 插件启用段），但不启用插件 hooks。
@@ -424,9 +425,9 @@ HelloAGENTS 支持两种安装模式，采用不同的安装方式：
 
 ### 知识库（`.helloagents/`）
 
-`~init` 创建项目本地知识库。`STATE.md` 是项目级恢复快照，不是所有交互的统一记忆文件。
+`~wiki` 只创建或同步项目本地知识库。`~init` 是更完整的项目初始化：它还会写入项目级载体文件（`AGENTS.md`、`CLAUDE.md`、`.gemini/GEMINI.md`）、刷新项目 `skills/helloagents` 链接，并补齐相关忽略项。在标准模式下，真正让当前项目进入完整项目流程的是 `.helloagents/` 的存在，项目级载体文件只是 `~init` 的附加能力。
 
-它会在 `~init`、`~design`、`~auto`、`~prd`、`~loop` 这类项目级连续流程中创建并持续更新；在验证/审查类任务中仅在文件已存在时更新；对 `~help` 这类一次性只读交互则不会创建。
+`STATE.md` 是项目级恢复快照，不是所有交互的统一记忆文件。它会在 `~wiki`、`~init`、`~design`、`~auto`、`~prd`、`~loop` 这类项目级连续流程中创建并持续更新；在验证/审查类任务中仅在文件已存在时更新；对 `~help` 这类一次性只读交互则不会创建。
 
 | 文件 | 用途 |
 |------|------|
@@ -483,7 +484,7 @@ npm test
 
 **A：** 全部重写了：
 - Python 包 → 纯 Node.js/Markdown 架构
-- 15 个命令 → 11 个命令 + 14 个自动激活质量技能
+- 15 个命令 → 12 个命令 + 14 个自动激活质量技能
 - 6 个 CLI 目标 → 3 个（Claude Code + Codex CLI + Gemini CLI）
 - 新增：检查清单门控、Guard 系统、~prd、~loop、~verify、设计系统生成
 - 详见[版本历史](#-版本历史)。
@@ -520,13 +521,13 @@ npm test
 <details>
 <summary><strong>Q：标准模式和全局模式有什么区别？</strong></summary>
 
-**A：** 标准模式（默认）把精简规则部署到你明确指定的目标 CLI，通常用 `helloagents install <target> --standby` 或 `helloagents install --all --standby`。项目需要 `~init` 才能激活完整功能。全局模式使用各 CLI 原生的插件/扩展系统，所有项目自动启用完整规则；可用 `helloagents install <target> --global`、`helloagents install --all --global`，或通过 `helloagents --global` 做整套切换。
+**A：** 标准模式（默认）把精简规则部署到你明确指定的目标 CLI，通常用 `helloagents install <target> --standby` 或 `helloagents install --all --standby`。项目只要建立了 `.helloagents/` 就会进入完整项目流程，通常通过 `~wiki`（仅知识库）或 `~init`（完整初始化）完成。全局模式使用各 CLI 原生的插件/扩展系统，所有项目自动启用完整规则；可用 `helloagents install <target> --global`、`helloagents install --all --global`，或通过 `helloagents --global` 做整套切换。
 </details>
 
 <details>
 <summary><strong>Q：项目知识存在哪里？</strong></summary>
 
-**A：** 项目本地的 `.helloagents/` 目录。由 `~init` 创建，代码变更时自动同步（由 `kb_create_mode` 控制）。其中 `STATE.md` 只作为长流程任务的精简恢复快照，不承担所有交互的统一记忆。
+**A：** 项目本地的 `.helloagents/` 目录。可以由 `~wiki`（仅知识库）或 `~init`（完整项目初始化）创建；之后会按 `kb_create_mode` 在代码变更场景中自动同步。其中 `STATE.md` 只作为长流程任务的精简恢复快照，不承担所有交互的统一记忆。
 </details>
 
 <details>
@@ -643,7 +644,15 @@ npm test
 
 ## 📈 版本历史
 
-### v3.0.2（当前版本）
+### v3.0.3（当前版本）
+
+**流程与知识库激活：**
+- ✨ 新增 `~wiki`，用于只创建或同步 `.helloagents/`，不写项目级载体文件
+- 🔧 明确标准模式下的激活边界：`.helloagents/` 才是项目进入完整流程的实际信号；项目级载体文件仍属于 `~init` 的职责
+- 🔧 统一修正 bootstrap、帮助文本和 README 中 `kb_create_mode` 的表述，使其只描述已激活项目或全局模式下的同步时机
+- 🧪 新增 `~wiki` 路由覆盖，并持续验证标准模式下基于 `.helloagents/` 的激活行为
+
+### v3.0.2
 
 **修复与验证：**
 - 🔧 移除误回流到 Codex 标准/全局安装产物 `AGENTS.md` 中的静态运行时上下文前缀
diff --git a/bootstrap-lite.md b/bootstrap-lite.md
index 886d9f7..d02e9db 100644
--- a/bootstrap-lite.md
+++ b/bootstrap-lite.md
@@ -142,7 +142,7 @@ templates/ 查找路径（按优先级，找到即停）：
 - STATE.md — ≤50 行，项目级恢复快照。读完它就能接上工作，不需要再读其他文件；它不是所有交互的统一记忆载体
   内容：正在做什么、关键上下文（决策/变更/假设）、下一步（具体可执行动作含文件路径）、阻塞项
   适用边界：
-  - 强制创建并持续更新：`~init`、`~design`、`~auto`、`~prd`、`~loop`
+  - 强制创建并持续更新：`~wiki`、`~init`、`~design`、`~auto`、`~prd`、`~loop`
   - 强制更新，不要求首次创建：`~clean`，主代理汇总子代理结果后
   - 已有则更新：`~review`、`~verify`、`~test`、`~commit`
   - 不创建：`~help`、未激活项目中的普通问答或一次性只读任务、子代理自身执行过程、压缩/恢复钩子
@@ -159,7 +159,7 @@ templates/ 查找路径（按优先级，找到即停）：
 - archive/YYYY-MM/ — 已归档的方案包（整个 plans/{feature}/ 目录移入）
 - archive/_index.md — 归档索引
 
-### 知识沉淀（受 kb_create_mode 控制，0=关闭/1=编码自动/2=始终）
+### 知识沉淀（受 kb_create_mode 控制，0=关闭/1=已激活项目中的编码自动/2=已激活项目中始终）
 - context.md — 项目架构、技术栈、目录结构、模块索引
 - guidelines.md — 编码约定（仅含非显而易见的约定）
 - CHANGELOG.md — 变更历史
diff --git a/bootstrap.md b/bootstrap.md
index 238e196..0795d6f 100644
--- a/bootstrap.md
+++ b/bootstrap.md
@@ -164,6 +164,7 @@ output_format 为 false 时，所有回复保持自然输出，不适用以下
 ### 1. ORIENT — 感知环境
 根据任务需要，按需读取项目上下文（知识库文件和项目文件）。
 若当前项目已存在由 `~init` 生成的 AGENTS.md / CLAUDE.md / .gemini/GEMINI.md，这些载体已由宿主自动加载，无需再次读取。
+当前项目只要已建立 `.helloagents/`（例如执行过 `~wiki`、`~init`，或已进入项目级连续流程），就按项目级完整流程执行，不要求项目根载体一定存在。
 简单任务：无额外操作。
 复杂任务：主动读取相关知识库文件和项目文件，理解现有架构。
 
@@ -206,7 +207,7 @@ hello-* 技能查找路径（按优先级，找到即停）：
 所有任务：
 - `STATE.md` 维护：按上文“流程状态”中的适用边界执行。属于“强制创建并持续更新”范围时，重写 `.helloagents/STATE.md`（"正在做什么"更新为已完成，清空关键上下文/下一步/阻塞项）；属于“已有则更新”范围时，仅在文件已存在时重写；属于“不创建”范围时不生成此文件
 - 有方案包且任务已完成 → 将整个 plans/{feature}/ 目录归档到 .helloagents/archive/YYYY-MM/，并更新 archive/_index.md。清理临时文件（loop-results.tsv、.ralph-breaker.json）
-- 按 kb_create_mode 同步知识库（0=关闭/1=编码自动/2=始终）：
+- 按 kb_create_mode 同步知识库（0=关闭/1=已激活项目或全局模式中的编码自动/2=已激活项目或全局模式中始终）：
   - .helloagents/ 不存在则按 templates/ 创建知识库文件（context.md、guidelines.md、verify.yaml、CHANGELOG.md、modules/）
   - 已存在但不完整（缺少上述核心文件）→ 按 templates/ 补全缺失文件，不覆盖已有文件
   - 已存在且完整则按模板格式更新 CHANGELOG.md、相关 modules/*.md、增量经验 delta 追加
@@ -239,7 +240,7 @@ templates/ 查找路径（按优先级，找到即停）：
 - STATE.md — ≤50 行，项目级恢复快照。读完它就能接上工作，不需要再读其他文件；它不是所有交互的统一记忆载体
   内容：正在做什么、关键上下文（决策/变更/假设）、下一步（具体可执行动作含文件路径）、阻塞项
   适用边界：
-  - 强制创建并持续更新：`~init`、`~design`、`~auto`、`~prd`、`~loop`，以及进入统一执行流程的项目级连续任务
+  - 强制创建并持续更新：`~wiki`、`~init`、`~design`、`~auto`、`~prd`、`~loop`，以及进入统一执行流程的项目级连续任务
   - 强制更新，不要求首次创建：`~clean`，主代理汇总子代理结果后
   - 已有则更新：`~review`、`~verify`、`~test`、`~commit`
   - 不创建：`~help`、一次性只读任务、子代理自身执行过程、压缩/恢复钩子
@@ -256,7 +257,7 @@ templates/ 查找路径（按优先级，找到即停）：
 - archive/YYYY-MM/ — 已归档的方案包（整个 plans/{feature}/ 目录移入）
 - archive/_index.md — 归档索引
 
-### 知识沉淀（受 kb_create_mode 控制，0=关闭/1=编码自动/2=始终）
+### 知识沉淀（受 kb_create_mode 控制，0=关闭/1=已激活项目或全局模式中的编码自动/2=已激活项目或全局模式中始终）
 - context.md — 项目架构、技术栈、目录结构、模块索引
 - guidelines.md — 编码约定（仅含非显而易见的约定）
 - CHANGELOG.md — 变更历史
diff --git a/gemini-extension.json b/gemini-extension.json
index eb2c19a..22de811 100644
--- a/gemini-extension.json
+++ b/gemini-extension.json
@@ -1,6 +1,6 @@
 {
   "name": "helloagents",
-  "version": "3.0.2",
+  "version": "3.0.3",
   "description": "Quality-driven orchestration kernel for AI CLIs",
   "contextFileName": "bootstrap.md",
   "author": "HelloWind",
diff --git a/package.json b/package.json
index 84264a7..185a1af 100644
--- a/package.json
+++ b/package.json
@@ -1,6 +1,6 @@
 {
   "name": "helloagents",
-  "version": "3.0.2",
+  "version": "3.0.3",
   "type": "module",
   "description": "HelloAGENTS — The orchestration kernel that makes any AI CLI smarter. Adds intelligent routing, quality verification (Ralph Loop), safety guards, and notifications.",
   "author": "HelloWind",
diff --git a/scripts/cli-messages.mjs b/scripts/cli-messages.mjs
index 0c33335..4497504 100644
--- a/scripts/cli-messages.mjs
+++ b/scripts/cli-messages.mjs
@@ -41,16 +41,16 @@ export function createInstallMessagePrinter({ home, pkgVersion, msg }) {
       ));
     } else {
       if (isInstall) console.log(msg(
-        `\n  ✅ HelloAGENTS 已安装（standby 模式）！\n\n    Claude Code:  已自动配置（~/.claude/CLAUDE.md + hooks）\n    Gemini CLI:   已自动配置（~/.gemini/GEMINI.md）\n    Codex:        ${codexStandbyStatus()}\n\n  standby 模式下，hello-* 技能不会自动触发。\n  在项目中使用 ~init 激活完整功能，或使用 ~command 按需调用。\n\n  切换模式：\n    helloagents --global    全局模式（Claude/Gemini 装插件；Codex 自动装原生本地插件）`,
-        `\n  ✅ HelloAGENTS installed (standby mode)!\n\n    Claude Code:  Auto-configured (~/.claude/CLAUDE.md + hooks)\n    Gemini CLI:   Auto-configured (~/.gemini/GEMINI.md)\n    Codex:        ${codexStandbyStatus()}\n\n  In standby mode, hello-* skills won't auto-trigger.\n  Use ~init in a project to activate full features, or use ~command on demand.\n\n  Switch modes:\n    helloagents --global    Global mode (manual plugins for Claude/Gemini; native local plugin auto-install for Codex)`,
+        `\n  ✅ HelloAGENTS 已安装（standby 模式）！\n\n    Claude Code:  已自动配置（~/.claude/CLAUDE.md + hooks）\n    Gemini CLI:   已自动配置（~/.gemini/GEMINI.md）\n    Codex:        ${codexStandbyStatus()}\n\n  standby 模式下，hello-* 技能不会自动触发。\n  在项目中使用 ~wiki 仅创建/同步知识库，或用 ~init 完整初始化项目；也可用 ~command 按需调用。\n\n  切换模式：\n    helloagents --global    全局模式（Claude/Gemini 装插件；Codex 自动装原生本地插件）`,
+        `\n  ✅ HelloAGENTS installed (standby mode)!\n\n    Claude Code:  Auto-configured (~/.claude/CLAUDE.md + hooks)\n    Gemini CLI:   Auto-configured (~/.gemini/GEMINI.md)\n    Codex:        ${codexStandbyStatus()}\n\n  In standby mode, hello-* skills won't auto-trigger.\n  Use ~wiki to create or sync the KB only, or ~init for the full project bootstrap; ~command stays available on demand.\n\n  Switch modes:\n    helloagents --global    Global mode (manual plugins for Claude/Gemini; native local plugin auto-install for Codex)`,
       ));
       else console.log(msg(
         isRefresh
           ? `  standby 模式已刷新，CLI 注入与链接已同步最新文件。\n  ${REMOVE_HINT}`
-          : `  项目需通过 ~init 激活完整功能，未激活项目仅注入通用规则。\n  ${REMOVE_HINT}`,
+          : `  项目可通过 ~wiki 创建/同步知识库，或通过 ~init 完整初始化；未激活项目仅注入通用规则。\n  ${REMOVE_HINT}`,
         isRefresh
           ? `  Standby mode refreshed; injected files and links were synchronized.\n  ${REMOVE_HINT}`
-          : `  Projects need ~init to activate full features. Unactivated projects get lite rules only.\n  ${REMOVE_HINT}`,
+          : `  Projects can use ~wiki for KB-only activation or ~init for the full bootstrap. Unactivated projects get lite rules only.\n  ${REMOVE_HINT}`,
       ));
     }
     if (isInstall || isRefresh) console.log();
diff --git a/scripts/notify.mjs b/scripts/notify.mjs
index eebe4ab..5f0c4f6 100644
--- a/scripts/notify.mjs
+++ b/scripts/notify.mjs
@@ -96,7 +96,7 @@ function cmdRoute() {
   if (cmdMatch) {
     const skillName = cmdMatch[1];
     const extraRules = skillName === 'help'
-      ? ' 这是 HelloAGENTS 的帮助命令，不是宿主 CLI 的内置帮助。适用条件：仅显示 HelloAGENTS 的帮助和当前设置；优先使用当前上下文中已注入的“当前用户设置”，只有上下文不存在该信息时才尝试读取 ~/.helloagents/helloagents.json；自动激活技能说明仅在全局模式或当前项目已通过 ~init 激活后生效。排除条件：不要调用宿主 CLI 的帮助工具（如 cli_help 或 /help），不要使用子代理，不要读取项目文件；若受工作区限制无法读取配置，必须明确说明并按已知默认值或已注入设置展示；纯标准模式未激活项目不会自动触发。'
+      ? ' 这是 HelloAGENTS 的帮助命令，不是宿主 CLI 的内置帮助。适用条件：仅显示 HelloAGENTS 的帮助和当前设置；优先使用当前上下文中已注入的“当前用户设置”，只有上下文不存在该信息时才尝试读取 ~/.helloagents/helloagents.json；自动激活技能说明仅在全局模式，或当前项目已存在 .helloagents/（例如执行过 ~wiki 或 ~init）时生效。排除条件：不要调用宿主 CLI 的帮助工具（如 cli_help 或 /help），不要使用子代理，不要读取项目文件；若受工作区限制无法读取配置，必须明确说明并按已知默认值或已注入设置展示；纯标准模式未激活项目不会自动触发。'
       : '';
     suppressedOutput(EVENT_NAME.UserPromptSubmit, buildRouteInstruction({
       skillName,
diff --git a/skills/commands/help/SKILL.md b/skills/commands/help/SKILL.md
index 41a52dd..9a2b646 100644
--- a/skills/commands/help/SKILL.md
+++ b/skills/commands/help/SKILL.md
@@ -15,7 +15,8 @@ Trigger: ~help
 | ~design | 深度设计：交互式需求挖掘 + 方案设计 + 方案包 |
 | ~prd | 完整 PRD：头脑风暴式逐维度挖掘，生成现代产品需求文档 |
 | ~loop | 自主迭代优化：设定目标和指标，循环修改-验证-保留/回滚 |
-| ~init | 初始化项目知识库和配置 |
+| ~wiki | 仅创建/同步项目知识库（`.helloagents/`） |
+| ~init | 完整初始化项目：知识库 + 项目级载体配置 |
 | ~test | 为指定模块或最近变更编写完整测试 |
 | ~verify | 运行所有验证命令并报告结果 |
 | ~review | 代码审查 |
@@ -24,7 +25,7 @@ Trigger: ~help
 | ~help | 显示此帮助 |
 
 ### 自动激活技能
-适用条件：以下技能仅在全局模式，或当前项目已通过 `~init` 激活后自动激活：
+适用条件：以下技能仅在全局模式，或当前项目已存在 `.helloagents/` 后自动激活（例如执行过 `~wiki`、`~init`，或已处于项目级连续流程）：
 排除条件：纯标准模式未激活项目不会自动触发。
 
 编码时：hello-ui, hello-api, hello-data, hello-security, hello-errors, hello-perf, hello-arch, hello-test
@@ -41,5 +42,5 @@ Trigger: ~help
 | notify_level | 0 | 0=关闭/1=桌面通知/2=声音/3=两者 | Claude Code + Gemini CLI + Codex CLI |
 | ralph_loop_enabled | true | 自动验证循环（任务完成时触发 lint/test/build） | Claude Code + Gemini CLI + Codex CLI |
 | guard_enabled | true | 阻断危险命令与写入后的安全扫描 | Claude Code + Gemini CLI + Codex CLI |
-| kb_create_mode | 1 | 0=关闭/1=编码自动/2=始终 | Claude Code + Gemini CLI + Codex CLI |
+| kb_create_mode | 1 | 0=关闭/1=已激活项目或全局模式中的编码自动/2=已激活项目或全局模式中始终 | Claude Code + Gemini CLI + Codex CLI |
 | commit_attribution | "" | 空=不添加/填写内容则添加到 commit message | Claude Code + Gemini CLI + Codex CLI |
diff --git a/skills/commands/wiki/SKILL.md b/skills/commands/wiki/SKILL.md
new file mode 100644
index 0000000..8efa069
--- /dev/null
+++ b/skills/commands/wiki/SKILL.md
@@ -0,0 +1,57 @@
+---
+name: ~wiki
+description: 初始化或同步项目知识库（仅 `.helloagents/`，不写项目根载体）
+policy:
+  allow_implicit_invocation: false
+---
+Trigger: ~wiki
+
+`~wiki` 是用户显式命令，用于只创建、补全或同步项目本地知识库，不创建项目根 `AGENTS.md` / `CLAUDE.md` / `.gemini/GEMINI.md`，也不创建项目级 `skills/helloagents` symlink。适用于标准模式下希望保留项目目录为“非载体项目”，但仍希望当前项目拥有 `.helloagents/`、`STATE.md` 和知识沉淀文件的场景。
+
+`~wiki` 是显式知识库命令，不受 `kb_create_mode` 限制。
+
+## 流程
+
+### 阶段 1：基础准备（必做）
+
+1. 创建 `.helloagents/` 目录 + `STATE.md`（按 templates/STATE.md 格式）
+2. 追加 `.gitignore`（如果对应行不存在）：
+   ```
+   .helloagents/
+   ```
+3. 明确不执行以下操作：
+   - 不创建或更新项目根 `AGENTS.md`
+   - 不创建或更新项目根 `CLAUDE.md`
+   - 不创建或更新 `.gemini/GEMINI.md`
+   - 不创建项目级 `skills/helloagents` symlink
+
+### 阶段 2：知识库创建或补全（条件性）
+
+检查项目是否有实际代码文件（非空项目）：
+- 有代码文件 → 执行完整知识库创建/补全（下方流程）
+- 空项目 → 保留 `.helloagents/` 和 `STATE.md`，告知用户“项目为空，其余知识文件将在后续开发或首次编码任务中补全”
+
+知识库创建/补全流程：
+1. 按 templates/ 目录的模板格式，分析项目代码库后创建或补全：
+   - context.md — 按 templates/context.md 格式，填入项目概述、技术栈、架构、目录结构、模块链接
+   - guidelines.md — 按 templates/guidelines.md 格式，从现有代码推断编码约定
+   - verify.yaml — 验证命令（从 package.json/pyproject.toml 检测）
+   - CHANGELOG.md — 按 templates/CHANGELOG.md 格式创建或更新
+   - DESIGN.md — 如果项目包含 UI 代码，按 templates/DESIGN.md 格式提取设计系统
+2. 创建或补全 modules/ 目录，按 templates/modules/module.md 格式为主要模块生成文档
+3. 已存在的文件按模板格式增量更新，不自由改写结构；无新增信息时保持原样
+
+## verify.yaml 格式
+```yaml
+commands:
+  - npm run lint
+  - npm run test
+```
+
+## 幂等性
+重复执行 `~wiki` 是安全的：
+- `.helloagents/` 缺失时创建，已存在时复用
+- `STATE.md` 按当前任务状态重写，不追加历史
+- 知识库文件缺失时补全，已存在时按模板增量更新
+- `.gitignore` 只追加缺失行
+- 永不写入项目根载体文件，也不创建项目级 `skills/helloagents` symlink
diff --git a/tests/runtime-chain.test.mjs b/tests/runtime-chain.test.mjs
index 0036b5a..eeeadb6 100644
--- a/tests/runtime-chain.test.mjs
+++ b/tests/runtime-chain.test.mjs
@@ -62,6 +62,14 @@ test('notify route and inject cover standby, activated projects, and global mode
   assert.match(payload.hookSpecificOutput.additionalContext, /skills[\\\/]commands[\\\/]help[\\\/]SKILL\.md/);
   assert.match(payload.hookSpecificOutput.additionalContext, /不要再为同一个命令 skill 重复 Test-Path \/ Get-Content/);
 
+  result = runNode(notifyScript, ['route'], {
+    cwd: project,
+    env,
+    input: JSON.stringify({ cwd: project, prompt: '~wiki' }),
+  });
+  payload = parseStdoutJson(result);
+  assert.match(payload.hookSpecificOutput.additionalContext, /skills[\\\/]commands[\\\/]wiki[\\\/]SKILL\.md/);
+
   result = runNode(notifyScript, ['route'], {
     cwd: project,
     env,

```

## Critical Instructions

1. The intent, focus, task description, and context files are background claims, not verified truth. Prioritize what the raw diff shows over what these materials say should happen.
2. Do NOT assume the change is correct. Your job is to find what might be wrong, not to confirm it works.
3. Be specific. Every issue you raise must point to a concrete location in the diff when possible.
4. Do NOT rationalize. If something looks off, report it.
5. Only report findings you can verify from the diff. If your analysis requires assumptions about unseen code or runtime behavior, move it to Observations.
6. If the diff rewrites or transforms code, check semantic equivalence instead of only syntax.
7. For shell, command, or parser rewrites, check statement-boundary and continuation semantics. For example, shell `&&` or `||` at line end can continue across a newline; do not assume every newline terminates the statement unless the diff proves that behavior.

## Your Output

Analyze the diff thoroughly. Separate your output into two sections: Findings (issues verifiable from the diff) and Observations (notes that require assumptions about unseen code or context).

## Section 1: Findings

Number each finding as f-001, f-002, etc. For each finding provide:
- **Where**: file path and line number if identifiable
- **What**: one-sentence summary
- **Why**: brief technical explanation grounded in the diff
- **Severity estimate**: HIGH / MEDIUM / LOW
- **Category**: logic_error / missing_test / spec_mismatch / security / performance / missing_validation / semantic_equivalence / other

## Section 2: Observations

Use this section for context-dependent concerns that are not verifiable from the diff alone.

## Section 3: Overall Assessment

Provide a short overall assessment of the diff quality. If there are no findings, say so explicitly.

