# memory/session_service.py

# ---------------------------------------------------------
# Project root fix so imports like `from schemas...` work
# no matter where you run the script from.
# ---------------------------------------------------------
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# ---------------------------------------------------------

from typing import Dict, Any, Optional

from schemas.user_profile import UserProfile
from schemas.country_ranking import CountryRanking


class SessionService:
    """
    Simple in-memory session manager for the Immigration Pathfinder project.

    Each session is stored as:
    {
        "user_profile": UserProfile | None,
        "country_ranking": CountryRanking | None,
        "recommendation_results": dict | None,
    }

    Behavior expected by tests:
      - If a session does not exist and update_* is called → create session automatically.
      - get_* methods return None if no data exists.
      - reset_session completely clears that session.
    """

    def __init__(self) -> None:
        # All sessions are stored here:
        # { session_id: { "user_profile": ..., "country_ranking": ..., "recommendation_results": ... } }
        self._sessions: Dict[str, Dict[str, Any]] = {}

    # -------------------------------------------------
    # Internal helper
    # -------------------------------------------------
    def _ensure_session(self, session_id: str) -> Dict[str, Any]:
        """
        Ensure a session exists for this session_id.
        If it does not exist, create an empty one.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "user_profile": None,
                "country_ranking": None,
                "recommendation_results": None,
            }
        return self._sessions[session_id]

    # -------------------------------------------------
    # User profile methods
    # -------------------------------------------------
    def get_user_profile(self, session_id: str) -> Optional[UserProfile]:
        """
        Return the user profile for this session_id, or None if missing.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        return session.get("user_profile")

    def update_user_profile(self, session_id: str, new_profile_data: Any) -> None:
        """
        Update the user profile for this session_id.

        Expected behavior (aligned with tests):

          - If the session does not exist → create it.
          - If there is no existing profile → store the new one directly.
          - If a profile already exists → merge existing + new data
            (new values override old values).

        Accepts:
          - UserProfile instance
          - dict-like object (e.g. from .model_dump())
        """
        session = self._ensure_session(session_id)

        current: Optional[UserProfile] = session.get("user_profile")

        # No existing profile → set directly
        if current is None:
            if isinstance(new_profile_data, UserProfile):
                session["user_profile"] = new_profile_data
            else:
                session["user_profile"] = UserProfile(**new_profile_data)
            return

        # Existing profile → merge
        if isinstance(new_profile_data, UserProfile):
            update_data = new_profile_data.model_dump(exclude_unset=True)
        else:
            update_data = dict(new_profile_data)

        base_data = current.model_dump()

        # Deep merge to properly handle nested structures
        def deep_merge(dest: Dict[str, Any], src: Dict[str, Any]) -> None:
            for key, value in src.items():
                if isinstance(value, dict) and isinstance(dest.get(key), dict):
                    deep_merge(dest[key], value)
                else:
                    dest[key] = value

        deep_merge(base_data, update_data)

        session["user_profile"] = UserProfile(**base_data)

    # -------------------------------------------------
    # Country ranking methods
    # -------------------------------------------------
    def get_country_ranking(self, session_id: str) -> Optional[CountryRanking]:
        """
        Return the country ranking for this session_id, or None if missing.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        return session.get("country_ranking")

    def update_country_ranking(self, session_id: str, ranking: CountryRanking) -> None:
        """
        Store/update the country ranking for this session_id.
        If the session does not exist, it will be created.
        """
        session = self._ensure_session(session_id)
        session["country_ranking"] = ranking

    # -------------------------------------------------
    # Recommendation results (raw dict, optional)
    # -------------------------------------------------
    def store_recommendation_results(self, session_id: str, results: Dict[str, Any]) -> None:
        """
        Store raw recommendation results (e.g. full JSON from orchestrator)
        for this session_id.
        """
        session = self._ensure_session(session_id)
        session["recommendation_results"] = results

    def get_recommendation_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Return raw recommendation results for this session_id, or None if missing.
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        return session.get("recommendation_results")

    # -------------------------------------------------
    # Reset / delete / debug
    # -------------------------------------------------
    def reset_session(self, session_id: str) -> None:
        """
        Completely clear one session's data.

        After this:
          - get_user_profile(session_id) → None
          - get_country_ranking(session_id) → None
          - get_recommendation_results(session_id) → None
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

    def delete_session(self, session_id: str) -> None:
        """
        Alias for removing a session completely.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Return the entire sessions dictionary. Useful for debugging/tests.
        """
        return self._sessions
