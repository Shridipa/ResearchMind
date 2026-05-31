"""Test and demonstration of research memory and session graph."""

import uuid
from datetime import datetime

from app.services.session_memory import SessionMemoryStore, ConversationTurn
from app.services.topic_graph import TopicGraph, ReasoningPath
from app.services.reasoning_engine import MultiTurnReasoningEngine
from app.rag.embeddings import build_embedder


def test_session_memory():
    """Test basic session memory functionality."""
    print("\n" + "="*80)
    print("SESSION MEMORY TEST")
    print("="*80 + "\n")
    
    store = SessionMemoryStore()
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Create session
    session = store.create_session(
        session_id,
        title="Transformer Architecture Research",
        description="Exploring evolution of transformer models",
    )
    
    print(f"Created session: {session.title}")
    print(f"Session ID: {session_id}\n")
    
    # Add turns
    turns_data = [
        {
            "question": "What is the Transformer architecture?",
            "answer": "The Transformer is a neural network model that uses self-attention mechanisms...",
            "concepts": ["transformer", "self-attention", "neural-network"],
            "papers": ["vaswani2017"],
        },
        {
            "question": "How does BERT extend transformers?",
            "answer": "BERT introduces bidirectional pre-training using masked language modeling...",
            "concepts": ["bert", "masked-language-modeling", "pre-training"],
            "papers": ["devlin2018"],
        },
        {
            "question": "What are the differences between BERT and GPT?",
            "answer": "BERT uses bidirectional context while GPT uses causal/unidirectional...",
            "concepts": ["gpt", "bidirectional", "causal"],
            "papers": ["radford2019"],
        },
    ]
    
    for i, turn_data in enumerate(turns_data):
        turn = ConversationTurn(
            turn_id=f"turn_{i}",
            timestamp=datetime.now(),
            question=turn_data["question"],
            answer=turn_data["answer"],
            papers_cited=turn_data["papers"],
            key_concepts=turn_data["concepts"],
        )
        session.add_turn(turn)
        print(f"✓ Turn {i}: {turn_data['question'][:50]}...")
    
    print(f"\nSession Summary:\n{session.get_session_summary()}")


def test_topic_graph():
    """Test topic graph construction."""
    print("\n" + "="*80)
    print("TOPIC GRAPH TEST")
    print("="*80 + "\n")
    
    graph = TopicGraph()
    
    # Add concepts and relationships
    concepts = [
        ("transformer", "turn_0"),
        ("self-attention", "turn_0"),
        ("bert", "turn_1"),
        ("masked-lm", "turn_1"),
        ("gpt", "turn_2"),
        ("causal-attention", "turn_2"),
    ]
    
    for concept, turn_id in concepts:
        graph.add_concept(concept, turn_id)
    
    # Add relationships
    graph.add_relationship("transformer", "self-attention", turn_id="turn_0")
    graph.add_relationship("bert", "transformer", turn_id="turn_1")
    graph.add_relationship("bert", "masked-lm", turn_id="turn_1")
    graph.add_relationship("gpt", "transformer", turn_id="turn_2")
    graph.add_relationship("gpt", "causal-attention", turn_id="turn_2")
    
    print(f"Added {len(graph.concepts)} concepts\n")
    
    # Analyze graph
    summary = graph.get_graph_summary()
    print(f"Graph Summary:")
    print(f"  Total Concepts: {summary['total_concepts']}")
    print(f"  Total Relationships: {summary['total_edges']}")
    print(f"  Average Degree: {summary['average_degree']:.2f}\n")
    
    print(f"Central Concepts: {', '.join(summary['central_concepts'])}\n")
    
    # Find clusters
    clusters = graph.get_topic_clusters()
    print(f"Topic Clusters: {len(clusters)}")
    for cluster_id, concepts in clusters.items():
        print(f"  {cluster_id}: {', '.join(concepts)}")
    
    # Find divergence points
    print(f"\nDivergence Points:")
    divergences = graph.get_divergence_points()
    for div in divergences:
        print(f"  {div['turn']}: Introduced {', '.join(div['new_concepts'])}")


