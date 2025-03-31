// app/providers.tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ThemeProvider from "@/components/theme-provider";
import { useState } from "react";
import {
  WagmiWeb3ConfigProvider,
  MetaMask,
  CoinbaseWallet,
  WalletConnect as WC,
  TokenPocket,
  SafeheronWallet,
  OkxWallet,
  MobileWallet,
} from "@ant-design/web3-wagmi";
import { http } from "viem";
import { mainnet, optimism, sepolia, localhost } from "viem/chains";
import { createConfig, injected } from "wagmi";

export function Providers({ children }: { children: React.ReactNode }) {
  const config = createConfig({
    chains: [mainnet, optimism, sepolia, localhost],
    transports: {
      [mainnet.id]: http(),
      [optimism.id]: http(),
      [sepolia.id]: http(),
      [localhost.id]: http(),
    },
    connectors: [
      // injected({
      //   target: "metaMask",
      // }),
    ],
  });

  // 创建 React Query 客户端
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnWindowFocus: false,
            retry: 1,
            staleTime: 30 * 1000,
          },
        },
      })
  );

  return (
    <WagmiWeb3ConfigProvider
      chains={[mainnet, optimism, sepolia, localhost]}
      config={config}
      eip6963={{
        autoAddInjectedWallets: true,
      }}
      wallets={[
        MetaMask(),
        WC(),
        CoinbaseWallet(),
        TokenPocket(),
        SafeheronWallet(),
        OkxWallet(),
        MobileWallet(),
      ]}
    >
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>{children}</ThemeProvider>
      </QueryClientProvider>
    </WagmiWeb3ConfigProvider>
  );
}
