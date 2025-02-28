import React from "react";
import PriceChart from "./PriceChart";
// import { ChevronDown, ChevronUp } from "lucide-react";

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
}) => {
  const isPositive = changePercentage ? changePercentage >= 0 : false;
  //   const [isExpanded, setIsExpanded] = useState<boolean>(false);

  return (
    <div
      className="bg-white shadow-md rounded-lg p-4 flex flex-col hover:bg-gray-50 dark:bg-black dark:hover:bg-gray-600 cursor-pointer hover:shadow-lg hover:scale-105 transition-transform"
      onClick={() => {
        console.log(`Clicked on ${title}`);
      }}
    >
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
      {chartData && (
        <div className="mt-2">
          {/* Placeholder for a chart component */}
          {/* We can integrate a chart library here, e.g., Recharts or TanStack Charts */}
          <PriceChart data={chartData} isPositive={isPositive} />
        </div>
      )}
      {children}
    </div>
  );
};

export default DashboardCard;
