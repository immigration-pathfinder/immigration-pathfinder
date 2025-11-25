import logging
from datetime import datetime


class Logger:
    """
    Simple project-wide logger for agents and tools.
    Keeps logs short, structured, and readable.
    """

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger("ImmigrationAI")

    def log_agent_call(self, agent_name: str, session_id: str, input_summary: str):
        self.logger.info(
            f"[Agent: {agent_name}] session={session_id} input='{input_summary}'"
        )

    def log_tool_call(self, tool_name: str, params: dict):
        self.logger.info(
            f"[Tool: {tool_name}] params={params}"
        )

    def log_exception(self, error: Exception, context: str):
        self.logger.error(
            f"[Exception] context={context} error={str(error)}"
        )
