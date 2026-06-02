import pandas as pd

def get_market_advice(crop, district):

    prices = pd.read_csv("data/market_prices.csv")
    weather = pd.read_csv("data/weather.csv")

    match_price = prices[
        (prices["crop"] == crop) &
        (prices["district"] == district)
    ]

    if match_price.empty:
        return {
            "error": "No market data found"
        }

    price = match_price["price"].values[0]

    rain = weather[
        weather["district"] == district
    ]["rain_days"].values[0]

    if rain <= 5:
        recommendation = "Sell 60% now and store 40%."
    else:
        recommendation = "Store crop carefully and monitor weather."

    return {
        "price": price,
        "rain": rain,
        "recommendation": recommendation
    }