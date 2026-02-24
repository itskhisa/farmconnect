"""
FarmConnect - Mock Data Store
Simulates a real backend database with sample Kenyan farming data
"""

from datetime import datetime, timedelta
import random

# ── Farmer Profile ────────────────────────────────────────────────────────────
FARMER = {
    'name': 'Farmer',
    'location': 'Nairobi',
    'total_area': 4.0,
    'total_revenue': 845000,
    'revenue_change': 23.5,
    'farm_efficiency': 87,
    'efficiency_change': 5.2,
    'active_crops': 3,
    'weather_score': 78,
}

# ── Crops Data ────────────────────────────────────────────────────────────────
CROPS = [
    {
        'id': 1,
        'name': 'Maize',
        'emoji': '🌽',
        'variety': 'Hybrid H614',
        'field': 'Field A',
        'area': 2.5,
        'status': 'growing',
        'days_to_harvest': 101,
        'expected_date': '15/05/2026',
        'planted': '04/02/2026',
    },
    {
        'id': 2,
        'name': 'Tomatoes',
        'emoji': '🍅',
        'variety': 'Rio Grande',
        'field': 'Greenhouse 1',
        'area': 0.5,
        'status': 'growing',
        'days_to_harvest': 76,
        'expected_date': '29/04/2026',
        'planted': '14/02/2026',
    },
    {
        'id': 3,
        'name': 'Beans',
        'emoji': '🫘',
        'variety': 'Rose Coco',
        'field': 'Field B',
        'area': 1.0,
        'status': 'ready',
        'days_to_harvest': 12,
        'expected_date': '15/03/2026',
        'planted': '01/01/2026',
    },
]

UPCOMING_HARVESTS = [
    {'crop': 'Beans',     'days': 12,  'status': 'ready'},
    {'crop': 'Tomatoes',  'days': 18,  'status': 'soon'},
    {'crop': 'Maize',     'days': 45,  'status': 'growing'},
    {'crop': 'Sukuma Wiki','days': 6,   'status': 'ready'},
    {'crop': 'Potatoes',  'days': 32,  'status': 'growing'},
]

CROP_DISTRIBUTION = [
    ('Maize',      35, '#2E7D32'),
    ('Beans',      26, '#C62828'),
    ('Tomatoes',   15, '#FF6F00'),
    ('Vegetables', 20, '#1565C0'),
    ('Others',     10, '#6A1B9A'),
]

LIVESTOCK = [
    {'type': 'Dairy Cows', 'emoji': '🐄', 'count': 5,  'notes': 'Friesian breed, healthy'},
    {'type': 'Goats',      'emoji': '🐐', 'count': 12, 'notes': 'Boer & local breeds'},
    {'type': 'Poultry',    'emoji': '🐔', 'count': 50, 'notes': 'Layers, 35 eggs/day avg'},
]

TODAY_TASKS = [
    {'task': 'Water tomato greenhouse',  'time': 'Morning',   'priority': 'high'},
    {'task': 'Check maize for pests',    'time': 'Afternoon', 'priority': 'medium'},
    {'task': 'Prepare beans for harvest','time': 'Morning',   'priority': 'high'},
    {'task': 'Apply fertilizer to Field A','time':'Afternoon','priority': 'medium'},
    {'task': 'Collect eggs',             'time': 'Morning',   'priority': 'low'},
]

# ── Market Prices ─────────────────────────────────────────────────────────────
MARKETS = ['All', 'Nairobi', 'Nakuru', 'Kiambu', 'Meru', 'Kericho', 'Machakos']

