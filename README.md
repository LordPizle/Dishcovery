# Dishcovery

Dishcovery is a Flask web app for finding restaurants by craving and location.
It combines Google Places search with a lightweight relevance reranker (TF-IDF + cosine similarity), plus a rule-based chat assistant for quick food suggestions.

## What It Does

- Search restaurants by dish, cuisine, diet, occasion or broad keywords
- Search using:
  - current location (browser geolocation), or
  - typed address/city (geocoded with Photon, with Google fallback)
- Filter by distance, result count, minimum rating, and open-now status
- Sort by distance, rating, or best match
- Rerank with TF-IDF + cosine similarity for "best match" results
- Show place metadata (rating, review count, distance, opening status, photos)
- Use an in-app chat assistant for:
  - keyword-based food guidance
  - nearby restaurant replies when location is available
  - city-aware queries (for example: "sushi in London")

## Project Structure

```text
Dishcovery/
  app/
    __init__.py          # Flask app factory
    routes.py            # Page routes + JSON APIs
    location.py          # Geocoding + Google Places integration
    recommender.py       # TF-IDF/cosine reranker + query expansion
    chat.py              # Rule/keyword chat logic
    templates/           # Jinja templates (index/find_food/about/base)
  static/
    style.css            # App styling
    script.js            # Front-end behavior (search UI, chat, drag/fullscreen)
  requirements.txt
  run.py                 # Local entrypoint
```

## Requirements

- Python 3.10+ recommended
- A Google Places API key (for restaurant search and place photos)

Python dependencies are listed in `requirements.txt`:

- `flask`
- `pandas`
- `numpy`
- `scikit-learn`
- `joblib`
- `requests`

## Quick Start (Windows Git Bash)

1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/Scripts/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set environment variables

```bash
export GOOGLE_PLACES_API_KEY="your_api_key_here"
# Optional (defaults to dishcovery-secret-key if omitted)
export FLASK_SECRET_KEY="your_secret_here"
```

4. Run the app

```bash
python run.py
```

Open `http://localhost:5000`.

## Quick Start (macOS/Linux)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GOOGLE_PLACES_API_KEY="your_api_key_here"
export FLASK_SECRET_KEY="your_secret_here"  # optional
python run.py
```

## API and Routes

### Pages

- `GET /` - Landing page
- `GET|POST /find-food` - Main restaurant search UI
- `GET /about` - App explanation page

### JSON APIs

- `GET /api/address-search?q=...` - Address autocomplete (Photon-backed)
- `POST /api/chat` - Chat assistant endpoint

Example chat request:

```json
{
  "message": "cheap sushi near me",
  "lat": 51.5074,
  "lng": -0.1278
}
```

Notes:

- `/api/chat` is rate-limited in-memory (30 requests per 60 seconds per IP)
- Chat can still respond without `lat/lng`, but nearby search replies are better with location

## How Ranking Works

When you choose **Best match**, Dishcovery reranks results in `app/recommender.py`:

1. Expand query terms with `QUERY_EXPAND` (for example, "bbq" also considers "barbecue grill")
2. Build TF-IDF vectors for:
   - name + place types
   - address text
3. Compute cosine similarity between query and each candidate
4. Combine relevance with distance/rating nudges and sort descending

If `scikit-learn` is unavailable, the app falls back gracefully to the original order.

## Chat Assistant Behavior

The assistant is keyword/pattern-based (no external LLM calls). It can:

- suggest cuisines, dishes, diets, and occasions
- answer app usage questions
- return nearby/city restaurant snippets using the same search pipeline
- include a direct "Open in Find Food" link for follow-up browsing

## Front-End Notes

- Responsive layout for desktop/mobile
- Chat widget supports:
  - open/close
  - clear messages
  - fullscreen mode
  - drag-to-move by holding the chat header bar
  - horizontal resize in fullscreen on larger screens

## Troubleshooting

- "Restaurant search is temporarily unavailable"
  - Check `GOOGLE_PLACES_API_KEY` is set in your current shell
  - Confirm Places API is enabled on your Google Cloud project
- No location results
  - Ensure browser location permission is allowed, or use typed address
- Chat rate-limit message
  - Wait around a minute and retry

## Security and Production Notes

- Current rate limit is in-memory and resets on server restart
- `run.py` runs Flask with `debug=True` for local development
- For production:
  - run behind a WSGI server (gunicorn/waitress/uwsgi)
  - disable debug mode
  - use a strong `FLASK_SECRET_KEY`
  - move rate limiting to shared storage (Redis, etc.) if scaling
