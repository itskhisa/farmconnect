"""
FarmConnect - Farmer's Personal Data Store
All data is saved locally and tied to the logged-in farmer.
Crops, livestock, tasks, records, community posts — all real, all persistent.
"""

from datetime import datetime, timedelta
from utils.storage import Storage

def _get_user_id():
    """Get current user's unique identifier for data isolation."""
    from utils.auth import auth
    user = auth.current_user
    if not user:
        return "guest"
    # Use phone number as unique ID (or uid if available)
    return user.get('phone', user.get('uid', 'guest')).replace('+', '')

def _user_file(base_name):
    """Generate user-specific filename."""
    user_id = _get_user_id()
    return f"{user_id}_{base_name}"

_s = Storage()

# ── File names (user-specific) ────────────────────────────────────
def _files():
    return {
        'crops': _user_file("farm_crops.json"),
        'livestock': _user_file("farm_livestock.json"),
        'tasks': _user_file("farm_tasks.json"),
        'records': _user_file("farm_records.json"),
    }

CROPS_FILE      = lambda: _files()['crops']
LIVESTOCK_FILE  = lambda: _files()['livestock']
TASKS_FILE      = lambda: _files()['tasks']
RECORDS_FILE    = lambda: _files()['records']
COMMUNITY_FILE  = "community_posts.json"  # Shared across all users

# ── Kenyan crop varieties database ───────────────────────────────
CROP_VARIETIES = {
    "Maize": ["H614D (Hybrid)", "H6213 (Hybrid)", "H5217 (Hybrid)",
              "DK8031 (Pioneer)", "SC403 (Seed Co)", "DUMA 43 (Monsanto)",
              "WH507 (Open Pollinated)", "Katumani (Drought Tolerant)"],
    "Beans": ["Rose Coco (Rosecoco)", "Canadian Wonder", "Mwitemania",
              "Lyamungu 85", "Jesca (Climbing)", "Faida (Bush)",
              "GLP-2 (Climbing)", "Selian 97B"],
    "Tomatoes": ["Tengeru 97", "Rio Grande", "Cal-J (Californian Jack)",
                 "Money Maker", "Anna F1", "Lycopersico F1",
                 "Prostar F1", "Bramble F1"],
    "Potatoes": ["Shangi", "Tigoni", "Kenya Mpya", "Dutch Robjin",
                 "Asante", "Unica", "Markies", "Panamera"],
    "Wheat": ["Eagle 10", "Fahari", "Duma", "Kenya Fahari",
              "Njoro BW1", "Kenya Swara", "Kwale"],
    "Tea": ["TRFK 6/8", "TRFK 31/8", "AHP S15/10", "BBK35",
            "SFS150", "TRFK 303/577", "Purple Tea"],
    "Coffee": ["Ruiru 11 (SL)", "Batian", "K7 (SL28)", "SL34",
               "Blue Mountain", "Catuai"],
    "Avocado": ["Hass", "Fuerte", "Jumbo", "Pinkerton", "Reed",
                "GEM", "Nabal"],
    "Sorghum": ["Gadam", "Serena", "E-1291", "Seredo", "KARI Mtama 1"],
    "Cassava": ["Migyera", "Tajirika", "Kibanda Meno", "Karembo"],
    "Sugarcane": ["Co 421", "N14", "N19", "EAC0119"],
    "Rice": ["Komboka", "IR2793-80-1", "Basmati 370", "TXD-306"],
    "Onions": ["Red Creole", "Jambar F1", "Bombay Red", "Red Pinoy F1"],
    "Cabbage": ["Gloria F1", "Pruktor F1", "Oxylus F1", "Copenhagen Market"],
    "Spinach": ["Texas Savoy", "Malabar", "New Zealand", "Bloomsdale"],
    "Bananas": ["Williams", "Grand Nain", "Cavendish", "Gros Michel",
                "Pisang Awak (Bokoboko)", "Muraru"],
    "Mangoes": ["Apple", "Tommy Atkins", "Kent", "Keitt", "Ngowe", "Boribo"],
    "Milk": ["Friesian (Holstein)", "Ayrshire", "Jersey", "Guernsey",
             "Sahiwal (Local)", "Crossbreed"],
    "Fish": ["Tilapia (Nile)", "Catfish (African)", "Trout (Rainbow)",
             "Common Carp"],
}

