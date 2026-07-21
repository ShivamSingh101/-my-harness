import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class SessionStore:
    """Creates, loads, lists, and saves session data."""

    def __init__(self, sessions_dir="sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create(self, kind="main", parent_name=None):
        session_id = str(uuid.uuid4())
        data = {
            "id": session_id,
            "kind": kind,
            "parent_name": parent_name,
            "created_at": self._now(),
            "updated_at": self._now(),
            "messages": [],
        }
        self.save(data)
        return data

    def load(self, session_id):
        path = self._path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        return json.loads(path.read_text(encoding="utf-8"))

    def load_or_create(self, session_id=None):
        if session_id:
            return self.load(session_id)
        return self.create()

    def save(self, session_data):
        session_data["updated_at"] = self._now()
        path = self._path(session_data["id"])
        path.write_text(json.dumps(session_data, indent=2), encoding="utf-8")
        return path

    def list_sessions(self):
        sessions = []
        for path in self.sessions_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                sessions.append(
                    {
                        "id": data.get("id"),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                        "kind": data.get("kind", "main"),
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except Exception:
                continue

        return sorted(sessions, key=lambda s: s.get("updated_at") or "", reverse=True)

    def _path(self, session_id):
        return self.sessions_dir / f"{session_id}.json"

    def _now(self):
        return datetime.now(timezone.utc).isoformat()


class Session:
    """Runtime session object used by the agent."""

    def __init__(self, store, data):
        self.store = store
        self.data = data

    @property
    def id(self):
        return self.data["id"]

    @property
    def messages(self):
        return self.data["messages"]

    @messages.setter
    def messages(self, value):
        self.data["messages"] = value

    def save(self):
        return self.store.save(self.data)
