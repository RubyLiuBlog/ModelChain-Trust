// components/test-task-card.tsx
import { useState } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Loader2, CheckCircle, AlertTriangle, Download, ArrowUpToLine } from 'lucide-react';
import { motion } from 'framer-motion';

// 测试任务状态常量
const TEST_STATUS = {
  QUEUED: 'queued',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

interface TestTaskProps {
  task: {
    id: string;
    modelId: string;
    modelName: string;
    category: string;
    status: string;
    progress: number;
    submittedAt: number;
    result?: {
      totalScore: number;
      languageScore: number;
      instructScore: number;
      codeScore: number;
      mathScore: number;
      reasoningScore: number;
      knowledgeScore: number;
    };
    reportSubmitted?: boolean;
  };
  onSubmitReport: (task: any) => Promise<void>;
}

export function TestTaskCard({ task, onSubmitReport }: TestTaskProps) {
  const [submitting, setSubmitting] = useState(false);
  
  const getStatusBadge = (status) => {
    switch (status) {
      case TEST_STATUS.QUEUED:
        return <Badge variant="outline" className="border-amber-500 text-amber-400">队列中</Badge>;
      case TEST_STATUS.RUNNING:
        return <Badge variant="outline" className="border-blue-500 text-blue-400">运行中</Badge>;
      case TEST_STATUS.COMPLETED:
        return <Badge variant="outline" className="border-emerald-500 text-emerald-400">已完成</Badge>;
      case TEST_STATUS.FAILED:
        return <Badge variant="destructive">测试失败</Badge>;
      default:
        return <Badge>未知状态</Badge>;
    }
  };
  
  const handleSubmit = async () => {
    setSubmitting(true);
    await onSubmitReport(task);
    setSubmitting(false);
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="bg-slate-900/60 border-slate-700">
        <CardHeader className="pb-2">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-medium text-lg">{task.modelName}</h3>
              <p className="text-sm text-slate-400">
                {new Date(task.submittedAt).toLocaleString()}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{task.category}</Badge>
              {getStatusBadge(task.status)}
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {task.status === TEST_STATUS.RUNNING && (
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-slate-400">测试进度</span>
                <span className="text-sm font-medium">{Math.round(task.progress)}%</span>
              </div>
              <Progress value={task.progress} className="h-2" />
            </div>
          )}
          
          {task.status === TEST_STATUS.QUEUED && (
            <div className="flex items-center gap-2 text-amber-400 py-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <p className="text-sm">等待测试节点处理...</p>
            </div>
          )}
          
          {task.status === TEST_STATUS.FAILED && (
            <div className="flex items-center gap-2 text-red-400 py-2">
              <AlertTriangle className="h-4 w-4" />
              <p className="text-sm">测试执行失败，请稍后重试</p>
            </div>
          )}
          
          {task.status === TEST_STATUS.COMPLETED && task.result && (
            <div className="space-y-4 pt-2">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <div className="bg-slate-800/50 p-3 rounded">
                  <p className="text-xs text-slate-400 mb-1">总分</p>
                  <p className={`text-xl font-bold ${task.result.totalScore >= 80 ? 'text-emerald-500' : 
                    task.result.totalScore >= 60 ? 'text-amber-500' : 'text-rose-500'}`}>
                    {task.result.totalScore}
                  </p>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <p className="text-xs text-slate-400 mb-1">语言</p>
                  <p className="text-lg">{task.result.languageScore}</p>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <p className="text-xs text-slate-400 mb-1">代码</p>
                  <p className="text-lg">{task.result.codeScore}</p>
                </div>
                <div className="bg-slate-800/50 p-3 rounded">
                  <p className="text-xs text-slate-400 mb-1">推理</p>
                  <p className="text-lg">{task.result.reasoningScore}</p>
                </div>
              </div>
              
              <div className="text-xs text-slate-400">
                {task.reportSubmitted ? (
                  <div className="flex items-center text-emerald-400">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    <span>报告已上链</span>
                  </div>
                ) : (
                  <div className="flex items-center">
                    <span>测试报告尚未同步至区块链</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
        
        {task.status === TEST_STATUS.COMPLETED && !task.reportSubmitted && (
          <CardFooter className="pt-0">
            <div className="flex gap-2 w-full">
              <Button 
                variant="outline" 
                className="flex-1" 
                size="sm"
                onClick={() => {
                  // 导出报告逻辑
                  const reportData = JSON.stringify(task.result, null, 2);
                  const blob = new Blob([reportData], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `report-${task.modelName}-${task.id}.json`;
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }}
              >
                <Download className="mr-1 h-4 w-4" /> 导出报告
              </Button>
              
              <Button 
                className="flex-1 bg-gradient-to-r from-blue-600 to-violet-600" 
                size="sm"
                onClick={handleSubmit}
                disabled={submitting}
              >
                {submitting ? (
                  <>
                    <Loader2 className="mr-1 h-4 w-4 animate-spin" /> 处理中
                  </>
                ) : (
                  <>
                    <ArrowUpToLine className="mr-1 h-4 w-4" /> 上链存证
                  </>
                )}
              </Button>
            </div>
          </CardFooter>
        )}
      </Card>
    </motion.div>
  );
}

export default TestTaskCard;