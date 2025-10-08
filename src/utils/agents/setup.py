import os
import dotenv
import json

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass

from agents import ModelSettings, AgentHooks
from openai.types.shared import Reasoning
from typing import Any, TypeVar

from agents import Agent, AgentBase
from agents.run_context import RunContextWrapper, TContext
from agents.tool import Tool

import json, threading, time
from typing import Any, Dict, Optional, Set

from agents.tracing.processor_interface import TracingProcessor
from agents.tracing.spans import Span
from agents.tracing.span_data import AgentSpanData, FunctionSpanData
from agents.tracing import add_trace_processor  # or set_trace_processors
TAgent = TypeVar("TAgent", bound=AgentBase)

dotenv.load_dotenv()

"""
Model Choice Explanations:

Fast: Suitable for quick tasks with lower complexity.
Core: Balances speed and detail for general tasks.
Expert: Offers more depth and nuance for complex queries.

Brief: Focuses on concise responses with essential information.
Standard: Balances detail and brevity for general tasks.
Detailed: Provides comprehensive responses with in-depth analysis.
"""

models = {
    "fast": "gpt-5-nano",
    "core": "gpt-5-mini",
    "expert": "gpt-5"
}

model_settings = {
    "brief-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="low"),
    "brief-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="low"),
    "brief-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="low"),
    "brief-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="low"),
    "standard-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="medium"),
    "standard-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="medium"),
    "standard-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="medium"),
    "standard-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="medium"),
    "detailed-min": ModelSettings(reasoning=Reasoning(effort="minimal"), verbosity="high"),
    "detailed-low": ModelSettings(reasoning=Reasoning(effort="low"), verbosity="high"),
    "detailed-med": ModelSettings(reasoning=Reasoning(effort="medium"), verbosity="high"),
    "detailed-high": ModelSettings(reasoning=Reasoning(effort="high"), verbosity="high"),
}

class PrintingAgentHooks(AgentHooks):
    """A class that receives callbacks on various lifecycle events for a specific agent. You can
    set this on `agent.hooks` to receive events for that specific agent.

    Subclass and override the methods you need.
    """

    async def on_start(self, context: RunContextWrapper[TContext], agent: TAgent) -> None:
        """Called before the agent is invoked. Called each time the running agent is changed to this
        agent."""
        print(f"Agent {agent.name} is starting")

    async def on_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        output: Any,
    ) -> None:
        """Called when the agent produces a final output."""
        print(f"Agent {agent.name} has finished")

    async def on_handoff(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        source: TAgent,
    ) -> None:
        """Called when the agent is being handed off to. The `source` is the agent that is handing
        off to this agent."""
        print(f"Handoff from {source.name} to {agent.name}")

    async def on_tool_start(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
    ) -> None:
        """Called concurrently with tool invocation."""
        print(f"Tool {tool.name} started for agent {agent.name}")

    async def on_tool_end(
        self,
        context: RunContextWrapper[TContext],
        agent: TAgent,
        tool: Tool,
        result: str,
    ) -> None:
        """Called after a tool is invoked."""
        print(f"Tool {tool.name} ended for agent {agent.name}")

def _sanitize_for_json(value: Any, *, _visited: Optional[Set[int]] = None) -> Any:
    """Recursively convert ``value`` into a JSON-serializable structure."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if _visited is None:
        _visited = set()

    obj_id = id(value)
    if obj_id in _visited:
        return "<recursion>"
    _visited.add(obj_id)

    if isinstance(value, BaseException):
        return {
            "type": f"{value.__class__.__module__}.{value.__class__.__name__}",
            "message": str(value),
        }

    if is_dataclass(value):
        try:
            return _sanitize_for_json(asdict(value), _visited=_visited)
        except TypeError:
            # Fallback to repr when dataclass fields are not serializable
            return repr(value)

    if isinstance(value, Mapping):
        return {
            str(key): _sanitize_for_json(item, _visited=_visited)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set, frozenset)):
        return [
            _sanitize_for_json(item, _visited=_visited)
            for item in value
        ]

    representation = repr(value)
    if len(representation) > 1000:
        representation = representation[:997] + "..."
    return representation


class JSONLLogger(TracingProcessor):
    """Generic JSONL tracing processor that logs every trace, span start, and span end.

    Records a superset of data for all span types, including agent ancestry resolution
    so consumers can easily filter by agent. Each line is one JSON object with a field
    "event" in {"trace_start","trace_end","span_start","span_end"}.
    """

    def __init__(self, path: str = "log/traces.jsonl", flush_every: int = 1):
        self.path = path
        self.flush_every = flush_every
        self._lock = threading.Lock()
        self._spans: Dict[str, Span[Any]] = {}
        self._write_count = 0
        self._buffer: list[str] = []

    # --------------- helpers ---------------
    def _resolve_agent_ancestor(self, span: Span[Any]) -> Optional[str]:
        parent_id = span.parent_id
        while parent_id:
            parent = self._spans.get(parent_id)
            if parent is None:
                break
            if isinstance(parent.span_data, AgentSpanData):
                return parent.span_data.name
            parent_id = parent.parent_id
        return None

    def _write_record(self, record: Dict[str, Any]) -> None:
        line = json.dumps(_sanitize_for_json(record), ensure_ascii=False)
        with self._lock:
            self._buffer.append(line)
            self._write_count += 1
            if self._write_count % self.flush_every == 0:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write("\n".join(self._buffer) + "\n")
                self._buffer.clear()

    # --------------- lifecycle hooks ---------------
    def on_trace_start(self, trace) -> None:
        self._write_record({
            "event": "trace_start",
            "ts": time.time(),
            "trace_id": getattr(trace, "trace_id", None),
        })

    def on_trace_end(self, trace) -> None:
        self._write_record({
            "event": "trace_end",
            "ts": time.time(),
            "trace_id": getattr(trace, "trace_id", None),
        })

    def on_span_start(self, span: Span[Any]) -> None:
        # store span early for ancestry resolution later
        self._spans[span.span_id] = span
        sd = span.span_data
        record = {
            "event": "span_start",
            "ts": time.time(),
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "parent_id": span.parent_id,
            "span_type": type(sd).__name__,
            "agent_name": self._resolve_agent_ancestor(span),
        }
        # Best-effort attribute extraction
        for attr in ("name", "input", "output", "role", "content"):
            if hasattr(sd, attr):
                record[attr] = getattr(sd, attr)
        self._write_record(record)

    def on_span_end(self, span: Span[Any]) -> None:
        sd = span.span_data
        record = {
            "event": "span_end",
            "ts": time.time(),
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "parent_id": span.parent_id,
            "span_type": type(sd).__name__,
            "agent_name": self._resolve_agent_ancestor(span),
            "error": getattr(span, "error", None).export() if getattr(span, "error", None) else None,
        }
        # Include final output if present
        for attr in ("name", "input", "output", "role", "content"):
            if hasattr(sd, attr):
                record[attr] = getattr(sd, attr)
        self._write_record(record)
        # cleanup
        self._spans.pop(span.span_id, None)

    def shutdown(self) -> None:
        with self._lock:
            if self._buffer:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write("\n".join(self._buffer) + "\n")
                self._buffer.clear()

    def force_flush(self) -> None:
        self.shutdown()

add_trace_processor(JSONLLogger("log/traces.jsonl", flush_every=1))