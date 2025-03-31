"use client";
// app/performance/page.tsx
import { useAtom } from "jotai";
import { motion } from "framer-motion";

const TEST_CATEGORIES = [
  { value: "language", label: "语言理解" },
  { value: "coding", label: "代码生成" },
  { value: "reasoning", label: "逻辑推理" },
  { value: "knowledge", label: "知识问答" },
  { value: "math", label: "数学能力" },
  { value: "comprehensive", label: "综合评测" },
];

const TEST_STATUS = {
  QUEUED: "wait",
  RUNNING: "running",
  COMPLETED: "completed",
  FAILED: "failed",
};

export default function TestPage() {
  return (
    <div className="container mx-auto py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold mb-8">模型性能测试</h1>
      </motion.div>
    </div>
  );
}
