"""
FarmConnect - Weather API
Uses Open-Meteo (free, no key). Passes correct lat/lon per county.
Falls back to climate-zone data when offline (Kenya has 4 distinct zones).
"""

import requests
from datetime import datetime

WMO_CODES = {
    0:  ("Clear Sky",        "☀️"),
    1:  ("Mainly Clear",     "🌤️"),
    2:  ("Partly Cloudy",    "⛅"),
    3:  ("Overcast",         "☁️"),
    45: ("Foggy",            "🌫️"),
    48: ("Icy Fog",          "🌫️"),
    51: ("Light Drizzle",    "🌦️"),
    53: ("Drizzle",          "🌦️"),
    55: ("Heavy Drizzle",    "🌧️"),
    61: ("Light Rain",       "🌧️"),
    63: ("Rain",             "🌧️"),
    65: ("Heavy Rain",       "🌧️"),
    80: ("Rain Showers",     "🌦️"),
    81: ("Heavy Showers",    "🌧️"),
    82: ("Violent Showers",  "⛈️"),
    95: ("Thunderstorm",     "⛈️"),
    96: ("Thunderstorm",     "⛈️"),
    99: ("Severe Storm",     "🌪️"),
}

# ── Kenya climate zones — realistic baseline data ─────────────────
# Source: Kenya Meteorological Department averages
CLIMATE_ZONES = {
    # Hot & humid coast
    "coast": {
        "counties": ["Mombasa","Kilifi","Kwale","Tana River","Lamu","Taita-Taveta"],
        "temp": 30, "feels_like": 33, "humidity": 80, "wind": 18,
        "rain_chance": 35, "uv_index": 9,
        "condition": "Partly Cloudy", "emoji": "⛅",
        "hourly_temps": [26,27,30,32,31,28],
        "daily": [
            {"day":"Mon","emoji":"⛅","high":31,"low":24,"rain":30,"humidity":80},
            {"day":"Tue","emoji":"🌦️","high":30,"low":24,"rain":45,"humidity":82},
            {"day":"Wed","emoji":"☀️","high":32,"low":25,"rain":15,"humidity":77},
            {"day":"Thu","emoji":"⛅","high":31,"low":24,"rain":25,"humidity":79},
            {"day":"Fri","emoji":"🌧️","high":29,"low":23,"rain":60,"humidity":85},
            {"day":"Sat","emoji":"⛅","high":30,"low":24,"rain":30,"humidity":80},
            {"day":"Sun","emoji":"☀️","high":32,"low":25,"rain":10,"humidity":75},
        ],
    },
    # Hot & dry arid north
    "arid": {
        "counties": ["Turkana","Marsabit","Mandera","Wajir","Garissa","Isiolo",
                     "Samburu","Tana River"],
        "temp": 36, "feels_like": 39, "humidity": 25, "wind": 22,
        "rain_chance": 5, "uv_index": 11,
        "condition": "Clear Sky", "emoji": "☀️",
        "hourly_temps": [30,33,37,39,38,34],
        "daily": [
            {"day":"Mon","emoji":"☀️","high":38,"low":22,"rain":2, "humidity":20},
            {"day":"Tue","emoji":"☀️","high":39,"low":23,"rain":0, "humidity":18},
            {"day":"Wed","emoji":"🌤️","high":37,"low":22,"rain":5, "humidity":22},
            {"day":"Thu","emoji":"☀️","high":40,"low":24,"rain":2, "humidity":19},
            {"day":"Fri","emoji":"☀️","high":38,"low":22,"rain":0, "humidity":20},
            {"day":"Sat","emoji":"🌤️","high":37,"low":21,"rain":8, "humidity":25},
            {"day":"Sun","emoji":"☀️","high":39,"low":23,"rain":2, "humidity":18},
        ],
    },
    # Cool & wet highlands
    "highlands": {
        "counties": ["Nyeri","Nyandarua","Kirinyaga","Murang'a","Kiambu",
                     "Nakuru","Kericho","Bomet","Nyamira","Kisii","Meru",
                     "Embu","Tharaka-Nithi","Laikipia","Trans Nzoia",
                     "Uasin Gishu","Nandi","Elgeyo-Marakwet","West Pokot","Baringo"],
        "temp": 19, "feels_like": 17, "humidity": 72, "wind": 14,
        "rain_chance": 55, "uv_index": 6,
        "condition": "Overcast", "emoji": "☁️",
        "hourly_temps": [15,17,20,21,20,17],
        "daily": [
            {"day":"Mon","emoji":"🌧️","high":20,"low":12,"rain":65,"humidity":75},
            {"day":"Tue","emoji":"⛅","high":21,"low":13,"rain":35,"humidity":70},
            {"day":"Wed","emoji":"☁️","high":18,"low":11,"rain":70,"humidity":78},
            {"day":"Thu","emoji":"🌦️","high":20,"low":12,"rain":50,"humidity":74},
            {"day":"Fri","emoji":"⛅","high":22,"low":13,"rain":30,"humidity":68},
            {"day":"Sat","emoji":"🌧️","high":19,"low":11,"rain":75,"humidity":80},
            {"day":"Sun","emoji":"🌤️","high":23,"low":14,"rain":20,"humidity":65},
        ],
    },
    # Warm & moderate central/western
    "central": {
        "counties": ["Nairobi","Machakos","Makueni","Kitui","Kajiado",
                     "Narok","Kakamega","Bungoma","Busia","Vihiga",
                     "Siaya","Kisumu","Homa Bay","Migori","Nyamira"],
        "temp": 24, "feels_like": 25, "humidity": 62, "wind": 13,
        "rain_chance": 30, "uv_index": 8,
        "condition": "Partly Cloudy", "emoji": "⛅",
        "hourly_temps": [18,20,25,26,24,21],
        "daily": [
            {"day":"Mon","emoji":"⛅","high":26,"low":15,"rain":25,"humidity":62},
            {"day":"Tue","emoji":"🌤️","high":27,"low":16,"rain":15,"humidity":58},
            {"day":"Wed","emoji":"🌦️","high":24,"low":14,"rain":45,"humidity":68},
            {"day":"Thu","emoji":"⛅","high":25,"low":15,"rain":30,"humidity":63},
            {"day":"Fri","emoji":"☀️","high":28,"low":16,"rain":10,"humidity":55},
            {"day":"Sat","emoji":"⛅","high":26,"low":15,"rain":25,"humidity":61},
            {"day":"Sun","emoji":"🌧️","high":23,"low":13,"rain":55,"humidity":70},
        ],
    },
}


