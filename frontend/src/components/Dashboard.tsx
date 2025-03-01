// components/Dashboard.tsx
"use client";

import { useCryptoStore } from "@/store/useCryptoStore";
import { Button } from "./ui/button";
import { Minus } from "lucide-react";
import DashboardCard from "./DashboardCard";
import AiQuestionCard from "./AiQuestionCard";

const Dashboard: React.FC = () => {
  const { dashboardCryptos, removeFromDashboard } = useCryptoStore();

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">My Dashboard</h2>

      {/* Always render the grid container */}
      <div className="grid grid-cols-1 gap-6 bg-gray-300 rounded-lg p-6 mb-4 md:grid-cols-2 lg:grid-cols-3 dark:bg-gray-800">
        {/* Dedicated slot for AiQuestionCard */}
        <div className="col-span-1 md:col-span-2 lg:col-span-3">
          <AiQuestionCard />
        </div>

        {/* Conditional message when no crypto cards */}
        {dashboardCryptos.length === 0 && (
          <div className="col-span-1 md:col-span-2 lg:col-span-3 text-center p-6 bg-gray-200 dark:bg-gray-700 rounded-lg">
            <p className="text-gray-700 dark:text-gray-300">
              Your dashboard is empty. Add cryptocurrencies from the market data
              panel.
            </p>
          </div>
        )}

        {/* Render crypto cards */}
        {dashboardCryptos.map((item) => (
          <div key={item.id} className="group/card">
            <DashboardCard
              title={item.name}
              value={`$${item.current_price.toLocaleString()}`}
              changePercentage={item.price_change_percentage_24h}
              chartData={item.sparkline_in_7d.price}
              marketCap={
                item.market_cap
                  ? `$${item.market_cap.toLocaleString()}`
                  : undefined
              }
              volume={
                item.total_volume
                  ? `$${item.total_volume.toLocaleString()}`
                  : undefined
              }
              supply={
                item.circulating_supply
                  ? `${item.circulating_supply.toLocaleString()} ${item.symbol.toUpperCase()}`
                  : undefined
              }
              high24h={
                item.high_24h ? `$${item.high_24h.toLocaleString()}` : undefined
              }
              low24h={
                item.low_24h ? `$${item.low_24h.toLocaleString()}` : undefined
              }
            >
              <div className="flex justify-center w-full mt-4">
                <Button
                  variant="default"
                  className="group/btn opacity-0 group-hover/card:opacity-100 transition-opacity duration-200 
                             w-16 bg-gray-500 hover:bg-red-500 flex items-center justify-center md:absolute md:top-2 md:right-2"
                  size="sm"
                  onClick={() => {
                    removeFromDashboard(item.id);
                  }}
                >
                  <Minus className="block group-hover/btn:hidden h-[1.2rem] mx-auto" />
                  <span className="hidden group-hover/btn:block text-center">
                    Remove
                  </span>
                </Button>
              </div>
            </DashboardCard>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
