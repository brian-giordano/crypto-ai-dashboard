from typing import Dict, Any, List

# Helper function to format large numbers
def format_large_number(num: float) -> str:
    """Format large numbers to K, M, B, T format"""
    if num >= 1_000_000_000_000:
        return f"{num / 1_000_000_000_000:.2f}T"
    elif num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.2f}K"
    return f"{num:.2f}"

def get_coin_metrics(coin_data: Dict[str, Any]) -> Dict[str, str]:
    """Generate metrics for a specific cryptocurrency"""
    return {
        "price": f"${coin_data['current_price']}",
        "marketCap": f"${format_large_number(coin_data['market_cap'])}",
        "volume24h": f"${format_large_number(coin_data['total_volume'])}",
        "change24h": f"{coin_data['price_change_percentage_24h']}%"
    }

def get_market_overview_metrics(market_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate metrics for overall market overview"""
    total_market_cap = sum(coin['market_cap'] for coin in market_data)
    total_volume = sum(coin['total_volume'] for coin in market_data)
    avg_change = sum(coin['price_change_percentage_24h'] for coin in market_data) / len(market_data)

    return {
        "totalMarketCap": f"${format_large_number(total_market_cap)}",
        "totalVolume": f"${format_large_number(total_volume)}",
        "avgChange24h": f"{avg_change:.2f}%",
        "coinsAnalyzed": f"{len(market_data)}"
    }