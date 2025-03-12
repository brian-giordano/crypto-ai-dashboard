// components/TopMarketData.tsx
"use client";

import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { Plus, RefreshCw } from "lucide-react";
import PriceChart from "./PriceChart";
import { useCryptoStore } from "@/store/useCryptoStore";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
console.log("API_URL: ", API_URL);

const MarketDataPanel: React.FC = () => {
  const { availableCryptos, addToDashboard, setAvailableCryptos } =
    useCryptoStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // If data is already available, skip fetching to avoid rate limit.
      if (availableCryptos.length > 0) {
        setLoading(false);
        return;
      }

      console.log("Fetching from: ", `${API_URL}/api/crypto`);

      try {
        const response = await fetch(`${API_URL}/api/crypto`);
        console.log("Response status: ", response.status);

        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }

        const data = await response.json(); // Only call .json() once
        console.log("API Response: ", data);

        setAvailableCryptos(data); // Set the data directly
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

  // sort by MC before render.
  const sortedAvailableCryptos = availableCryptos.sort(
    (a, b) => b.market_cap - a.market_cap
  );

  // Empty state check
  if (sortedAvailableCryptos.length === 0) {
    return (
      <div className="p-8 text-center border rounded-lg dark:border-gray-700">
        <div className="text-gray-500 dark:text-gray-400 mb-4">
          No cryptocurrency data available
        </div>
        <Button
          variant="outline"
          onClick={() => window.location.reload()}
          className="text-sm gap-2"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh Data
        </Button>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Top Crypto Market Data</h2>
      <div className="space-y-4">
        {sortedAvailableCryptos.slice(0, 15).map((crypto) => (
          <div
            key={crypto.id}
            className="p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors dark:bg-gray-800"
          >
            <div className="flex justify-between items-center">
              <span className="font-medium">{crypto.name}</span>
              <Button
                variant="default"
                className="group size-8 dark:bg-gray-500 hover:dark:bg-green-600 hover:scale-105"
                size="sm"
                onClick={() => {
                  addToDashboard(crypto);
                }}
              >
                <Plus className="dark:text-gray-200 group-hover:text-gray-200 group-hover:scale-125 transition-all" />
              </Button>
            </div>
            <div className="mt-2 text-sm text-gray-600 flex justify-between items-start dark:text-gray-300">
              <div>
                <div>${crypto.current_price.toLocaleString()}</div>
                <div
                  className={
                    crypto.price_change_percentage_24h >= 0
                      ? "text-green-600"
                      : "text-red-500"
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
