// DashboardLayout.tsx
"use client";

import React from "react";
import Dashboard from "@/components/Dashboard";
import TopMarketData from "@/components/MarketDataPanel";
import { ThemeToggle } from "./ThemeToggle";

const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col dark:bg-gray-900">
      <header className="bg-black text-white p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl">Vision Dashboard</h1>
          <ThemeToggle />
        </div>
      </header>

      {/* 🚀 DEMO MODE BANNER - only shows in demo mode */}
      {process.env.NEXT_PUBLIC_DEMO_MODE === "true" && (
        <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white text-xs font-medium px-6 py-2 text-center tracking-widest flex items-center justify-center gap-3">
          🚀 DEMO MODE — Instant mock data for portfolio showcase
          <button
            onClick={() => {
              const url = new URL(window.location.href);
              url.searchParams.set("demo", "false");
              window.location.href = url.toString();
            }}
            className="underline hover:no-underline text-white/90 text-[10px] transition-colors"
          >
            Switch to live data →
          </button>
        </div>
      )}

      <main className="flex-grow p-4 flex flex-col md:flex-row">
        <div className="flex-grow mv-4 md:mb-0 md:w-3/4">
          <Dashboard />
        </div>
        <div className="w-full md:w-80 md:border-t-0 md:pl-4 md:ml-4">
          <TopMarketData />
        </div>
      </main>
      <footer className="bg-black text-white p-4 text-center">
        © 2025 Crypto AI Dashboard
      </footer>
    </div>
  );
};

export default DashboardLayout;
