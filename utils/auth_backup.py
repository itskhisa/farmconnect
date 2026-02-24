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

    # ── Step 1: Login with Password ──────────────────────────────────────────

    def login_with_password(self, phone_number: str, password: str) -> dict:
        """Login with phone and password."""
        if not phone_number or len(phone_number) < 10:
            return {"success": False, "error": "Invalid phone number"}
        
        if not password:
            return {"success": False, "error": "Password required"}
        
        # Load stored password
        s = Storage()
        stored = s.load_json(f"user_{phone_number}.json")
        
        if not stored:
            return {"success": False, "error": "Account not found. Please register."}
        
        # Verify password (in production, use bcrypt or similar)
        import hashlib
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        
        if stored.get('password_hash') != hashed_input:
            return {"success": False, "error": "Incorrect password"}
        
        # Return user data
        user_data = stored.get('user', {})
        user_data['phone'] = phone_number
        
        return {"success": True, "user": user_data}
    
    def register_with_password(self, phone_number: str, name: str, password: str) -> dict:
        """Register new user with password."""
        if not phone_number or len(phone_number) < 10:
            return {"success": False, "error": "Invalid phone number"}
        
        if not name or len(name) < 2:
            return {"success": False, "error": "Name required"}
        
        if not password or len(password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        # Check if user exists
        s = Storage()
        existing = s.load_json(f"user_{phone_number}.json")
        if existing:
            return {"success": False, "error": "Account already exists. Please login."}
        
        # Hash password
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user
        user_data = {
            "phone": phone_number,
            "uid": f"user_{phone_number}",
            "name": name,
            "joined": datetime.now().strftime("%b %Y"),
            "demo": False
        }
        
        # Save
        s.save_json(f"user_{phone_number}.json", {
            "user": user_data,
            "password_hash": password_hash,
            "created_at": datetime.now().isoformat()
        })
        
        return {"success": True, "user": user_data}
    
    def send_otp(self, phone_number: str) -> dict:
        """Send OTP via SMS for password reset only."""
        if not phone_number or len(phone_number) < 10:
            return {"success": False, "error": "Invalid phone number"}
        
        # Check if user exists
        s = Storage()
        user_data = s.load_json(f"user_{phone_number}.json")
        if not user_data:
            return {"success": False, "error": "Account not found"}
        
        # Generate 6-digit OTP
        import random
        otp_code = str(random.randint(100000, 999999))
        
        # Store OTP for verification
        s.save_json(f"otp_{phone_number}.json", {
            "code": otp_code,
            "created_at": datetime.now().isoformat(),
            "verified": False,
            "attempts": 0,
            "purpose": "password_reset"
        })
        
        if USE_REAL_OTP:
            # Send real SMS
            try:
                import africastalking
                africastalking.initialize(AFRICASTALKING_USERNAME, AFRICASTALKING_API_KEY)
                sms = africastalking.SMS
                
                if phone_number.startswith('0'):
                    phone_number = '+254' + phone_number[1:]
                
                message = f"Your FarmConnect password reset code is: {otp_code}. Valid for 10 minutes."
                response = sms.send(message, [phone_number], AFRICASTALKING_SENDER)
                
                return {"success": True, "message": "OTP sent via SMS"}
            except Exception:
                return {"success": True, "message": "SMS unavailable. Demo OTP: 123456", "demo_otp": "123456"}
        else:
            # Demo mode
            return {"success": True, "message": "Demo mode: Use OTP 123456", "demo_otp": "123456"}

        def verify_otp_and_reset_password(self, phone_number: str, otp_code: str, new_password: str) -> dict:
        """Verify OTP and reset password."""
        from datetime import datetime, timedelta
        
        s = Storage()
        stored = s.load_json(f"otp_{phone_number}.json")
        
        if not stored:
            return {"success": False, "error": "No OTP found. Request a new one."}
        
        if stored.get("verified"):
            return {"success": False, "error": "OTP already used."}
        
        # Check expiry (10 minutes)
        try:
            created = datetime.fromisoformat(stored.get("created_at"))
            if datetime.now() - created > timedelta(minutes=10):
                s.delete(f"otp_{phone_number}.json")
                return {"success": False, "error": "OTP expired."}
        except Exception:
            pass
        
        # Check attempts
        attempts = stored.get("attempts", 0)
        if attempts >= 5:
            s.delete(f"otp_{phone_number}.json")
            return {"success": False, "error": "Too many attempts."}
        
        # Verify code
        if stored.get("code") != otp_code:
            stored["attempts"] = attempts + 1
            s.save_json(f"otp_{phone_number}.json", stored)
            return {"success": False, "error": f"Invalid OTP. {5 - stored['attempts']} attempts remaining."}
        
        # OTP verified - reset password
        if not new_password or len(new_password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters"}
        
        import hashlib
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        user_data = s.load_json(f"user_{phone_number}.json")
        if not user_data:
            return {"success": False, "error": "User not found"}
        
        user_data['password_hash'] = password_hash
        s.save_json(f"user_{phone_number}.json", user_data)
        
        # Mark OTP as used
        stored["verified"] = True
        s.save_json(f"otp_{phone_number}.json", stored)
        
        return {"success": True, "message": "Password reset successfully"}

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
