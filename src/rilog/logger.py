"""Enhanced logger with progress tracking module."""

from __future__ import annotations

from collections.abc import Sized
from typing import TYPE_CHECKING

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class Logger:
    """Enhanced logger with progress tracking."""

    _console: Console
    """Rich high-level console interface."""

    _live: Live | None
    """Rich auto-updating live display."""

    _progress: Progress | None
    """Rich auto-updating progress bar."""

    _prefix: str
    """Info log prefix."""

    def __init__(self) -> None:
        """Initializes an enhanced logger."""
        self._console = Console()
        self._live = None
        self._progress = None
        self._prefix = ""

    def _progress_print(self, message: str, *, live: bool) -> None:
        if self._progress is None:
            msg = "Logger progress bar should be initialized."
            raise RuntimeError(msg)
        if len(self._progress.task_ids) != 1:
            msg = "Logger progress bar should have a single task running."
            raise RuntimeError(msg)

        task_id = self._progress.task_ids[0]
        if live:
            self._progress.update(task_id, log=message)
        else:
            self._progress.update(task_id, log="")
            self._progress.print(message)

    def _print(self, message: str, *, live: bool) -> None:
        if self._progress:
            self._progress_print(message, live=live)
        elif live:
            if self._live:
                self._live.update(message)
            else:
                self._live = Live(message, console=self._console)
                self._live.start()
        elif self._live:
            self._live.update(message)
            self._live.stop()
            self._live = None
        else:
            self._console.print(message)

    def log(self, *logs: object, live: bool = False) -> None:
        """Prints messages or objects to the console with the default log level (info).

        Args:
            logs: Messages or objects to log.
            live: Whether to log live (temporarily) or permanently. \
                Defaults to False.
        """
        prefix = f"[bold magenta]{self._prefix}[/]" if self._prefix else ""
        for log in logs:
            self._print(f"{prefix}{log!s}", live=live)

    def warn(self, *logs: object, live: bool = False) -> None:
        """Prints messages or objects to the console with the warning log level.

        Args:
            logs: Messages or objects to log.
            live: Whether to log live (temporarily) or permanently. \
                Defaults to False.
        """
        prefix = "[bold yellow]Warning: "
        for log in logs:
            self._print(f"{prefix}{log!s}", live=live)

    def set_prefix(self, prefix: str) -> None:
        """Defines a prefix for future logs.

        Args:
            prefix: Prefix to set.
        """
        self._prefix = prefix

    def remove_prefix(self) -> None:
        """Removes the prefix from future logs."""
        self._prefix = ""

    def progress[T](
        self,
        data: Iterable[T],
        total: int | None = None,
        description: str | None = None,
    ) -> Iterator[T]:
        """Tracks progress of data iteration by logging a progress bar to the console.

        Args:
            data: Iterable collection of items to process.
            total: Total number of items to process. \
                If None, it will be inferred from the data size if possible.
            description: Description for the progress task.

        Yields:
            Original (unchanged) data.
        """
        if total is None and isinstance(data, Sized):
            total = len(data)

        if self._live:
            self._live.stop()
            self._live = None

        count = 0
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                TimeRemainingColumn(),
                TextColumn("{task.fields[log]}"),
                console=self._console,
                transient=True,
            ) as self._progress:
                task = self._progress.add_task(description or "Processing", total=total, log="")
                for item in data:
                    yield item
                    count += 1
                    self._progress.advance(task)
        finally:
            self._progress = None
            if total is not None and count != total:
                self.warn(f"Progress ended after {count} iterations but {total} were expected.")


logger: Logger = Logger()
"""Default enhanced logger."""