CROP_EMOJIS = {
    "Maize":"🌽","Beans":"🫘","Tomatoes":"🍅","Potatoes":"🥔","Wheat":"🌾",
    "Tea":"🍵","Coffee":"☕","Avocado":"🥑","Sorghum":"🌾","Cassava":"🥕",
    "Sugarcane":"🎋","Rice":"🍚","Onions":"🧅","Cabbage":"🥬","Spinach":"🥬",
    "Bananas":"🍌","Mangoes":"🥭","Milk":"🥛","Fish":"🐟","Other":"🌱",
}

LIVESTOCK_TYPES = {
    "Dairy Cows": {"emoji":"🐄","breeds":["Friesian (Holstein)","Ayrshire","Jersey",
                                          "Sahiwal","Crossbreed"]},
    "Beef Cattle": {"emoji":"🐂","breeds":["Boran","Zebu","Hereford","Aberdeen Angus",
                                           "Crossbreed"]},
    "Goats":      {"emoji":"🐐","breeds":["Boer","Galla (Somali)","Toggenburg",
                                          "Saanen","East African Goat"]},
    "Sheep":      {"emoji":"🐑","breeds":["Dorper","Red Maasai","Merino","Hampshire"]},
    "Poultry":    {"emoji":"🐔","breeds":["Kienyeji (Indigenous)","Kari Improved",
                                          "Broiler (Cobb 500)","Layer (ISA Brown)",
                                          "Roadrunner"]},
    "Pigs":       {"emoji":"🐷","breeds":["Large White","Landrace","Duroc","Crossbreed"]},
    "Rabbits":    {"emoji":"🐇","breeds":["New Zealand White","California White",
                                          "Kenya White","Chinchilla"]},
    "Bees":       {"emoji":"🐝","breeds":["African Honey Bee","Langstroth Hive",
                                          "Kenyan Top Bar Hive"]},
    "Fish":       {"emoji":"🐟","breeds":["Tilapia","Catfish","Trout","Common Carp"]},
}

TASK_CATEGORIES = ["Planting","Irrigation","Fertilizing","Pesticides",
                   "Weeding","Harvesting","Livestock Care","Record Keeping","Other"]

STATUS_OPTIONS = ["growing","flowering","ready","harvested","poor"]

# Realistic days from planting/preparation to harvest for Kenyan crops
# For annual crops: planting to harvest
# For perennial crops: cycle time between harvests (after establishment)
CROP_MATURITY_DAYS = {
    "Maize": {"short": 90, "medium": 120, "long": 150, "default": 110},       # 3-5 months
    "Beans": {"short": 60, "medium": 75, "long": 90, "default": 70},          # 2-3 months
    "Tomatoes": {"short": 60, "medium": 75, "long": 90, "default": 75},       # 2-3 months
    "Potatoes": {"short": 90, "medium": 105, "long": 120, "default": 100},    # 3-4 months
    "Wheat": {"short": 90, "medium": 110, "long": 130, "default": 110},       # 3-4 months
    "Tea": {"short": 14, "medium": 21, "long": 28, "default": 21},            # 2-4 weeks between plucking (established bushes)
    "Coffee": {"short": 150, "medium": 180, "long": 210, "default": 180},     # 6 months flowering to ripe cherries
    "Avocado": {"short": 150, "medium": 180, "long": 210, "default": 180},    # 6 months flowering to mature fruit
    "Sorghum": {"short": 90, "medium": 110, "long": 130, "default": 105},     # 3-4 months
    "Cassava": {"short": 270, "medium": 300, "long": 365, "default": 300},    # 10-12 months
    "Sugarcane": {"short": 300, "medium": 365, "long": 450, "default": 365},  # 12 months
    "Rice": {"short": 90, "medium": 120, "long": 150, "default": 120},        # 3-5 months
    "Onions": {"short": 75, "medium": 105, "long": 135, "default": 105},      # 3-4 months
    "Cabbage": {"short": 60, "medium": 75, "long": 90, "default": 70},        # 2-3 months
    "Spinach": {"short": 30, "medium": 45, "long": 60, "default": 40},        # 1-2 months
    "Bananas": {"short": 270, "medium": 300, "long": 365, "default": 300},    # 10-12 months for first bunch
    "Mangoes": {"short": 120, "medium": 150, "long": 180, "default": 150},    # 5 months flowering to ripe (established tree)
    "Milk": {"short": 1, "medium": 1, "long": 1, "default": 1},               # Daily (not a crop)
    "Fish": {"short": 150, "medium": 180, "long": 210, "default": 180},       # 6 months to market size
    "Other": {"short": 60, "medium": 90, "long": 120, "default": 90},         # Default for custom crops
}

