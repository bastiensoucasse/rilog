"""Rilog module."""

from importlib.metadata import version

from rilog.logger import Logger, logger

__version__ = version("rilog")

__all__ = ["Logger", "logger"]
