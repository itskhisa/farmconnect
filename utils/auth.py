"""
FarmConnect - Auth Manager
Supports two modes:
  1. DEMO MODE  (default) - works instantly, no setup needed
  2. FIREBASE   - real SMS OTP (paste your API key below to enable)

To enable Firebase:
  - Replace FIREBASE_API_KEY with your real key from Firebase Console
  - The app auto-detects and switches to real auth
"""

import os
import requests
from datetime import date
from utils.storage import Storage

# SMS/OTP Configuration
# For production, set these environment variables:
# AFRICASTALKING_USERNAME - Your Africa's Talking username
# AFRICASTALKING_API_KEY - Your Africa's Talking API key
# AFRICASTALKING_SENDER - Sender ID (e.g., 'FarmConnect')

import os
AFRICASTALKING_USERNAME = os.environ.get('AFRICASTALKING_USERNAME', '')
AFRICASTALKING_API_KEY = os.environ.get('AFRICASTALKING_API_KEY', '')
AFRICASTALKING_SENDER = os.environ.get('AFRICASTALKING_SENDER', 'FarmConnect')
USE_REAL_OTP = bool(AFRICASTALKING_USERNAME and AFRICASTALKING_API_KEY)

# ── Firebase config (optional) ────────────────────────────────────
# Leave as "YOUR_FIREBASE_WEB_API_KEY" to use Demo Mode
FIREBASE_API_KEY = "YOUR_FIREBASE_WEB_API_KEY"
FIREBASE_BASE    = "https://identitytoolkit.googleapis.com/v1"
FIREBASE_DB_URL  = ""   # e.g. "https://farmconnect-abc.firebaseio.com"
# ─────────────────────────────────────────────────────────────────

SESSION_FILE  = "session.json"
DEMO_OTP_CODE = "123456"   # Fixed OTP code used in demo mode


def _is_demo_mode():
    return (not FIREBASE_API_KEY
            or FIREBASE_API_KEY == "YOUR_FIREBASE_WEB_API_KEY"
            or len(FIREBASE_API_KEY) < 20)


