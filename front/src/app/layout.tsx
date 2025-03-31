// app/layout.tsx
import { Inter } from "next/font/google";
import { Metadata } from "next";
import { WalletConnect } from "@/components/wallet-connect";
import { Toaster } from "@/components/ui/sonner";
import { Providers } from "./providers";
import Link from "next/link";
import { cn } from "@/lib/utils";
import "./globals.css";
import { AntdRegistry } from "@ant-design/nextjs-registry";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "区块链模型交易与评测平台",
  description:
    "一个基于区块链技术的AI模型交易市场，支持模型注册、购买和性能测试",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const navItems = [
    { label: "首页", href: "/" },
    { label: "模型市场", href: "/market" },
    { label: "注册模型", href: "/register" },
    { label: "性能测试", href: "/performance" },
  ];

  return (
    <html lang="zh-CN" className="dark">
      <body
        className={cn(
          inter.className,
          "min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100 dark"
        )}
      >
        <AntdRegistry>
          <Providers>
            <div className="flex min-h-screen flex-col">
              <header className="sticky top-0 z-50 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm">
                <div className="container mx-auto flex h-16 items-center justify-between px-4">
                  <div className="flex items-center gap-6">
                    <Link href="/" className="flex items-center space-x-2">
                      <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-violet-600"></div>
                      <span className="font-bold text-xl">ModelChain</span>
                    </Link>
                    <nav className="hidden md:flex items-center gap-6">
                      {navItems.map((item, index) => (
                        <Link
                          key={index}
                          href={item.href}
                          className="text-sm font-medium text-slate-300 transition-colors hover:text-white"
                        >
                          {item.label}
                        </Link>
                      ))}
                    </nav>
                  </div>
                  <div className="flex items-center gap-4">
                    <WalletConnect />
                  </div>
                </div>
              </header>

              <main className="flex-1">{children}</main>

              <footer className="border-t border-slate-800 bg-slate-950">
                <div className="container mx-auto py-8 px-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div>
                      <h3 className="text-lg font-medium mb-4">关于我们</h3>
                      <p className="text-slate-400">
                        区块链模型交易与评测平台是一个基于区块链技术的去中心化AI模型交易市场，
                        为模型创建者和使用者搭建一个安全、透明的交易环境。
                      </p>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-4">快速链接</h3>
                      <ul className="space-y-2">
                        {navItems.map((item, index) => (
                          <li key={index}>
                            <Link
                              href={item.href}
                              className="text-slate-400 hover:text-white transition-colors"
                            >
                              {item.label}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium mb-4">联系我们</h3>
                      <p className="text-slate-400">
                        如有任何问题或建议，请通过以下方式与我们联系
                      </p>
                      <p className="text-slate-400 mt-2">
                        邮箱: support@modelchain.example
                      </p>
                    </div>
                  </div>
                  <div className="mt-8 pt-4 border-t border-slate-800 text-center">
                    <p className="text-sm text-slate-500">
                      © {new Date().getFullYear()} ModelChain. 保留所有权利
                    </p>
                  </div>
                </div>
              </footer>
            </div>
            <Toaster />
          </Providers>
        </AntdRegistry>
      </body>
    </html>
  );
}
