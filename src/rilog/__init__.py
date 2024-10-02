"""Rilog module."""

from importlib.metadata import version

from rilog.logger import Logger, logger

__version__ = version(__name__)

__all__ = ["Logger", "logger"]
