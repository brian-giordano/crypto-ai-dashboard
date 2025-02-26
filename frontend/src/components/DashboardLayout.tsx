// DashboardLayout.tsx
"use client";

import React from "react";
import Dashboard from "@/components/Dashboard";
import TopMarketData from "@/components/MarketDataPanel"; // New component for top market data
import { ThemeToggle } from "./ThemeToggle"; // Ensure the theme toggle is imported

const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-neutral-800 text-white p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl">Crypto AI Dashboard</h1>
          <ThemeToggle /> {/* Keep the theme toggle here */}
        </div>
      </header>
      <main className="flex-grow p-4 flex">
        <div className="flex-grow h-3/4">
          <Dashboard />
        </div>
        <div className="w-80 ml-4 border-l pl-4">
          <TopMarketData />
        </div>
      </main>
      <footer className="bg-neutral-900 text-white p-4 text-center">
        © 2025 Crypto AI Dashboard
      </footer>
    </div>
  );
};

export default DashboardLayout;
