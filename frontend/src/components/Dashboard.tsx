// components/Dashboard.tsx
"use client";

import { useState } from "react";
import type { CryptoData } from "@/types/crypto";

const Dashboard: React.FC = () => {
  const [selectedCryptos] = useState<CryptoData[]>([]);

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">My Dashboard</h3>
      {selectedCryptos.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">
            Your dashboard is empty. Add cryptocurrencies from the market data
            panel.
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {selectedCryptos.map((item) => (
            <li
              key={item.id}
              className="border-b py-2 flex justify-between items-center"
            >
              {/* We'll add the crypto display logic later */}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Dashboard;
