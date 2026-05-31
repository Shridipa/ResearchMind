export type SourceSpan = {
  paper_id: string;
  title?: string;
  page?: number;
  chunk_id: string;
  score: number;
  text: string;
};

export type RetrievalStats = {
  semantic_score?: number | null;
  bm25_score?: number | null;
  final_score: number;
  retrieval_mode: string;
};

export type SummarizationStats = {
  mode: string;  // "extractive", "transformer", "llm"
  tokens_saved: number;
  api_calls_avoided: number;
  cache_hit?: boolean;
};

export type GroundingStats = {
  groundedness_score: number;  // 0-100
  hallucination_risk: number;  // 0-100
  risk_level: string;  // low, medium, high
  supported_claims: number;
  total_claims: number;
};

export type SectionComparison = {
  section_name: string;
  similarity_score: number;
  key_differences: string[];
  key_similarities: string[];
  paper1_length: number;
  paper2_length: number;
};

export type PaperComparisonResponse = {
  paper1_id: string;
  paper1_title: string;
  paper2_id: string;
  paper2_title: string;
  overall_similarity: number;
  shared_concepts: string[];
  distinctive_concepts_p1: string[];
  distinctive_concepts_p2: string[];
  relationship_type: string;  // building_on, alternative, complementary, unrelated
  confidence: number;
  section_comparisons: Record<string, SectionComparison>;
  recommendations: string[];
};

export type ProviderMetadata = {
  selected_model: string;
  latency_ms: number;
  retry_count: number;
  fallback_triggered: boolean;
  attempted_models: string[];
  error?: string | null;
};

export type ChatResponse = {
  answer: string;
  confidence: number;
  unsupported_claim_risk: number;
  sources: SourceSpan[];
  provider_metadata?: ProviderMetadata | null;
  retrieval_stats?: RetrievalStats | null;
  grounding_stats?: GroundingStats | null;
};

export type PaperRecord = {
  paper_id: string;
  filename: string;
  title: string;
  authors: string[];
  upload_date: string;
  chunks_indexed: number;
  citations_found: number;
  status: string;
  processing_state: string;
  embedding_status: string;
  abstract?: string | null;
  sections: string[];
  methodology?: string | null;
  limitations: string[];
  key_contributions: string[];
  citations: string[];
  summary?: Record<string, string | string[]> | null;
};

export type PaperSearchResult = PaperRecord & {
  similarity_score: number;
};

export type BenchmarkMetric = {
  name: string;
  value: number;
  unit: string;
  delta?: number | null;
  trend: string;
};

export type ChartPoint = {
  label: string;
  value: number;
  secondary?: number | null;
};

export type EmbeddingModelMetric = {
  model: string;
  speed_ms: number;
  retrieval_quality: number;
  memory_mb: number;
};

export type ExperimentRecord = {
  experiment_id: string;
  dataset: string;
  model: string;
  metric: string;
  score: number;
  timestamp: string;
  status: string;
};

export type BenchmarkResponse = {
  metrics: BenchmarkMetric[];
  latency_trends: ChartPoint[];
  embedding_models: EmbeddingModelMetric[];
  chunking_strategies: ChartPoint[];
  hallucination_reduction: ChartPoint[];
  confidence_heatmap: ChartPoint[];
};

export type SummaryResponse = {
  paper_id: string;
  summary: Record<string, string | string[]>;
  sources: SourceSpan[];
};

export type PaperActionResponse = {
  action: string;
  status: string;
  result: Record<string, string | string[] | Array<Record<string, string>>>;
};

export type EvaluateResponse = {
  experiment: ExperimentRecord;
  details?: Record<string, string | number | null> | null;
};

export type LiteratureReviewResponse = {
  topic: string;
  review: string;
  confidence: number;
  unsupported_claim_risk: number;
  sources: SourceSpan[];
};

export type SessionInsights = {
  total_turns: number;
  papers_explored: number;
  unique_concepts: number;
  average_grounding: number;
  topic_clusters: number;
  divergence_points: number;
  session_summary: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function uploadPaper(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/v1/papers/upload`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function askQuestion(question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: 5 })
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function askQuestionStream(
  question: string,
  onMetadata: (metadata: Partial<ChatResponse>) => void,
  onContent: (text: string) => void,
  onEnd: () => void
) {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: 5 }),
  });

  if (!response.ok) throw new Error(await response.text());
  if (!response.body) throw new Error("No body in response");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const parts = line.split("\n");
      const eventPart = parts.find((p) => p.startsWith("event:"));
      const dataPart = parts.find((p) => p.startsWith("data:"));

      if (eventPart && dataPart) {
        const event = eventPart.replace("event:", "").trim();
        const dataStr = dataPart.replace("data:", "").trim();

        if (event === "metadata") {
          onMetadata(JSON.parse(dataStr));
        } else if (event === "content") {
          onContent(JSON.parse(dataStr).text);
        } else if (event === "end") {
          onEnd();
        }
      }
    }
  }
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export async function listPapers(): Promise<PaperRecord[]> {
  return fetchJson("/api/v1/papers");
}

export async function deletePaper(paperId: string): Promise<void> {
  await fetchJson(`/api/v1/papers/${paperId}`, {
    method: "DELETE",
  });
}

export async function getPaper(paperId: string): Promise<PaperRecord> {
  return fetchJson(`/api/v1/papers/${paperId}`);
}

export async function searchPapers(query: string): Promise<PaperSearchResult[]> {
  const response = await fetchJson<{ results: PaperSearchResult[] }>("/api/v1/papers/search", {
    method: "POST",
    body: JSON.stringify({ query, top_k: 5 })
  });
  return response.results;
}

export async function summarizePaper(paperId: string): Promise<SummaryResponse> {
  return fetchJson<SummaryResponse>("/api/v1/papers/summarize", {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId })
  });
}

export async function runPaperAction(action: string, paperId?: string): Promise<PaperActionResponse> {
  return fetchJson<PaperActionResponse>(`/api/v1/papers/actions/${action}`, {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId })
  });
}

export async function getBenchmarks(): Promise<BenchmarkResponse> {
  return fetchJson("/api/v1/benchmarks");
}

export async function getExperiments(): Promise<ExperimentRecord[]> {
  const response = await fetchJson<{ experiments: ExperimentRecord[] }>("/api/v1/benchmarks/experiments");
  return response.experiments;
}

export async function runEvaluation(dataset = "sample_qa", model = "BGE embeddings"): Promise<EvaluateResponse> {
  return fetchJson<EvaluateResponse>("/api/v1/benchmarks/evaluate", {
    method: "POST",
    body: JSON.stringify({ dataset, model })
  });
}

export async function generateLiteratureReview(
  topic: string,
  paperIds?: string[]
): Promise<LiteratureReviewResponse> {
  return fetchJson<LiteratureReviewResponse>("/api/v1/literature-review", {
    method: "POST",
    body: JSON.stringify({ topic, paper_ids: paperIds ?? null }),
  });
}