def get_crop_maturity_suggestion(crop_name):
    """Get typical maturity days for a crop."""
    info = CROP_MATURITY_DAYS.get(crop_name, {"default": 90})
    default = info["default"]
    short = info.get("short", default - 20)
    long = info.get("long", default + 20)
    return {
        "default": default,
        "range": f"{short}-{long} days",
        "short": short,
        "long": long,
    }


# ── CRUD helpers ──────────────────────────────────────────────────

def _now():
    return datetime.now().isoformat()

def _today():
    return datetime.now().strftime("%d/%m/%Y")

def _uid():
    import time
    return str(int(time.time() * 1000))

# ── Crops ─────────────────────────────────────────────────────────

def get_crops():
    d = _s.load_json(CROPS_FILE())
    return d.get("crops", []) if d else []

def save_crops(crops):
    _s.save_json(CROPS_FILE(), {"crops": crops, "updated": _now()})

def add_crop(name, variety, field, area_acres, planted_date, expected_days):
    crops = get_crops()
    harvest_dt = (datetime.strptime(planted_date, "%d/%m/%Y")
                  + timedelta(days=int(expected_days)))
    crop = {
        "id":            _uid(),
        "name":          name,
        "emoji":         CROP_EMOJIS.get(name, "🌱"),
        "variety":       variety,
        "field":         field,
        "area":          float(area_acres),
        "status":        "growing",
        "planted":       planted_date,
        "expected_days": int(expected_days),
        "expected_date": harvest_dt.strftime("%d/%m/%Y"),
        "notes":         "",
        "created":       _now(),
    }
    crops.append(crop)
    save_crops(crops)
    return crop

def update_crop(crop_id, updates):
    crops = get_crops()
    for c in crops:
        if c["id"] == crop_id:
            c.update(updates)
            break
    save_crops(crops)

def delete_crop(crop_id):
    crops = [c for c in get_crops() if c["id"] != crop_id]
    save_crops(crops)

def days_to_harvest(crop):
    try:
        h = datetime.strptime(crop["expected_date"], "%d/%m/%Y")
        return max(0, (h - datetime.now()).days)
    except Exception:
        return 0

# ── Livestock ─────────────────────────────────────────────────────

def get_livestock():
    d = _s.load_json(LIVESTOCK_FILE())
    return d.get("livestock", []) if d else []

def save_livestock(lst):
    _s.save_json(LIVESTOCK_FILE(), {"livestock": lst, "updated": _now()})

def add_livestock(animal_type, breed, count, notes=""):
    lst = get_livestock()
    item = {
        "id":      _uid(),
        "type":    animal_type,
        "emoji":   LIVESTOCK_TYPES.get(animal_type, {}).get("emoji", "🐾"),
        "breed":   breed,
        "count":   int(count),
        "notes":   notes,
        "created": _now(),
    }
    lst.append(item)
    save_livestock(lst)
    return item

def delete_livestock(lsid):
    lst = [l for l in get_livestock() if l["id"] != lsid]
    save_livestock(lst)

# ── Tasks ─────────────────────────────────────────────────────────

def get_tasks():
    d = _s.load_json(TASKS_FILE())
    return d.get("tasks", []) if d else []

def save_tasks(tasks):
    _s.save_json(TASKS_FILE(), {"tasks": tasks, "updated": _now()})

