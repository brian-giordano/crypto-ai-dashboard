import { StringToBoolean } from "class-variance-authority/types";
import React from "react";
import PriceChart from "./PriceChart";

interface DashboardCardProps {
  title: string;
  value: string | number;
  changePercentage?: number;
  chartData?: number[];
  children?: React.ReactNode;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  changePercentage,
  chartData,
  children,
}) => {
  const isPositive = changePercentage ? changePercentage >= 0 : false;

  return (
    <div className="bg-white shadow-md rounded-lg p-4 flex flex-col dark:bg-black">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="text-2xl font-bold">{value}</p>
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
          {/* You can integrate a chart library here, e.g., Recharts or TanStack Charts */}
          <PriceChart data={chartData} isPositive={isPositive} />
        </div>
      )}
    </div>
  );
};

export default DashboardCard;
