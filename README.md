# Dishcovery

AI-powered food recommendation system. Discover restaurants near you based on what you crave.

## Features

- **Find Food** – Search restaurants by dish or cuisine using your location
- **AI Chat** – Chat with the built-in assistant for cuisine suggestions and dietary tips
- **About** – Learn how the app works
- **Responsive** – Works on desktop and mobile

## Setup

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. Set your Google Places API key:
   ```
   set GOOGLE_PLACES_API_KEY=your_api_key_here
   ```
   Get a key at [Google Cloud Console](https://console.cloud.google.com/apis/credentials).

3. Run the app:
   ```
   python run.py
   ```
   Open http://localhost:5000
