"""FarmConnect - Simplified Web App."""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
from datetime import timedelta

# Import only what exists
from utils.auth import auth
from utils.farm_data import (
    get_farm_crops, add_farm_crop,
    get_farm_tasks, add_farm_task,
    get_farm_records, add_farm_record
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        result = auth.login_with_password(data.get('phone'), data.get('password'))
        
        if result.get('success'):
            session['user'] = result['user']
            session.permanent = True
            return jsonify({'success': True, 'redirect': '/dashboard'})
        return jsonify({'success': False, 'error': result.get('error')})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        result = auth.register_with_password(
            data.get('phone'), 
            data.get('name'), 
            data.get('password')
        )
        
        if result.get('success'):
            session['user'] = result['user']
            session.permanent = True
            return jsonify({'success': True, 'redirect': '/dashboard'})
        return jsonify({'success': False, 'error': result.get('error')})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = session.get('user', {})
    phone = user.get('phone', '')
    
    crops = get_farm_crops(phone)
    records = get_farm_records(phone)
    
    revenue = sum(r['amount'] for r in records if r['type'] == 'income')
    expenses = sum(r['amount'] for r in records if r['type'] == 'expense')
    
    return render_template('dashboard.html',
                         user=user,
                         crops=crops[:5],
                         total_revenue=revenue,
                         total_expenses=expenses,
                         net_income=revenue - expenses,
                         total_crops=len(crops))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
