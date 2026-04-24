# Plan Preview Fixtures

v1+ plan artifact 验证的预备 case 集合。

## 状态

**Not active** — 当前 eval harness 不消费这些 case。等 `artifact_type: plan` 实现后启用。

## 与 code_diff fixtures 的关系

| 目录 | artifact_type | eval harness |
|------|--------------|--------------|
| `fixtures/001-*` ~ `020-*` | code_diff | ✅ 活跃 |
| `fixtures/plan-preview/*` | plan | ❌ 预备 |

## Case 格式

```
plan-preview/
└── 001-feishu-webhook/
    ├── fixture.yaml        # fixture_id, artifact_type, pool
    ├── intent.md           # 原始需求（对应 ReviewPack.intent）
    ├── background.md       # 方案包文件
    ├── design.md
    └── tasks.md
```

## v1 启用时需要补充

- `pack.json` — plan artifact 的 ReviewPack（需要 pack assembly 支持 `--plan`）
- `review-result.json` — verify 产出
- `manual-findings.yaml` — 人工 baseline
- `auto-adjudications.yaml` — 自动 finding 判定

## 来源

Case 来自 Sopify 方案包的真实产出（`ai-daily-brief` 项目的飞书推送方案）。
