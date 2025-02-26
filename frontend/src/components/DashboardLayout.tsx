// DashboardLayout.tsx
"use client";

import React from "react";
import Dashboard from "@/components/Dashboard";
import TopMarketData from "@/components/MarketDataPanel";
import { ThemeToggle } from "./ThemeToggle";

const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-neutral-800 text-white p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl">Vision Dashboard</h1>
          <ThemeToggle />
        </div>
      </header>
      <main className="flex-grow p-4 flex flex-col md:flex-row">
        <div className="flex-grow mv-4 md:mb-0 md:w-3/4">
          <Dashboard />
        </div>
        <div className="w-full md:w-80 md:border-t-0 md:pl-4 md:ml-4">
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
