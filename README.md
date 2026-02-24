# FarmConnect Web Application

A web-based farm management system for Kenyan farmers.

## Features
- Password authentication (no OTP needed)
- Farm management (crops, livestock, tasks, records)
- Market prices across 47 Kenyan counties
- Weather forecasts
- Community forum
- Financial tracking

## Deploy to Render

1. Create account on [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Render will auto-detect settings from `render.yaml`
5. Click "Create Web Service"
6. Done! Your app will be live at: `https://farmconnect-xxxx.onrender.com`

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Visit: http://localhost:5000

## Environment Variables (Render Dashboard)

- `SECRET_KEY`: Auto-generated (for sessions)
- `PORT`: Auto-set by Render

## First Time Setup

1. Go to your deployed URL
2. Click "Register"
3. Create account (phone + password)
4. Select your counties
5. Start farming! 🌾

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JS
- **Database**: JSON files (file-based storage)
- **Deployment**: Render
- **No mobile build required** - works in any browser!
