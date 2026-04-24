# CrossReview Reviewer Prompt Template (product/v0.1)

You are an independent code reviewer. You have NO access to the original development session, conversation history, or the author's reasoning process. You are seeing this code change for the first time.

## Your Input

**Task Intent** (background claim — NOT verified truth):
v0.4.21: fix #422 cluster-only KeyError total_files, fix #423 --update drops existing nodes

**Task Description** (background claim — NOT verified truth):
(no task file provided)

**Focus Areas** (author's suggestion — verify independently):
(no focus specified)

**Context Files**:
(no context files provided)

**Changed Files**:
- graphify/__main__.py (python)
- graphify/skill.md (markdown)

**Evidence** (deterministic tool output):
[]

**Code Diff**:
```diff
diff --git a/graphify/__main__.py b/graphify/__main__.py
index e2b3d9e..e9e39a2 100644
--- a/graphify/__main__.py
+++ b/graphify/__main__.py
@@ -1308,7 +1308,8 @@ def main() -> None:
         questions = suggest_questions(G, communities, labels)
         tokens = {"input": 0, "output": 0}
         report = generate(G, communities, cohesion, labels, gods, surprises,
-                          {}, tokens, str(watch_path), suggested_questions=questions)
+                          {"warning": "cluster-only mode — file stats not available"},
+                          tokens, str(watch_path), suggested_questions=questions)
         out = watch_path / "graphify-out"
         (out / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
         to_json(G, communities, str(out / "graph.json"))
diff --git a/graphify/skill.md b/graphify/skill.md
index eef1144..6ec8ae2 100644
--- a/graphify/skill.md
+++ b/graphify/skill.md
@@ -862,6 +862,17 @@ if deleted:
 # Merge: new nodes/edges into existing graph
 G_existing.update(G_new)
 print(f'Merged: {G_existing.number_of_nodes()} nodes, {G_existing.number_of_edges()} edges')
+
+# Write merged result back to .graphify_extract.json so Step 4 sees the full graph
+merged_out = {
+    'nodes': [{'id': n, **d} for n, d in G_existing.nodes(data=True)],
+    'edges': [{'source': u, 'target': v, **d} for u, v, d in G_existing.edges(data=True)],
+    'hyperedges': new_extraction.get('hyperedges', []),
+    'input_tokens': new_extraction.get('input_tokens', 0),
+    'output_tokens': new_extraction.get('output_tokens', 0),
+}
+Path('graphify-out/.graphify_extract.json').write_text(json.dumps(merged_out))
+print(f'[graphify update] Merged extraction written ({len(merged_out[\"nodes\"])} nodes, {len(merged_out[\"edges\"])} edges)')
 " 
 ```
 

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

