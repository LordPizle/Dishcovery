"""Rerank restaurants by relevance to the user's query using TF-IDF and cosine similarity."""

import math

# Simple query expansion: add related terms so we don't miss places that use different words
QUERY_EXPAND = {
    "vegan": "vegan vegetarian plant based",
    "vegetarian": "vegetarian vegan",
    "halal": "halal",
    "gluten free": "gluten free gf",
    "gluten-free": "gluten free gf",
    "gf": "gluten free",
    "bbq": "bbq barbecue grill",
    "barbecue": "barbecue bbq",
    "coffee": "coffee cafe",
    "cafe": "cafe coffee",
    "breakfast": "breakfast brunch",
    "brunch": "brunch breakfast",
    "pizza": "pizza italian",
    "sushi": "sushi japanese",
    "burger": "burger burgers",
    "tacos": "tacos mexican",
    "indian": "indian curry",
    "chinese": "chinese dim sum",
    "thai": "thai",
    "italian": "italian pizza pasta",
    "healthy": "healthy salad",
    "cheap": "cheap budget",
    "open now": "open",
    "ramen": "ramen noodles japanese",
    "noodles": "noodles ramen asian",
    "steak": "steak grill steakhouse",
    "dessert": "dessert cake sweet bakery",
    "cake": "cake dessert bakery",
    "mexican": "mexican tacos burrito",
    "korean": "korean bbq kimchi",
    "japanese": "japanese sushi ramen",
    "seafood": "seafood fish",
    "fish": "fish seafood",
    "wings": "wings chicken",
    "sandwich": "sandwich deli subs",
    "salad": "salad healthy",
    "curry": "curry indian thai",
    "mediterranean": "mediterranean greek middle eastern",
    "greek": "greek mediterranean",
    "french": "french bistro",
    "vietnamese": "vietnamese pho",
    "pho": "pho vietnamese noodles",
    "dim sum": "dim sum chinese dumplings",
    "dumplings": "dumplings dim sum",
    "fried chicken": "fried chicken",
    "comfort food": "comfort food pub",
    "pub": "pub food",
    "bakery": "bakery bread pastries",
    "late night": "late night open",
    "date night": "date night romantic",
    "family": "family friendly kids",
    "kid friendly": "family friendly kids",
    "open late": "open late night",
    "fine dining": "fine dining restaurant",
    "buffet": "buffet all you can eat",
    "spanish": "spanish tapas paella",
    "tapas": "tapas spanish",
    "paella": "paella spanish",
    "british": "british fish chips pub",
    "fish and chips": "fish chips british",
    "american": "american burger diner",
    "turkish": "turkish kebab",
    "kebab": "kebab turkish middle eastern",
    "middle eastern": "middle eastern kebab falafel",
    "lebanese": "lebanese mediterranean",
    "moroccan": "moroccan",
    "ethiopian": "ethiopian",
    "nigerian": "nigerian african",
    "caribbean": "caribbean",
    "brazilian": "brazilian",
    "peruvian": "peruvian ceviche",
    "indonesian": "indonesian",
    "malaysian": "malaysian",
    "pakistani": "pakistani indian",
    "bangladeshi": "bangladeshi indian",
    "lunch": "lunch sandwich salad",
    "dinner": "dinner restaurant",
    "quick bite": "quick bite sandwich cafe",
    "takeaway": "takeaway take away",
    "delivery": "delivery takeaway",
    "spicy": "spicy hot",
    "keto": "keto low carb",
    "dairy free": "dairy free vegan",
    "pescatarian": "pescatarian seafood fish",
    "ice cream": "ice cream dessert gelato",
    "bubble tea": "bubble tea boba",
    "boba": "boba bubble tea",
    "smoothie": "smoothie juice",
    "juice": "juice smoothie",
    "wine": "wine bar",
    "beer": "beer pub brewery",
    "pasta": "pasta italian",
    "risotto": "risotto italian",
    "burrito": "burrito mexican",
    "falafel": "falafel middle eastern",
    "shawarma": "shawarma kebab",
    "gyro": "gyro greek",
    "bao": "bao dim sum chinese",
    "udon": "udon noodles japanese",
    "tempura": "tempura japanese",
    "ceviche": "ceviche peruvian seafood",
    "pierogi": "pierogi polish",
    "bagel": "bagel breakfast",
    "croissant": "croissant bakery french",
    "pancakes": "pancakes breakfast",
    "waffles": "waffles breakfast brunch",
    "pad thai": "pad thai thai noodles",
    "biryani": "biryani indian",
    "poke": "poke hawaiian",
    "mac and cheese": "mac cheese comfort",
    "street food": "street food",
    "food truck": "food truck street",
    "romantic": "romantic date night",
    "celebration": "celebration fine dining",
    "birthday": "birthday celebration",
    "group": "group family",
    "rooftop": "rooftop",
    "outdoor": "outdoor terrace garden",
    "organic": "organic healthy",
    "local": "local",
    "cheap eats": "cheap budget",
    "budget": "budget cheap",
}


