# CrossReview v0 Prompt Lab + Phase 1 — 设计

## Prompt Lab 落地结构

### 目录结构

```
prompt-lab/
├── README.md              # 说明：目标、怎么跑、怎么记录
├── prompt-template.md     # 固定的 reviewer prompt 模板
├── cases/
│   ├── 001-xxx/
│   │   ├── diff.patch     # 原始 diff
│   │   ├── pack.json      # 手工组装的 ReviewPack
│   │   ├── manual-findings.yaml  # 手工 cross-review baseline
│   │   ├── raw-output.md  # 模型原始输出
│   │   └── adjudication.yaml  # 人工判定
│   └── 002-xxx/
└── run.py                 # 单脚本 runner
```

### run.py 工作流

1. 读取 `cases/<name>/pack.json`
2. 将 pack 内容注入 `prompt-template.md` 的占位符
3. 调用 LLM（isolated session，无历史上下文）
4. 保存 raw output 到 `cases/<name>/raw-output.md`
5. 记录 model / latency_sec / input_tokens / output_tokens

### prompt-template.md 关键设计

- intent/focus/task 标注为 "background claims, NOT verified truth"
- raw diff 是优先证据
- 要求 reviewer 先自由分析，不强制输出 JSON schema
- 要求区分 plausible vs speculative
- 防合理化约束："Do not talk yourself out of a finding"

### 人工 adjudication 格式

每个 case 的 `adjudication.yaml` 记录：

- 每个 auto finding 的 judgment (valid/invalid/unclear)
- matched_manual_id（关联手工 baseline）
- actionability_judgment
- 观察笔记

### Phase 0.5 Gate 判定

完成 3-5 个 case 后，回答三个问题：

1. **模型是否能稳定给出真问题？** → valid rate 是否 > 50%
2. **需要哪些 context 才能给出真问题？** → 哪些 case 因缺 context 导致质量差
3. **主要噪音来自 prompt 还是 pack 缺失？** → invalid finding 的根因分类

如果通过 → 进入 Phase 1。

---

## Phase 1 工程结构预览

> 以下是 Phase 1 进入后的目标结构，当前不实现。

```
crossreview/
├── __init__.py
├── schema.py           # ReviewPack / Finding / ReviewResult dataclass
├── pack.py             # pack 构建逻辑
├── evidence.py         # deterministic_evidence collector
├── budget.py           # budget gate
├── reviewer.py         # fresh_llm_reviewer
├── normalizer.py       # FindingNormalizer（从 raw analysis 提取 Finding）
├── adjudicator.py      # deterministic adjudicator
├── formatter.py        # JSON / human-readable output
└── config.py           # 配置加载

cli/
├── __init__.py
└── main.py             # crossreview pack / verify 命令
```

### Reviewer Backend Strategy

`fresh_llm_reviewer` 是逻辑角色，不等同于某个固定 provider SDK 调用。

v0 采用两层设计：

1. `ReviewerBackend` 抽象接口
2. 具体 backend 实现

默认优先级：

1. 若宿主提供 fresh-session reviewer backend，则优先使用 host-integrated same-model fresh review
2. 否则使用 standalone provider backend
3. 若用户显式指定 provider / model，则按显式 override 解析

v0 当前分支的首个 concrete backend 可先实现 `AnthropicReviewerBackend`，用于跑通 standalone `crossreview verify`。后续宿主接入只需新增 `HostSessionReviewerBackend`，不改变 budget / normalizer / adjudicator 链路。

### FindingNormalizer 关键约束

v0 的 normalizer 只做 deterministic extraction，不引入 LLM fallback。

具体：
- 首选且唯一实现路径：regex / heuristic 从 reviewer 的半结构化 markdown 中提取 Finding
- parse 失败视为 reviewer / prompt 质量信号
- 不允许通过第二次 LLM 调用补 extraction，否则会稀释 "reviewer 只有一种 + adjudicator deterministic" 的语义
