import { ChatResponse } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, AlertCircle, CheckCircle } from "lucide-react";

interface SourcesPanelProps {
  answer: ChatResponse | null;
  isStreaming: boolean;
}

export function SourcesPanel({ answer, isStreaming }: SourcesPanelProps) {
  // Wait until streaming finishes to show sources, matching the HTML prototype behavior
  const showSources = answer && !isStreaming;
  const semanticScore = answer?.retrieval_stats?.semantic_score ?? null;
  const bm25Score = answer?.retrieval_stats?.bm25_score ?? null;

  const getGroundingColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "low":
        return "bg-[#10b981]/10 text-[#059669]";
      case "medium":
        return "bg-[#f59e0b]/10 text-[#b45309]";
      case "high":
        return "bg-[#ef4444]/10 text-[#dc2626]";
      default:
        return "bg-[#6b7280]/10 text-[#4b5563]";
    }
  };

  const getGroundingIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case "low":
        return <CheckCircle size={14} />;
      case "high":
        return <AlertCircle size={14} />;
      default:
        return <Zap size={14} />;
    }
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-[22px] border border-[#1A3B25] bg-[#0B1E12] transition-colors hover:border-[#29A662]">
      <div className="border-b border-[#1A3B25] bg-[#13311E] px-[22px] py-5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-bold text-[#FFFFFF]">Sources & Grounding</span>
          {answer?.retrieval_stats && (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-[#1F6F50]/20 px-2.5 py-1 text-[11px] font-semibold text-[#29A662]">
              <Zap size={12} />
              Hybrid
            </span>
          )}
        </div>
      </div>

      <div className="min-h-[300px] flex-1 bg-[#0B1E12] px-[22px] py-7 overflow-y-auto">
        <AnimatePresence mode="wait">
          {!showSources ? (
            <motion.p
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-[13.5px] text-[#A3BCA9]"
            >
              Sources and grounding analysis appear here after a response.
            </motion.p>
          ) : (
            <motion.div
              key="sources"
              initial="hidden"
              animate="visible"
              variants={{
                hidden: {},
                visible: {
                  transition: { staggerChildren: 0.05 }
                }
              }}
              className="flex flex-col space-y-4"
            >
              {/* Retrieval stats */}
              {answer?.retrieval_stats && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3"
                >
                  <div className="text-[11px] font-semibold text-[#829987] mb-2">RETRIEVAL SCORES</div>
                  <div className="grid grid-cols-3 gap-3">
                    {semanticScore !== null && semanticScore > 0 && (
                      <div>
                        <div className="text-[10px] text-[#829987]">Semantic</div>
                        <div className="text-[13px] font-semibold text-[#D1CEC7]">{semanticScore.toFixed(3)}</div>
                      </div>
                    )}
                    {bm25Score !== null && bm25Score > 0 && (
                      <div>
                        <div className="text-[10px] text-[#829987]">Keyword</div>
                        <div className="text-[13px] font-semibold text-[#D1CEC7]">{bm25Score.toFixed(3)}</div>
                      </div>
                    )}
                    <div>
                      <div className="text-[10px] text-[#829987]">Final</div>
                      <div className="text-[13px] font-semibold text-[#29A662]">{answer.retrieval_stats.final_score.toFixed(3)}</div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Grounding stats */}
              {answer?.grounding_stats && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className={`rounded-lg border border-[#1A3B25] p-3 ${getGroundingColor(answer.grounding_stats.risk_level)}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-semibold flex items-center gap-1">
                      {getGroundingIcon(answer.grounding_stats.risk_level)}
                      ANSWER GROUNDING
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-[10px] opacity-75">Groundedness</div>
                      <div className="text-[14px] font-bold">{answer.grounding_stats.groundedness_score.toFixed(0)}%</div>
                    </div>
                    <div>
                      <div className="text-[10px] opacity-75">Hallucination Risk</div>
                      <div className="text-[14px] font-bold">{answer.grounding_stats.hallucination_risk.toFixed(0)}%</div>
                    </div>
                    <div className="col-span-2">
                      <div className="text-[10px] opacity-75">Claims Supported</div>
                      <div className="text-[13px] font-semibold">{answer.grounding_stats.supported_claims}/{answer.grounding_stats.total_claims}</div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Sources */}
              <div>
                {answer?.sources && answer.sources.length > 0 && (
                  <div className="text-[11px] font-semibold text-[#829987] mb-2">EVIDENCE SOURCES</div>
                )}
                <div className="space-y-2">
                  {answer?.sources.map((source, idx) => (
                    <motion.div
                      key={source.chunk_id || idx}
                      variants={{
                        hidden: { opacity: 0, y: 10 },
                        visible: { opacity: 1, y: 0 }
                      }}
                      className="w-full border-b border-[#1A3B25] py-3.5 last:border-0"
                    >
                      <div className="text-sm leading-[1.65] text-[#A3BCA9]">
                        <span className="font-semibold text-[#D1CEC7]">pg. {source.page ?? "?"}</span> — {source.text}
                      </div>
                      {(source.title || source.paper_id) && (
                        <div className="mt-1 text-xs uppercase tracking-wider text-[#829987]">
                          {source.title ?? source.paper_id} · Score: {source.score.toFixed(3)}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