def add_task(title, category, due_date, priority="medium", crop_id=None, notes=""):
    tasks = get_tasks()
    task = {
        "id":       _uid(),
        "title":    title,
        "category": category,
        "due":      due_date,
        "priority": priority,
        "done":     False,
        "crop_id":  crop_id,
        "notes":    notes,
        "created":  _now(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task

def complete_task(task_id):
    tasks = get_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            t["completed_at"] = _now()
            break
    save_tasks(tasks)

def delete_task(task_id):
    tasks = [t for t in get_tasks() if t["id"] != task_id]
    save_tasks(tasks)

def get_todays_tasks():
    today = _today()
    tasks = get_tasks()
    return [t for t in tasks if not t.get("done") and t.get("due") == today]

def get_pending_tasks():
    tasks = get_tasks()
    return [t for t in tasks if not t.get("done")]

# ── Records (sales/expenses) ──────────────────────────────────────

def get_records():
    d = _s.load_json(RECORDS_FILE())
    return d.get("records", []) if d else []

def save_records(records):
    _s.save_json(RECORDS_FILE(), {"records": records, "updated": _now()})

def add_record(record_type, amount, description, date=None, crop=None):
    records = get_records()
    record = {
        "id":          _uid(),
        "type":        record_type,   # "income" or "expense"
        "amount":      float(amount),
        "description": description,
        "date":        date or _today(),
        "crop":        crop or "",
        "created":     _now(),
    }
    records.append(record)
    save_records(records)
    return record

def get_total_revenue():
    return sum(r["amount"] for r in get_records() if r["type"] == "income")

def get_total_expenses():
    return sum(r["amount"] for r in get_records() if r["type"] == "expense")

# ── Computed farm stats ────────────────────────────────────────────

def get_farm_stats():
    crops   = get_crops()
    lst     = get_livestock()
    records = get_records()

    active_crops = [c for c in crops if c.get("status") not in ("harvested",)]
    total_area   = sum(c.get("area", 0) for c in crops)
    revenue      = sum(r["amount"] for r in records if r["type"] == "income")
    expenses     = sum(r["amount"] for r in records if r["type"] == "expense")

    # Upcoming harvests (next 60 days, not yet harvested)
    upcoming = []
    for c in active_crops:
        d = days_to_harvest(c)
        if d <= 90:
            upcoming.append({
                "crop":   c["name"],
                "variety":c.get("variety",""),
                "days":   d,
                "date":   c.get("expected_date",""),
                "status": "ready" if d <= 7 else ("soon" if d <= 21 else "growing"),
            })
    upcoming.sort(key=lambda x: x["days"])

    return {
        "active_crops":   len(active_crops),
        "total_area":     round(total_area, 1),
        "total_livestock":sum(l.get("count",0) for l in lst),
        "revenue":        revenue,
        "expenses":       expenses,
        "net_income":     revenue - expenses,
        "upcoming":       upcoming[:5],
        "todays_tasks":   get_todays_tasks(),
        "pending_tasks":  get_pending_tasks(),
    }

# ── Community posts ───────────────────────────────────────────────

def get_posts():
    d = _s.load_json(COMMUNITY_FILE)
    return d.get("posts", []) if d else []

def save_posts(posts):
    _s.save_json(COMMUNITY_FILE, {"posts": posts, "updated": _now()})

def add_post(author_name, author_phone, text, county=""):
    posts = get_posts()
    from datetime import datetime
    post = {
        "id":        _uid(),
        "author":    author_name,
        "phone":     author_phone,
        "initials":  (author_name[:1] + (author_name.split()[-1][:1] if len(author_name.split())>1 else "")).upper(),
        "text":      text,
        "county":    county,
        "likes":     0,
        "liked_by":  [],
        "time":      datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "timestamp": _now(),
    }
    posts.insert(0, post)   # newest first
    save_posts(posts)
    return post

def like_post(post_id, phone):
    posts = get_posts()
    for p in posts:
        if p["id"] == post_id:
            if phone not in p.get("liked_by", []):
                p.setdefault("liked_by", []).append(phone)
                p["likes"] = len(p["liked_by"])
            break
    save_posts(posts)
