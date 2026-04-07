// frontend/src/lib/mock-data.ts
export const mockCryptoData = [
  {
    id: "bitcoin",
    symbol: "btc",
    name: "Bitcoin",
    image: "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
    current_price: 87234.56,
    market_cap: 1728450000000,
    market_cap_rank: 1,
    price_change_percentage_24h: 3.24,
    sparkline_in_7d: {
      price: [84500, 85100, 84900, 86200, 85900, 87100, 87234],
    },
  },
  {
    id: "ethereum",
    symbol: "eth",
    name: "Ethereum",
    image: "https://assets.coingecko.com/coins/images/279/large/ethereum.png",
    current_price: 3421.87,
    market_cap: 411234000000,
    market_cap_rank: 2,
    price_change_percentage_24h: -1.78,
    sparkline_in_7d: { price: [3380, 3400, 3350, 3390, 3410, 3435, 3421] },
  },
  {
    id: "solana",
    symbol: "sol",
    name: "Solana",
    image: "https://assets.coingecko.com/coins/images/4128/large/solana.png",
    current_price: 218.45,
    market_cap: 101234000000,
    market_cap_rank: 3,
    price_change_percentage_24h: 4.91,
    sparkline_in_7d: { price: [205, 210, 212, 215, 217, 219, 218] },
  },
  {
    id: "binancecoin",
    symbol: "bnb",
    name: "BNB",
    image: "https://assets.coingecko.com/coins/images/825/large/bnb-icon2.png",
    current_price: 612.34,
    market_cap: 89456000000,
    market_cap_rank: 4,
    price_change_percentage_24h: 1.12,
    sparkline_in_7d: { price: [600, 605, 608, 610, 611, 612, 612] },
  },
  {
    id: "ripple",
    symbol: "xrp",
    name: "XRP",
    image:
      "https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-01.png",
    current_price: 2.34,
    market_cap: 132456000000,
    market_cap_rank: 5,
    price_change_percentage_24h: -2.45,
    sparkline_in_7d: { price: [2.4, 2.38, 2.35, 2.33, 2.36, 2.35, 2.34] },
  },
  {
    id: "cardano",
    symbol: "ada",
    name: "Cardano",
    image: "https://assets.coingecko.com/coins/images/975/large/cardano.png",
    current_price: 0.89,
    market_cap: 31890000000,
    market_cap_rank: 6,
    price_change_percentage_24h: 5.67,
    sparkline_in_7d: { price: [0.82, 0.84, 0.85, 0.87, 0.88, 0.89, 0.89] },
  },
  {
    id: "dogecoin",
    symbol: "doge",
    name: "Dogecoin",
    image: "https://assets.coingecko.com/coins/images/5/large/dogecoin.png",
    current_price: 0.312,
    market_cap: 45678000000,
    market_cap_rank: 7,
    price_change_percentage_24h: 8.91,
    sparkline_in_7d: { price: [0.28, 0.29, 0.295, 0.3, 0.305, 0.31, 0.312] },
  },
  {
    id: "avalanche-2",
    symbol: "avax",
    name: "Avalanche",
    image:
      "https://assets.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png",
    current_price: 48.76,
    market_cap: 19876000000,
    market_cap_rank: 8,
    price_change_percentage_24h: -0.89,
    sparkline_in_7d: { price: [49, 48.5, 48.2, 48.8, 48.9, 48.7, 48.76] },
  },
  {
    id: "tron",
    symbol: "trx",
    name: "TRON",
    image:
      "https://assets.coingecko.com/coins/images/10951/large/tron-logo.png",
    current_price: 0.234,
    market_cap: 20345000000,
    market_cap_rank: 9,
    price_change_percentage_24h: 2.34,
    sparkline_in_7d: {
      price: [0.225, 0.228, 0.23, 0.231, 0.232, 0.233, 0.234],
    },
  },
  {
    id: "chainlink",
    symbol: "link",
    name: "Chainlink",
    image:
      "https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png",
    current_price: 18.76,
    market_cap: 11789000000,
    market_cap_rank: 10,
    price_change_percentage_24h: 3.45,
    sparkline_in_7d: { price: [18, 18.2, 18.4, 18.5, 18.6, 18.7, 18.76] },
  },
  {
    id: "polkadot",
    symbol: "dot",
    name: "Polkadot",
    image: "https://assets.coingecko.com/coins/images/12151/large/polkadot.png",
    current_price: 7.89,
    market_cap: 11876000000,
    market_cap_rank: 11,
    price_change_percentage_24h: -3.12,
    sparkline_in_7d: { price: [8.1, 8.05, 8.0, 7.95, 7.9, 7.85, 7.89] },
  },
  {
    id: "litecoin",
    symbol: "ltc",
    name: "Litecoin",
    image: "https://assets.coingecko.com/coins/images/2/large/litecoin.png",
    current_price: 98.45,
    market_cap: 7389000000,
    market_cap_rank: 12,
    price_change_percentage_24h: 1.67,
    sparkline_in_7d: { price: [96, 96.5, 97, 97.5, 98, 98.3, 98.45] },
  },
];

export const mockAIResponse = (
  question: string,
): { response: string; sources?: string[] } => {
  const q = question.toLowerCase();

  if (q.includes("bitcoin") || q.includes("btc")) {
    return {
      response:
        "Bitcoin is currently in a strong accumulation phase. On-chain metrics show increasing whale activity and a bullish RSI divergence. Short-term target: $92,000–$95,000. Long-term outlook remains extremely positive with ETF inflows continuing.",
      sources: ["Glassnode", "CryptoQuant", "CoinGecko"],
    };
  }
  if (q.includes("ethereum") || q.includes("eth")) {
    return {
      response:
        "Ethereum is consolidating after the latest Dencun upgrade. Gas fees are at multi-year lows and staking participation is at an all-time high (32%+). Expect continued growth as Layer-2 activity explodes.",
      sources: ["Dune Analytics", "Beacon Chain"],
    };
  }
  if (q.includes("solana") || q.includes("sol")) {
    return {
      response:
        "Solana continues to lead in daily active users and DEX volume. The Firedancer upgrade is on track and should significantly improve network stability. High conviction long-term hold.",
      sources: ["Solana Beach", "DefiLlama"],
    };
  }
  if (q.includes("market") || q.includes("sentiment")) {
    return {
      response:
        "Overall crypto market sentiment is neutral-to-bullish (Fear & Greed Index: 68). Bitcoin dominance is stable at ~52%. Altcoins are starting to rotate in as we enter the next leg up.",
      sources: ["Alternative.me", "TradingView"],
    };
  }

  // Default thoughtful response
  return {
    response:
      "Great question! Based on current on-chain data, technical indicators, and macro factors, the asset is showing positive momentum. I'd recommend watching volume and key resistance levels before entering a position.",
    sources: ["CoinGecko", "Glassnode"],
  };
};
