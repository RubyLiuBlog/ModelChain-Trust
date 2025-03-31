"use client";

import React from "react";
import { createConfig, http } from "wagmi";
import { mainnet, optimism, sepolia, localhost } from "wagmi/chains";
import { ConnectButton, Connector } from "@ant-design/web3";
import { injected } from "wagmi/connectors";
import { motion } from "framer-motion";
import { useAccountStore } from "@/store/wallet";
import type { Account } from "@ant-design/web3";

export function WalletConnect() {
  const config = createConfig({
    chains: [mainnet, optimism, sepolia, localhost],
    transports: {
      [mainnet.id]: http(),
      [optimism.id]: http(),
      [sepolia.id]: http(),
      [localhost.id]: http(),
    },
    connectors: [
      injected({
        target: "metaMask",
      }),
    ],
  });

  const { account, loginAccount, logout } = useAccountStore();

  return (
    <motion.div whileHover={{ scale: 1.05 }} className="flex items-center">
      <Connector
        account={account}
        onConnected={(account?: Account) => {
          if (account) {
            console.log("onConnected", account);
            loginAccount(account);
          }
        }}
        onDisconnected={() => {
          logout();
          console.log("onDisconnected");
        }}
        modalProps={{
          title: "ModelChain",
        }}
      >
        <ConnectButton chainSelect={false} />
      </Connector>
    </motion.div>
  );
}
