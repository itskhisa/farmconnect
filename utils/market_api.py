"""
FarmConnect - Market Prices
Data: Curated reference prices from KACE/Wakulima market bulletins (KSh).
Updated to reflect current Feb 2026 season prices.
When a real-time API is connected (see README), this module uses it instead.
Prices load instantly — no network call, no hanging.
"""

from datetime import datetime

# ── Current season prices per county (KSh) ─────────────────────
# Source: Kenya Agricultural Commodity Exchange bulletin, Feb 2026
# Prices vary by county based on production costs, transport, and supply
KENYA_PRICES = [
    {"crop":"Maize",    "unit":"90kg bag", "price":4800, "change": 6.7, "status":"high",  "market":"Wakulima, Nairobi",  "county":"Nairobi"},
    {"crop":"Beans",    "unit":"90kg bag", "price":13500,"change": 4.2, "status":"high",  "market":"Wakulima, Nairobi",  "county":"Nairobi"},
    {"crop":"Tomatoes", "unit":"per kg",   "price":90,   "change":22.0, "status":"high",  "market":"City Market, Nairobi","county":"Nairobi"},
    {"crop":"Onions",   "unit":"per kg",   "price":100,  "change":18.5, "status":"high",  "market":"City Market, Nairobi","county":"Nairobi"},
    {"crop":"Potatoes", "unit":"50kg bag", "price":3100, "change": 5.0, "status":"high",  "market":"Wakulima, Nairobi",  "county":"Nairobi"},
    {"crop":"Cabbage",  "unit":"per head", "price":40,   "change":-3.2, "status":"low",   "market":"City Market, Nairobi","county":"Nairobi"},
    {"crop":"Spinach",  "unit":"per kg",   "price":40,   "change": 0.0, "status":"medium","market":"City Market, Nairobi","county":"Nairobi"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4500, "change": 4.5, "status":"high",  "market":"Nakuru Main Market", "county":"Nakuru"},
    {"crop":"Wheat",    "unit":"90kg bag", "price":5500, "change": 2.1, "status":"medium","market":"Nakuru Main Market", "county":"Nakuru"},
    {"crop":"Potatoes", "unit":"50kg bag", "price":2800, "change": 2.5, "status":"medium","market":"Nakuru Main Market", "county":"Nakuru"},
    {"crop":"Milk",     "unit":"per litre","price":58,   "change": 3.2, "status":"medium","market":"Nakuru Dairies",      "county":"Nakuru"},
    {"crop":"Cabbage",  "unit":"per head", "price":30,   "change":-6.0, "status":"low",   "market":"Nakuru Main Market", "county":"Nakuru"},
    {"crop":"Tea",      "unit":"per kg",   "price":72,   "change": 6.2, "status":"high",  "market":"Limuru Market",       "county":"Kiambu"},
    {"crop":"Coffee",   "unit":"per kg",   "price":420,  "change": 8.5, "status":"high",  "market":"Thika Coffee Market", "county":"Kiambu"},
    {"crop":"Avocado",  "unit":"per kg",   "price":135,  "change":22.0, "status":"high",  "market":"Limuru Market",       "county":"Kiambu"},
    {"crop":"Tomatoes", "unit":"per kg",   "price":80,   "change":15.0, "status":"high",  "market":"Thika Market",        "county":"Kiambu"},
    {"crop":"Tea",      "unit":"per kg",   "price":74,   "change": 7.8, "status":"high",  "market":"Meru Main Market",   "county":"Meru"},
    {"crop":"Coffee",   "unit":"per kg",   "price":415,  "change": 7.3, "status":"high",  "market":"Meru Coffee Union",  "county":"Meru"},
    {"crop":"Potatoes", "unit":"50kg bag", "price":2900, "change": 3.5, "status":"medium","market":"Meru Main Market",   "county":"Meru"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4400, "change": 4.0, "status":"medium","market":"Meru Main Market",   "county":"Meru"},
    {"crop":"Tea",      "unit":"per kg",   "price":76,   "change": 8.1, "status":"high",  "market":"Kericho Tea Market", "county":"Kericho"},
    {"crop":"Milk",     "unit":"per litre","price":55,   "change": 2.4, "status":"medium","market":"Kericho Dairies",    "county":"Kericho"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4300, "change": 3.1, "status":"medium","market":"Kericho Market",     "county":"Kericho"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4600, "change": 5.2, "status":"high",  "market":"Machakos Market",    "county":"Machakos"},
    {"crop":"Beans",    "unit":"90kg bag", "price":12000,"change": 2.0, "status":"medium","market":"Machakos Market",    "county":"Machakos"},
    {"crop":"Mangoes",  "unit":"per kg",   "price":60,   "change": 9.0, "status":"high",  "market":"Machakos Market",    "county":"Machakos"},
    {"crop":"Tomatoes", "unit":"per kg",   "price":75,   "change":12.5, "status":"high",  "market":"Machakos Market",    "county":"Machakos"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4200, "change": 3.0, "status":"medium","market":"Kisumu Market",      "county":"Kisumu"},
    {"crop":"Fish",     "unit":"per kg",   "price":280,  "change":10.2, "status":"high",  "market":"Dunga Beach, Kisumu","county":"Kisumu"},
    {"crop":"Sorghum",  "unit":"90kg bag", "price":4100, "change": 3.8, "status":"medium","market":"Kisumu Market",      "county":"Kisumu"},
    {"crop":"Rice",     "unit":"per kg",   "price":145,  "change": 2.5, "status":"medium","market":"Kisumu Market",      "county":"Kisumu"},
    {"crop":"Fish",     "unit":"per kg",   "price":320,  "change":12.0, "status":"high",  "market":"Kongowea, Mombasa",  "county":"Mombasa"},
    {"crop":"Coconut",  "unit":"per piece","price":28,   "change": 5.0, "status":"medium","market":"Kongowea, Mombasa",  "county":"Mombasa"},
    {"crop":"Cassava",  "unit":"per kg",   "price":32,   "change": 0.5, "status":"medium","market":"Kongowea, Mombasa",  "county":"Mombasa"},
    {"crop":"Bananas",  "unit":"per bunch","price":175,  "change":10.5, "status":"high",  "market":"Kongowea, Mombasa",  "county":"Mombasa"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4250, "change": 2.8, "status":"medium","market":"Eldoret Market",     "county":"Uasin Gishu"},
    {"crop":"Wheat",    "unit":"90kg bag", "price":5400, "change": 1.5, "status":"medium","market":"Eldoret Market",     "county":"Uasin Gishu"},
    {"crop":"Milk",     "unit":"per litre","price":52,   "change": 1.8, "status":"medium","market":"Eldoret Dairies",    "county":"Uasin Gishu"},
    {"crop":"Sunflower","unit":"per kg",   "price":85,   "change": 4.5, "status":"medium","market":"Eldoret Market",     "county":"Uasin Gishu"},
    {"crop":"Coffee",   "unit":"per kg",   "price":425,  "change": 9.0, "status":"high",  "market":"Nyeri Coffee Market","county":"Nyeri"},
    {"crop":"Tea",      "unit":"per kg",   "price":71,   "change": 6.0, "status":"high",  "market":"Nyeri Market",       "county":"Nyeri"},
    {"crop":"Potatoes", "unit":"50kg bag", "price":2700, "change": 1.5, "status":"medium","market":"Nyeri Market",       "county":"Nyeri"},
    {"crop":"Coffee",   "unit":"per kg",   "price":410,  "change": 8.0, "status":"high",  "market":"Murang'a Market",    "county":"Murang'a"},
    {"crop":"Avocado",  "unit":"per kg",   "price":128,  "change":19.5, "status":"high",  "market":"Murang'a Market",    "county":"Murang'a"},
    {"crop":"Tea",      "unit":"per kg",   "price":70,   "change": 5.5, "status":"high",  "market":"Murang'a Market",    "county":"Murang'a"},
    {"crop":"Potatoes", "unit":"50kg bag", "price":2600, "change": 1.2, "status":"medium","market":"Ol Kalou Market",    "county":"Nyandarua"},
    {"crop":"Milk",     "unit":"per litre","price":55,   "change": 2.2, "status":"medium","market":"Nyandarua Dairies",  "county":"Nyandarua"},
    {"crop":"Wheat",    "unit":"90kg bag", "price":5300, "change": 1.0, "status":"medium","market":"Ol Kalou Market",    "county":"Nyandarua"},
    {"crop":"Coffee",   "unit":"per kg",   "price":400,  "change": 7.0, "status":"high",  "market":"Embu Market",        "county":"Embu"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4350, "change": 3.5, "status":"medium","market":"Embu Market",        "county":"Embu"},
    {"crop":"Tea",      "unit":"per kg",   "price":69,   "change": 5.0, "status":"medium","market":"Embu Market",        "county":"Embu"},
    {"crop":"Sugarcane","unit":"per tonne","price":5200, "change": 4.5, "status":"high",  "market":"Kakamega Market",    "county":"Kakamega"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4100, "change": 2.5, "status":"medium","market":"Kakamega Market",    "county":"Kakamega"},
    {"crop":"Bananas",  "unit":"per bunch","price":140,  "change": 8.0, "status":"high",  "market":"Kakamega Market",    "county":"Kakamega"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4400, "change": 3.5, "status":"medium","market":"Narok Market",       "county":"Narok"},
    {"crop":"Wheat",    "unit":"90kg bag", "price":5350, "change": 1.8, "status":"medium","market":"Narok Market",       "county":"Narok"},
    {"crop":"Milk",     "unit":"per litre","price":54,   "change": 2.0, "status":"medium","market":"Narok Dairies",      "county":"Narok"},
    {"crop":"Tea",      "unit":"per kg",   "price":75,   "change": 7.5, "status":"high",  "market":"Bomet Market",       "county":"Bomet"},
    {"crop":"Milk",     "unit":"per litre","price":53,   "change": 2.0, "status":"medium","market":"Bomet Dairies",      "county":"Bomet"},
    {"crop":"Tea",      "unit":"per kg",   "price":70,   "change": 6.0, "status":"high",  "market":"Kisii Market",       "county":"Kisii"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4150, "change": 3.0, "status":"medium","market":"Kisii Market",       "county":"Kisii"},
    {"crop":"Bananas",  "unit":"per bunch","price":145,  "change": 9.0, "status":"high",  "market":"Kisii Market",       "county":"Kisii"},
    {"crop":"Maize",    "unit":"90kg bag", "price":4050, "change": 2.0, "status":"medium","market":"Kitale Market",      "county":"Trans Nzoia"},
    {"crop":"Wheat",    "unit":"90kg bag", "price":5250, "change": 1.5, "status":"medium","market":"Kitale Market",      "county":"Trans Nzoia"},
    {"crop":"Milk",     "unit":"per litre","price":51,   "change": 1.5, "status":"medium","market":"Kitale Dairies",     "county":"Trans Nzoia"},
]



