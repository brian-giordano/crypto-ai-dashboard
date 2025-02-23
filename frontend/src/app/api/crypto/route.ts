import { NextResponse } from "next/server";

export async function GET() {
  const response = await fetch(
    "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
  );
  const data = await response.json();

  return NextResponse.json(data);
}