def _get_zone(county_name):
    for zone, data in CLIMATE_ZONES.items():
        if county_name in data["counties"]:
            return zone, data
    return "central", CLIMATE_ZONES["central"]


def _climate_fallback(county_name):
    """Returns realistic climate-zone data when API is unavailable."""
    zone, z = _get_zone(county_name)
    now = datetime.now()
    hourly = [
        {"time": t, "temp": z["hourly_temps"][i], "rain": z["rain_chance"]}
        for i, t in enumerate(["6am","9am","12pm","3pm","6pm","9pm"])
    ]
    insights = _farm_insights_from_climate(county_name, z)
    return {
        "success":   True,
        "source":    "climate_zone",
        "current_weather": {
            "location":    county_name,
            "date":        now.strftime("%A, %d %b %Y"),
            "time":        now.strftime("%I:%M %p"),
            "temp":        z["temp"],
            "feels_like":  z["feels_like"],
            "condition":   z["condition"],
            "emoji":       z["emoji"],
            "humidity":    z["humidity"],
            "wind":        z["wind"],
            "rain_chance": z["rain_chance"],
            "uv_index":    z["uv_index"],
        },
        "hourly_forecast": hourly,
        "seven_day":       z["daily"],
        "weekly_rainfall": [int(z["rain_chance"]*0.4), int(z["rain_chance"]*0.6),
                            int(z["rain_chance"]*0.35), int(z["rain_chance"]*0.5)],
        "farm_insights":   insights,
        "alert":           _alert_from_climate(z),
    }


