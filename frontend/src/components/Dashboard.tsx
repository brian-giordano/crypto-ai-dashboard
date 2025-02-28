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
        <div className="text-center p-12 bg-gray-300 rounded-lg dark:bg-gray-950 ">
          <p className="text-gray-700 dark:text-gray-700">
            Your dashboard is empty. Add cryptocurrencies from the market data
            panel.
          </p>
        </div>
      ) : (
        // Use a grid layout for displaying DashboardCard components
        <div className="grid grid-cols-2 gap-6 bg-gray-300 rounded-lg p-6 md:grid-cols-2 lg:grid-cols-3 dark:bg-gray-800">
          {dashboardCryptos.map((item) => (
            <div key={item.id} className="group/card">
              <DashboardCard
                title={item.name} // Title of the cryptocurrency
                value={`$${item.current_price.toLocaleString()}`} // Current price formatted as a string
                changePercentage={item.price_change_percentage_24h} // Percentage change in price (assuming this property exists)
                chartData={item.sparkline_in_7d.price} // Sparkline data for the price chart (assuming this property exists)
              >
                <div className="flex justify-center w-full mt-4">
                  <Button
                    variant="default"
                    className="group/btn opacity-0 group-hover/card:opacity-100 transition-opacity duration-200 
                               w-16 bg-gray-500 hover:bg-red-500 absolute top-2 right-2"
                    size="sm"
                    onClick={() => {
                      removeFromDashboard(item.id); // Remove the cryptocurrency from the dashboard
                    }}
                  >
                    <Minus className="block group-hover/btn:hidden h-[1.2rem] mx-auto" />
                    <span className="hidden group-hover/btn:block text-center">
                      Remove
                    </span>
                    {/* Minus icon for removing the cryptocurrency */}
                  </Button>
                </div>
              </DashboardCard>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
