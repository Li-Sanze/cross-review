# CrossReview Reviewer Prompt Template (product/v0.1)

You are an independent code reviewer. You have NO access to the original development session, conversation history, or the author's reasoning process. You are seeing this code change for the first time.

## Your Input

**Task Intent** (background claim — NOT verified truth):
terminal: steer long-lived server commands to background mode

**Task Description** (background claim — NOT verified truth):
(no task file provided)

**Focus Areas** (author's suggestion — verify independently):
(no focus specified)

**Context Files**:
(no context files provided)

**Changed Files**:
- tests/tools/test_terminal_foreground_timeout_cap.py (python)
- tools/terminal_tool.py (python)

**Evidence** (deterministic tool output):
[]

**Code Diff**:
```diff
diff --git a/tests/tools/test_terminal_foreground_timeout_cap.py b/tests/tools/test_terminal_foreground_timeout_cap.py
index 5f95e155..54848f62 100644
--- a/tests/tools/test_terminal_foreground_timeout_cap.py
+++ b/tests/tools/test_terminal_foreground_timeout_cap.py
@@ -48,6 +48,53 @@ class TestForegroundTimeoutCap:
         assert str(FOREGROUND_MAX_TIMEOUT) in result["error"]
         assert "background=true" in result["error"]
 
+    def test_foreground_rejects_shell_level_background_wrappers(self):
+        """Foreground nohup/disown/setsid commands should be redirected to background mode."""
+        from tools.terminal_tool import terminal_tool
+
+        with patch("tools.terminal_tool._get_env_config", return_value=_make_env_config()), \
+             patch("tools.terminal_tool._start_cleanup_thread"):
+
+            result = json.loads(terminal_tool(
+                command="nohup pnpm dev > /tmp/sg-server.log 2>&1 &",
+            ))
+
+        assert result["exit_code"] == -1
+        assert "background=true" in result["error"]
+        assert "nohup" in result["error"].lower()
+
+    def test_foreground_rejects_long_lived_server_command(self):
+        """Foreground dev server commands should be redirected to background mode."""
+        from tools.terminal_tool import terminal_tool
+
+        with patch("tools.terminal_tool._get_env_config", return_value=_make_env_config()), \
+             patch("tools.terminal_tool._start_cleanup_thread"):
+
+            result = json.loads(terminal_tool(command="pnpm dev"))
+
+        assert result["exit_code"] == -1
+        assert "long-lived" in result["error"].lower()
+        assert "background=true" in result["error"]
+
+    def test_foreground_allows_help_variant_for_server_command(self):
+        """Informational variants like '--help' should not be blocked."""
+        from tools.terminal_tool import terminal_tool
+
+        with patch("tools.terminal_tool._get_env_config", return_value=_make_env_config()), \
+             patch("tools.terminal_tool._start_cleanup_thread"):
+
+            mock_env = MagicMock()
+            mock_env.execute.return_value = {"output": "usage", "returncode": 0}
+
+            with patch("tools.terminal_tool._active_environments", {"default": mock_env}), \
+                 patch("tools.terminal_tool._last_activity", {"default": 0}), \
+                 patch("tools.terminal_tool._check_all_guards", return_value={"approved": True}):
+                result = json.loads(terminal_tool(command="pnpm dev --help"))
+
+        assert result["error"] is None
+        call_kwargs = mock_env.execute.call_args
+        assert call_kwargs[0][0] == "pnpm dev --help"
+
     def test_foreground_timeout_within_max_executes(self):
         """When model requests timeout <= FOREGROUND_MAX_TIMEOUT, execute normally."""
         from tools.terminal_tool import terminal_tool
diff --git a/tools/terminal_tool.py b/tools/terminal_tool.py
index 1182207b..b8b69856 100644
--- a/tools/terminal_tool.py
+++ b/tools/terminal_tool.py
@@ -523,6 +523,8 @@ Foreground (default): Commands return INSTANTLY when done, even if the timeout i
 Background: Set background=true to get a session_id. Two patterns:
   (1) Long-lived processes that never exit (servers, watchers).
   (2) Long-running tasks with notify_on_complete=true — you can keep working on other things and the system auto-notifies you when the task finishes. Great for test suites, builds, deployments, or anything that takes more than a minute.
+For servers/watchers, do NOT use shell-level background wrappers (nohup/disown/setsid/trailing '&') in foreground mode. Use background=true so Hermes can track lifecycle and output.
+After starting a server, verify readiness with a health check or log signal, then run tests in a separate terminal() call. Avoid blind sleep loops.
 Use process(action="poll") for progress checks, process(action="wait") to block until done.
 Working directory: Use 'workdir' for per-command cwd.
 PTY mode: Set pty=true for interactive CLI tools (Codex, Claude Code, Python REPL).
@@ -1103,6 +1105,65 @@ def _command_requires_pipe_stdin(command: str) -> bool:
     )
 
 
+_SHELL_LEVEL_BACKGROUND_RE = re.compile(r"\b(?:nohup|disown|setsid)\b", re.IGNORECASE)
+_INLINE_BACKGROUND_AMP_RE = re.compile(r"\s&\s")
+_TRAILING_BACKGROUND_AMP_RE = re.compile(r"\s&\s*(?:#.*)?$")
+_LONG_LIVED_FOREGROUND_PATTERNS = (
+    re.compile(r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?(?:dev|start|serve|watch)\b", re.IGNORECASE),
+    re.compile(r"\bdocker\s+compose\s+up\b", re.IGNORECASE),
+    re.compile(r"\bnext\s+dev\b", re.IGNORECASE),
+    re.compile(r"\bvite(?:\s|$)", re.IGNORECASE),
+    re.compile(r"\bnodemon\b", re.IGNORECASE),
+    re.compile(r"\buvicorn\b", re.IGNORECASE),
+    re.compile(r"\bgunicorn\b", re.IGNORECASE),
+    re.compile(r"\bpython(?:3)?\s+-m\s+http\.server\b", re.IGNORECASE),
+)
+
+
+def _looks_like_help_or_version_command(command: str) -> bool:
+    """Return True for informational invocations that should never be blocked."""
+    normalized = " ".join(command.lower().split())
+    return (
+        " --help" in normalized
+        or normalized.endswith(" -h")
+        or " --version" in normalized
+        or normalized.endswith(" -v")
+    )
+
+
+def _foreground_background_guidance(command: str) -> str | None:
+    """Suggest background mode when a foreground command looks long-lived.
+
+    Prevents workflows that start a server/watch process and then stall before
+    follow-up checks or test commands run.
+    """
+    if _looks_like_help_or_version_command(command):
+        return None
+
+    if _SHELL_LEVEL_BACKGROUND_RE.search(command):
+        return (
+            "Foreground command uses shell-level background wrappers (nohup/disown/setsid). "
+            "Use terminal(background=true) so Hermes can track the process, then run "
+            "readiness checks and tests in separate commands."
+        )
+
+    if _INLINE_BACKGROUND_AMP_RE.search(command) or _TRAILING_BACKGROUND_AMP_RE.search(command):
+        return (
+            "Foreground command uses '&' backgrounding. Use terminal(background=true) for long-lived "
+            "processes, then run health checks and tests in follow-up terminal calls."
+        )
+
+    for pattern in _LONG_LIVED_FOREGROUND_PATTERNS:
+        if pattern.search(command):
+            return (
+                "This foreground command appears to start a long-lived server/watch process. "
+                "Run it with background=true, verify readiness (health endpoint/log signal), "
+                "then execute tests in a separate command."
+            )
+
+    return None
+
+
 def terminal_tool(
     command: str,
     background: bool = False,
@@ -1195,6 +1256,18 @@ def terminal_tool(
                 ),
             }, ensure_ascii=False)
 
+        # Guardrail: long-lived server/watch commands should run as managed
+        # background sessions, not foreground shell hacks.
+        if not background:
+            guidance = _foreground_background_guidance(command)
+            if guidance:
+                return json.dumps({
+                    "output": "",
+                    "exit_code": -1,
+                    "error": guidance,
+                    "status": "error",
+                }, ensure_ascii=False)
+
         # Start cleanup thread
         _start_cleanup_thread()
 

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