class AuthManager:
    def __init__(self):
        self.storage       = Storage()
        self.current_user  = None
        self.id_token      = None
        self.refresh_token = None
        self._load_session()

    # ── Session ───────────────────────────────────────────────────

    def _load_session(self):
        s = self.storage.load_json(SESSION_FILE)
        if s:
            self.current_user  = s.get("user")
            self.id_token      = s.get("id_token")
            self.refresh_token = s.get("refresh_token")

    def _save_session(self, user, id_token, refresh_token):
        self.current_user  = user
        self.id_token      = id_token
        self.refresh_token = refresh_token
        self.storage.save_json(SESSION_FILE, {
            "user": user, "id_token": id_token, "refresh_token": refresh_token
        })

    def clear_session(self):
        self.current_user  = None
        self.id_token      = None
        self.refresh_token = None
        self.storage.delete(SESSION_FILE)

    def is_logged_in(self):
        return self.current_user is not None and self.id_token is not None

    def is_demo(self):
        return _is_demo_mode()

    # ── Phone formatting ──────────────────────────────────────────

    @staticmethod
    def format_phone(number: str) -> str:
        number = number.strip().replace(" ", "").replace("-", "")
        if number.startswith("+254"):
            return number
        if number.startswith("254"):
            return "+" + number
        if number.startswith("0"):
            return "+254" + number[1:]
        return "+254" + number

    # ── Step 1: Send OTP ──────────────────────────────────────────

    def send_otp(self, phone_number: str) -> dict:
        formatted = self.format_phone(phone_number)

        if _is_demo_mode():
            # Demo: always succeeds, OTP is always 123456
            return {
                "success":      True,
                "session_info": f"DEMO:{formatted}",
                "phone":        formatted,
                "demo":         True,
            }

        # Real Firebase
        url = f"{FIREBASE_BASE}/accounts:sendVerificationCode?key={FIREBASE_API_KEY}"
        try:
            resp = requests.post(url, json={
                "phoneNumber":    formatted,
                "recaptchaToken": "faketoken",
            }, timeout=10)
            data = resp.json()
            if "sessionInfo" in data:
                return {"success": True,
                        "session_info": data["sessionInfo"],
                        "phone": formatted,
                        "demo": False}
            err = data.get("error", {}).get("message", "Unknown error")
            return {"success": False, "error": err}
        except requests.RequestException as e:
            return {"success": False, "error": f"Network error: {e}"}

    # ── Step 2: Verify OTP ────────────────────────────────────────

    def verify_otp(self, session_info: str, otp_code: str,
                   name: str = "", phone: str = "") -> dict:

        # Demo mode verification
        if session_info.startswith("DEMO:"):
            if otp_code == DEMO_OTP_CODE:
                uid  = f"demo_{phone.replace('+','').replace(' ','')}"
                user = {
                    "uid":       uid,
                    "phone":     phone,
                    "name":      name or "Farmer",
                    "joined":    date.today().strftime("%d %b %Y"),
                    "location":  "Kenya",
                    "farm_type": "",
                    "demo":      True,
                }
                self._save_session(user, f"demo_token_{uid}", "demo_refresh")
                return {"success": True, "user": user}
            else:
                return {"success": False,
                        "error": f"Wrong code. Demo code is {DEMO_OTP_CODE}"}

        # Real Firebase verification
        url = f"{FIREBASE_BASE}/accounts:signInWithPhoneNumber?key={FIREBASE_API_KEY}"
        try:
            resp = requests.post(url, json={
                "sessionInfo": session_info,
                "code":        otp_code,
            }, timeout=10)
            data = resp.json()
            if "idToken" in data:
                uid  = data.get("localId", "")
                user = {
                    "uid":       uid,
                    "phone":     phone or data.get("phoneNumber", ""),
                    "name":      name,
                    "joined":    date.today().strftime("%d %b %Y"),
                    "location":  "Kenya",
                    "farm_type": "",
                    "demo":      False,
                }
                self._save_profile(uid, user, data["idToken"])
                self._save_session(user, data["idToken"],
                                   data.get("refreshToken", ""))
                return {"success": True, "user": user}
            err = data.get("error", {}).get("message", "Invalid OTP")
            return {"success": False, "error": err}
        except requests.RequestException as e:
            return {"success": False, "error": f"Network error: {e}"}

    # ── Delete account ────────────────────────────────────────────

    def delete_account(self) -> dict:
        if not self.current_user:
            return {"success": False, "error": "Not logged in"}

        if self.current_user.get("demo"):
            self.clear_session()
            return {"success": True}

        if not self.id_token:
            return {"success": False, "error": "Not logged in"}

        url = f"{FIREBASE_BASE}/accounts:delete?key={FIREBASE_API_KEY}"
        try:
            uid = self.current_user.get("uid", "")
            if uid and FIREBASE_DB_URL:
                requests.delete(
                    f"{FIREBASE_DB_URL}/users/{uid}.json?auth={self.id_token}",
                    timeout=10,
                )
            resp = requests.post(url, json={"idToken": self.id_token}, timeout=10)
            if resp.status_code == 200:
                self.clear_session()
                return {"success": True}
            err = resp.json().get("error", {}).get("message", "Delete failed")
            return {"success": False, "error": err}
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    # ── Helpers ───────────────────────────────────────────────────

    def _save_profile(self, uid, profile, id_token):
        if not FIREBASE_DB_URL:
            return
        try:
            requests.put(
                f"{FIREBASE_DB_URL}/users/{uid}.json?auth={id_token}",
                json=profile, timeout=10,
            )
        except Exception:
            pass

    def get_profile(self):
        return self.current_user or {}

    def update_profile(self, updates: dict) -> bool:
        if not self.current_user:
            return False
        self.current_user.update(updates)
        self._save_session(self.current_user, self.id_token, self.refresh_token)
        if not self.current_user.get("demo") and self.id_token and FIREBASE_DB_URL:
            uid = self.current_user.get("uid", "")
            try:
                requests.patch(
                    f"{FIREBASE_DB_URL}/users/{uid}.json?auth={self.id_token}",
                    json=updates, timeout=10,
                )
            except Exception:
                pass
        return True

    
    def register_with_password(self, phone: str, name: str, password: str) -> dict:
        """Register with password."""
        from datetime import datetime
        import hashlib
        
        if not phone or len(phone) < 10:
            return {"success": False, "error": "Invalid phone"}
        if not name or len(name) < 2:
            return {"success": False, "error": "Name required"}
        if not password or len(password) < 6:
            return {"success": False, "error": "Password must be 6+ characters"}
        
        s = Storage()
        if s.load_json(f"user_{phone}.json"):
            return {"success": False, "error": "Account exists"}
        
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = {
            "phone": phone,
            "uid": f"user_{phone}",
            "name": name,
            "joined": datetime.now().strftime("%b %Y"),
            "counties": []
        }
        
        s.save_json(f"user_{phone}.json", {
            "user": user,
            "password_hash": pwd_hash
        })
        
        return {"success": True, "user": user}
    
    def login_with_password(self, phone: str, password: str) -> dict:
        """Login with password."""
        if not phone or not password:
            return {"success": False, "error": "Phone and password required"}
        
        s = Storage()
        data = s.load_json(f"user_{phone}.json")
        
        if not data:
            return {"success": False, "error": "Account not found"}
        
        import hashlib
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if data.get('password_hash') != pwd_hash:
            return {"success": False, "error": "Incorrect password"}
        
        return {"success": True, "user": data.get('user', {})}

    def cleanup_expired_accounts(self) -> dict:
        """Permanently delete accounts past 30-day grace period."""
        from datetime import datetime
        s = Storage()
        
        deletion_queue = s.load_json('deletion_queue.json') or {'accounts': []}
        now = datetime.now()
        
        deleted_count = 0
        remaining = []
        
        for acc in deletion_queue['accounts']:
            try:
                delete_date = datetime.fromisoformat(acc['delete_after'])
                if now > delete_date:
                    # Permanently delete this account's data
                    phone = acc.get('phone', '')
                    if phone:
                        # Delete all user data files
                        for filename in [f'{phone}_farm_crops.json', f'{phone}_farm_livestock.json',
                                       f'{phone}_farm_tasks.json', f'{phone}_farm_records.json']:
                            s.delete(filename)
                    deleted_count += 1
                else:
                    # Still within grace period
                    remaining.append(acc)
            except Exception:
                remaining.append(acc)
        
        # Update deletion queue
        deletion_queue['accounts'] = remaining
        s.save_json('deletion_queue.json', deletion_queue)
        
        return {"success": True, "deleted": deleted_count, "remaining": len(remaining)}


# Singleton instance
auth = AuthManager()
