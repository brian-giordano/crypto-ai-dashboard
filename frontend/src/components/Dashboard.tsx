import React from "react";

interface CryptoData {
  id: string;
  name: string;
  current_price: number;
  price_change_percentage_24h: number;
  market_cap: number;
}

const Dashboard: React.FC<{ data: CryptoData[] }> = ({ data }) => {
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold mb-4">Market Data</h3>
      <ul className="space-y-2">
        {data.map((item) => (
          <li
            key={item.id}
            className="border-b py-2 flex justify-between items-center hover:bg-gray-100 transition"
          >
            <span className="font-medium">{item.name}</span>
            <span>${item.current_price.toLocaleString()}</span>
            <span className="text-gray-500">
              24: {item.price_change_percentage_24h.toFixed(2)}%
            </span>
            <span className="text-gray-500">
              Market Cap: ${item.market_cap.toLocaleString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;
