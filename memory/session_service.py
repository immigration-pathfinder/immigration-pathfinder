from typing import Dict, Any, Optional # Add Optional here
from schemas.user_profile import UserProfile
from schemas.country_ranking import CountryRanking
import uuid
import copy

class SessionService:
    _sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "user_profile": UserProfile(),
            "recommendation_results": None
        }
        return session_id

    def get_user_profile(self, session_id: str) -> Optional[UserProfile]: # Change here
        session = self._sessions.get(session_id)
        if session:
            return session["user_profile"]
        return None

    def update_user_profile(self, session_id: str, new_profile_data: Dict[str, Any]):
        session = self._sessions.get(session_id)
        if session:
            current_profile = session["user_profile"].model_dump()
            # Merge new data into current profile
            # This is a shallow merge, for nested structures, a deeper merge might be needed
            for key, value in new_profile_data.items():
                if hasattr(session["user_profile"], key):
                    setattr(session["user_profile"], key, value)
            # Re-validate the profile after update
            session["user_profile"] = UserProfile(**session["user_profile"].model_dump())
        else:
            raise ValueError(f"Session with ID {session_id} not found.")

    def store_recommendation_results(self, session_id: str, results: Dict[str, Any]):
        session = self._sessions.get(session_id)
        if session:
            session["recommendation_results"] = copy.deepcopy(results)
        else:
            raise ValueError(f"Session with ID {session_id} not found.")

    def get_recommendation_results(self, session_id: str) -> Optional[Dict[str, Any]]: # Change here
        session = self._sessions.get(session_id)
        if session:
            return session["recommendation_results"]
        return None

    def reset_session(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id] = {
                "user_profile": UserProfile(),
                "recommendation_results": None
            }
        else:
            raise ValueError(f"Session with ID {session_id} not found.")

    def delete_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
        else:
            raise ValueError(f"Session with ID {session_id} not found.")

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        return self._sessions

