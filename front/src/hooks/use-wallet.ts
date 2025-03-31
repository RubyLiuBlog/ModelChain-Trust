// hooks/use-wallet.ts
import { useState, useEffect } from 'react';
import { useAccount, useDisconnect, useConnect } from 'wagmi';
import { InjectedConnector } from 'wagmi/connectors/injected';
import { WalletConnectConnector } from 'wagmi/connectors/walletConnect';
import { useAtom } from 'jotai';
import { walletAtom } from '@/store/wallet';

export function useWallet() {
  const { address, isConnected } = useAccount();
  const { disconnect } = useDisconnect();
  const { connect } = useConnect();
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [walletState, setWalletState] = useAtom(walletAtom);

  // 支持的连接器
  const connectors = {
    injected: new InjectedConnector(),
    walletConnect: new WalletConnectConnector({
      projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID || 'your-project-id',
    })
  };

  // 当地址或连接状态改变时更新全局状态
  useEffect(() => {
    if (address && isConnected) {
      setWalletState({
        address,
        isConnected: true
      });
    } else if (!isConnected) {
      setWalletState({
        address: '',
        isConnected: false
      });
    }
  }, [address, isConnected, setWalletState]);

  // 连接钱包
  const connectWallet = async (connectorType: 'injected' | 'walletConnect' = 'injected') => {
    try {
      setConnecting(true);
      setError(null);

      const connector = connectors[connectorType];
      await connect({ connector });
      
    } catch (err) {
      console.error("Failed to connect wallet:", err);
      setError(err instanceof Error ? err : new Error('Failed to connect wallet'));
    } finally {
      setConnecting(false);
    }
  };

  // 断开钱包连接
  const disconnectWallet = async () => {
    try {
      await disconnect();
      setWalletState({
        address: '',
        isConnected: false
      });
    } catch (err) {
      console.error("Failed to disconnect wallet:", err);
    }
  };

  // 获取缩略地址显示
  const getDisplayAddress = (addr?: string) => {
    const displayAddress = addr || address;
    if (!displayAddress) return '';
    return `${displayAddress.slice(0, 6)}...${displayAddress.slice(-4)}`;
  };

  return {
    address: walletState.address,
    isConnected: walletState.isConnected,
    connecting,
    error,
    connectWallet,
    disconnectWallet,
    getDisplayAddress
  };
}