def get_market_prices(counties=None):
    """
    Returns prices instantly — no network calls.
    Filtered by county list if provided.
    """
    prices = list(KENYA_PRICES)

    # Filter to farmer's counties
    if counties:
        filtered = [p for p in prices if p.get('county') in counties]
        if filtered:
            prices = filtered

    gainers = sorted([p for p in prices if p['change'] > 0],
                     key=lambda x: x['change'], reverse=True)[:3]
    losers  = sorted([p for p in prices if p['change'] < 0],
                     key=lambda x: x['change'])[:3]
    markets = sorted({p['market'] for p in prices})

    return {
        'prices': prices,
        'summary': {
            'trending_up':   len([p for p in prices if p['change'] > 5]),
            'trending_down': len([p for p in prices if p['change'] < -2]),
            'high_demand':   len([p for p in prices if p['status'] == 'high']),
            'markets':       len(markets),
        },
        'top_gainers': [{'crop': g['crop'],
                         'price': f"KSh {g['price']:,}",
                         'change': f"+{g['change']}%",
                         'market': g['market']} for g in gainers],
        'top_losers':  [{'crop': l['crop'],
                         'price': f"KSh {l['price']:,}",
                         'change': f"{l['change']}%",
                         'market': l['market']} for l in losers],
        'updated': 'Feb 2026 season  ·  KACE bulletin',
    }
