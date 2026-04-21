# CrossReview Architecture Learning Notes

> Status: working reference
> Purpose: 记录从 `claude-code` 多代理与验证设计中学到的可迁移经验，用于指导 CrossReview 后续架构演进
> Scope: 本文档是架构学习与演进参考，不替代 [docs/v0-scope.md](/Users/weixin.li/Desktop/Sopify/cross-review/docs/v0-scope.md) 的 v0 执行边界

---

## 1. 为什么写这份文档

CrossReview 当前已经有了比较清晰的 v0 主张：

- `pack` 是一等能力
- `verify` 是下一阶段主线
- 价值来源是 context isolation，不是 model diversity
- v0 只做 `code_diff`
- v0 输出 advisory verdict，不做 block

但在真正从 Prompt Lab 转向实现时，问题会从“prompt 是否有效”变成“runtime 应该如何分层”和“哪些职责必须分离”。这时单看 v0-scope 还不够，需要一个更偏工程实现的参考文档，回答三个问题：

1. 外部成熟系统是怎么做多角色验证和多代理隔离的
2. 这些做法里哪些值得 CrossReview 学，哪些不值得学
3. 对 CrossReview 自己，下一阶段最合理的目标架构是什么

这份文档的作用就是把这些问题写清楚，便于后续实现 `verify`、`normalizer`、`adjudicator`，以及未来可能的 `validator` / `adjudicator` 扩展。

---

## 2. 当前 CrossReview 状态

截至当前仓库状态，CrossReview 已有以下基础：

- `crossreview/schema.py`
  - 已定义 `ReviewPack` / `ReviewResult` / `Finding` / `ReviewerMeta` / `QualityMetrics`
  - 已有 `validate_review_pack()` / `validate_review_result()`
- `crossreview/pack.py`
  - 已能从 git diff 组装 `ReviewPack`
  - 已能计算 fingerprint 和 `pack_completeness`
  - 已在输出前强制做 `validate_review_pack()`
- `crossreview/cli.py`
  - `crossreview pack` 已工作
  - `crossreview verify` 仍是 stub

这意味着：

- CrossReview 的“输入边界”已经开始成形
- CrossReview 的“输出边界”也已有 schema 壳
- 真正缺的是 `verify` 主链路，也就是：
  - reviewer 调用
  - raw analysis 保留
  - deterministic normalizer
  - deterministic adjudicator / verdict
  - output formatting

换句话说，下一阶段不是继续论证“要不要做产品”，而是把 `verify` 的内部 runtime 结构立起来。

---

## 3. 从 claude-code 观察到的架构事实

本节不是泛泛讨论“多 agent 很厉害”，而是记录在 `claude-code` 仓库里实际存在的设计。

### 3.1 它至少有三层代理抽象

#### A. 普通 subagent

最轻的一层是普通子代理。它的核心价值不是“扮演角色”，而是：

- 上下文隔离
- 并行执行
- 针对特定任务临时运行

相关证据：