MARKET_PRICES = [
    {'crop': 'Maize',    'unit': 'per 90kg bag', 'price': 4500, 'change': 5.2,  'status': 'high',   'market': 'Nairobi'},
    {'crop': 'Beans',    'unit': 'per 90kg bag', 'price': 12000,'change': -2.1, 'status': 'medium', 'market': 'Nairobi'},
    {'crop': 'Tomatoes', 'unit': 'per kg',       'price': 85,   'change': 20.3, 'status': 'high',   'market': 'Nairobi'},
    {'crop': 'Avocado',  'unit': 'per kg',       'price': 120,  'change': 18.5, 'status': 'high',   'market': 'Kiambu'},
    {'crop': 'Onions',   'unit': 'per kg',       'price': 95,   'change': 19.0, 'status': 'high',   'market': 'Nairobi'},
    {'crop': 'Cabbage',  'unit': 'per head',     'price': 35,   'change': -5.0, 'status': 'low',    'market': 'Nakuru'},
    {'crop': 'Tea',      'unit': 'per kg',       'price': 65,   'change': 4.2,  'status': 'medium', 'market': 'Kericho'},
    {'crop': 'Mangoes',  'unit': 'per kg',       'price': 55,   'change': 7.3,  'status': 'medium', 'market': 'Machakos'},
    {'crop': 'Spinach',  'unit': 'per kg',       'price': 35,   'change': -1.5, 'status': 'low',    'market': 'Kiambu'},
    {'crop': 'Potatoes', 'unit': 'per 50kg bag', 'price': 2800, 'change': 3.1,  'status': 'medium', 'market': 'Meru'},
]

MARKET_SUMMARY = {
    'trending_up': 8,
    'trending_down': 3,
    'high_demand': 7,
    'markets': 5,
}

TOP_GAINERS = [
    {'crop': 'Tomatoes', 'price': 'KSh 85',  'change': '+20.3%', 'market': 'Nairobi'},
    {'crop': 'Avocado',  'price': 'KSh 120', 'change': '+18.5%', 'market': 'Kiambu'},
    {'crop': 'Onions',   'price': 'KSh 95',  'change': '+19%',   'market': 'Nairobi'},
]

TOP_LOSERS = [
    {'crop': 'Cabbage', 'price': 'KSh 35',    'change': '-5%',   'market': 'Nakuru'},
    {'crop': 'Beans',   'price': 'KSh 12,000','change': '-2.1%', 'market': 'Nairobi'},
    {'crop': 'Spinach', 'price': 'KSh 35',    'change': '-1.5%', 'market': 'Kiambu'},
]

# 6-week price trend data (in hundreds for display)
PRICE_TRENDS = {
    'weeks':    ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6'],
    'Tomatoes': [55, 60, 65, 70, 78, 85],
    'Onions':   [60, 63, 68, 72, 80, 95],
    'Maize':    [3800, 4000, 4100, 4200, 4350, 4500],
}

# ── Weather Data ──────────────────────────────────────────────────────────────
CURRENT_WEATHER = {
    'location': 'Nairobi',
    'date': 'Tuesday, Feb 4, 2026',
    'time': '2:30 PM',
    'temp': 28,
    'feels_like': 30,
    'condition': 'Partly Cloudy',
    'emoji': '⛅',
    'humidity': 65,
    'wind': 12,
    'rain_chance': 20,
    'uv_index': 7,
}

HOURLY_FORECAST = [
    {'time': '6am',  'temp': 18, 'rain': 5},
    {'time': '9am',  'temp': 22, 'rain': 10},
    {'time': '12pm', 'temp': 27, 'rain': 15},
    {'time': '3pm',  'temp': 28, 'rain': 20},
    {'time': '6pm',  'temp': 25, 'rain': 25},
    {'time': '9pm',  'temp': 21, 'rain': 30},
]

SEVEN_DAY_FORECAST = [
    {'day': 'Mon', 'emoji': '☀️',  'high': 29, 'low': 18, 'rain': 10, 'humidity': 60},
    {'day': 'Tue', 'emoji': '⛅',  'high': 27, 'low': 17, 'rain': 38, 'humidity': 70},
    {'day': 'Wed', 'emoji': '🌧️', 'high': 22, 'low': 16, 'rain': 80, 'humidity': 85},
    {'day': 'Thu', 'emoji': '🌧️', 'high': 21, 'low': 15, 'rain': 75, 'humidity': 88},
    {'day': 'Fri', 'emoji': '⛅',  'high': 24, 'low': 16, 'rain': 30, 'humidity': 72},
    {'day': 'Sat', 'emoji': '☀️',  'high': 27, 'low': 17, 'rain': 8,  'humidity': 58},
    {'day': 'Sun', 'emoji': '☀️',  'high': 29, 'low': 18, 'rain': 5,  'humidity': 55},
]

