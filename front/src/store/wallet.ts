import { create } from "zustand";
import type { Account } from "@ant-design/web3";
import { createJSONStorage, persist } from "zustand/middleware";

type AccountState = {
  account: Account | undefined;
  loginAccount: (account: Account) => void;
  logout: () => void;
};

export const useAccountStore = create<AccountState>()(
  persist(
    (set) => ({
      account: {} as Account,
      loginAccount: (account) => set({ account }),
      logout: () => set({ account: undefined }),
    }),
    {
      name: "theme-storage",
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
