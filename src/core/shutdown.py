"""
CipherFlow Graceful Shutdown
==============================
Handles SIGTERM and SIGINT signals for clean container shutdown.
Ensures in-flight requests complete before the process exits.
Critical for Kubernetes pod termination (preStop hook).
"""

import signal
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

_shutdown_event: Optional[asyncio.Event] = None


def get_shutdown_event() -> asyncio.Event:
    """Get or create the global shutdown event."""
    global _shutdown_event
    if _shutdown_event is None:
        _shutdown_event = asyncio.Event()
    return _shutdown_event


def _signal_handler(signum: int, frame) -> None:
    """Handle termination signals gracefully."""
    sig_name = signal.Signals(signum).name
    logger.info(f"Received {sig_name} — initiating graceful shutdown")
    event = get_shutdown_event()
    event.set()


def register_signal_handlers() -> None:
    """Register handlers for SIGTERM and SIGINT."""
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)
    logger.info("Graceful shutdown handlers registered")