WEEKLY_RAINFALL = [15, 28, 12, 45]   # mm per week, last 4 weeks

FARM_INSIGHTS = [
    {
        'title': 'Irrigation Planning',
        'desc': 'Rain expected Wed-Thu. Reduce irrigation by 60% for those days.',
        'priority': 'high',
        'icon': '💧',
    },
    {
        'title': 'Pest Control',
        'desc': 'High humidity (80%+) expected mid-week. Monitor crops for fungal diseases.',
        'priority': 'high',
        'icon': '🐛',
    },
    {
        'title': 'Planting Window',
        'desc': 'Excellent conditions for planting after Wednesday\'s rain. Soil moisture will be optimal.',
        'priority': 'medium',
        'icon': '🌱',
    },
    {
        'title': 'UV Protection',
        'desc': 'High UV this weekend. Consider shade for young seedlings and ensure livestock have shade.',
        'priority': 'medium',
        'icon': '☀️',
    },
]

WEATHER_ALERT = {
    'title': '⚠️ Heavy Rain Alert',
    'desc': 'Heavy rainfall expected Wed-Thu (40-60mm). Ensure drainage systems are clear. Protect young seedlings and secure loose farm equipment. Excellent opportunity to collect rainwater for irrigation.',
    'level': 'warning',
}

# ── Tips & Resources ──────────────────────────────────────────────────────────
TIPS_CATEGORIES = ['All', 'Planting', 'Pest Control', 'Irrigation', 'Soil Health', 'Marketing', 'Videos']

TIPS = [
    {
        'id': 1,
        'title': 'Optimal Maize Planting',
        'category': 'Planting',
        'level': 'Beginner',
        'season': 'Long Rains',
        'content': 'Plant maize at the onset of long rains (March-April). Ensure 75cm between rows and 25cm between plants. Use certified seeds and apply DAP fertilizer at planting.',
    },
    {
        'id': 2,
        'title': 'Intercropping Benefits',
        'category': 'Planting',
        'level': 'Intermediate',
        'season': 'All Seasons',
        'content': 'Intercrop beans with maize to maximize land use and improve soil nitrogen. Plant beans 2-3 weeks after maize to prevent competition.',
    },
    {
        'id': 3,
        'title': 'Tomato Nursery Management',
        'category': 'Planting',
        'level': 'Intermediate',
        'season': 'All Seasons',
        'content': 'Start tomato seedlings in trays with good drainage. Transplant when 4-6 weeks old. Ensure proper hardening before transplanting to the main field.',
    },
    {
        'id': 4,
        'title': 'Drip Irrigation Setup',
        'category': 'Irrigation',
        'level': 'Advanced',
        'season': 'Dry Season',
        'content': 'Drip irrigation saves 40-60% water compared to furrow irrigation. Install main line, sub-mains, and laterals. Use pressure regulators to maintain consistent flow.',
    },
    {
        'id': 5,
        'title': 'Fall Armyworm Control',
        'category': 'Pest Control',
        'level': 'Beginner',
        'season': 'Long Rains',
        'content': 'Scout fields every 3 days. Look for egg masses and early instar larvae. Apply recommended pesticides early morning. Use biological controls like Bt for organic farming.',
    },
    {
        'id': 6,
        'title': 'Soil pH Testing',
        'category': 'Soil Health',
        'level': 'Beginner',
        'season': 'All Seasons',
        'content': 'Test soil pH before planting. Most vegetables prefer 6.0-7.0. Apply lime to raise pH and sulphur to lower it. Retest after 3 months for accuracy.',
    },
    {
        'id': 7,
        'title': 'Selling at the Right Time',
        'category': 'Marketing',
        'level': 'Intermediate',
        'season': 'All Seasons',
        'content': 'Monitor FarmConnect market prices daily. Sell when prices are above your target. Avoid selling during gluts (peak harvest of others). Form groups to negotiate better prices.',
    },
]

