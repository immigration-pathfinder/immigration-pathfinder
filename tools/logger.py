# tools/logger.py

import logging

# 🔥 Global toggle for all logging
LOGGING_ENABLED = True   # Set to False to disable logging everywhere


class Logger:
    """
    Lightweight project-wide logger.
    When LOGGING_ENABLED = False → all logging methods become no-op (silent).
    """

    def __init__(self):
        if LOGGING_ENABLED:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            self.logger = logging.getLogger("ImmigrationAI")
        else:
            # No logger created when logging disabled
            self.logger = None

    def log_agent_call(self, agent_name: str, session_id: str, input_summary: str):
        if not LOGGING_ENABLED:
            return
        session_id = session_id or "none"
        safe_summary = (input_summary or "")[:200]
        self.logger.info(
            f"[Agent: {agent_name}] session={session_id} input='{safe_summary}'"
        )

    def log_tool_call(self, tool_name: str, params: dict):
        if not LOGGING_ENABLED:
            return
        self.logger.info(f"[Tool: {tool_name}] params={params}")

    def log_exception(self, error: Exception, context: str):
        if not LOGGING_ENABLED:
            return
        self.logger.error(f"[Exception] context={context} error='{str(error)}'")

    def log_api_call(self, api_name: str, duration: float, status: str):
        if not LOGGING_ENABLED:
            return
        try:
            self.logger.info(
                f"[API: {api_name}] duration={duration:.2f}s status={status}"
            )
        except:
            pass
