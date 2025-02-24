// DashboardLayout.tsx
"use client";

import React from "react";
import Dashboard from "@/components/Dashboard";
import { ThemeToggle } from "./ThemeToggle";

const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gray-800 text-white p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl">Crypto AI Dashboard</h1>
          <ThemeToggle />
        </div>
      </header>
      <main className="flex-grow p-4">
        <Dashboard />
      </main>
      <footer className="bg-gray-800 text-white p-4 text-center">
        © 2025 Crypto AI Dashboard
      </footer>
    </div>
  );
};

export default DashboardLayout;
