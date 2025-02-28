import { NextResponse } from "next/server";

export async function GET() {
  try {
    const marketDataResponse = await fetch(
      "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=true"
    );

    if (!marketDataResponse.ok) {
      // Log the actual error response for debugging
      const errorText = await marketDataResponse.text();
      console.error("CoinGecko API Error:", errorText);

      return NextResponse.json(
        { error: "Failed to fetch market data" },
        { status: marketDataResponse.status }
      );
    }

    const data = await marketDataResponse.json();
    //console.log("API Response Data: ", data);

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching crypto data: ", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
