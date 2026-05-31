"""Topic graph for research conversation tracking."""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import math


@dataclass
class Concept:
    """A research concept/topic."""
    name: str
    frequency: int = 1  # How many times mentioned
    embedding: Optional[list[float]] = None
    related_concepts: set[str] = field(default_factory=set)
    first_mentioned: Optional[str] = None  # Turn ID
    last_mentioned: Optional[str] = None
    
    def similarity_to(self, other: "Concept") -> float:
        """Compute similarity to another concept."""
        if not self.embedding or not other.embedding:
            # Lexical similarity fallback
            common_chars = set(self.name.lower()) & set(other.name.lower())
            return len(common_chars) / max(len(self.name), len(other.name), 1)
        
        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(self.embedding, other.embedding))
        norm_a = math.sqrt(sum(a * a for a in self.embedding))
        norm_b = math.sqrt(sum(b * b for b in other.embedding))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)


@dataclass
class Edge:
    """Connection between two concepts."""
    source: str
    target: str
    weight: float = 1.0  # Strength of connection
    connection_type: str = "related"  # related, contradicts, builds_on
    evidence: list[str] = field(default_factory=list)  # Turn IDs where connected


class TopicGraph:
    """
    Build and maintain a topic graph of research concepts.
    
    Tracks:
    - Concepts mentioned in conversation
    - Relationships between concepts
    - Concept frequency and importance
    - Evolution of topics over turns
    """
    
    def __init__(self):
        self.concepts: dict[str, Concept] = {}
        self.edges: list[Edge] = []
        self.concept_by_turn: dict[str, list[str]] = defaultdict(list)
    
    def add_concept(
        self,
        name: str,
        turn_id: str,
        embedding: Optional[list[float]] = None,
    ):
        """Add a concept to the graph."""
        name_lower = name.lower()
        
        if name_lower not in self.concepts:
            self.concepts[name_lower] = Concept(
                name=name,
                embedding=embedding,
                first_mentioned=turn_id,
                last_mentioned=turn_id,
            )
        else:
            # Update existing concept
            concept = self.concepts[name_lower]
            concept.frequency += 1
            concept.last_mentioned = turn_id
            if embedding:
                concept.embedding = embedding
        
        self.concept_by_turn[turn_id].append(name_lower)
    
    def add_relationship(
        self,
        source: str,
        target: str,
        connection_type: str = "related",
        turn_id: Optional[str] = None,
        weight: float = 1.0,
    ):
        """Add relationship between two concepts."""
        source_lower = source.lower()
        target_lower = target.lower()
        
        # Create concepts if they don't exist
        if source_lower not in self.concepts:
            self.concepts[source_lower] = Concept(name=source)
        if target_lower not in self.concepts:
            self.concepts[target_lower] = Concept(name=target)
        
        # Add bidirectional reference
        self.concepts[source_lower].related_concepts.add(target_lower)
        self.concepts[target_lower].related_concepts.add(source_lower)
        
        # Create edge
        edge = Edge(
            source=source_lower,
            target=target_lower,
            weight=weight,
            connection_type=connection_type,
        )
        if turn_id:
            edge.evidence.append(turn_id)
        
        self.edges.append(edge)
    
    def get_neighbors(self, concept: str, depth: int = 1) -> set[str]:
        """Get concepts within N hops."""
        concept_lower = concept.lower()
        neighbors = set()
        to_explore = {concept_lower}
        current_depth = 0
        
        while to_explore and current_depth < depth:
            next_explore = set()
            for node in to_explore:
                if node in self.concepts:
                    related = self.concepts[node].related_concepts
                    neighbors.update(related)
                    next_explore.update(related - neighbors)
            
            to_explore = next_explore
            current_depth += 1
        
        return neighbors
    
    def get_concept_importance(self) -> dict[str, float]:
        """Rank concepts by importance."""
        importance = {}
        
        for name, concept in self.concepts.items():
            # Frequency score
            freq_score = math.log(concept.frequency + 1)
            
            # Connectivity score
            connectivity = len(concept.related_concepts)
            conn_score = math.log(connectivity + 1)
            
            # Combined score
            importance[name] = 0.7 * freq_score + 0.3 * conn_score
        
        return importance
    
    def get_central_concepts(self, top_k: int = 10) -> list[str]:
        """Get most central/important concepts."""
        importance = self.get_concept_importance()
        sorted_concepts = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in sorted_concepts[:top_k]]
    
    def get_topic_clusters(self) -> dict[str, list[str]]:
        """Group related concepts into clusters."""
        clusters = {}
        visited = set()
        
        for concept_name in self.concepts:
            if concept_name in visited:
                continue
            
            # BFS to find connected component
            cluster = set()
            to_explore = {concept_name}
            
            while to_explore:
                node = to_explore.pop()
                if node in visited:
                    continue
                
                visited.add(node)
                cluster.add(node)
                
                if node in self.concepts:
                    related = self.concepts[node].related_concepts
                    to_explore.update(related - visited)
            
            if len(cluster) > 1:
                cluster_id = f"cluster_{len(clusters)}"
                clusters[cluster_id] = [self.concepts[c].name for c in cluster]
        
        return clusters
    
    def get_graph_summary(self) -> dict:
        """Get summary statistics of the graph."""
        total_edges = len(self.edges)
        avg_degree = (
            2 * total_edges / len(self.concepts)
            if self.concepts else 0
        )
        
        return {
            "total_concepts": len(self.concepts),
            "total_edges": total_edges,
            "average_degree": avg_degree,
            "central_concepts": self.get_central_concepts(5),
            "num_clusters": len(self.get_topic_clusters()),
        }
    
    def get_concept_evolution(self, concept: str) -> list[dict]:
        """Get temporal evolution of a concept."""
        concept_lower = concept.lower()
        evolution = []
        
        for turn_id, concepts_in_turn in self.concept_by_turn.items():
            if concept_lower in concepts_in_turn:
                evolution.append({
                    "turn": turn_id,
                    "mentioned": True,
                })
        
        return evolution
    
    def get_divergence_points(self) -> list[dict]:
        """Find where conversation branches into new topics."""
        divergence = []
        
        prev_concepts = set()
        for turn_id in sorted(self.concept_by_turn.keys(), key=lambda x: int(x.split("_")[-1])):
            current_concepts = set(self.concept_by_turn[turn_id])
            
            # New concepts introduced
            new_concepts = current_concepts - prev_concepts
            if new_concepts and prev_concepts:  # Not the first turn
                divergence.append({
                    "turn": turn_id,
                    "new_concepts": list(new_concepts),
                    "previous_concepts": list(prev_concepts),
                })
            
            prev_concepts = current_concepts
        
        return divergence
    
    def suggest_related_papers(self, concept: str, num_suggestions: int = 5) -> list[str]:
        """Suggest papers related to a concept."""
        # This is a placeholder - would integrate with paper metadata
        central = self.get_central_concepts(num_suggestions)
        return [c for c in central if c != concept.lower()][:num_suggestions]
    
    def to_dict(self) -> dict:
        """Serialize graph to dictionary."""
        return {
            "concepts": {
                name: {
                    "frequency": c.frequency,
                    "related": list(c.related_concepts),
                    "first_mentioned": c.first_mentioned,
                    "last_mentioned": c.last_mentioned,
                }
                for name, c in self.concepts.items()
            },
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "weight": e.weight,
                    "type": e.connection_type,
                }
                for e in self.edges
            ],
            "summary": self.get_graph_summary(),
        }