# ── Community Posts ───────────────────────────────────────────────────────────
COMMUNITY_POSTS = [
    {
        'id': 1,
        'initials': 'JM',
        'name': 'James Mwangi',
        'role': 'Maize Farmer',
        'time': '2 hours ago',
        'tag': 'Success Story',
        'tag_color': '#2E7D32',
        'content': 'Just harvested my first acre of hybrid maize - got 32 bags! 🌽 Thank you to everyone who shared tips on proper spacing and fertilizer application. The results are amazing!',
        'likes': 45,
        'comments': 12,
    },
    {
        'id': 2,
        'initials': 'MW',
        'name': 'Mary Wanjiku',
        'role': 'Dairy Farmer',
        'time': '5 hours ago',
        'tag': 'Question',
        'tag_color': '#1565C0',
        'content': 'Has anyone dealt with mastitis in dairy cows? My Friesian is showing symptoms. Looking for natural remedies before calling the vet. Please help!',
        'likes': 23,
        'comments': 18,
    },
    {
        'id': 3,
        'initials': 'PO',
        'name': 'Peter Omondi',
        'role': 'Vegetable Farmer',
        'time': '1 day ago',
        'tag': 'Market Update',
        'tag_color': '#FF6F00',
        'content': 'Market prices for tomatoes have gone up by 20% this week in Nairobi! 📈 If you\'re planning to harvest soon, now is a great time to sell. I got KSh 85/kg today at Wakulima Market.',
        'likes': 67,
        'comments': 31,
    },
    {
        'id': 4,
        'initials': 'GW',
        'name': 'Grace Wairimu',
        'role': 'Horticulture Farmer',
        'time': '2 days ago',
        'tag': 'Question',
        'tag_color': '#1565C0',
        'content': 'What\'s the best variety of capsicum to grow in Kiambu? I have half an acre ready and want to try something new this season.',
        'likes': 15,
        'comments': 9,
    },
]

TOP_FARMERS = [
    {'initials': 'JK', 'name': 'John Kamau',    'specialty': 'Maize Expert',     'followers': '1,250'},
    {'initials': 'GA', 'name': 'Grace Achieng', 'specialty': 'Dairy Farming',    'followers': '980'},
    {'initials': 'DK', 'name': 'David Kipchoge','specialty': 'Horticulture',     'followers': '856'},
    {'initials': 'RW', 'name': 'Rose Wambui',   'specialty': 'Organic Farming',  'followers': '745'},
]

EVENTS = [
    {
        'title': 'Dairy Farmers Meeting',
        'date': 'Feb 25, 2026',
        'location': 'Nakuru',
        'attendees': 145,
    },
    {
        'title': 'Agribusiness Workshop',
        'date': 'Mar 5, 2026',
        'location': 'Nairobi',
        'attendees': 230,
    },
]

# ── Notifications ─────────────────────────────────────────────────────────────
NOTIFICATIONS = [
    {
        'icon': '📈',
        'title': 'Market Opportunity Alert',
        'desc': 'Tomato and avocado prices are at their peak. Consider selling if you have ready produce.',
        'time': '10 min ago',
        'color': '#FF6F00',
        'unread': True,
    },
    {
        'icon': '🌧️',
        'title': 'Heavy Rain Alert',
        'desc': 'Heavy rainfall expected Wed-Thu (40-60mm). Secure loose equipment and protect seedlings.',
        'time': '1 hour ago',
        'color': '#1565C0',
        'unread': True,
    },
    {
        'icon': '🌱',
        'title': 'Beans Ready for Harvest',
        'desc': 'Your Rose Coco beans in Field B are ready for harvest. Optimal window: next 5-7 days.',
        'time': '3 hours ago',
        'color': '#2E7D32',
        'unread': True,
    },
    {
        'icon': '💬',
        'title': 'New Reply on Your Post',
        'desc': 'Grace Achieng replied to your question about tomato varieties.',
        'time': '5 hours ago',
        'color': '#6A1B9A',
        'unread': False,
    },
    {
        'icon': '💡',
        'title': 'Price Alert Tip',
        'desc': 'Set up price alerts for your crops to get notified when prices reach your target.',
        'time': '1 day ago',
        'color': '#2E7D32',
        'unread': False,
    },
]

# ── Revenue & Expense Trend ───────────────────────────────────────────────────
REVENUE_TREND = {
    'months':   ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'],
    'revenue':  [550, 620, 710, 780, 820, 845],   # in thousands KSh
    'expenses': [320, 350, 380, 420, 450, 480],
}
