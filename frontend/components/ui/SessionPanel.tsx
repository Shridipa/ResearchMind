"use client";

import { SessionInsights } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, GitBranch, BookOpen, TrendingUp, MessageSquare } from "lucide-react";

interface SessionPanelProps {
  sessionId: string | null;
  insights: SessionInsights | null;
  followUpSuggestions: string[];
  isLoading: boolean;
}

export function SessionPanel({
  sessionId,
  insights,
  followUpSuggestions,
  isLoading,
}: SessionPanelProps) {
  return (
    <div className="flex flex-col overflow-hidden rounded-[22px] border border-[#1A3B25] bg-[#0B1E12] transition-colors hover:border-[#29A662]">
      <div className="border-b border-[#1A3B25] bg-[#13311E] px-[22px] py-5">
        <h2 className="text-[13px] font-bold text-[#FFFFFF]">Research Session Memory</h2>
      </div>

      <div className="min-h-[500px] flex-1 bg-[#0B1E12] px-[22px] py-7 overflow-y-auto">
        <AnimatePresence mode="wait">
          {isLoading ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center h-full"
            >
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-[#29A662] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-[13px] text-[#829987]">Building session graph...</p>
              </div>
            </motion.div>
          ) : !insights ? (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-[13.5px] text-[#A3BCA9]"
            >
              Session memory tracks your research across multiple questions, building a knowledge graph of concepts and relationships.
            </motion.p>
          ) : (
            <motion.div
              initial="hidden"
              animate="visible"
              variants={{
                hidden: {},
                visible: {
                  transition: { staggerChildren: 0.05 }
                }
              }}
              className="space-y-6"
            >
              {/* Session Header */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen size={14} className="text-[#29A662]" />
                  <span className="text-[11px] text-[#829987] font-semibold">SESSION ID</span>
                </div>
                <p className="text-[12px] font-mono text-[#D1CEC7] break-all">{sessionId}</p>
              </motion.div>

              {/* Key Metrics */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className="grid grid-cols-2 gap-3"
              >
                <div className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3">
                  <div className="text-[10px] text-[#829987] font-semibold mb-1">TURNS</div>
                  <div className="text-[18px] font-bold text-[#D1CEC7]">{insights.total_turns}</div>
                </div>
                <div className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3">
                  <div className="text-[10px] text-[#829987] font-semibold mb-1">PAPERS</div>
                  <div className="text-[18px] font-bold text-[#D1CEC7]">{insights.papers_explored}</div>
                </div>
                <div className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3">
                  <div className="text-[10px] text-[#829987] font-semibold mb-1">CONCEPTS</div>
                  <div className="text-[18px] font-bold text-[#D1CEC7]">{insights.unique_concepts}</div>
                </div>
                <div className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3">
                  <div className="text-[10px] text-[#829987] font-semibold mb-1">GROUNDING</div>
                  <div className="text-[18px] font-bold text-[#29A662]">{(insights.average_grounding * 100).toFixed(0)}%</div>
                </div>
              </motion.div>

              {/* Topic Clusters */}
              {insights.topic_clusters > 0 && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <GitBranch size={14} className="text-[#f59e0b]" />
                    <span className="text-[11px] font-semibold text-[#829987]">TOPIC CLUSTERS</span>
                  </div>
                  <p className="text-[13px] text-[#D1CEC7] font-semibold">{insights.topic_clusters} clusters</p>
                  <p className="text-[11px] text-[#829987] mt-1">Research organized into {insights.topic_clusters} related topic groups</p>
                </motion.div>
              )}

              {/* Divergence Points */}
              {insights.divergence_points > 0 && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={14} className="text-[#10b981]" />
                    <span className="text-[11px] font-semibold text-[#829987]">TOPIC SHIFTS</span>
                  </div>
                  <p className="text-[13px] text-[#D1CEC7] font-semibold">{insights.divergence_points} divergences</p>
                  <p className="text-[11px] text-[#829987] mt-1">Discussion branched into new areas {insights.divergence_points} times</p>
                </motion.div>
              )}

              {/* Summary Preview */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
              >
                <div className="text-[11px] font-semibold text-[#829987] mb-2">SUMMARY</div>
                <p className="text-[12px] text-[#A3BCA9] leading-relaxed line-clamp-4">
                  {insights.session_summary}
                </p>
              </motion.div>

              {/* Follow-up Suggestions */}
              {followUpSuggestions.length > 0 && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <MessageSquare size={14} className="text-[#8b5cf6]" />
                    <span className="text-[11px] font-semibold text-[#829987]">SUGGESTED FOLLOW-UPS</span>
                  </div>
                  <div className="space-y-2">
                    {followUpSuggestions.slice(0, 3).map((suggestion, i) => (
                      <div
                        key={i}
                        className="p-2 rounded bg-[#0B1E12] border border-[#1A3B25] cursor-pointer hover:border-[#29A662] transition-colors"
                      >
                        <p className="text-[11px] text-[#A3BCA9]">{suggestion}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Memory Stats */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
              >
                <div className="flex items-center gap-2 mb-3">
                  <Zap size={14} className="text-[#fbbf24]" />
                  <span className="text-[11px] font-semibold text-[#829987]">REASONING POWER</span>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-[11px]">
                    <span className="text-[#829987]">Context Depth</span>
                    <span className="text-[#D1CEC7]">5 turns</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-[#829987]">Graph Size</span>
                    <span className="text-[#D1CEC7]">{insights.unique_concepts} nodes</span>
                  </div>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-[#829987]">Grounding</span>
                    <span className="text-[#10b981]">Active</span>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
