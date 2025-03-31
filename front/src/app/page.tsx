"use client";
// app/page.tsx

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { motion } from "framer-motion";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900">
      <div className="container mx-auto py-20 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <h1 className="text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-violet-500 to-purple-500 mb-6">
            区块链模型交易与评测平台
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-10">
            基于区块链技术的去中心化AI模型交易市场，集成模型存储、智能合约交互、性能测试等功能。
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            {[
              {
                title: "模型市场",
                desc: "探索和购买高质量AI模型",
                link: "/market",
                icon: "🛒",
              },
              {
                title: "性能测试",
                desc: "测试您的模型性能表现",
                link: "/performance",
                icon: "🧪",
              },
              {
                title: "模型管理",
                desc: "管理您拥有的AI模型",
                link: "/my-models",
                icon: "📁",
              },
            ].map((item, i) => (
              <motion.div
                key={i}
                whileHover={{ scale: 1.05 }}
                className="bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl border border-slate-700 shadow-lg"
              >
                <div className="text-4xl mb-4">{item.icon}</div>
                <h2 className="text-2xl font-bold mb-3 text-white">
                  {item.title}
                </h2>
                <p className="text-slate-300 mb-6">{item.desc}</p>
                <Button
                  asChild
                  className="bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700"
                >
                  <Link href={item.link}>立即体验</Link>
                </Button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
