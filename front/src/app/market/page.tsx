"use client";
import { useState, useMemo } from "react";
import { useContract } from "@/hooks/use-contract";
import { ModelCard } from "@/components/model-card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { useAccount } from "wagmi";
import { formatEther } from "ethers";

interface ModelI {
  _price: string;
  id: number;
  name: string;
  description?: string;
  price: number;
  readmeLink?: string;
  modelFolderLink?: string;
  owner?: string;
}

export default function MarketPage() {
  const { address } = useAccount();
  const { getModelListByPage } = useContract();

  const { data, isLoading, error } = getModelListByPage(1, 10); // 每页10条数据，当前页1

  // 筛选状态
  const [search, setSearch] = useState("");
  const [priceRange, setPriceRange] = useState([0, 10]);
  const [showOwned, setShowOwned] = useState(false);

  const sourceData = useMemo(() => {
    if (isLoading) return [];
    if (data === undefined) return [];
    if (data && Array.isArray(data)) {
      return data[0].filter((item: ModelI) => item.name.includes(search));
    }
    return [];
  }, [data, isLoading, search]);

  const filteredModels = useMemo(() => {
    return sourceData.map((model: ModelI) => {
      model._price = formatEther(model.price);
      return model;
    });
  }, [sourceData]);

  return (
    <div className="container mx-auto py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold mb-8">模型市场</h1>
        <div className="bg-slate-800/50 p-6 rounded-xl mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <label className="text-sm text-slate-400 mb-2 block">
                关键字搜索
              </label>
              <Input
                placeholder="搜索模型名称..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-slate-700"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-2 block">
                价格范围 ({priceRange[0]} - {priceRange[1]} ETH)
              </label>
              <Slider
                min={0}
                max={10}
                step={0.1}
                value={priceRange}
                onValueChange={setPriceRange}
                className="mt-6"
              />
            </div>
            <div className="flex items-end">
              <div className="flex items-center space-x-2">
                <Switch
                  id="owned-switch"
                  checked={showOwned}
                  onCheckedChange={setShowOwned}
                />
                <label htmlFor="owned-switch" className="cursor-pointer">
                  只显示已拥有
                </label>
              </div>
            </div>
          </div>
          <div className="mt-6 flex justify-end">
            <Button
              variant="outline"
              className="mr-2"
              onClick={() => {
                setSearch("");
                setPriceRange([0, 10]);
                setShowOwned(false);
              }}
            >
              重置筛选
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500 mr-2" />
            <p className="text-xl">加载模型列表中...</p>
          </div>
        ) : filteredModels.length === 0 ? (
          <div className="text-center py-20 bg-slate-800/30 rounded-xl">
            <p className="text-xl text-slate-400">未找到符合条件的模型</p>
            <Button
              variant="link"
              onClick={() => {
                setSearch("");
                setPriceRange([0, 10]);
                setShowOwned(false);
              }}
            >
              清除筛选条件
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredModels.map((model: ModelI) => (
              <ModelCard
                key={model.id}
                id={model.id}
                name={model.name}
                description={model.description || "暂无描述"}
                price={model._price}
                isOwned={model.owner === address}
              />
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
