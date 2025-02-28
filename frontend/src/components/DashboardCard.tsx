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

  return (
    <div
      className={`bg-white shadow-md rounded-lg p-4 flex flex-col dark:bg-black cursor-pointer hover:shadow-lg transition-all duration-300 ${
        isExpanded ? "col-span-2 row-span-2" : ""
      }`}
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex justify-between items-start">
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

        <div className="flex items-center space-x-2">
          <div onClick={(e) => e.stopPropagation()}>{children}</div>
          <div className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full">
            {isExpanded ? (
              <ChevronUp className="h-5 w-5" />
            ) : (
              <ChevronDown className="h-5 w-5" />
            )}
          </div>
        </div>
      </div>

      {chartData && (
        <div className={`mt-2 ${isExpanded ? "h-40" : "h-20"}`}>
          {/* Placeholder for a chart component */}
          {/* We can integrate a chart library here, e.g., Recharts or TanStack Charts */}
          <PriceChart data={chartData} isPositive={isPositive} />
        </div>
      )}

      {/* EXPANDED CONTENT */}
      {isExpanded && (
        <div className="mt-4 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            {marketCap && (
              <div>
                <h3 className="text-sm text-gray-500 dark:text-gray-400">
                  Market Cap
                </h3>
                <p className="font-medium">{marketCap}</p>
              </div>
            )}
            {volume && (
              <div>
                <h3 className="text-sm text-gray-500 dark:text-gray-400">
                  24h Volume
                </h3>
                <p className="font-medium">{volume}</p>
              </div>
            )}
            {supply && (
              <div>
                <h3 className="text-sm text-gray-500 dark:text-gray-400">
                  Circulating Supply
                </h3>
                <p className="font-medium">{supply}</p>
              </div>
            )}
            {high24h && (
              <div>
                <h3 className="text-sm text-gray-500 dark:text-gray-400">
                  24h High
                </h3>
                <p className="font-medium">{high24h}</p>
              </div>
            )}
            {low24h && (
              <div>
                <h3 className="text-sm text-gray-500 dark:text-gray-400">
                  24h Low
                </h3>
                <p className="font-medium">{low24h}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* {children} */}
    </div>
  );
};

export default DashboardCard;
