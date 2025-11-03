import threading
import time
from typing import Any, Dict, List, Optional


class OperationRecorder:
    """
    Simple in-memory recorder for executed operations as DSL.

    - Records both DSL-triggered and button-triggered operations.
    - Supports three contexts: 'linear', 'tree', and 'global'.
    - Exposes history since the latest boundary (global clear or context create/build).

    Note: In-memory storage is sufficient for prompt enrichment within the app session.
    """

    _lock = threading.Lock()
    _records: Dict[str, List[Dict[str, Any]]] = {"linear": [], "tree": [], "global": []}

    @classmethod
    def _now(cls) -> float:
        return time.time()

    @classmethod
    def record_dsl(
        cls,
        dsl_text: str,
        context: str,
        success: bool = True,
        source: str = "dsl",
    ) -> None:
        if not dsl_text or context not in ("linear", "tree", "global"):
            return
        with cls._lock:
            cls._records[context].append(
                {
                    "dsl": dsl_text.strip(),
                    "context": context,
                    "success": bool(success),
                    "source": source,
                    "ts": cls._now(),
                }
            )

    # ---------- Mapping helpers for button actions ----------

    @staticmethod
    def _norm_linear_name(structure_type: Optional[str]) -> Optional[str]:
        if not structure_type:
            return None
        key = structure_type.strip().lower()
        if key in ("array_list", "arraylist", "array-list"):
            return "arraylist"
        if key in ("linked_list", "linkedlist", "linked-list"):
            return "linkedlist"
        if key in ("stack",):
            return "stack"
        return structure_type

    @staticmethod
    def _norm_tree_name(structure_type: Optional[str]) -> Optional[str]:
        if not structure_type:
            return None
        key = structure_type.strip().lower()
        if key in ("binary_tree", "binarytree", "binary-tree"):
            return "binarytree"
        if key in ("bst", "binary_search_tree", "binary-search-tree"):
            return "bst"
        if key in ("avl", "avl_tree", "avl-tree"):
            return "avl"
        if key in ("huffman", "huffman_tree", "huffman-tree"):
            return "huffman"
        return structure_type

    @classmethod
    def record_linear_action(
        cls,
        action_type: str,
        params: Dict[str, Any],
        structure_type: Optional[str],
        executed: bool = True,
    ) -> None:
        """Convert a linear button action to DSL and record it.

        Only records when a meaningful DSL can be produced. Uses conservative grammar.
        """
        st = cls._norm_linear_name(structure_type)
        action = (action_type or "").strip().lower()
        dsl: Optional[str] = None

        if action == "create":
            values = params.get("values")
            size = params.get("size") or params.get("capacity")
            if st:
                if values:
                    vals_str = ", ".join(map(str, values))
                    dsl = f"create {st} with {vals_str}"
                else:
                    dsl = f"create {st}"
                if size:
                    dsl = f"{dsl} size {int(size)}"
        elif action == "insert":
            value = params.get("value")
            pos = params.get("position")
            if st is not None and value is not None and pos is not None:
                dsl = f"insert {value} at {pos} in {st}"
        elif action in ("delete", "remove"):
            value = params.get("value")
            pos = params.get("position")
            if st:
                if pos is not None:
                    dsl = f"delete at {pos} in {st}"
                elif value is not None:
                    dsl = f"delete {value} from {st}"
        elif action == "get":
            pos = params.get("position")
            if st and pos is not None:
                dsl = f"get {pos} from {st}"
        elif action == "push":
            value = params.get("value")
            if st == "stack" and value is not None:
                dsl = f"push {value} to stack"
        elif action == "pop":
            if st == "stack":
                dsl = "pop from stack"
        elif action == "peek":
            if st == "stack":
                dsl = "peek stack"
        elif action == "clear":
            if st:
                dsl = f"clear {st}"

        if dsl:
            cls.record_dsl(dsl, context="linear", success=executed, source="button")

    @classmethod
    def record_tree_action(
        cls,
        action_type: str,
        params: Dict[str, Any],
        structure_type: Optional[str],
        executed: bool = True,
    ) -> None:
        """Convert a tree button action to DSL and record it.

        Covers binary, bst, avl, and huffman actions.
        """
        st = cls._norm_tree_name(structure_type)
        action = (action_type or "").strip().lower()
        dsl: Optional[str] = None

        if action == "create":
            values = params.get("values")
            if st:
                if values:
                    vals_str = ", ".join(map(str, values))
                    dsl = f"create {st} with {vals_str}"
                else:
                    dsl = f"create {st}"
        elif action == "build_bst":
            values = params.get("values")
            if values:
                vals_str = ", ".join(map(str, values))
                dsl = f"build bst with {vals_str}"
        elif action == "build_avl":
            values = params.get("values")
            if values:
                vals_str = ", ".join(map(str, values))
                dsl = f"build avl with {vals_str}"
        elif action == "build_huffman":
            pairs = params.get("pairs") or params.get("freqs") or params.get("values")
            if pairs:
                # Expect pairs like [(char, freq), ...]
                def _fmt_pair(p: Any) -> str:
                    try:
                        c, f = p
                        return f"{c}:{int(f)}"
                    except Exception:
                        return str(p)
                dsl = "build huffman with " + ", ".join(_fmt_pair(p) for p in pairs)
        elif action in ("insert", "remove", "delete"):
            value = params.get("value")
            where = params.get("position") or params.get("path")
            verb = "delete" if action in ("remove", "delete") else "insert"
            tgt = st or "binarytree"
            if value is not None:
                if where:
                    dsl = f"{verb} {value} at {where} in {tgt}"
                else:
                    dsl = f"{verb} {value} in {tgt}"
        elif action in ("search", "find"):
            value = params.get("value")
            tgt = st or "binarytree"
            if value is not None:
                dsl = f"search {value} in {tgt}"
        elif action == "traverse":
            order = (params.get("order") or "inorder").lower()
            dsl = f"traverse {order} in binarytree"
        elif action == "encode":
            text = params.get("text") or params.get("value")
            if text is not None:
                dsl = f"encode \"{text}\" using huffman"
        elif action == "decode":
            bits = params.get("bits") or params.get("value")
            if bits is not None:
                dsl = f"decode {bits} using huffman"
        elif action == "clear":
            tgt = st or "binarytree"
            dsl = f"clear {tgt}"

        if dsl:
            cls.record_dsl(dsl, context="tree", success=executed, source="button")

    # ---------- History for prompt ----------

    @classmethod
    def _last_boundary_ts(cls, context: str) -> Optional[float]:
        """Latest ts of boundary events (global clear or context create/build)."""
        with cls._lock:
            # Last global clear
            last_clear_ts: Optional[float] = None
            for r in reversed(cls._records.get("global", [])):
                if r.get("success") and isinstance(r.get("dsl"), str) and r["dsl"].strip().startswith("clear"):
                    last_clear_ts = r["ts"]
                    break

            # Last context create/build
            last_ctx_ts: Optional[float] = None
            for r in reversed(cls._records.get(context, [])):
                d = (r.get("dsl") or "").strip().lower()
                if r.get("success") and (d.startswith("create ") or d.startswith("build ")):
                    last_ctx_ts = r["ts"]
                    break

            if last_clear_ts and last_ctx_ts:
                return max(last_clear_ts, last_ctx_ts)
            return last_clear_ts or last_ctx_ts

    @classmethod
    def get_history(cls, context: Optional[str]) -> List[str]:
        """Return DSL history since the latest boundary for the given context.

        If context is None, combine both linear and tree histories.
        """
        def _collect(ctx: str) -> List[str]:
            since = cls._last_boundary_ts(ctx)
            lines: List[str] = []
            with cls._lock:
                # If boundary is a global clear newer than context create, include the clear as first line
                if since:
                    # find boundary line(s)
                    # include global clear if it's at or after since
                    for r in reversed(cls._records.get("global", [])):
                        if r.get("success") and r.get("ts") and r["ts"] >= since and (r.get("dsl") or "").strip().startswith("clear"):
                            lines.append(r["dsl"])  # include boundary clear
                            break
                for r in cls._records.get(ctx, []):
                    if not r.get("success"):
                        continue
                    if since is not None and r.get("ts", 0) < since:
                        continue
                    lines.append(r["dsl"])
            return lines

        if not context:
            linear = _collect("linear")
            tree = _collect("tree")
            return linear + tree
        if context not in ("linear", "tree"):
            return []
        return _collect(context)

    @classmethod
    def get_history_text(cls, context: Optional[str]) -> str:
        lines = cls.get_history(context)
        return "\n".join(lines)

    # ---------- History with timestamps ----------
    @classmethod
    def _format_ts(cls, ts: Optional[float]) -> str:
        try:
            if ts is None:
                return "-"
            return time.strftime("%H:%M:%S", time.localtime(ts))
        except Exception:
            return str(ts or "-")

    @classmethod
    def get_history_entries(cls, context: Optional[str]) -> List[Dict[str, Any]]:
        """Return list of entries {dsl, ts, ctx} since boundary.

        If context is None, merge linear and tree entries and include a single
        global clear if it is newer than the earlier boundary.
        """
        def _collect_ctx(ctx: str, since: Optional[float]) -> List[Dict[str, Any]]:
            entries: List[Dict[str, Any]] = []
            with cls._lock:
                # include context entries since boundary
                for r in cls._records.get(ctx, []):
                    if not r.get("success"):
                        continue
                    if since is not None and r.get("ts", 0) < since:
                        continue
                    entries.append({"dsl": r.get("dsl", ""), "ts": r.get("ts"), "ctx": ctx})
            return entries

        if not context:
            since_linear = cls._last_boundary_ts("linear")
            since_tree = cls._last_boundary_ts("tree")
            min_since = None
            if since_linear is not None and since_tree is not None:
                min_since = min(since_linear, since_tree)
            else:
                min_since = since_linear or since_tree

            entries = _collect_ctx("linear", since_linear) + _collect_ctx("tree", since_tree)
            # include one global clear as boundary if applicable
            if min_since is not None:
                with cls._lock:
                    for r in reversed(cls._records.get("global", [])):
                        if r.get("success") and r.get("ts") and r["ts"] >= min_since and (r.get("dsl") or "").strip().startswith("clear"):
                            entries.append({"dsl": r.get("dsl", ""), "ts": r.get("ts"), "ctx": "global"})
                            break
            # sort by timestamp ascending
            entries.sort(key=lambda e: (e.get("ts") or 0))
            return entries

        # single-context collection
        since = cls._last_boundary_ts(context)
        entries = _collect_ctx(context, since)
        if since is not None:
            with cls._lock:
                for r in reversed(cls._records.get("global", [])):
                    if r.get("success") and r.get("ts") and r["ts"] >= since and (r.get("dsl") or "").strip().startswith("clear"):
                        entries.insert(0, {"dsl": r.get("dsl", ""), "ts": r.get("ts"), "ctx": "global"})
                        break
        entries.sort(key=lambda e: (e.get("ts") or 0))
        return entries

    @classmethod
    def get_history_text_with_ts(cls, context: Optional[str]) -> str:
        entries = cls.get_history_entries(context)
        lines: List[str] = []
        for e in entries:
            ts = cls._format_ts(e.get("ts"))
            ctx = e.get("ctx")
            dsl = e.get("dsl") or ""
            # For combined view, include context tag; otherwise omit
            if context is None:
                tag = f"[{ctx}] " if ctx else ""
            else:
                tag = ""
            lines.append(f"{ts} {tag}{dsl}")
        return "\n".join(lines)