def _farm_insights_from_climate(county_name, z):
    insights = []
    if z["rain_chance"] > 60:
        insights.append({"title":"Irrigation Planning","priority":"high","icon":"💧",
            "desc":"Heavy rainfall expected this week. Reduce irrigation, clear drainage channels."})
    elif z["rain_chance"] < 15:
        insights.append({"title":"Irrigation Needed","priority":"high","icon":"💧",
            "desc":"Dry conditions. Increase irrigation frequency, especially for young crops."})
    if z["humidity"] > 75:
        insights.append({"title":"Pest Control Alert","priority":"high","icon":"🐛",
            "desc":f"High humidity ({z['humidity']}%) increases fungal disease risk. Inspect crops."})
    if z["uv_index"] >= 9:
        insights.append({"title":"Extreme UV Alert","priority":"medium","icon":"☀️",
            "desc":f"UV index {z['uv_index']} — protect young seedlings and provide shade for livestock."})
    if z["wind"] > 20:
        insights.append({"title":"Avoid Spraying","priority":"medium","icon":"🌬️",
            "desc":f"Wind {z['wind']}km/h — postpone pesticide/herbicide spraying."})
    return insights[:4]


def _alert_from_climate(z):
    if z["rain_chance"] > 65:
        return {"title":"⚠️ Heavy Rain Alert",
                "desc":"Heavy rainfall expected. Secure equipment and check drainage on your farm.",
                "level":"warning"}
    if z["temp"] > 36:
        return {"title":"🌡️ Heat Alert",
                "desc":"Extreme heat. Ensure livestock have water and shade. Avoid fieldwork midday.",
                "level":"warning"}
    return None


