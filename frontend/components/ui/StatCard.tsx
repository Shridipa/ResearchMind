import { ReactNode } from "react";
import { motion } from "framer-motion";

interface StatCardProps {
  label: string;
  value: string;
  subValue: string;
  children?: ReactNode;
  delay?: number;
}

export function StatCard({ label, value, subValue, children, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="flex flex-col justify-between rounded-xl border border-[#1A3B25] bg-[#0B1E12] p-7 transition-colors hover:border-[#29A662]"
    >
      <div>
        <div className="mb-4 text-xs font-bold uppercase tracking-[0.18em] text-[#829987]">
          {label}
        </div>
        <div className="mb-1.5 font-serif text-[28px] text-[#FFFFFF]">
          {value}
        </div>
        <div className="text-sm leading-[1.6] text-[#A3BCA9]">
          {subValue}
        </div>
      </div>
      {children && <div className="mt-6">{children}</div>}
    </motion.div>
  );
}
