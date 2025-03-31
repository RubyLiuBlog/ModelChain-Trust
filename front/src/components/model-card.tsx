// components/model-card.tsx
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { motion } from "framer-motion";

interface ModelCardProps {
  id: number;
  name: string;
  description: string;
  price: number | string;
  isOwned: boolean;
}

export function ModelCard({
  id,
  name,
  description,
  price,
  isOwned,
}: ModelCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <Card className="overflow-hidden bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="text-xl font-bold text-white">
              {name}
            </CardTitle>
          </div>
          <CardDescription className="text-gray-300 line-clamp-2">
            {description}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center">
            <p className="font-medium text-lg text-emerald-400">{price} ETH</p>
            {isOwned && (
              <Badge
                variant="outline"
                className="border-emerald-500 text-emerald-500"
              >
                Owned
              </Badge>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-between gap-2">
          <Button asChild variant="outline" className="w-1/2">
            <Link href={`/model/${id}`}>Details</Link>
          </Button>
          {!isOwned ? (
            <Button
              variant="default"
              className="w-1/2 bg-gradient-to-r from-violet-500 to-indigo-500"
            >
              Buy Now
            </Button>
          ) : (
            <Button
              variant="default"
              className="w-1/2 bg-gradient-to-r from-emerald-500 to-blue-500"
            >
              Download
            </Button>
          )}
        </CardFooter>
      </Card>
    </motion.div>
  );
}