def _expand_query(query):
    """Add related terms to the query so more places match."""
    if not query or not query.strip():
        return query.strip()
    q = query.lower().strip()
    out = [q]
    for key, extra in QUERY_EXPAND.items():
        if key in q:
            out.append(extra)
    return " ".join(out)


def _doc_parts(r):
    """Name+types (for relevance) and address (for location context)."""
    name = (r.get("name") or "") or ""
    types = r.get("types") or []
    types_str = " ".join(str(t) for t in types)
    address = (r.get("address") or "") or ""
    name_part = " ".join(filter(None, [name, types_str]))
    return name_part.strip(), (address or "").strip()


def _norm_distance(distance_km):
    """Turn distance into a 0-1 score (closer = higher)."""
    if distance_km is None:
        return 0.0
    return max(0.0, 1.0 - (float(distance_km) / 20.0))


def _norm_rating(rating):
    """Turn rating into 0-1 (higher = better)."""
    if rating is None:
        return 0.0
    return float(rating) / 5.0


def rerank_restaurants_by_query(restaurants, query):
    """
    Rerank restaurants by similarity of (name + types) and address to the query,
    with tie-breaking by distance and rating. Uses TF-IDF and cosine similarity.
    """
    if not restaurants:
        return list(restaurants)

    query = (query or "").strip()
    if not query:
        return list(restaurants)

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        return list(restaurants)

    expanded = _expand_query(query)
    if not expanded:
        return list(restaurants)

    # Build documents: name+types (weighted more) and address (weighted less).
    # Append the original query once so the query terms appear in every doc and we avoid empty docs.
    name_docs = []
    address_docs = []
    for r in restaurants:
        name_part, address_part = _doc_parts(r)
        # Ensure we have something to vectorize; append query so at least query terms exist
        name_docs.append((name_part or "") + " " + query)
        address_docs.append((address_part or "") + " " + query)

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            token_pattern=r"(?u)\b\w+\b",
            sublinear_tf=True,
            max_features=8000,
            min_df=1,
            max_df=0.95,
        )
        # Name+types similarity (weight 0.7)
        X_name = vectorizer.fit_transform(name_docs)
        q_vec_name = vectorizer.transform([expanded])
        name_sims = cosine_similarity(q_vec_name, X_name).ravel()

        # Address similarity (weight 0.3) with same token style
        vectorizer_addr = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            token_pattern=r"(?u)\b\w+\b",
            sublinear_tf=True,
            max_features=8000,
            min_df=1,
            max_df=0.95,
        )
        X_addr = vectorizer_addr.fit_transform(address_docs)
        q_vec_addr = vectorizer_addr.transform([expanded])
        address_sims = cosine_similarity(q_vec_addr, X_addr).ravel()
    except Exception:
        return list(restaurants)

    # Combined relevance: 70% name/type, 30% address (handle NaN from zero-norm vectors)
    relevance = []
    for i in range(len(restaurants)):
        n = name_sims[i] if i < len(name_sims) else 0.0
        a = address_sims[i] if i < len(address_sims) else 0.0
        if math.isnan(n):
            n = 0.0
        if math.isnan(a):
            a = 0.0
        relevance.append(0.7 * n + 0.3 * a)

    # Mix in distance and rating (relevance is main; distance and rating nudge)
    alpha, beta, gamma = 1.0, 0.15, 0.15
    scored = []
    for i, r in enumerate(restaurants):
        rel = relevance[i] if i < len(relevance) else 0.0
        dist_norm = _norm_distance(r.get("distance_km"))
        rating_norm = _norm_rating(r.get("rating"))
        combined = alpha * rel + beta * dist_norm + gamma * rating_norm
        scored.append((combined, rel, r))

    # Sort by combined score, then by relevance, then by distance, then by rating
    scored.sort(
        key=lambda x: (
            -x[0],
            -x[1],
            (x[2].get("distance_km") is None, (x[2].get("distance_km") or 999)),
            (x[2].get("rating") is None, -(x[2].get("rating") or 0)),
        )
    )
    return [r for _, _, r in scored]
