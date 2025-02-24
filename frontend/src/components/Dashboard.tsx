// Dashboard.tsx
"use client";

import { useEffect, useState } from "react";
import PriceChart from "./PriceChart";
import type { CryptoData } from "@/types/crypto";

const Dashboard: React.FC = () => {
  const [data, setData] = useState<CryptoData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/api/crypto");
        if (!response.ok) {
          throw new Error("Failed to fetch data");
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">Market Data</h3>
      <ul className="space-y-2">
        {data.map((item) => (
          <li
            key={item.id}
            className="border-b py-2 flex justify-between items-center hover:bg-gray-100 transition"
          >
            <span className="font-medium">{item.name}</span>
            <span>${item.current_price.toLocaleString()}</span>
            <span className="text-gray-500">
              24h: {item.price_change_percentage_24h.toFixed(2)}%
            </span>
            <span className="text-gray-500">
              Market Cap: ${item.market_cap.toLocaleString()}
            </span>
            <div className="w-48 h-24">
              <PriceChart
                data={item.sparkline_in_7d.price} // Ensure this is the correct path to your price data
                isPositive={item.price_change_percentage_24h >= 0}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
