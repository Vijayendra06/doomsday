from collections import OrderedDict, deque
from dataclasses import dataclass
from threading import RLock
from uuid import UUID

MAX_TURNS = 6
MAX_ACTIVE_SESSIONS = 32


@dataclass(frozen=True)
class Message:
    role: str
    content: str


# ==============================================================================
# PHASE 2: THE BRAIN (6-Turn Bounded Conversation Memory)
# ==============================================================================
class ConversationStore:
    """
    TODO (Phase 2 - Step 4):
    Bounded, process-local history. One turn is one user/assistant pair.
    """

    def __init__(self) -> None:
        self._sessions: OrderedDict[UUID, deque[Message]] = OrderedDict()
        self._lock = RLock()

    def history(self, session_id: UUID) -> list[dict[str, str]]:
        """
        TODO: Return past messages for this session in OpenAI format:
        [{"role": "user"|"assistant", "content": "..."}]
        """
        with self._lock:
            messages = self._sessions.get(session_id, ())
            return [{"role": message.role, "content": message.content} for message in messages]

    def append_turn(self, session_id: UUID, user_text: str, assistant_text: str) -> int:
        """
        TODO: Store user message + assistant reply in a deque(maxlen=12).
        Retain max 6 turns. Return len(messages) // 2.
        """
        with self._lock:
            messages = self._sessions.setdefault(session_id, deque(maxlen=MAX_TURNS * 2))
            messages.extend((Message("user", user_text), Message("assistant", assistant_text)))
            self._sessions.move_to_end(session_id)
            while len(self._sessions) > MAX_ACTIVE_SESSIONS:
                self._sessions.popitem(last=False)
            return len(messages) // 2

    def clear(self, session_id: UUID) -> None:
        """Clear memory for a session."""
        with self._lock:
            self._sessions.pop(session_id, None)