class ReasoningPath:
    """Track the reasoning path through a research session."""
    
    def __init__(self):
        self.steps: list[dict] = []
    
    def add_step(
        self,
        question: str,
        reasoning: str,
        conclusion: str,
        supporting_papers: list[str],
    ):
        """Add a reasoning step."""
        self.steps.append({
            "question": question,
            "reasoning": reasoning,
            "conclusion": conclusion,
            "supporting_papers": supporting_papers,
        })
    
    def get_reasoning_chain(self) -> str:
        """Get the full reasoning chain."""
        chain_parts = []
        for i, step in enumerate(self.steps, 1):
            chain_parts.append(f"Step {i}: {step['question']}")
            chain_parts.append(f"  Reasoning: {step['reasoning']}")
            chain_parts.append(f"  Conclusion: {step['conclusion']}")
        
        return "\n".join(chain_parts)
    
    def visualize(self) -> dict:
        """Get visualization-ready reasoning chain."""
        nodes = []
        edges = []
        
        for i, step in enumerate(self.steps):
            # Question node
            q_node_id = f"q_{i}"
            nodes.append({
                "id": q_node_id,
                "label": step["question"],
                "type": "question",
            })
            
            # Conclusion node
            c_node_id = f"c_{i}"
            nodes.append({
                "id": c_node_id,
                "label": step["conclusion"],
                "type": "conclusion",
            })
            
            # Question -> Conclusion edge
            edges.append({
                "source": q_node_id,
                "target": c_node_id,
                "type": "reasoning",
            })
            
            # Link to next question
            if i < len(self.steps) - 1:
                next_q_node_id = f"q_{i+1}"
                edges.append({
                    "source": c_node_id,
                    "target": next_q_node_id,
                    "type": "leads_to",
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "steps": len(self.steps),
        }
