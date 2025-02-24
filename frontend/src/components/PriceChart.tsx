// PriceChart.tsx
"use client";

import { FC } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface PriceChartProps {
  data: number[];
  isPositive: boolean;
}

const PriceChart: FC<PriceChartProps> = ({ data, isPositive }) => {
  const recentData = data.slice(-24); // Adjust this number as needed

  const maxPrice = Math.max(...recentData);
  const minPrice = Math.min(...recentData);
  const range = maxPrice - minPrice;

  const chartData = recentData.map((price, index) => ({
    time: index,
    price: range > 0 ? ((price - minPrice) / range) * 100 : 0, // Normalize to a 0-100 scale
  }));

  return (
    <ResponsiveContainer width="100%" height={50}>
      <LineChart data={chartData}>
        <XAxis dataKey="time" hide />
        <YAxis hide domain={[0, 100]} /> // Adjust domain for normalized data
        <Tooltip contentStyle={{ display: "none" }} />
        <Line
          type="monotone"
          dataKey="price"
          stroke={isPositive ? "#4caf50" : "#f44336"}
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PriceChart;
