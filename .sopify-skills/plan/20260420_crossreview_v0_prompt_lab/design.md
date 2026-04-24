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

## Phase 1 工程结构（已实现）

```
crossreview/
├── __init__.py
├── schema.py           # ReviewPack / Finding / ReviewResult dataclass
├── pack.py             # pack 构建逻辑
├── budget.py           # budget gate
├── reviewer.py         # ReviewerBackend 接口 + Anthropic standalone
├── normalizer.py       # FindingNormalizer（从 raw analysis 提取 Finding）
├── adjudicator.py      # deterministic adjudicator
├── ingest.py           # host-integrated ingest pipeline（raw analysis → ReviewResult）
├── config.py           # 配置加载（CLI > YAML > env 优先级链）
├── cli.py              # crossreview pack / verify / render-prompt / ingest 命令
└── core/
    ├── __init__.py
    └── prompt.py        # canonical reviewer prompt 模板 + 渲染（product/v0.1）
```

### 待实现模块

- `evidence.py` — deterministic evidence collector（命令执行 + 结果收集）
- `formatter.py` — human-readable output formatter (`--format human`)

### Reviewer Backend Strategy

`fresh_llm_reviewer` 是逻辑角色，不等同于某个固定 provider SDK 调用。

v0 采用两层设计：

1. `ReviewerBackend` 抽象接口（`crossreview/reviewer.py`）
2. 具体 backend 实现

**两种执行路径**：

| 路径 | 使用场景 | CLI 命令 |
|------|----------|----------|
| **Host-integrated** | 宿主（Copilot CLI / Claude Code 等）在隔离上下文中执行 | `render-prompt` → 宿主执行 → `ingest` |
| **Standalone** | 直接调用 LLM API | `verify` |

Host-integrated 路径不需要实现 Python `ReviewerBackend` 类。宿主通过 CLI 管道完成集成：

```bash
# 1. 渲染 canonical prompt
crossreview render-prompt --pack pack.json > prompt.md

# 2. 宿主在隔离上下文执行 prompt（宿主自行实现）
host_execute_in_fresh_session prompt.md > raw-output.md

# 3. 回传 raw analysis → ReviewResult
crossreview ingest --raw-analysis raw-output.md --pack pack.json --model host_model
```

Standalone 路径使用 `ReviewerBackend` 接口 + 具体 provider 实现（当前：`AnthropicReviewerBackend`）。

### FindingNormalizer 关键约束

v0 的 normalizer 只做 deterministic extraction，不引入 LLM fallback。

具体：
- 首选且唯一实现路径：regex / heuristic 从 reviewer 的半结构化 markdown 中提取 Finding
- parse 失败视为 reviewer / prompt 质量信号
- 不允许通过第二次 LLM 调用补 extraction，否则会稀释 "reviewer 只有一种 + adjudicator deterministic" 的语义
