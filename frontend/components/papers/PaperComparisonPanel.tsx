"use client";

import { PaperComparisonResponse } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, AlertCircle, TrendingUp, Copy, Download } from "lucide-react";

interface PaperComparisonPanelProps {
  comparison: PaperComparisonResponse | null;
  isLoading: boolean;
}

export function PaperComparisonPanel({ comparison, isLoading }: PaperComparisonPanelProps) {
  const getRelationshipColor = (type: string) => {
    switch (type) {
      case "building_on":
        return "bg-blue-500/10 text-blue-700";
      case "alternative":
        return "bg-purple-500/10 text-purple-700";
      case "complementary":
        return "bg-green-500/10 text-green-700";
      default:
        return "bg-gray-500/10 text-gray-700";
    }
  };

  const getRelationshipLabel = (type: string) => {
    return type.replace("_", " ").split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity > 0.75) return "#10b981";  // Green
    if (similarity > 0.6) return "#f59e0b";   // Amber
    return "#ef4444";  // Red
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-[22px] border border-[#1A3B25] bg-[#0B1E12] transition-colors hover:border-[#29A662]">
      <div className="border-b border-[#1A3B25] bg-[#13311E] px-[22px] py-5">
        <h2 className="text-[13px] font-bold text-[#FFFFFF]">Paper Comparison</h2>
      </div>

      <div className="min-h-[400px] flex-1 bg-[#0B1E12] px-[22px] py-7 overflow-y-auto">
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
                <p className="text-[13px] text-[#829987]">Analyzing papers...</p>
              </div>
            </motion.div>
          ) : !comparison ? (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-[13.5px] text-[#A3BCA9]"
            >
              Select two papers to compare their methodology, results, and approach.
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
              {/* Header */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="text-[11px] text-[#829987] font-semibold">COMPARING</p>
                    <p className="text-[12px] font-semibold text-[#D1CEC7] mt-1">{comparison.paper1_title}</p>
                    <p className="text-[11px] text-[#829987]">vs</p>
                    <p className="text-[12px] font-semibold text-[#D1CEC7]">{comparison.paper2_title}</p>
                  </div>
                </div>
              </motion.div>

              {/* Overall Similarity */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
              >
                <div className="text-[11px] font-semibold text-[#829987] mb-3">OVERALL SIMILARITY</div>
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="text-[20px] font-bold text-[#D1CEC7]">
                        {(comparison.overall_similarity * 100).toFixed(0)}%
                      </span>
                      <span className="text-[12px] text-[#829987]">
                        Confidence: {(comparison.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-[#0B1E12] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${comparison.overall_similarity * 100}%`,
                          backgroundColor: getSimilarityColor(comparison.overall_similarity),
                        }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>

              {/* Relationship */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className={`rounded-lg border border-[#1A3B25] p-4 ${getRelationshipColor(comparison.relationship_type)}`}
              >
                <div className="text-[11px] font-semibold mb-2">RELATIONSHIP</div>
                <p className="text-[13px] font-bold">{getRelationshipLabel(comparison.relationship_type)}</p>
              </motion.div>

              {/* Shared Concepts */}
              {comparison.shared_concepts.length > 0 && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle size={14} className="text-[#10b981]" />
                    <span className="text-[11px] font-semibold text-[#829987]">SHARED CONCEPTS</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {comparison.shared_concepts.map((concept, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 rounded-full bg-[#0B1E12] border border-[#1A3B25] text-[11px] text-[#A3BCA9]"
                      >
                        {concept}
                      </span>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Distinctive Concepts */}
              <motion.div
                variants={{
                  hidden: { opacity: 0, y: 10 },
                  visible: { opacity: 1, y: 0 }
                }}
                className="grid grid-cols-2 gap-3"
              >
                {comparison.distinctive_concepts_p1.length > 0 && (
                  <div className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3">
                    <p className="text-[10px] text-[#829987] font-semibold mb-2">PAPER 1 FOCUSES</p>
                    <div className="space-y-1">
                      {comparison.distinctive_concepts_p1.slice(0, 3).map((concept, i) => (
                        <p key={i} className="text-[11px] text-[#A3BCA9]">• {concept}</p>
                      ))}
                    </div>
                  </div>
                )}
                {comparison.distinctive_concepts_p2.length > 0 && (
                  <div className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-3">
                    <p className="text-[10px] text-[#829987] font-semibold mb-2">PAPER 2 FOCUSES</p>
                    <div className="space-y-1">
                      {comparison.distinctive_concepts_p2.slice(0, 3).map((concept, i) => (
                        <p key={i} className="text-[11px] text-[#A3BCA9]">• {concept}</p>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>

              {/* Section Comparisons */}
              {Object.keys(comparison.section_comparisons).length > 0 && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
                >
                  <div className="text-[11px] font-semibold text-[#829987] mb-3">SECTION ANALYSIS</div>
                  <div className="space-y-2">
                    {Object.entries(comparison.section_comparisons).map(([_, comp]) => (
                      <div key={comp.section_name} className="flex items-center justify-between text-[12px]">
                        <span className="text-[#A3BCA9] capitalize">{comp.section_name}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-[#0B1E12] rounded-full overflow-hidden">
                            <div
                              className="h-full"
                              style={{
                                width: `${comp.similarity_score * 100}%`,
                                backgroundColor: getSimilarityColor(comp.similarity_score),
                              }}
                            />
                          </div>
                          <span className="text-[#829987] w-10 text-right">{(comp.similarity_score * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Recommendations */}
              {comparison.recommendations.length > 0 && (
                <motion.div
                  variants={{
                    hidden: { opacity: 0, y: 10 },
                    visible: { opacity: 1, y: 0 }
                  }}
                  className="rounded-lg border border-[#1A3B25] bg-[#13311E] p-4"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp size={14} className="text-[#f59e0b]" />
                    <span className="text-[11px] font-semibold text-[#829987]">RECOMMENDATIONS</span>
                  </div>
                  <div className="space-y-2">
                    {comparison.recommendations.map((rec, i) => (
                      <p key={i} className="text-[12px] text-[#A3BCA9]">
                        {i + 1}. {rec}
                      </p>
                    ))}
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
