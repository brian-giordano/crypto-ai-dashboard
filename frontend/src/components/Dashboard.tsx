// components/Dashboard.tsx
"use client";

import { useCryptoStore } from "@/store/useCryptoStore"; // Import the crypto store for state management
import { Button } from "./ui/button"; // Import the Button component
import { Minus } from "lucide-react"; // Import the Minus icon
import DashboardCard from "./DashboardCard"; // Import the DashboardCard component

const Dashboard: React.FC = () => {
  const { dashboardCryptos, removeFromDashboard } = useCryptoStore(); // Access the dashboardCryptos and removeFromDashboard from the store

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">My Dashboard</h2>
      {dashboardCryptos.length === 0 ? ( // Check if there are no cryptocurrencies in the dashboard
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">
            Your dashboard is empty. Add cryptocurrencies from the market data
            panel.
          </p>
        </div>
      ) : (
        // Use a grid layout for displaying DashboardCard components
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dashboardCryptos.map((item) => (
            <DashboardCard
              key={item.id} // Unique key for each card
              title={item.name} // Title of the cryptocurrency
              value={`$${item.current_price.toLocaleString()}`} // Current price formatted as a string
              changePercentage={item.price_change_percentage_24h} // Percentage change in price (assuming this property exists)
              chartData={item.sparkline_in_7d.price} // Sparkline data for the price chart (assuming this property exists)
            >
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  removeFromDashboard(item.id); // Remove the cryptocurrency from the dashboard
                }}
              >
                <Minus className="h-[1.2rem] w-[1.2rem]" />{" "}
                {/* Minus icon for removing the cryptocurrency */}
              </Button>
            </DashboardCard>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
