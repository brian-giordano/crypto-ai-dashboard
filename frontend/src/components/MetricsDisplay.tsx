import React from "react";

interface MetricsDisplayProps {
  metrics: {
    price: string;
    marketCap: string;
    volume24h: string;
    change24h: string;
  };
}

const MetricsDisplay: React.FC<MetricsDisplayProps> = ({ metrics }) => {
  return (
    <div className="grid grid-cols-2 gap-2 mt-4">
      <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
        <p className="text-xs text-gray-500 dark:text-gray-400">Price</p>
        <p className="font-medium">{metrics.price}</p>
      </div>
      <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
        <p className="text-xs text-gray-500 dark:text-gray-400">Market Cap</p>
        <p className="font-medium">{metrics.marketCap}</p>
      </div>
      <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
        <p className="text-xs text-gray-500 dark:text-gray-400">24h Volume</p>
        <p className="font-medium">{metrics.volume24h}</p>
      </div>
      <div className="bg-white dark:bg-gray-700 p-2 rounded border border-gray-200 dark:border-gray-600">
        <p className="text-xs text-gray-500 dark:text-gray-400">24h Change</p>
        <p
          className={`font-medium ${
            metrics.change24h.startsWith("+")
              ? "text-green-500"
              : "text-red-500"
          }`}
        >
          {metrics.change24h}
        </p>
      </div>
    </div>
  );
};

export default MetricsDisplay;
