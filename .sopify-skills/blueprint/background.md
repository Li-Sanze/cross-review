# CrossReview — 项目背景

## 是什么

CrossReview 是一个独立验证引擎，核心价值是 **context isolation**：用全新 LLM session（无生产过程上下文）对 code diff 进行独立审查，产出结构化 finding 和 advisory verdict。

## 当前产品定位

> 来源：`plan/20260425_crossreview_product_master_plan/`。以下为结论性摘要。

CrossReview 定位为 **独立审查基础设施 / external quality loop**：

- **核心差异化**：context isolation 是价值来源，不是 model diversity。审查质量来自隔离边界和确定性判定层（Normalizer + Adjudicator 全规则化），而不仅是"换个模型再看一遍"。
- **ReviewPack / ReviewResult** 是核心协议方向：结构化输入（diff + context）→ 结构化输出（findings + verdict），可被任意宿主或 CI 系统消费。
- **Release gate** 是质量门禁：9 指标阈值体系，不通过则退回 prompt pattern，不做产品发布。
- **与 Sopify 的关系**：CrossReview 是独立产品，Sopify 是首个深度集成宿主。CrossReview 不依赖 Sopify；Sopify 集成只能走 advisory 或 checkpoint proposal，不能直接写 Sopify state。
- **v0 通过前**：路线图仍以 plan 为准，不固化到 blueprint。

## 为什么做

手工 fresh-session cross-review 已被证明有效——新开 session 往往比原 session 的"自审"更容易发现回归、遗漏和逻辑不一致。但手工流程不可重复、不可度量、每次 ~5 分钟 copy-paste。

CrossReview 把这个手工模式协议化：ReviewPack（结构化输入）→ Finding（结构化输出）→ Verdict（建议性判定）。

## 上游决策来源

产品命名、架构边界、MVP 范围等核心决策来自 Sopify 上游方案包 `20260418_cross_review_engine`（Q1-Q9 已拍板，存放于 sopify-skills 仓库）。本仓库不依赖上游方案包文件，仅以 `docs/v0-scope.md` 为 canonical scope。

## 当前定位

验证型 incubator。不是正式产品发布仓库。v0 release gate 通过后再考虑产品化。