def get_weather(lat: float, lon: float, location_name: str = "Nairobi") -> dict:
    """
    Fetch real weather from Open-Meteo for the exact lat/lon.
    Falls back to climate zone data if offline.
    Each county gets DIFFERENT data because each county has different lat/lon.
    """
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":    lat,
                "longitude":   lon,
                "current":     ["temperature_2m","relative_humidity_2m",
                                "apparent_temperature","weather_code",
                                "wind_speed_10m","precipitation_probability","uv_index"],
                "hourly":      ["temperature_2m","precipitation_probability"],
                "daily":       ["weather_code","temperature_2m_max","temperature_2m_min",
                                "precipitation_probability_max","precipitation_sum"],
                "timezone":    "Africa/Nairobi",
                "forecast_days": 7,
                "wind_speed_unit": "kmh",
            },
            timeout=8,
        )
        raw = resp.json()
        if "current" not in raw:
            return _climate_fallback(location_name)

        cur   = raw["current"]
        code  = cur.get("weather_code", 1)
        cond, emoji = WMO_CODES.get(code, ("Partly Cloudy", "⛅"))
        now   = datetime.now()

        current_weather = {
            "location":    location_name,
            "date":        now.strftime("%A, %d %b %Y"),
            "time":        now.strftime("%I:%M %p"),
            "temp":        int(cur.get("temperature_2m", 24)),
            "feels_like":  int(cur.get("apparent_temperature", 24)),
            "condition":   cond,
            "emoji":       emoji,
            "humidity":    int(cur.get("relative_humidity_2m", 60)),
            "wind":        int(cur.get("wind_speed_10m", 12)),
            "rain_chance": int(cur.get("precipitation_probability", 20)),
            "uv_index":    int(cur.get("uv_index", 6)),
        }

        # Hourly (pick 6 slots across the day)
        h_times = raw.get("hourly", {}).get("time", [])
        h_temps = raw.get("hourly", {}).get("temperature_2m", [])
        h_rain  = raw.get("hourly", {}).get("precipitation_probability", [])
        LABELS  = ["6am","9am","12pm","3pm","6pm","9pm"]
        hourly  = []
        for i, lbl in enumerate(LABELS):
            idx = min(i * 3, len(h_temps) - 1) if h_temps else 0
            hourly.append({
                "time": lbl,
                "temp": int(h_temps[idx]) if h_temps else 24,
                "rain": int(h_rain[idx])  if h_rain  else 20,
            })

        # 7-day forecast
        daily   = raw.get("daily", {})
        d_codes = daily.get("weather_code", [])
        d_max   = daily.get("temperature_2m_max", [])
        d_min   = daily.get("temperature_2m_min", [])
        d_rain  = daily.get("precipitation_probability_max", [])
        d_prec  = daily.get("precipitation_sum", [])
        DAYS    = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        seven_day = []
        for i in range(min(7, len(d_codes))):
            dc, de = WMO_CODES.get(d_codes[i], ("","⛅"))
            seven_day.append({
                "day":      DAYS[i],
                "emoji":    de,
                "high":     int(d_max[i]) if d_max else 27,
                "low":      int(d_min[i]) if d_min else 16,
                "rain":     int(d_rain[i]) if d_rain else 25,
                "humidity": current_weather["humidity"],
                "precip":   round(d_prec[i], 1) if d_prec else 0,
            })

        # Rainfall totals
        weekly_rainfall = []
        for j in range(0, 28, 7):
            total = sum(int(d_prec[i]) for i in range(j, min(j+7, len(d_prec))) if d_prec)
            weekly_rainfall.append(total or int(current_weather["rain_chance"] * 0.5))

        insights = _farm_insights_live(current_weather, seven_day)

        return {
            "success":          True,
            "source":           "live",
            "current_weather":  current_weather,
            "hourly_forecast":  hourly,
            "seven_day":        seven_day,
            "weekly_rainfall":  weekly_rainfall,
            "farm_insights":    insights,
            "alert":            _alert_live(current_weather, seven_day),
        }

    except Exception:
        # Always fall back to climate zone — never show same data for all counties
        return _climate_fallback(location_name)


def _farm_insights_live(cw, seven_day):
    insights = []
    future_rain = [d["rain"] for d in seven_day[:3]]
    if any(r > 60 for r in future_rain):
        insights.append({"title":"Irrigation Planning","priority":"high","icon":"💧",
            "desc":"Heavy rain expected this week. Reduce irrigation by 50% to avoid waterlogging."})
    elif all(r < 15 for r in future_rain):
        insights.append({"title":"Irrigation Needed","priority":"high","icon":"💧",
            "desc":"Dry conditions ahead. Increase watering frequency for your crops."})
    if cw["humidity"] > 75:
        insights.append({"title":"Fungal Disease Risk","priority":"high","icon":"🐛",
            "desc":f"Humidity at {cw['humidity']}% — inspect crops for blight, mildew, and rust."})
    if cw["wind"] > 20:
        insights.append({"title":"Spraying Advisory","priority":"medium","icon":"🌬️",
            "desc":f"Wind {cw['wind']}km/h — postpone pesticide spraying today."})
    if cw["uv_index"] >= 9:
        insights.append({"title":"High UV Alert","priority":"medium","icon":"☀️",
            "desc":f"UV index {cw['uv_index']} — protect seedlings and provide livestock shade."})
    return insights[:4]


def _alert_live(cw, seven_day):
    heavy = [d for d in seven_day[:4] if d["rain"] > 70]
    if heavy:
        days = ", ".join(d["day"] for d in heavy[:2])
        return {"title":f"⚠️ Heavy Rain — {days}",
                "desc":"Secure equipment, clear drainage channels, protect young seedlings.",
                "level":"warning"}
    if cw["temp"] > 36:
        return {"title":"🌡️ Heat Alert",
                "desc":"Extreme heat today. Water crops early morning. Provide livestock shade.",
                "level":"warning"}
    return None
