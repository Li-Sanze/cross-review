# CrossReview Reviewer Prompt Template (product/v0.1)

You are an independent code reviewer. You have NO access to the original development session, conversation history, or the author's reasoning process. You are seeing this code change for the first time.

## Your Input

**Task Intent** (background claim — NOT verified truth):
Fix 9 issues: kiro package data, betweenness perf, wiki step, opencode plugin, cache root, PHP missing edges, Windows stability, cross-file calls

**Task Description** (background claim — NOT verified truth):
(no task file provided)

**Focus Areas** (author's suggestion — verify independently):
(no focus specified)

**Context Files**:
(no context files provided)

**Changed Files**:
- graphify/__main__.py (python)
- graphify/analyze.py (python)
- graphify/cache.py (python)
- graphify/extract.py (python)
- graphify/skill.md (markdown)
- pyproject.toml (toml)
- tests/test_claude_md.py (python)

**Evidence** (deterministic tool output):
[]

**Code Diff**:
```diff
diff --git a/graphify/__main__.py b/graphify/__main__.py
index 5813d5c..ce3f3e2 100644
--- a/graphify/__main__.py
+++ b/graphify/__main__.py
@@ -156,6 +156,9 @@ def install(platform: str = "claude") -> None:
             claude_md.write_text(_SKILL_REGISTRATION.lstrip(), encoding="utf-8")
             print(f"  CLAUDE.md        ->  created at {claude_md}")
 
+    if platform == "opencode":
+        _install_opencode_plugin(Path("."))
+
     print()
     print("Done. Open your AI coding assistant and type:")
     print()
@@ -171,7 +174,7 @@ This project has a graphify knowledge graph at graphify-out/.
 Rules:
 - Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
 - If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
-- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
+- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
 """
 
 _CLAUDE_MD_MARKER = "## graphify"
@@ -325,7 +328,7 @@ Rules:
 - Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
 - If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
 - If the graphify MCP server is active, utilize tools like `query_graph`, `get_node`, and `shortest_path` for precise architecture navigation instead of falling back to `grep`
-- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
+- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
 """
 
 _ANTIGRAVITY_WORKFLOW = """\
@@ -487,7 +490,7 @@ This project has a graphify knowledge graph at graphify-out/.
 
 - Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
 - If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
-- After modifying code files in this session, run `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"` to keep the graph current
+- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)
 """
 
 
@@ -1235,7 +1238,8 @@ def main() -> None:
         if ok:
             print("Code graph updated. For doc/paper/image changes run /graphify --update in your AI assistant.")
         else:
-            print("Nothing to update or rebuild failed — check output above.")
+            print("Nothing to update or rebuild failed — check output above.", file=sys.stderr)
+            sys.exit(1)
 
     elif cmd == "benchmark":
         from graphify.benchmark import run_benchmark, print_benchmark
diff --git a/graphify/analyze.py b/graphify/analyze.py
index f953d9b..d9bd479 100644
--- a/graphify/analyze.py
+++ b/graphify/analyze.py
@@ -262,6 +262,8 @@ def _cross_community_surprises(
         # No community info - use edge betweenness centrality
         if G.number_of_edges() == 0:
             return []
+        if G.number_of_nodes() > 5000:
+            return []
         betweenness = nx.edge_betweenness_centrality(G)
         top_edges = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:top_n]
         result = []
@@ -360,7 +362,8 @@ def suggest_questions(
 
     # 2. Bridge nodes (high betweenness) → cross-cutting concern questions
     if G.number_of_edges() > 0:
-        betweenness = nx.betweenness_centrality(G)
+        k = min(100, G.number_of_nodes()) if G.number_of_nodes() > 1000 else None
+        betweenness = nx.betweenness_centrality(G, k=k)
         # Top bridge nodes that are NOT file-level hubs
         bridges = sorted(
             [(n, s) for n, s in betweenness.items()
diff --git a/graphify/cache.py b/graphify/cache.py
index d27edf1..03e62d3 100644
--- a/graphify/cache.py
+++ b/graphify/cache.py
@@ -79,7 +79,14 @@ def save_cached(path: Path, result: dict, root: Path = Path(".")) -> None:
     tmp = entry.with_suffix(".tmp")
     try:
         tmp.write_text(json.dumps(result), encoding="utf-8")
-        os.replace(tmp, entry)
+        try:
+            os.replace(tmp, entry)
+        except PermissionError:
+            # Windows: os.replace can fail with WinError 5 if the target is
+            # briefly locked. Fall back to copy-then-delete.
+            import shutil
+            shutil.copy2(tmp, entry)
+            tmp.unlink(missing_ok=True)
     except Exception:
         tmp.unlink(missing_ok=True)
         raise
diff --git a/graphify/extract.py b/graphify/extract.py
index f420256..abe3b46 100644
--- a/graphify/extract.py
+++ b/graphify/extract.py
@@ -563,7 +563,7 @@ _PHP_CONFIG = LanguageConfig(
     class_types=frozenset({"class_declaration"}),
     function_types=frozenset({"function_definition", "method_declaration"}),
     import_types=frozenset({"namespace_use_clause"}),
-    call_types=frozenset({"function_call_expression", "member_call_expression"}),
+    call_types=frozenset({"function_call_expression", "member_call_expression", "scoped_call_expression", "class_constant_access_expression"}),
     static_prop_types=frozenset({"scoped_property_access_expression"}),
     helper_fn_names=frozenset({"config"}),
     container_bind_methods=frozenset({"bind", "singleton", "scoped", "instance"}),
@@ -936,6 +936,7 @@ def _extract_generic(path: Path, config: LanguageConfig) -> dict:
     seen_static_ref_pairs: set[tuple[str, str, str]] = set()
     seen_helper_ref_pairs: set[tuple[str, str, str]] = set()
     seen_bind_pairs: set[tuple[str, str, str]] = set()
+    raw_calls: list[dict] = []  # unresolved calls for cross-file resolution in extract()
 
     def _php_class_const_scope(n) -> str | None:
         scope = n.child_by_field_name("scope")
@@ -1009,11 +1010,16 @@ def _extract_generic(path: Path, config: LanguageConfig) -> dict:
                                 callee_name = raw
                             break
             elif config.ts_module == "tree_sitter_php":
-                # PHP: distinguish function_call_expression vs member_call_expression
+                # PHP: distinguish call expression subtypes
                 if node.type == "function_call_expression":
                     func_node = node.child_by_field_name("function")
                     if func_node:
                         callee_name = _read_text(func_node, source)
+                elif node.type == "scoped_call_expression":
+                    # Static method call: Helper::format() → callee = "Helper"
+                    scope_node = node.child_by_field_name("scope")
+                    if scope_node:
+                        callee_name = _read_text(scope_node, source)
                 else:
                     name_node = node.child_by_field_name("name")
                     if name_node:
@@ -1059,6 +1065,14 @@ def _extract_generic(path: Path, config: LanguageConfig) -> dict:
                             "source_location": f"L{line}",
                             "weight": 1.0,
                         })
+                elif callee_name and not tgt_nid:
+                    # Callee not in this file — save for cross-file resolution in extract()
+                    raw_calls.append({
+                        "caller_nid": caller_nid,
+                        "callee": callee_name,
+                        "source_file": str_path,
+                        "source_location": f"L{node.start_point[0] + 1}",
+                    })
 
             # Helper function calls: config('foo.bar') → uses_config edge to "foo"
             if (callee_name and callee_name in config.helper_fn_names):
@@ -1163,6 +1177,27 @@ def _extract_generic(path: Path, config: LanguageConfig) -> dict:
                             "weight": 1.0,
                         })
 
+        # PHP class constant access: Foo::BAR → references_constant edge
+        if config.ts_module == "tree_sitter_php" and node.type == "class_constant_access_expression":
+            class_name = _php_class_const_scope(node)
+            if class_name:
+                tgt_nid = label_to_nid.get(class_name.lower())
+                if tgt_nid and tgt_nid != caller_nid:
+                    pair3 = (caller_nid, tgt_nid, "references_constant")
+                    if pair3 not in seen_static_ref_pairs:
+                        seen_static_ref_pairs.add(pair3)
+                        line = node.start_point[0] + 1
+                        edges.append({
+                            "source": caller_nid,
+                            "target": tgt_nid,
+                            "relation": "references_constant",
+                            "confidence": "EXTRACTED",
+                            "confidence_score": 1.0,
+                            "source_file": str_path,
+                            "source_location": f"L{line}",
+                            "weight": 1.0,
+                        })
+
         for child in node.children:
             walk_calls(child, caller_nid)
 
@@ -1199,7 +1234,7 @@ def _extract_generic(path: Path, config: LanguageConfig) -> dict:
         if src in valid_ids and (tgt in valid_ids or edge["relation"] in ("imports", "imports_from")):
             clean_edges.append(edge)
 
-    return {"nodes": nodes, "edges": clean_edges}
+    return {"nodes": nodes, "edges": clean_edges, "raw_calls": raw_calls}
 
 
 # ── Python rationale extraction ───────────────────────────────────────────────
@@ -2992,13 +3027,19 @@ def _check_tree_sitter_version() -> None:
         )
 
 
-def extract(paths: list[Path]) -> dict:
+def extract(paths: list[Path], cache_root: Path | None = None) -> dict:
     """Extract AST nodes and edges from a list of code files.
 
     Two-pass process:
     1. Per-file structural extraction (classes, functions, imports)
     2. Cross-file import resolution: turns file-level imports into
        class-level INFERRED edges (DigestAuth --uses--> Response)
