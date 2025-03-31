1. 项目目录结构

```
src/
├── app/                      # Next.js App Router
│   ├── page.tsx              # 首页
│   ├── layout.tsx            # 根布局
│   ├── market/               # 模型市场
│   │   └── page.tsx
│   ├── model/                # 模型详情
│   │   └── [modelId]/
│   │       └── page.tsx
│   ├── register/             # 模型注册
│   │   └── page.tsx
│   ├── test/                 # 性能测试
│   │   └── page.tsx
│   ├── my-models/            # 我的模型
│   │   └── page.tsx
│   └── providers.tsx         # 全局提供者
├── components/               # 组件库
│   ├── ui/                   # UI 基础组件 (shadcn)
│   ├── model-card.tsx        # 模型卡片
│   ├── wallet-connect.tsx    # 钱包连接组件
│   ├── markdown-render.tsx   # Markdown渲染组件
│   └── ...
├── hooks/                    # 自定义钩子
│   ├── use-wallet.ts         # 钱包连接钩子
│   ├── use-models.ts         # 模型数据获取钩子
│   └── use-store.ts          # 全局状态管理
├── lib/                      # 工具函数库
│   ├── contract.ts           # 合约交互
│   ├── web3storage.ts        # IPFS存储工具
│   └── animations.ts         # 动画效果工具
└── store/                    # 状态管理
    ├── wallet.ts             # 钱包状态
    └── tasks.ts              # 任务队列状态
```

2. 核心依赖安装

# 基础框架

`pnpm add next@15 react react-dom typescript tailwindcss`

# UI 库

```bash
pnpm dlx shadcn@latest init
pnpm add  @tailwindcss/typography framer-motion
# shadcn ui
pnpm dlx shadcn@latest add button table card badge input select slider switch tabs use-toast alert progress textarea sonner
```

# Web3 相关

```bash
pnpm add antd @ant-design/web3 @ant-design/web3-wagmi wagmi viem @tanstack/react-query   --save
pnpm add @web3-storage/w3up-client ethers --save
```

# 工具库

```bash
pnpm add react-markdown remark-gfm @mdx-editor/react @tanstack/react-query jotai
```

3. 环境变量

```env
NEXT_PUBLIC_W3_DID_KEY=
NEXT_PUBLIC_W3_EMAIL=
```
