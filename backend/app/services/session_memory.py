"""Session memory for multi-turn research conversations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json
from pathlib import Path


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    turn_id: str
    timestamp: datetime
    question: str
    answer: str
    sources: list[dict] = field(default_factory=list)
    grounding_score: Optional[float] = None
    papers_cited: list[str] = field(default_factory=list)
    key_concepts: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "turn_id": self.turn_id,
            "timestamp": self.timestamp.isoformat(),
            "question": self.question,
            "answer": self.answer,
            "sources": self.sources,
            "grounding_score": self.grounding_score,
            "papers_cited": self.papers_cited,
            "key_concepts": self.key_concepts,
        }


@dataclass
class ResearchSession:
    """A research session with multiple turns."""
    session_id: str
    created_at: datetime
    title: Optional[str] = None
    description: Optional[str] = None
    turns: list[ConversationTurn] = field(default_factory=list)
    papers_used: set[str] = field(default_factory=set)
    all_concepts: set[str] = field(default_factory=set)
    metadata: dict = field(default_factory=dict)
    
    def add_turn(self, turn: ConversationTurn):
        """Add a conversation turn."""
        self.turns.append(turn)
        self.papers_used.update(turn.papers_cited)
        self.all_concepts.update(turn.key_concepts)
    
    def get_context(self, include_turns: int = 5) -> str:
        """Get conversation context for context window."""
        recent_turns = self.turns[-include_turns:]
        
        context_parts = []
        for turn in recent_turns:
            context_parts.append(f"Q: {turn.question}")
            context_parts.append(f"A: {turn.answer}")
        
        return "\n\n".join(context_parts)
    
    def get_session_summary(self) -> str:
        """Get summary of entire session."""
        summary = f"Session: {self.title or self.session_id}\n"
        summary += f"Turns: {len(self.turns)}\n"
        summary += f"Papers Used: {len(self.papers_used)}\n"
        summary += f"Unique Concepts: {len(self.all_concepts)}\n"
        
        if self.turns:
            first_turn = self.turns[0]
            last_turn = self.turns[-1]
            summary += f"\nFirst Question: {first_turn.question}\n"
            summary += f"Latest Question: {last_turn.question}\n"
        
        return summary
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "title": self.title,
            "description": self.description,
            "turns": [turn.to_dict() for turn in self.turns],
            "papers_used": list(self.papers_used),
            "all_concepts": list(self.all_concepts),
            "metadata": self.metadata,
        }


class SessionMemoryStore:
    """
    Store and manage research session memory.
    
    Persists sessions to disk for recovery and analysis.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize session memory store.
        
        Args:
            storage_path: Path to store session data (default: data/sessions)
        """
        self.storage_path = storage_path or Path("../data/sessions")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions = {}  # In-memory cache
    
    def create_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ResearchSession:
        """Create a new research session."""
        session = ResearchSession(
            session_id=session_id,
            created_at=datetime.now(),
            title=title,
            description=description,
        )
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def add_turn(self, session_id: str, turn: ConversationTurn):
        """Add turn to session."""
        session = self.get_session(session_id)
        if session:
            session.add_turn(turn)
            self.persist_session(session)
    
    def persist_session(self, session: ResearchSession):
        """Save session to disk."""
        filepath = self.storage_path / f"{session.session_id}.json"
        
        with open(filepath, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def load_session(self, session_id: str) -> Optional[ResearchSession]:
        """Load session from disk."""
        filepath = self.storage_path / f"{session_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        # Reconstruct session
        session = ResearchSession(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            title=data.get("title"),
            description=data.get("description"),
            metadata=data.get("metadata", {}),
        )
        
        # Reconstruct turns
        for turn_data in data.get("turns", []):
            turn = ConversationTurn(
                turn_id=turn_data["turn_id"],
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                question=turn_data["question"],
                answer=turn_data["answer"],
                sources=turn_data.get("sources", []),
                grounding_score=turn_data.get("grounding_score"),
                papers_cited=turn_data.get("papers_cited", []),
                key_concepts=turn_data.get("key_concepts", []),
            )
            session.add_turn(turn)
        
        self.sessions[session_id] = session
        return session
    
    def list_sessions(self) -> list[str]:
        """List all available sessions."""
        files = self.storage_path.glob("*.json")
        return [f.stem for f in files]
    
    def get_session_stats(self, session_id: str) -> dict:
        """Get statistics about a session."""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        total_questions = len(session.turns)
        avg_grounding = (
            sum(t.grounding_score for t in session.turns if t.grounding_score) / 
            len([t for t in session.turns if t.grounding_score])
            if any(t.grounding_score for t in session.turns)
            else 0
        )
        
        return {
            "session_id": session_id,
            "turns": total_questions,
            "papers_used": len(session.papers_used),
            "unique_concepts": len(session.all_concepts),
            "average_grounding": avg_grounding,
            "created_at": session.created_at.isoformat(),
        }


class ConversationContext:
    """Build conversation context from session history."""
    
    def __init__(self, session: ResearchSession):
        self.session = session
    
    def get_recent_context(self, num_turns: int = 3) -> str:
        """Get recent conversation turns as context."""
        return self.session.get_context(num_turns)
    
    def get_topic_context(self) -> str:
        """Get context about all topics discussed."""
        concepts = list(self.session.all_concepts)[:20]
        papers = list(self.session.papers_used)[:10]
        
        context = "Research Context:\n"
        context += f"Topics: {', '.join(concepts)}\n"
        context += f"Papers: {', '.join(papers)}\n"
        
        return context
    
    def get_qa_pairs(self, include_answers: bool = True) -> list[dict]:
        """Get all Q&A pairs from session."""
        pairs = []
        for turn in self.session.turns:
            pair = {"question": turn.question}
            if include_answers:
                pair["answer"] = turn.answer
            pairs.append(pair)
        
        return pairs
    
    def identify_follow_ups(self) -> list[str]:
        """Suggest follow-up questions based on session."""
        suggestions = []
        
        # Suggest exploring related concepts
        if self.session.all_concepts:
            unexplored = list(self.session.all_concepts)[:5]
            for concept in unexplored:
                suggestions.append(f"How does {concept} relate to the papers we've discussed?")
        
        # Suggest comparisons
        if len(self.session.papers_used) >= 2:
            papers = list(self.session.papers_used)[:2]
            suggestions.append(f"How do {papers[0]} and {papers[1]} compare?")
        
        return suggestions