def test_reasoning_engine():
    """Test multi-turn reasoning engine."""
    print("\n" + "="*80)
    print("MULTI-TURN REASONING ENGINE TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    memory_store = SessionMemoryStore()
    engine = MultiTurnReasoningEngine(memory_store, embedder)
    
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Initialize session
    ctx = engine.initialize_session(session_id, "Transformer Models Analysis")
    print(f"Initialized session: {session_id}\n")
    
    # Simulate conversation turns
    turns = [
        {
            "question": "What is the Transformer architecture?",
            "answer": "The Transformer uses self-attention and feed-forward networks...",
            "concepts": ["transformer", "attention"],
            "papers": ["vaswani2017"],
            "grounding": 0.92,
        },
        {
            "question": "How does it improve over RNNs?",
            "answer": "Transformers allow parallel processing and better long-range dependencies...",
            "concepts": ["parallel-processing", "long-range-dependencies", "rnn"],
            "papers": ["vaswani2017"],
            "grounding": 0.88,
        },
        {
            "question": "What are attention heads?",
            "answer": "Multiple attention mechanisms running in parallel, each focusing on different features...",
            "concepts": ["attention-heads", "parallel-mechanisms"],
            "papers": ["vaswani2017"],
            "grounding": 0.85,
        },
    ]
    
    for i, turn in enumerate(turns):
        print(f"Turn {i+1}: {turn['question'][:50]}...")
        
        ctx = engine.process_turn(
            session_id,
            turn["question"],
            turn["answer"],
            turn["concepts"],
            turn["papers"],
            grounding_score=turn["grounding"],
        )
        
        print(f"  ✓ Added to session")
        print(f"  Concepts tracked: {len(ctx.topic_graph.concepts)}")
        print(f"  Papers cited: {', '.join(ctx.recent_papers)}\n")
    
    # Get insights
    print("Session Insights:")
    insights = engine.get_session_insights(session_id)
    for key, value in insights.items():
        if key != "session_summary":
            print(f"  {key}: {value}")


def test_follow_up_generation():
    """Test automatic follow-up question generation."""
    print("\n" + "="*80)
    print("FOLLOW-UP QUESTION GENERATION TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    memory_store = SessionMemoryStore()
    engine = MultiTurnReasoningEngine(memory_store, embedder)
    
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    ctx = engine.initialize_session(session_id, "Research Session")
    
    # Add some turns
    engine.process_turn(
        session_id,
        "What is BERT?",
        "BERT is a bidirectional transformer...",
        ["bert", "transformer"],
        ["devlin2018"],
        grounding_score=0.9,
    )
    
    engine.process_turn(
        session_id,
        "How is it pre-trained?",
        "BERT uses masked language modeling and next sentence prediction...",
        ["masked-lm", "pre-training"],
        ["devlin2018"],
        grounding_score=0.88,
    )
    
    # Generate follow-ups
    print("Suggested Follow-up Questions:\n")
    follow_ups = engine.generate_follow_ups(session_id)
    for i, question in enumerate(follow_ups, 1):
        print(f"  {i}. {question}")


def test_context_accumulation():
    """Test context accumulation for multi-turn understanding."""
    print("\n" + "="*80)
    print("CONTEXT ACCUMULATION TEST")
    print("="*80 + "\n")
    
    embedder = build_embedder()
    memory_store = SessionMemoryStore()
    engine = MultiTurnReasoningEngine(memory_store, embedder)
    
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    ctx = engine.initialize_session(session_id, "Knowledge Accumulation")
    
    # Simulate conversation
    questions = [
        "What is attention?",
        "How does it work with multiple heads?",
        "Why is positional encoding needed?",
    ]
    
    for question in questions:
        engine.process_turn(
            session_id,
            question,
            f"Answer to: {question}",
            ["concept1", "concept2"],
            ["paper1"],
            grounding_score=0.9,
        )
    
    # Get context for next turn
    print("Context for next turn:\n")
    context = engine.get_context_for_next_turn(session_id)
    print(context)


if __name__ == "__main__":
    print("\n" + "🎯 RESEARCH MEMORY + SESSION GRAPH DEMO")
    print("=" * 80)
    
    test_session_memory()
    test_topic_graph()
    test_reasoning_engine()
    test_follow_up_generation()
    test_context_accumulation()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✓ Session memory with persistent storage")
    print("✓ Topic graph construction and analysis")
    print("✓ Multi-turn reasoning with context")
    print("✓ Automatic follow-up generation")
    print("✓ Context accumulation across turns")
    print("✓ Session insights and metrics\n")
