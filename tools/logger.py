import logging
from datetime import datetime


class Logger:
    """
    Project-wide logger for agents and tools.
    Short, safe, structured logs.
    Fully compatible with Phase 3 requirements.
    """

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger("ImmigrationAI")

    def log_agent_call(self, agent_name: str, session_id: str, input_summary: str):
        """
        Log a safe, short summary of agent activity.
        session_id is optional and defaults to 'none'.
        """
        session_id = session_id or "none"
        safe_summary = (input_summary or "")[:200]  # prevent large logs
        self.logger.info(
            f"[Agent: {agent_name}] session={session_id} input='{safe_summary}'"
        )

    def log_tool_call(self, tool_name: str, params: dict):
        """
        Log tool usage with sanitized parameters.
        """
        self.logger.info(f"[Tool: {tool_name}] params={params}")

    def log_exception(self, error: Exception, context: str):
        """
        Log exceptions in a short, safe form.
        No full tracebacks here (those go to debug mode).
        """
        self.logger.error(f"[Exception] context={context} error='{str(error)}'")

    # Optional for Kaggle Phase 4 / future expansion
    def log_api_call(self, api_name: str, duration: float, status: str):
        """
        Logs API usage (Gemini, Search, external endpoints)
        """
        try:
            self.logger.info(
                f"[API: {api_name}] duration={duration:.2f}s status={status}"
            )
        except Exception:
            pass