+
+    Args:
+        paths: files to extract from
+        cache_root: explicit root for graphify-out/cache/ (overrides the
+            inferred common path prefix). Pass Path('.') when running on a
+            subdirectory so the cache stays at ./graphify-out/cache/.
     """
     _check_tree_sitter_version()
     per_file: list[dict] = []
@@ -3068,13 +3109,13 @@ def extract(paths: list[Path]) -> dict:
             extractor = _DISPATCH.get(path.suffix)
         if extractor is None:
             continue
-        cached = load_cached(path, root)
+        cached = load_cached(path, cache_root or root)
         if cached is not None:
             per_file.append(cached)
             continue
         result = extractor(path)
         if "error" not in result:
-            save_cached(path, result, root)
+            save_cached(path, result, cache_root or root)
         per_file.append(result)
     if total >= _PROGRESS_INTERVAL:
         print(f"  AST extraction: {total}/{total} files (100%)", flush=True)
@@ -3096,6 +3137,37 @@ def extract(paths: list[Path]) -> dict:
             import logging
             logging.getLogger(__name__).warning("Cross-file import resolution failed, skipping: %s", exc)
 
+    # Cross-file call resolution for all languages
+    # Each extractor saved unresolved calls in raw_calls. Now that we have all
+    # nodes from all files, resolve any callee that exists in another file.
+    global_label_to_nid: dict[str, str] = {}
+    for n in all_nodes:
+        raw = n.get("label", "")
+        normalised = raw.strip("()").lstrip(".")
+        if normalised:
+            global_label_to_nid[normalised.lower()] = n["id"]
+
+    existing_pairs = {(e["source"], e["target"]) for e in all_edges}
+    for result in per_file:
+        for rc in result.get("raw_calls", []):
+            callee = rc.get("callee", "")
+            if not callee:
+                continue
+            tgt = global_label_to_nid.get(callee.lower())
+            caller = rc["caller_nid"]
+            if tgt and tgt != caller and (caller, tgt) not in existing_pairs:
+                existing_pairs.add((caller, tgt))
+                all_edges.append({
+                    "source": caller,
+                    "target": tgt,
+                    "relation": "calls",
+                    "confidence": "INFERRED",
+                    "confidence_score": 0.8,
+                    "source_file": rc.get("source_file", ""),
+                    "source_location": rc.get("source_location"),
+                    "weight": 1.0,
+                })
+
     return {
         "nodes": all_nodes,
         "edges": all_edges,
diff --git a/graphify/skill.md b/graphify/skill.md
index c9fdb85..3a0b732 100644
--- a/graphify/skill.md
+++ b/graphify/skill.md
@@ -548,6 +548,36 @@ else:
 "
 ```
 
+### Step 6b - Wiki (only if --wiki flag)
+
+**Only run this step if `--wiki` was explicitly given in the original command.**
+
+Run this before Step 9 (cleanup) so `.graphify_labels.json` is still available.
+
+```bash
+$(cat graphify-out/.graphify_python) -c "
+import json
+from graphify.build import build_from_json
+from graphify.wiki import to_wiki
+from graphify.analyze import god_nodes
+from pathlib import Path
+
+extraction = json.loads(Path('graphify-out/.graphify_extract.json').read_text())
+analysis   = json.loads(Path('graphify-out/.graphify_analysis.json').read_text())
+labels_raw = json.loads(Path('graphify-out/.graphify_labels.json').read_text()) if Path('graphify-out/.graphify_labels.json').exists() else {}
+
+G = build_from_json(extraction)
+communities = {int(k): v for k, v in analysis['communities'].items()}
+cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
+labels = {int(k): v for k, v in labels_raw.items()}
+gods = god_nodes(G)
+
+n = to_wiki(G, communities, 'graphify-out/wiki', community_labels=labels or None, cohesion=cohesion, god_nodes_data=gods)
+print(f'Wiki: {n} articles written to graphify-out/wiki/')
+print('  graphify-out/wiki/index.md  ->  agent entry point')
+"
+```
+
 ### Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag)
 
 **If `--neo4j`** - generate a Cypher file for manual import:
diff --git a/pyproject.toml b/pyproject.toml
index 9f6b5e9..2f0c418 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -60,4 +60,4 @@ where = ["."]
 include = ["graphify*"]
 
 [tool.setuptools.package-data]
-graphify = ["skill.md", "skill-codex.md", "skill-opencode.md", "skill-aider.md", "skill-copilot.md", "skill-claw.md", "skill-windows.md", "skill-droid.md", "skill-trae.md"]
+graphify = ["skill.md", "skill-codex.md", "skill-opencode.md", "skill-aider.md", "skill-copilot.md", "skill-claw.md", "skill-windows.md", "skill-droid.md", "skill-trae.md", "skill-kiro.md"]
diff --git a/tests/test_claude_md.py b/tests/test_claude_md.py
index d7d6c96..4a5a519 100644
--- a/tests/test_claude_md.py
+++ b/tests/test_claude_md.py
@@ -22,7 +22,7 @@ def test_install_contains_expected_rules(tmp_path):
     content = (tmp_path / "CLAUDE.md").read_text()
     assert "GRAPH_REPORT.md" in content
     assert "wiki/index.md" in content
-    assert "_rebuild_code" in content
+    assert "graphify update" in content
 
 
 def test_install_appends_to_existing_claude_md(tmp_path):

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

