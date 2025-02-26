export interface SparklineData {
  price: number[];
}

export interface CryptoData {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  total_volume: number;
  market_cap: number;
  market_cap_rank: number;
  price_change_percentage_24h: number;
  sparkline_in_7d: {
    price: number[];
  };
}
