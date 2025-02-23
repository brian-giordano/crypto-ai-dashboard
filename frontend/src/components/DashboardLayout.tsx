"use client";

import React, { useEffect, useState } from "react";
import Dashboard from "@/components/Dashboard";

const DashboardLayout: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    const response = await fetch("/api/crypto");
    const result = await response.json();
    setData(result);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-gray-800 text-white p-4">
        <h1 className="text-2xl">Crypto AI Dashboard</h1>
      </header>
      <main className="flex-grow p-4">
        {loading ? <p>Loading...</p> : <Dashboard data={data} />}
      </main>
      <footer className="bg-gray-800 text-white p-4 text-center">
        © 2025 Crypto AI Dashboard
      </footer>
    </div>
  );
};

export default DashboardLayout;
