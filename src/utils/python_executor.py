"""Utilities for executing user-provided Python code in a restricted sandbox."""

from __future__ import annotations

import builtins
import io
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, Mapping, Optional


@dataclass
class ExecutionResult:
	"""
	Structured result returned by :func:`execute_python`.

	Attributes:
        out:
            The value of the ``out`` variable set by the executed code, or ``None``
            if it was not defined.
        stdout:
            Text captured from ``stdout`` during execution.
        stderr:
            Text captured from ``stderr`` during execution.
        execution_time:
            Wall-clock runtime in seconds consumed by ``exec``.
        error:
            The exception instance raised by the executed code, if any; ``None``
            when the code completed successfully.
        error_type:
            The fully-qualified name of the raised exception type when ``error`` is
            present; otherwise ``None``.
        traceback:
            The formatted traceback string when an exception is raised; otherwise
            ``None``.
        globals_snapshot:
            A shallow copy of the sandbox globals after execution finishes. This
            can be helpful for debugging or extracting additional variables.
	"""

	out: Any
	stdout: str
	stderr: str
	execution_time: float
	error: Optional[BaseException]
	error_type: Optional[str]
	traceback: Optional[str]
	globals_snapshot: Optional[Dict[str, Any]] = None


def _build_sandbox_builtins() -> Dict[str, Any]:
	"""
	Return a copy of Python builtins with ``__import__`` removed.
	"""

	safe_builtins: Dict[str, Any] = {}
	for name in dir(builtins):
		if name == "__import__":
			continue
		safe_builtins[name] = getattr(builtins, name)
	return safe_builtins


def execute_python(code: str, *, context: Optional[Mapping[str, Any]] = None) -> ExecutionResult:
	"""
	Execute ``code`` inside a restricted sandbox using ``exec``.

	Args:
        code:
            The Python source code to run.
        context:
            Optional mapping of variable names to objects that will be injected into
            the global namespace prior to execution. This is the only mechanism for
            the code to access external packages or helpers.

	Returns:
        ExecutionResult:
            Structured execution metadata including captured outputs, timing
            information, the ``out`` value, and any exception details.
	"""

	sandbox_globals: Dict[str, Any] = {"__builtins__": _build_sandbox_builtins()}
	if context:
		sandbox_globals.update(context)

	stdout_buffer = io.StringIO()
	stderr_buffer = io.StringIO()
	execution_error: Optional[BaseException] = None
	error_traceback: Optional[str] = None

	start_time = perf_counter()
	with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
		try:
			exec(code, sandbox_globals)
		except Exception as exc:  # noqa: BLE001 - intentionally catching broad exceptions from user code
			execution_error = exc
			error_traceback = traceback.format_exc()
	end_time = perf_counter()

	out_value = sandbox_globals.get("out")
	error_type = None
	if execution_error is not None:
		error_type = f"{execution_error.__class__.__module__}.{execution_error.__class__.__name__}"

	return ExecutionResult(
		out=out_value,
		stdout=stdout_buffer.getvalue(),
		stderr=stderr_buffer.getvalue(),
		execution_time=end_time - start_time,
		error=execution_error,
		error_type=error_type,
		traceback=error_traceback,
		#globals_snapshot=dict(sandbox_globals),
	)

if __name__ == "__main__":
    result = execute_python('print("Hello, World!");out = 42')
    print(result)
