import React, { useState } from "react";
import PriceChart from "./PriceChart";
import { ChevronDown, ChevronUp } from "lucide-react";

interface DashboardCardProps {
  title: string;
  value: string | number;
  changePercentage?: number;
  chartData?: number[];
  children?: React.ReactNode;
  marketCap?: string;
  volume?: string;
  supply?: string;
  high24h?: string;
  low24h?: string;
}

// Utility function for formatting large numbers
const formatLargeNumber = (value: string | number | undefined): string => {
  if (value === undefined) return "-";

  // Convert to string, if necessary
  const num =
    typeof value === "string"
      ? parseFloat(value.replace(/[^0-9.-]+/g, ""))
      : value;

  if (isNaN(num)) return "-";

  // Format number based on size
  if (num >= 1e12) {
    return `${(num / 1e12).toFixed(2)} T`;
  } else if (num >= 1e9) {
    return `${(num / 1e9).toFixed(2)} B`;
  } else if (num >= 1e6) {
    return `${(num / 1e6).toFixed(2)} M`;
  } else if (num >= 1e3) {
    return `${(num / 1e3).toFixed(2)} K`;
  } else {
    return num.toFixed(2);
  }
};

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  changePercentage,
  chartData,
  children,
  marketCap,
  volume,
  supply,
  high24h,
  low24h,
}) => {
  const isPositive = changePercentage ? changePercentage >= 0 : false;
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  // Format the values
  const formattedMarketCap = formatLargeNumber(marketCap);
  const formattedVolume = formatLargeNumber(volume);
  const formattedSupply = formatLargeNumber(supply);

  return (
    <div
      className={`relative bg-white dark:bg-black hover:bg-gray-50 dark:hover:bg-gray-900 shadow-md hover:shadow-xl rounded-lg p-4 flex flex-col cursor-pointer transition-all duration-300 ${
        isExpanded ? "col-span-2 row-span-2" : ""
      }`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      {/* Card Header - Always visible */}
      <div className="flex justify-between items-start mb-2">
        <div>
          <h2 className="text-lg font-semibold">{title}</h2>
          <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">
            {value}
          </p>
          {changePercentage !== undefined && (
            <p
              className={`text-sm ${
                changePercentage >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {changePercentage >= 0 ? "+" : ""}
              {changePercentage}%
            </p>
          )}
        </div>

        {/* Remove Button - Top right on all screen sizes */}
        <div
          onClick={(e) => e.stopPropagation()}
          className="absolute top-3 right-3 z-10"
        >
          {children}
        </div>
      </div>

      {/* Chart - Always visible but can be larger when expanded */}
      {chartData && (
        // <div className={`mt-2 ${isExpanded ? "h-40" : "h-20"} flex-grow`}>
        <div className={`mt-2 flex-grow`}>
          <PriceChart data={chartData} isPositive={isPositive} />
        </div>
      )}

      {/* Expand/Collapse Indicator - Bottom right */}
      <div className="flex justify-end mt-2">
        <div className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full">
          {isExpanded ? (
            <ChevronUp className="h-5 w-5" />
          ) : (
            <ChevronDown className="h-5 w-5" />
          )}
        </div>
      </div>

      {/* EXPANDED CONTENT */}
      {isExpanded && (
        <div className="mt-4 space-y-3 border-t pt-3">
          <div className="grid grid-cols-2 gap-x-4 gap-y-2">
            {marketCap && (
              <>
                <h3 className="text-sm text-gray-500 dark:text-gray-400 text-left">
                  Market Cap
                </h3>
                <p className="text-sm text-right">${formattedMarketCap}</p>
              </>
            )}
            {volume && (
              <>
                <h3 className="text-sm text-gray-500 dark:text-gray-400 text-left">
                  24h Volume
                </h3>
                <p className="text-sm text-right">${formattedVolume}</p>
              </>
            )}
            {supply && (
              <>
                <h3 className="text-sm text-gray-500 dark:text-gray-400 text-left">
                  Circ. Supply
                </h3>
                <p className="text-sm text-right">{formattedSupply}</p>
              </>
            )}
            {high24h && (
              <>
                <h3 className="text-sm text-gray-500 dark:text-gray-400 text-left">
                  24h High
                </h3>
                <p className="text-sm text-right">{high24h}</p>
              </>
            )}
            {low24h && (
              <>
                <h3 className="text-sm text-gray-500 dark:text-gray-400 text-left">
                  24h Low
                </h3>
                <p className="text-sm text-right">{low24h}</p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardCard;
