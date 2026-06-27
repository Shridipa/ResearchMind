"""Reasoning engine that uses memory and topic graphs."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.services.session_memory import SessionMemoryStore, ConversationTurn, ConversationContext
from app.services.topic_graph import TopicGraph, ReasoningPath
from app.rag.embeddings import EmbeddingModel


@dataclass
class ReasoningContext:
    """Context for reasoning over a research session."""
    session_id: str
    turn_id: str
    question: str
    available_context: str
    topic_graph: TopicGraph
    reasoning_path: ReasoningPath
    recent_papers: list[str]
    recent_concepts: list[str]


class MultiTurnReasoningEngine:
    """
    Multi-turn reasoning with memory and topic understanding.
    
    Provides:
    - Context accumulation across turns
    - Topic graph for understanding discourse
    - Follow-up question generation
    - Reasoning chain tracking
    - Paper recommendation based on history
    """
    
    def __init__(
        self,
        memory_store: SessionMemoryStore,
        embedder: EmbeddingModel,
    ):
        """
        Initialize reasoning engine.
        
        Args:
            memory_store: Session memory storage
            embedder: Embedding model for concept similarity
        """
        self.memory_store = memory_store
        self.embedder = embedder
        self.topic_graphs: dict[str, TopicGraph] = {}
        self.reasoning_paths: dict[str, ReasoningPath] = {}
    
    def initialize_session(self, session_id: str, title: str = "") -> ReasoningContext:
        """Start a new reasoning session."""
        # Create session in memory store
        self.memory_store.create_session(
            session_id,
            title=title or f"Research Session {session_id}",
        )
        
        # Create topic graph and reasoning path
        self.topic_graphs[session_id] = TopicGraph()
        self.reasoning_paths[session_id] = ReasoningPath()
        
        context = ReasoningContext(
            session_id=session_id,
            turn_id="turn_0",
            question="",
            available_context="",
            topic_graph=self.topic_graphs[session_id],
            reasoning_path=self.reasoning_paths[session_id],
            recent_papers=[],
            recent_concepts=[],
        )
        
        return context
    
    def process_turn(
        self,
        session_id: str,
        question: str,
        answer: str,
        concepts: list[str],
        papers_cited: list[str],
        grounding_score: Optional[float] = None,
        sources: Optional[list[dict]] = None,
    ) -> ReasoningContext:
        """
        Process a conversation turn and update memory/graph.
        
        Args:
            session_id: Session ID
            question: User question
            answer: Generated answer
            concepts: Concepts mentioned in answer
            papers_cited: Papers cited in answer
            grounding_score: Grounding validation score
            sources: Evidence sources
        
        Returns:
            Updated reasoning context
        """
        session = self.memory_store.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Create turn
        turn_id = f"turn_{len(session.turns) + 1}"
        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=datetime.now(),
            question=question,
            answer=answer,
            sources=sources or [],
            grounding_score=grounding_score,
            papers_cited=papers_cited,
            key_concepts=concepts,
        )
        
        # Add turn to session
        self.memory_store.add_turn(session_id, turn)
        
        # Update topic graph
        graph = self.topic_graphs[session_id]
        for concept in concepts:
            try:
                # Get embedding for concept if available
                concept_emb = self.embedder.embed(concept)
                graph.add_concept(concept, turn_id, concept_emb)
            except Exception:
                graph.add_concept(concept, turn_id)
        
        # Add relationships between concepts
        if len(concepts) > 1:
            for i, c1 in enumerate(concepts):
                for c2 in concepts[i+1:]:
                    graph.add_relationship(c1, c2, turn_id=turn_id)
        
        # Create context for next turn
        session_context = ConversationContext(session)
        
        context = ReasoningContext(
            session_id=session_id,
            turn_id=turn_id,
            question=question,
            available_context=session_context.get_recent_context(5),
            topic_graph=graph,
            reasoning_path=self.reasoning_paths[session_id],
            recent_papers=papers_cited[-3:],  # Last 3 papers
            recent_concepts=concepts[-5:],  # Last 5 concepts
        )
        
        return context
    
    def get_context_for_next_turn(self, session_id: str) -> str:
        """Get context to prepend to next query."""
        session = self.memory_store.get_session(session_id)
        if not session or not session.turns:
            return ""
        
        session_context = ConversationContext(session)
        
        # Build context from recent turns and topic graph
        context_parts = []
        
        # Recent conversation context
        context_parts.append("Previous discussion:\n")
        context_parts.append(session_context.get_recent_context(3))
        
        # Topic summary
        graph = self.topic_graphs.get(session_id)
        if graph:
            central_topics = graph.get_central_concepts(5)
            context_parts.append(f"\nKey topics: {', '.join(central_topics)}")
        
        # Paper context
        all_papers = list(session.papers_used)[-5:]
        if all_papers:
            context_parts.append(f"\nRecent papers: {', '.join(all_papers)}")
        
        return "\n".join(context_parts)
    
    def generate_follow_ups(self, session_id: str) -> list[str]:
        """Generate follow-up questions for session."""
        session = self.memory_store.get_session(session_id)
        if not session:
            return []
        
        session_context = ConversationContext(session)
        suggestions = session_context.identify_follow_ups()
        
        graph = self.topic_graphs.get(session_id)
        if graph:
            # Suggest exploring concept relationships
            central = graph.get_central_concepts(3)
            for i, concept in enumerate(central):
                neighbors = graph.get_neighbors(concept, depth=1)
                if neighbors:
                    related = list(neighbors)[0]
                    suggestions.append(
                        f"How does {concept} relate to {related}?"
                    )
        
        return suggestions[:5]  # Return top 5
    
    def get_reasoning_chain(self, session_id: str) -> str:
        """Get the reasoning chain for a session."""
        path = self.reasoning_paths.get(session_id)
        if not path:
            return ""
        
        return path.get_reasoning_chain()
    
    def get_session_insights(self, session_id: str) -> dict:
        """Get insights about research session."""
        session = self.memory_store.get_session(session_id)
        if not session:
            return {}
        
        graph = self.topic_graphs.get(session_id)
        
        insights = {
            "session_summary": session.get_session_summary(),
            "total_turns": len(session.turns),
            "papers_explored": len(session.papers_used),
            "unique_concepts": len(session.all_concepts),
        }
        
        if graph:
            insights.update(graph.get_graph_summary())
            insights["topic_clusters"] = len(graph.get_topic_clusters())
            insights["divergence_points"] = len(graph.get_divergence_points())
        
        # Average grounding score
        grounded_turns = [t for t in session.turns if t.grounding_score]
        if grounded_turns:
            avg_grounding = sum(t.grounding_score for t in grounded_turns) / len(grounded_turns)
            insights["average_grounding"] = avg_grounding
        
        return insights
    
    def export_session_graph(self, session_id: str) -> dict:
        """Export session as graph for visualization."""
        graph = self.topic_graphs.get(session_id)
        if not graph:
            return {}
        
        return graph.to_dict()
    
    def export_reasoning_visualization(self, session_id: str) -> dict:
        """Export reasoning chain as visualization."""
        path = self.reasoning_paths.get(session_id)
        if not path:
            return {}
        
        return path.visualize()

