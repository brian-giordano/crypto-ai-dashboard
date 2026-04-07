// frontend/src/app/api/crypto/route.ts
import { NextRequest, NextResponse } from "next/server";
import { mockCryptoData } from "@/lib/mock-data";

const GcApiUrl = process.env.NEXT_PUBLIC_GC_MARKET_DATA_API_URL;
const IS_DEMO_ENV = process.env.NEXT_PUBLIC_DEMO_MODE === "true";

export async function GET(request: NextRequest) {
  // Check demo mode
  const url = new URL(request.url);
  const forceDemo = url.searchParams.get("demo") === "true";
  const IS_DEMO = IS_DEMO_ENV || forceDemo;

  console.log("🔍 [API Crypto] Demo mode check:", {
    IS_DEMO,
    IS_DEMO_ENV,
    forceDemo,
  });

  // 🚀 DEMO MODE - Return mock data instantly
  if (IS_DEMO) {
    await new Promise((resolve) => setTimeout(resolve, 420));
    console.log("✅ [API Crypto] Returning mock data");
    return NextResponse.json(mockCryptoData);
  }

  // === REAL CoinGecko fallback (only used if demo is off) ===
  try {
    const params = new URLSearchParams({
      vs_currency: "usd",
      order: "market_cap_desc",
      page_per: "100",
      sparkline: "true",
      price_change_percentage: "24h",
    });

    const marketDataResponse = await fetch(`${GcApiUrl}?${params}`);

    if (!marketDataResponse.ok) {
      const errorText = await marketDataResponse.text();
      console.error("CoinGecko API Error:", errorText);
      return NextResponse.json(
        { error: "Failed to fetch market data" },
        { status: marketDataResponse.status },
      );
    }

    const data = await marketDataResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching crypto data: ", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}
