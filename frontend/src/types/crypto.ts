import { LargeNumberLike } from "crypto";

export interface SparklineData {
  price: number[];
}

export interface CryptoData {
  id: string;
  name: string;
  current_price: number;
  total_volume: number;
  market_cap: number;
  sparkline_in_7d: SparklineData;
  price_change_percentage_24h: number;
}
