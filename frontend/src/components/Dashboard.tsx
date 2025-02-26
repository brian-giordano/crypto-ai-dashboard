// components/Dashboard.tsx
"use client";

import { useCryptoStore } from "@/store/useCryptoStore";
import { Button } from "./ui/button";
import { Minus } from "lucide-react";

const Dashboard: React.FC = () => {
  const { dashboardCryptos } = useCryptoStore(); // Access the dashboardCryptos from the store
  const { removeFromDashboard } = useCryptoStore(); // Access the addToDashboard method

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">My Dashboard</h2>
      {dashboardCryptos.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">
            Your dashboard is empty. Add cryptocurrencies from the market data
            panel.
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {dashboardCryptos.map((item) => (
            <li
              key={item.id}
              className="border-b py-2 flex justify-between items-center"
            >
              <span>{item.name}</span>
              <span>${item.current_price.toLocaleString()}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  removeFromDashboard(item.id);
                  // console.log(`Add ${crypto.name} to dashboard`);
                }}
              >
                <Minus className="h-[1.2rem] w-[1.2rem]" />
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Dashboard;
