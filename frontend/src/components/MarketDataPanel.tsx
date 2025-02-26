// components/TopMarketData.tsx
"use client";

import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Plus } from "lucide-react";
import PriceChart from "./PriceChart";
import { useCryptoStore } from "@/store/useCryptoStore";

const MarketDataPanel: React.FC = () => {
  const { availableCryptos, addToDashboard, setAvailableCryptos } =
    useCryptoStore(); // Access the addToDashboard method
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // If data is already available, skip fetching to avoid rate limit.
      if (availableCryptos.length > 0) {
        setLoading(false);
        return;
      }

      try {
        const response = await fetch("/api/crypto");
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const result = await response.json();
        setAvailableCryptos(result); // for maintaining list of available cryptos
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [availableCryptos, setAvailableCryptos]);

  if (loading) return <div>Loading market data...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  const sortedAvailableCryptos = availableCryptos.sort(
    (a, b) => b.market_cap - a.market_cap
  ); // sort by MC before render.

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Top Crypto Market Data</h2>
      <div className="space-y-4">
        {sortedAvailableCryptos.slice(0, 15).map((crypto) => (
          <div
            key={crypto.id}
            className="p-3 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="flex justify-between items-center">
              <span className="font-medium">{crypto.name}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  addToDashboard(crypto);
                  // console.log(`Add ${crypto.name} to dashboard`);
                }}
              >
                <Plus className="h-[1.2rem] w-[1.2rem]" />
              </Button>
            </div>
            <div className="mt-2 text-sm text-gray-600 flex justify-between items-start">
              <div>
                <div>${crypto.current_price.toLocaleString()}</div>
                <div
                  className={
                    crypto.price_change_percentage_24h >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }
                >
                  24h: {crypto.price_change_percentage_24h.toFixed(2)}%
                </div>
              </div>
              <div className="w-36 h-12">
                <PriceChart
                  data={crypto.sparkline_in_7d.price}
                  isPositive={crypto.price_change_percentage_24h >= 0}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketDataPanel;
