// components/Dashboard.tsx
"use client";

import { useCryptoStore } from "@/store/useCryptoStore";
import { Button } from "./ui/button";
import { Minus, Plus } from "lucide-react"; // ← added Plus for empty state
import DashboardCard from "./DashboardCard";
import AiQuestionCard from "./AiQuestionCard";

const Dashboard: React.FC = () => {
  const { dashboardCryptos, removeFromDashboard } = useCryptoStore();

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">My Dashboard</h2>

      {/* Modernized grid container */}
      <div className="grid grid-cols-1 gap-6 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border border-border/60 shadow-sm rounded-3xl p-6 mb-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Dedicated slot for AiQuestionCard */}
        <div className="col-span-1 md:col-span-2 lg:col-span-3">
          <AiQuestionCard />
        </div>

        {/* Improved empty state */}
        {dashboardCryptos.length === 0 && (
          <div className="col-span-1 md:col-span-2 lg:col-span-3 flex flex-col items-center justify-center py-12 text-center bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-dashed border-border">
            <Plus className="w-8 h-8 text-gray-400 dark:text-gray-500 mb-3" />
            <p className="text-gray-600 dark:text-gray-400 font-medium">
              Your dashboard is empty
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-1 max-w-[240px]">
              Add cryptocurrencies from the market data panel on the right to
              get started
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
