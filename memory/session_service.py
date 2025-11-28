from typing import Dict, Any
from schemas.user_profile import UserProfile
from schemas.country_ranking import CountryRanking

class SessionService:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def _get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "user_profile": None,
                "country_ranking": None
            }
        return self.sessions[session_id]

    def get_user_profile(self, session_id: str) -> UserProfile | None:
        session = self._get_or_create_session(session_id)
        return session["user_profile"]

    def update_user_profile(self, session_id: str, user_profile: UserProfile):
        session = self._get_or_create_session(session_id)
        session["user_profile"] = user_profile

    def get_country_ranking(self, session_id: str) -> CountryRanking | None:
        session = self._get_or_create_session(session_id)
        return session["country_ranking"]

    def update_country_ranking(self, session_id: str, country_ranking: CountryRanking):
        session = self._get_or_create_session(session_id)
        session["country_ranking"] = country_ranking

    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        return self.sessions