- [Agent prompt usage notes](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/AgentTool/prompt.ts#L255)
- [analytics agent types](/Users/weixin.li/Desktop/Sopify/claude-code/src/services/analytics/metadata.ts#L486)

#### B. coordinator + worker

第二层是显式编排模式：

- coordinator 负责拆任务和综合信息
- worker 负责 research / implementation / verification

最关键的是，它不是笼统说“让 agent 干活”，而是把工程工作流写成了明确阶段：

- Research
- Synthesis
- Implementation
- Verification

相关证据：

- [Coordinator role and workflow](/Users/weixin.li/Desktop/Sopify/claude-code/src/coordinator/coordinatorMode.ts#L116)
- [Task workflow phases](/Users/weixin.li/Desktop/Sopify/claude-code/src/coordinator/coordinatorMode.ts#L204)

#### C. team + teammate

第三层是长生命周期团队模型，不再是“一次调用一个 worker”，而是：

- team 配置
- teammate 成员
- 共享 task list
- 点对点消息
- idle 通知
- 团队恢复和 reconnection

相关证据：

- [TeamCreate workflow](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/TeamCreateTool/prompt.ts#L39)
- [Teammate spawn path](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/AgentTool/AgentTool.tsx#L284)
- [Teammate identity/runtime context](/Users/weixin.li/Desktop/Sopify/claude-code/src/utils/teammate.ts#L44)
- [Swarm reconnection](/Users/weixin.li/Desktop/Sopify/claude-code/src/utils/swarm/reconnection.ts#L23)

### 3.2 它不是只有并行，还强调“第二层 QA”

这点对 CrossReview 最有价值。

`claude-code` 在 coordinator prompt 里明确写到：

- implementation worker 自己跑测试和 typecheck，只算第一层 QA
- 独立 verification worker 是第二层 QA

相关证据：

- [First-layer QA vs separate verification worker](/Users/weixin.li/Desktop/Sopify/claude-code/src/coordinator/coordinatorMode.ts#L328)

这说明它的设计不是“让实现者顺手说一句 done”，而是明确承认：

- 实现者自检不足以构成独立验证
- verification 必须有角色隔离
- verification 必须和 implementation 分离

这和 CrossReview 的核心主张高度同构。

### 3.3 它有内建 verification agent，而且要求强输出契约

`claude-code` 里有一个内建 `verification` agent，且角色定义非常强：

- 目标不是确认实现者说得对
- 目标是尝试把实现搞坏，主动找最后 20% 的问题
- 禁止修改项目
- 要求跑真实命令
- 必须输出 `VERDICT: PASS|FAIL|PARTIAL`

相关证据：

- [Verification system prompt](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/AgentTool/built-in/verificationAgent.ts#L10)
- [Required verdict line](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/AgentTool/built-in/verificationAgent.ts#L117)
- [Built-in registration](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/AgentTool/builtInAgents.ts#L64)

这说明：

- 它把 verification 当成独立能力，不是实现流程的尾注
- 它要求 verification 有硬契约，而不是自由发挥
- 它通过读写权限限制，保证 verification 的角色纯度

### 3.4 teammate 不是普通 subagent 的别名

`claude-code` 里 teammate 和普通 subagent 是两类东西，不应该混为一谈。

teammate 的额外特征包括：

- 有团队身份和名字
- 可以互相发消息
- 共享 task list
- 有 idle 状态和可恢复状态
- roster 是 flat 的，teammate 不能再 spawn teammate

相关证据：

- [Teammate communication addendum](/Users/weixin.li/Desktop/Sopify/claude-code/src/utils/swarm/teammatePromptAddendum.ts#L11)
- [Teammates cannot spawn other teammates](/Users/weixin.li/Desktop/Sopify/claude-code/src/tools/AgentTool/AgentTool.tsx#L266)

这对 CrossReview 的启发是：

- “多个角色”不等于“需要 team runtime”
- 角色隔离可以先做成无状态角色调用
- 只有当需要长期协作、持续消息、共享任务列表时，才需要 teammate 级复杂度

---

## 4. 对 CrossReview 最有价值的学习点

本节只写“该学什么”，不写炫技项。

### 4.1 角色隔离必须是真隔离，不是提示词里换个口吻

CrossReview 的价值主张本来就是 context isolation。`claude-code` 的经验进一步证明：

- implementation 角色和 verification 角色必须分开
- verifier 不应共享 implementer 的推理链
- verifier 的输入应是稳定工件，而不是 implementation session 的历史上下文

映射到 CrossReview：

- `ReviewPack` 是 verifier 的主输入
- verifier 不应该看到宿主 session 的全量上下文
- verifier 必须被提醒：`intent/focus/task` 是待验证背景声明，不是真相；`diff` 和 `evidence` 才是优先证据

### 4.2 “实现者自检”不能代替“独立验证”

如果 `crossreview verify` 未来只做成：

- 调一下 LLM reviewer
- 跑个 normalizer
- 出 JSON

那它仍然只是“第一次意见生成器”，还不是更强的验证系统。

真正值得学习的是：

- reviewer 和 verifier 可以是两个逻辑角色
- reviewer 负责提出候选问题
- verifier 负责检查候选问题是否站得住
- normalizer / adjudicator 再做最终结构化收口

这和 `claude-code` 的“双层 QA”思路是一致的，只是 CrossReview 会更 artifact-first、更 deterministic。

### 4.3 输出必须有硬边界

`claude-code` verification agent 强制要求 `VERDICT: PASS|FAIL|PARTIAL`。这反映了一个关键工程原则：

- 如果验证结果没有稳定边界，下游很难消费
- verification 不应该只吐一段看起来很聪明的自然语言

映射到 CrossReview：

- `ReviewResult` 必须是硬契约
- `pack_fingerprint` 必须强校验
- `reviewer.model` 必须存在
- `review_status` / `advisory_verdict` / `quality_metrics` 必须是稳定字段

CrossReview 当前 `schema.py` 已经在这个方向上了，后续不要退回到“先把字符串吐出来再说”。

### 4.4 只读 verifier 很有价值

`claude-code` 的 verification agent 被明确限制：

- 不能改项目文件
- 不能做 git 写操作
- 只能验证

CrossReview 虽然不是直接执行 bash/browser 的 verifier，但同样应该坚持“验证角色尽量纯”：

- reviewer 不负责修复代码
- normalizer 不负责发明新 finding
- adjudicator 不负责二次猜测 reviewer 的意图

每层只做一件事，才能保证可审计和可调试。

### 4.5 复杂 team runtime 不是早期必需品

`claude-code` 的 team / teammate 很强，但它解决的是：

- 长生命周期协作
- 团队内消息传递
- 任务分发
- UI/状态恢复

CrossReview 当前最缺的不是这些，而是：

- `pack -> reviewer -> normalizer -> verdict` 闭环
- 输出边界稳定
- 评测和实现共用统一 contract

因此，至少在 v0 和紧随其后的 Phase 1，不应把精力投到：

- 长生命周期多 agent runtime
- mailbox
- team roster
- idle 状态
- teammate UI

这些会大幅增加复杂度，但不会直接提高 v0 的验证质量。

---

## 5. 不该直接照搬的部分

为了避免“看到成熟系统就想全学”，这里明确列出不建议直接搬进 CrossReview 的部分。

### 5.1 不照搬 team / teammate 基础设施

原因：

- CrossReview 是 artifact-first verification harness，不是交互式 swarm orchestrator
- 当前用户面对的是 `pack` / `verify` 命令和 `ReviewPack` / `ReviewResult` 契约
- team runtime 会把产品重心从“验证协议”拉偏到“运行时协作平台”

### 5.2 不照搬 coordinator 作为最终控制中枢

CrossReview 更适合：

- 用 deterministic pipeline 作为主干
- 用 reviewer / verifier 作为可替换计算节点

而不是：

- 搭一个中心 coordinator，在运行时口头综合所有 agent 输出

后者更适合通用 coding agent，不适合需要结果稳定性和可评测性的 verification harness。

### 5.3 不照搬“用户会话内持续协作”的交互模式

`claude-code` 的很多设计依赖交互式对话和异步 agent 生命周期。CrossReview 则应优先保证：

- 同一输入的可重复性
- 输出契约稳定
- 和 eval harness 对齐

所以 CrossReview 的设计中心应继续是：

- pack contract
- result contract
- deterministic normalization / adjudication

而不是异步对话体验。

---

## 6. CrossReview 推荐目标架构

本节给出推荐的中期目标架构。它不是 v0 承诺清单，而是 `verify` 主线应逐步演进到的结构。

### 6.1 分层图

```text
Host / CLI
  |
  v
Pack Builder
  - git diff
  - changed_files
  - intent / task / focus / context_files
  - evidence passthrough
  - validate_review_pack()
  |
  v
Review Runtime
  - budget gate
  - reviewer invocation
  - raw analysis capture
  |
  +------------------------------+
  |                              |
  v                              v
Finding Normalizer           Optional Validator
  - deterministic parse        - independent check of candidate findings
  - finding extraction         - drop hallucinations / confirm evidence
  - locatability/confidence    - future phase, not v0 required
  |
  +--------------+
                 |
                 v
Deterministic Adjudicator
  - evidence cross-check
  - severity/verdict rules
  - review_status / advisory_verdict
  - quality metrics
  - validate_review_result()
  |
  v
Output Formatter
  - human
  - json
  - eval harness consumption
```

### 6.2 角色定义

#### Pack Builder

职责：

- 组装 `ReviewPack`
- 计算 fingerprint
- 在输出边界调用 `validate_review_pack()`

不负责：

- 运行 reviewer
- 给出 verdict

当前状态：

- 已基本落地

#### Reviewer

职责：

- 在隔离上下文中消费 `ReviewPack`
- 输出原始分析文本 `raw_analysis`
- 可以是自由文本或半结构化 markdown

不负责：

- 最终 JSON schema 输出
- 最终 verdict
- 修改代码

当前状态：

- 还未落地

#### Finding Normalizer

职责：

- 从 `raw_analysis` 中提取结构化 `Finding`
- 进行 deterministic mapping
- 处理：
  - file / line / diff_hunk
  - severity / confidence / locatability
  - summary / detail / category

不负责：

- 重新发明 reviewer 观点
- 再调一个 LLM 兜底

推荐原则：

- v0 保持 deterministic
- 如果 parse 不稳，优先视为 reviewer/prompt 质量问题，而不是再加 LLM fallback

#### Validator

职责：

- 对 candidate findings 做独立核查
- 判断 finding 是否能被 diff / evidence / context 支撑
- 过滤 reviewer 幻觉

不负责：

- 生成最终人类输出

状态建议：

- 这是很值得学 `claude-code verification agent` 的部分
- 但不一定要在 v0 第一版就落地
- 可以作为 `v0.1 / phase 2` 的增强层

#### Deterministic Adjudicator

职责：

- 把 normalizer 和 validator 的结果收口成稳定 verdict
- 基于规则输出：
  - `review_status`
  - `advisory_verdict`
  - `quality_metrics`
  - 最终 findings

不负责：

- 再次调用 LLM 做主观判决

这层是 CrossReview 和一般 agent orchestration 最大的不同之一：

- 结果收口必须 deterministic
- 否则无法稳定评测，也无法复现

---

## 7. 推荐演进路线

这里给出从当前仓库状态往后走的推荐顺序。

### Phase 1: 把 `verify` 主链路跑通

目标：

- 从 `ReviewPack` 到 `ReviewResult` 真正可跑

建议顺序：

1. 接 reviewer invocation
2. 保存 `raw_analysis`
3. 做最小 deterministic normalizer
4. 做最小 deterministic adjudicator
5. 在输出边界调用 `validate_review_result()`

第一版不要做：

- 多 reviewer 并行
- team runtime
- validator agent
- cross-model

### Phase 2: 引入独立 validator

目标：

- 把 reviewer 的“候选问题生成”与“独立核查”分开

可以有两种实现思路：

1. **deterministic validator**
   - 基于 diff、path、evidence、locatability 做规则核验
   - 优点：稳定、便宜、好测
   - 缺点：对语义问题能力有限

2. **isolated validator**
   - 给 validator 同一个 `ReviewPack`，再附 candidate findings
   - 要求它只做“支撑/不支撑”判断，不重新自由发挥
   - 优点：能补语义核查
   - 缺点：复杂度和波动更高

推荐：

- 先 deterministic validator
- 再考虑 isolated validator

### Phase 3: 如有必要，再考虑 adjudicator 扩展

当有以下需求时，再考虑更强 adjudication：

- 多 reviewer 输出冲突
- reviewer 与 validator 结论冲突
- 需要 workflow-level cross-validation 指标

这时才值得引入：

- multi-pass reviewer
- reviewer / validator disagreement handling
- optional adjudicator role

但在此之前，不要预支复杂度。

---

## 8. 对现有 v0 文档的补充解释

`docs/v0-scope.md` 里当前已经写了：

- reviewer 先输出自由分析
- deterministic parser 提取 finding
- deterministic adjudicator 收口

这和本文并不冲突。本文的补充价值在于把这些抽象和外部成熟系统做了映射：

- `fresh_llm_reviewer`
  - 对应成熟系统中的 implementation-independent review role
- `Finding Normalizer`
  - 对应“不要让模型直接承担最终结构化边界”的工程化手段
- `deterministic adjudicator`
  - 对应“最终输出不能完全依赖自由文本推断”
- 未来 `validator`
  - 对应成熟系统里的 second-layer QA / verification worker

因此，CrossReview 当前的文档方向是对的，只是还缺一份“为什么这么分层”和“哪些外部经验值得吸收”的工程注释，本文正是补这一层。

---

## 9. 对后续实现的具体建议

### 9.1 `verify` 第一版输入输出建议

`verify` 第一版至少支持两种入口：

- `crossreview verify --diff ...`
- `crossreview verify --pack pack.json`

内部流程建议统一成：

1. 先拿到 `ReviewPack`
2. `validate_review_pack()`
3. 调 reviewer
4. 保存 `raw_analysis`
5. normalizer
6. adjudicator
7. `validate_review_result()`
8. 输出

### 9.2 `raw_analysis` 一定要保留

原因：

- 这是审计证据
- 这是 prompt 调优依据
- 这是 normalizer 失败时的 debug 基础
- 后续如果引入 validator，也需要对照它判断 reviewer 是否在胡说

不要为了“整洁”把 `raw_analysis` 丢掉。

### 9.3 `validator` 如果要做，先限制输入边界

如果未来要加 validator，建议输入明确固定为：

- 原始 `ReviewPack`
- candidate findings
- reviewer raw_analysis 摘要或片段

并明确要求 validator：

- 不重新做开放式 review
- 只判断 candidate finding 是否被输入证据支撑
- 输出 supported / unsupported / unclear

否则 validator 很容易退化成第二个 reviewer，导致职责混乱。

### 9.4 不要把“多 agent”误当成“质量提升的自动保证”

成熟系统给出的真正经验不是“多几个 agent 就更强”，而是：

- 角色边界清晰才会更强
- 输入边界清晰才会更强
- 输出契约清晰才会更强

如果没有这些前提，多角色只会增加噪声和成本。

---

## 10. 一句话总结

从 `claude-code` 学到的最重要经验不是“要做 agent team”，而是：

> 把实现、候选问题生成、独立验证、最终收口分成不同职责层，并让最终输出保持 deterministic contract。

对 CrossReview 来说，真正值得学习的是：

- verification 是独立角色
- 第二层 QA 很重要
- 输出必须有硬边界
- 角色越纯，系统越可调试

而不值得过早学习的是：

- team runtime
- teammate mailbox
- 长生命周期 swarm orchestration

CrossReview 当前最合理的主线，仍然是把下面这条链路做扎实：

```text
pack -> reviewer -> raw_analysis -> deterministic normalizer -> deterministic adjudicator -> ReviewResult
```

如果未来需要进一步提升质量，再在这条主链上增加：

```text
pack -> reviewer -> validator -> adjudicator
```

而不是把产品重心提前转向团队运行时。
