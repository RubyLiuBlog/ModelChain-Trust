"use client";
import { motion } from "framer-motion";

export default function ModelDetailPage() {
  return (
    <div className="container mx-auto py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        模型详情
      </motion.div>
    </div>
  );
}
