# Fixtures

v0 eval harness 使用的 diff fixture 集合。

## 格式

每个 fixture 是一个目录：

```
fixtures/
├── 001-auth-refresh/
│   ├── diff.patch              # unified diff
│   ├── pack.json               # ReviewPack（可从 prompt-lab case 复制）
│   ├── manual-findings.yaml    # 手工 cross-review baseline（gold-ish）
│   └── auto-adjudications.yaml # 对自动 finding 的人工判定
└── 002-cache-layer/
    └── ...
```

## Manual Findings 格式

```yaml
fixture_id: "001-auth-refresh"
source: manual_fresh_session
reviewer_model: "claude-sonnet-4-20250514"
reviewed_at: "2026-04-20T16:00:00+08:00"

context_items:
  - type: diff
    path_or_desc: "src/auth/token.ts"
    required: true
    covered_by_pack: null    # eval 时人工标记

findings:
  - id: "mf-001"
    summary: "Token expiry off-by-one"
    file: "src/auth/token.ts"
    severity_estimate: high
```

## 分阶段目标

| 阶段 | 数量 | 目的 |
|------|------|------|
| Prompt Lab | 3-5 | 验证 prompt 质量 |
| Dev Milestone | 10 | 跑通 eval harness |
| Release Gate | ≥ 20 | v0 发布门槛 |

详见 [docs/v0-scope.md §4](../docs/v0-scope.md) 和 [§12](../docs/v0-scope.md)。

## Prompt Lab 与 Fixtures 的关系

- `prompt-lab/cases/` 是 Prompt Lab 当前使用的工作目录，采用 `--render-only` 渲染 prompt 后手动粘贴到模型会话
- `fixtures/` 是后续 eval harness 使用的正式 fixture 集合
- Prompt Lab 通过后，可把已验证的 case 迁移/复制到 `fixtures/`
- Prompt Lab 第一批 case 固定来自真实 commit，优先从 `cross-review/`、`helloagents/`、`hermes-agent/` 提取，且至少保留 1 个 clean diff
