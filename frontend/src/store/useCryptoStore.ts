// src/store/useCryptoStore.ts
import { create } from "zustand";
import { CryptoData } from "@/types/crypto";

interface CryptoStore {
  availableCryptos: CryptoData[];
  dashboardCryptos: CryptoData[];
  setAvailableCryptos: (cryptos: CryptoData[]) => void;
  addToDashboard: (crypto: CryptoData) => void;
  removeFromDashboard: (cryptoId: string) => void;
}

export const useCryptoStore = create<CryptoStore>((set) => ({
  availableCryptos: [],
  dashboardCryptos: [],
  setAvailableCryptos: (cryptos) => set({ availableCryptos: cryptos }),
  addToDashboard: (crypto) =>
    set((state) => ({
      dashboardCryptos: [...state.dashboardCryptos, crypto],
      availableCryptos: state.availableCryptos.filter(
        (c) => c.id !== crypto.id
      ),
    })),
  removeFromDashboard: (cryptoId) =>
    set((state) => {
      const cryptoToRemove = state.dashboardCryptos.find(
        (c) => c.id === cryptoId
      );
      return {
        dashboardCryptos: state.dashboardCryptos.filter(
          (c) => c.id !== cryptoId
        ),
        availableCryptos: cryptoToRemove
          ? [...state.availableCryptos, cryptoToRemove] // Add back to available
          : state.availableCryptos,
      };
    }),
}));
