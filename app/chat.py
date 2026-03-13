import re
import random

# Cuisine and dish keywords with helpful, specific replies
FOOD_KEYWORDS = {
    "pizza": "Pizza is a great choice! Search for 'pizza' on Find Food to discover nearby pizzerias. Try margherita, pepperoni or a wood-fired option.",
    "sushi": "Sushi lovers, unite! Search 'sushi' on Find Food for Japanese spots near you. Salmon nigiri, rolls and sashimi are always a hit.",
    "vegan": "Going vegan? Search 'vegan' on Find Food for plant-based restaurants. Many places do great vegan bowls, burgers and desserts.",
    "burger": "Burgers are a crowd-pleaser! Search 'burger' on Find Food. You can filter by distance and try a local craft or classic joint.",
    "tacos": "Tacos for the win! Search 'tacos' on Find Food for Mexican spots. Carnitas, al pastor and fish tacos are must-tries.",
    "indian": "Indian food has amazing flavors! Search 'Indian' on Find Food for curry houses and tandoori. Butter chicken and naan are classics.",
    "chinese": "Craving Chinese? Search 'Chinese' on Find Food. Dim sum, fried rice and noodle dishes are popular choices.",
    "italian": "Italian never disappoints! Search 'Italian' on Find Food for pasta, risotto and wood-fired pizzas near you.",
    "thai": "Thai brings bold flavors! Search 'Thai' on Find Food for pad thai, green curry and tom yum soup.",
    "breakfast": "Breakfast is the most important meal! Search 'breakfast' or 'brunch' on Find Food for cafes and diners nearby.",
    "healthy": "Eating healthy? Search 'healthy' or 'salad' on Find Food. Many restaurants offer nutritious bowls and lighter options.",
    "spicy": "Love spice? Search 'spicy' or try Thai, Indian or Mexican on Find Food for bold, flavorful options.",
    "ramen": "Ramen is perfect when you want something warming! Search 'ramen' on Find Food for Japanese noodle spots near you.",
    "curry": "Curry hits the spot! Search 'curry' on Find Food for Indian, Thai or Japanese curry restaurants.",
    "seafood": "Seafood fan? Search 'seafood' or 'fish' on Find Food for restaurants that specialize in fresh fish and shellfish.",
    "steak": "Steak night! Search 'steak' or 'grill' on Find Food for steakhouses and grill restaurants nearby.",
    "bbq": "BBQ is always a good idea! Search 'bbq' or 'barbecue' on Find Food for smoked meats and ribs.",
    "korean": "Korean food is full of flavor! Search 'Korean' on Find Food for bibimbap, BBQ and kimchi dishes.",
    "japanese": "Japanese cuisine is versatile! Search 'Japanese' on Find Food for sushi, ramen, tempura and more.",
    "mexican": "Mexican food is vibrant and tasty! Search 'Mexican' on Find Food for tacos, burritos and authentic spots.",
    "mediterranean": "Mediterranean is fresh and healthy! Search 'Mediterranean' on Find Food for Greek, Lebanese and similar cuisines.",
    "greek": "Greek food is delicious! Search 'Greek' on Find Food for souvlaki, gyros and Greek salads.",
    "french": "French cuisine is classic! Search 'French' on Find Food for bistros, pastries and fine dining.",
    "vietnamese": "Vietnamese is fresh and fragrant! Search 'Vietnamese' on Find Food for pho, banh mi and spring rolls.",
    "brunch": "Brunch time! Search 'brunch' on Find Food for cafes and restaurants serving breakfast and lunch combos.",
    "dessert": "Something sweet? Search 'dessert' or 'cake' on Find Food for bakeries and dessert spots.",
    "coffee": "Need a coffee fix? Search 'coffee' or 'cafe' on Find Food for cafes and coffee shops.",
    "halal": "Looking for halal options? Search 'halal' on Find Food for halal-certified restaurants near you.",
    "gluten free": "Gluten-free dining? Search 'gluten free' on Find Food for places with GF options.",
    "vegetarian": "Vegetarian options? Search 'vegetarian' on Find Food for meat-free restaurants and menus.",
    "keto": "On keto? Search 'keto' or 'low carb' on Find Food for restaurants with keto-friendly dishes.",
    "noodles": "Noodle craving? Search 'noodles' on Find Food for Asian noodle spots, ramen and pasta.",
    "wings": "Wings and game day! Search 'wings' on Find Food for places that do buffalo, BBQ or other wing styles.",
    "sandwich": "Sandwich spot? Search 'sandwich' or 'deli' on Find Food for subs, paninis and delis.",
    "salad": "Light and fresh! Search 'salad' on Find Food for places with great salad options.",
    "soup": "Soup weather! Search 'soup' on Find Food for pho, ramen, and classic soup spots.",
    "dim sum": "Dim sum is perfect for sharing! Search 'dim sum' or 'Chinese' on Find Food for dumplings and small plates.",
    "pad thai": "Pad thai is a classic! Search 'pad thai' or 'Thai' on Find Food for Thai restaurants near you.",
    "pho": "Pho hits the spot! Search 'pho' or 'Vietnamese' on Find Food for noodle soup spots.",
    "biryani": "Biryani is flavourful and filling! Search 'biryani' or 'Indian' on Find Food.",
    "falafel": "Falafel is tasty and often veggie-friendly! Search 'falafel' or 'Middle Eastern' on Find Food.",
    "hummus": "Hummus and mezze! Search 'hummus' or 'Mediterranean' on Find Food for Middle Eastern spots.",
    "kebab": "Kebabs are a solid choice! Search 'kebab' on Find Food for Turkish or Middle Eastern grills.",
    "pasta": "Pasta night! Search 'pasta' or 'Italian' on Find Food for spaghetti, penne and more.",
    "risotto": "Risotto is cosy and creamy! Search 'risotto' or 'Italian' on Find Food.",
    "fish and chips": "British classic! Search 'fish and chips' on Find Food for proper chippies.",
    "pancakes": "Pancakes for any time! Search 'pancakes' or 'breakfast' on Find Food.",
    "waffles": "Waffles are a treat! Search 'waffles' or 'brunch' on Find Food.",
    "ice cream": "Something sweet! Search 'ice cream' or 'dessert' on Find Food.",
    "bubble tea": "Bubble tea fix! Search 'bubble tea' or 'boba' on Find Food.",
    "smoothie": "Fresh and filling! Search 'smoothie' or 'juice' on Find Food for cafes and juice bars.",
    "pie": "Pie and mash or sweet pie! Search 'pie' on Find Food for savoury and dessert spots.",
    "dumplings": "Dumplings are a crowd-pleaser! Search 'dumplings' or 'dim sum' on Find Food.",
    "poke": "Poke bowls are fresh and healthy! Search 'poke' on Find Food for Hawaiian-style bowls.",
    "burrito": "Burrito craving? Search 'burrito' or 'Mexican' on Find Food.",
    "fried chicken": "Fried chicken never disappoints! Search 'fried chicken' on Find Food.",
    "comfort food": "Comfort food mood! Search 'comfort food', 'mac and cheese' or 'pub food' on Find Food.",
    "date night": "For date night try something a bit special: search 'Italian', 'French' or 'steak' on Find Food and filter by distance for a cosy spot.",
    "quick bite": "Quick bite? Search 'sandwich', 'wrap', 'fast food' or 'cafe' on Find Food and pick somewhere close.",
    "family dinner": "Family dinner? Search something everyone likes: 'Italian', 'Chinese', 'pizza' or 'burger' on Find Food and check opening hours.",
    "late night": "Late night hunger? Search 'late night' or 'open late' on Find Food, or try 'pizza' or 'kebab' – many stay open late.",
    "cheap": "Eating on a budget? Search 'cheap eats', 'budget' or a cuisine like 'Chinese' or 'Indian' on Find Food and filter by distance.",
    "fancy": "Feeling fancy? Search 'fine dining', 'French', 'steak' or 'seafood' on Find Food for a special meal.",
    "open now": "To see what's open now, use Find Food: enter your craving and location. Results show opening status so you can pick places that are open.",
    "takeaway": "Takeaway? Use Find Food to find places near you, then check Google Maps from the result for takeaway or delivery options.",
    "delivery": "We show you nearby restaurants; for delivery check the place on Google Maps (via 'View on Maps') or their website. Search your craving on Find Food first!",
    "lunch": "Lunch break! Search 'lunch', 'sandwich', 'salad' or a cuisine like 'Japanese' on Find Food for quick options near you.",
    "dinner": "Dinner plans! Search what you're in the mood for (e.g. Italian, Thai, steak) on Find Food and add your location.",
    "snack": "Snack attack? Search 'cafe', 'bakery', 'pastries' or 'coffee' on Find Food for something light.",
    "hungry": "When you're hungry, head to Find Food and type what you fancy (pizza, curry, anything!) plus your location. You'll see nearby options with ratings.",
    "starving": "Find Food is your friend! Enter your craving and location (or use current location) and we'll show you nearby restaurants so you can eat soon.",
    "dairy free": "Dairy-free? Search 'dairy free' or 'vegan' on Find Food for places with dairy-free options.",
    "pescatarian": "Pescatarian options? Search 'seafood', 'fish' or 'vegetarian' on Find Food for places with good fish and veggie choices.",
    "mac and cheese": "Mac and cheese comfort! Search 'mac and cheese' or 'comfort food' on Find Food.",
    "shawarma": "Shawarma craving? Search 'shawarma' or 'Middle Eastern' on Find Food for wraps and grills.",
    "gyro": "Gyros are delicious! Search 'gyro' or 'Greek' on Find Food for souvlaki and gyro spots.",
    "bao": "Bao buns are a treat! Search 'bao' or 'dim sum' on Find Food for steamed buns.",
    "udon": "Udon noodles are hearty! Search 'udon' or 'Japanese' on Find Food.",
    "tempura": "Tempura is light and crispy! Search 'tempura' or 'Japanese' on Find Food.",
    "ceviche": "Ceviche is fresh and zingy! Search 'ceviche' or 'Peruvian' on Find Food.",
    "tapas": "Tapas are perfect for sharing! Search 'tapas' or 'Spanish' on Find Food.",
    "paella": "Paella is a Spanish classic! Search 'paella' or 'Spanish' on Find Food.",
    "pierogi": "Pierogi are cosy and filling! Search 'pierogi' or 'Polish' on Find Food.",
    "bagel": "Bagel fix? Search 'bagel' or 'breakfast' on Find Food for bagel shops and delis.",
    "croissant": "Croissants and pastries! Search 'croissant' or 'bakery' on Find Food.",
    "cake": "Something sweet! Search 'cake' or 'bakery' on Find Food for dessert and coffee.",
    "pub": "Pub grub! Search 'pub' or 'pub food' on Find Food for classic British and Irish pubs.",
    "bakery": "Fresh bread and pastries! Search 'bakery' on Find Food for bakeries and patisseries.",
    "buffet": "All you can eat? Search 'buffet' on Find Food for buffet restaurants.",
    "street food": "Street food vibe? Search 'street food' or 'food market' on Find Food.",
    "food truck": "Food truck hunt? Search 'food truck' or check Find Food for markets and street food areas.",
    "romantic": "Romantic dinner? Search 'Italian', 'French', 'fine dining' or 'steak' on Find Food and pick a cosy spot.",
    "celebration": "Celebrating? Search 'fine dining', 'steak', 'seafood' or a favourite cuisine on Find Food for somewhere special.",
    "birthday": "Birthday meal? Search something they love (e.g. Italian, steak, Japanese) on Find Food and filter by rating for a treat.",
    "group": "Eating with a group? Search something versatile like 'Italian', 'Chinese', 'pizza' or 'burger' on Find Food and check opening hours and space.",
    "kids": "Kid-friendly? Search 'family restaurant', 'pizza', 'burger' or 'Italian' on Find Food for places that welcome families.",
    "child friendly": "Family meal? Search 'family restaurant', 'pizza' or 'burger' on Find Food for kid-friendly options.",
    "outdoor": "Outdoor seating? Use Find Food to find places, then check Google Maps or the place's listing for garden or terrace info.",
    "rooftop": "Rooftop vibes? Search 'rooftop' or 'rooftop bar' on Find Food for elevated dining.",
    "casual": "Casual bite? Search 'cafe', 'sandwich', 'pizza' or 'burger' on Find Food for relaxed spots.",
    "light": "Something light? Search 'salad', 'soup', 'sushi' or 'cafe' on Find Food.",
    "filling": "Something filling? Search 'curry', 'burger', 'pasta', 'bbq' or 'comfort food' on Find Food.",
    "organic": "Organic options? Search 'organic' or 'healthy' on Find Food for places that focus on organic produce.",
    "local": "Support local? Use Find Food with your area and a craving; you'll see nearby independent spots with ratings.",
    "sugar free": "Sugar-free? Search 'sugar free', 'healthy' or 'vegan' on Find Food for low-sugar options.",
    "low calorie": "Watching calories? Search 'low calorie', 'healthy' or 'salad' on Find Food.",
    "boba": "Bubble tea! Search 'bubble tea' or 'boba' on Find Food.",
    "juice": "Fresh juice? Search 'juice' or 'smoothie' on Find Food for juice bars and cafes.",
    "tea": "Tea time? Search 'tea' or 'cafe' on Find Food for tea rooms and cafes.",
    "wine": "Wine and food? Search 'wine bar', 'French' or 'Italian' on Find Food for places with good wine lists.",
    "beer": "Beer and a bite? Search 'pub', 'brewery' or 'beer' on Find Food.",
    "all you can eat": "All you can eat? Search 'buffet' or 'all you can eat' on Find Food.",
    "sharing": "Sharing plates? Search 'tapas', 'dim sum', 'mezze' or 'sharing' on Find Food.",
    "gluten": "Gluten-free? Search 'gluten free' on Find Food for GF options.",
    "veggie": "Veggie options? Search 'vegetarian' or 'vegan' on Find Food for plant-based choices.",
    "plant based": "Plant-based? Search 'vegan' or 'plant based' on Find Food.",
    "no meat": "No meat? Search 'vegetarian' or 'vegan' on Find Food.",
    "breakfast near me": "Breakfast nearby? Go to Find Food, use your current location and search 'breakfast' or 'brunch'.",
    "brunch near me": "Brunch nearby? Find Food with 'Use my current location' and search 'brunch' or 'breakfast'.",
}

GREETINGS = [
    "Hi! I'm your Dishcovery assistant. Ask me about cuisines (pizza, Thai, vegan), meals (breakfast, brunch), occasions (date night, quick bite), diets (halal, gluten free) or how to find restaurants. Use Find Food to search by craving and location!",
    "Hello! What are you in the mood for? I can suggest cuisines, dishes, dietary options or what to search for date night, lunch, cheap eats and more. Head to Find Food and enter your craving and address (or use your location).",
    "Hey there! I'm here to help with food and finding restaurants. Ask me about a type of food, diet, occasion (e.g. family dinner, late night) or how the app works. Use Find Food to search by keyword and location.",
    "Hi there! Fancy something to eat? Ask me for ideas (cuisine, dish, diet, occasion) or go straight to Find Food and search by craving and location.",
    "Hello! I can help you discover places to eat. Tell me what you're craving, what diet you're on, or an occasion (date night, quick bite). Use Find Food with your location to see nearby spots.",
]

HELP_RESPONSES = [
    "I can help with: (1) Cuisine ideas (pizza, sushi, Indian, Thai). (2) Meals and occasions (breakfast, date night, quick bite, late night). (3) Diets (vegan, halal, gluten free). (4) Mood (hungry, tired, lazy: I'll suggest easy options). (5) Finding restaurants: use Find Food with your craving and address or location. What would you like?",
    "Here's what I do: suggest what to eat and point you to restaurants. Ask things like 'Where can I find good pizza?', 'What's good for vegan?', 'Date night ideas', 'Quick bite near me' or 'I'm tired'. Then use Find Food to search by that keyword and your location. Need a specific suggestion?",
    "You can ask me about: cuisines (Italian, Mexican, Japanese), dishes (burgers, tacos, ramen), diets (vegan, keto, halal), occasions (family dinner, cheap eats, open now) or just 'what should I eat'. To see actual restaurants, go to Find Food, type your craving and enter an address or use your current location. I'll keep giving you ideas here!",
]

DEFAULT_RESPONSES = [
    "Sounds good! Use the Find Food page: enter what you're craving (e.g. pizza, Thai, vegan) and your location. We'll show you nearby restaurants with photos, ratings and opening hours.",
    "I'd love to help! Head to Find Food, type your craving and your address or use 'Use my current location'. You can also adjust max distance and how many results you want.",
    "Try the Find Food page: put in your craving (dish or cuisine) and where you are. You'll get a list of nearby places. If you tell me a cuisine or diet, I can suggest what to search for!",
    "Use Find Food to search. Enter a keyword (e.g. sushi, breakfast, halal) and your location. You'll see nearby options with ratings and links to maps. Want a suggestion for what to search?",
    "Tell me what you're in the mood for (a cuisine, dish, diet or occasion) and I'll suggest a search. Or go to Find Food and type your craving and location to see results straight away.",
    "I can suggest what to search for. Say a cuisine (Italian, Japanese), dish (burger, ramen), diet (vegan, halal) or occasion (date night, quick bite). Then use Find Food with that and your location.",
]

# App / what is Dishcovery
APP_RESPONSES = [
    "Dishcovery helps you discover restaurants by what you're craving. Use Find Food: enter a keyword (cuisine, dish or diet) and your address or current location. You'll get nearby places with ratings, photos and opening hours. I'm here to suggest what to search for!",
    "This is Dishcovery, your food discovery app. You can find restaurants via Find Food: type what you want (e.g. pizza, Thai, vegan) and where you are. Results are ranked by how well they match your search. Ask me for ideas anytime!",
    "Dishcovery is all about finding food by craving and location. Open Find Food, enter what you want to eat and where you are (or use current location). I'm the chat assistant: ask me for cuisine ideas, diets, occasions or how to use the app.",
]

# Mood / state (tired, lazy, bored, stressed)
MOOD_RESPONSES = [
    "When you're tired or lazy, something easy hits the spot. Try searching 'delivery', 'takeaway', 'pizza' or 'comfort food' on Find Food and pick somewhere close.",
    "No worries. Search something low-effort on Find Food: 'cafe', 'sandwich', 'pizza' or 'noodles' and use your location. You'll see nearby options without the hassle.",
    "Been there. Use Find Food with 'pizza', 'comfort food' or 'cafe' and your location. Pick somewhere close and you're sorted.",
]

# Small talk (how are you, what's up, ok, cool, nice, sure)
SMALL_TALK_RESPONSES = [
    "All good! If you're thinking about food, tell me what you're in the mood for or head to Find Food and search by craving and location.",
    "Here if you need ideas! You can ask about cuisines, diets or how to find restaurants, or just use Find Food with a keyword and your address.",
    "Good to hear! Want a food suggestion or help finding a place? Just say the craving or occasion and I'll point you to Find Food.",
]

# Confusion / idk / can't decide
CONFUSED_RESPONSES = [
    "No problem. Try Find Food and search something broad like 'restaurant', 'food' or a cuisine (e.g. Italian, Japanese). You can also tell me a mood like 'something light' or 'comfort food' and I'll suggest a keyword.",
    "If you're not sure, head to Find Food and browse by location, or tell me: quick bite, date night, healthy, spicy, etc. and I'll suggest what to search.",
    "That's fine. Type a craving (even something like 'food' or 'restaurant') in Find Food with your location and browse. Or say a cuisine and I'll suggest a search.",
]

# Location (in London, in NYC, etc.)
LOCATION_RESPONSES = [
    "You can search that area on Find Food: enter the city or address in the location field and type what you're craving. We'll show restaurants there with ratings and opening hours.",
    "Use Find Food and type the area in the address box (e.g. London, NYC), then add your craving. You'll get results for that location.",
    "Search that city on Find Food: put the place in the location field and your craving in the search. Results will show spots there with ratings.",
]

# Extra patterns: recommend, suggest, near me, what to eat, thanks, bye
RECOMMEND_RESPONSES = [
    "I'd recommend using Find Food and trying a search for something you're in the mood for (e.g. pizza, curry, brunch). Enter your location and you'll see nearby options. If you tell me a cuisine or diet, I can suggest a keyword to search!",
    "Try Find Food: enter a craving like 'Italian', 'vegan' or 'ramen' and your address. You'll get personalised nearby results. Tell me a cuisine or diet and I can suggest what to type in the search.",
    "Use Find Food with a keyword (e.g. Thai, steak, breakfast) and your location. Results are ranked by relevance. Tell me what you fancy and I can suggest a search term.",
]
NEAR_ME_RESPONSES = [
    "To find food near you, go to Find Food and choose 'Use my current location', then enter what you're craving (e.g. pizza, Thai). We'll show nearby restaurants with ratings and distance.",
    "Use Find Food, select 'Use my current location', and type your craving. You'll get a list of places near you with photos and opening hours.",
    "Find Food with 'Use my current location' and your craving (pizza, sushi, whatever you fancy). You'll see nearby spots with distance and opening status.",
]
WHAT_TO_EAT_RESPONSES = [
    "If you're unsure, try searching for a mood: 'comfort food', 'healthy', 'spicy' or a cuisine like 'Italian' or 'Japanese' on Find Food. Or tell me a cuisine or diet and I'll suggest a search keyword!",
    "Think about what you're in the mood for: something light (salad, sushi), hearty (burger, curry) or quick (tacos, sandwich). Tell me the vibe and I'll suggest what to search on Find Food.",
    "Try Find Food with a broad term like 'restaurant' or a cuisine. Or say something like 'quick bite', 'date night' or 'healthy' and I'll suggest a keyword to search.",
]
THANKS_BYE = [
    "You're welcome! Enjoy your meal. Come back if you need more ideas or use Find Food to search again.",
    "Glad I could help! Use Find Food whenever you want to discover new spots. Happy eating!",
    "Pleasure! Have a great meal. I'm here if you need more suggestions.",
]

# Where can I find / best place / any good
WHERE_BEST_RESPONSES = [
    "Use Find Food: enter what you're looking for (e.g. pizza, Thai, vegan) and your location. Results show nearby places with ratings and opening hours so you can pick the best fit.",
    "Search your craving on Find Food with your address or current location. You'll get a list ranked by relevance; check ratings and distance to find a good spot.",
]

# Never mind / no thanks / cancel
NEVERMIND_RESPONSES = [
    "No problem. When you're ready, just ask for a suggestion or head to Find Food to search. I'm here!",
    "All good. Come back anytime you want food ideas or help finding a place.",
]

# Ratings / reviews
RATING_RESPONSES = [
    "Find Food results show star ratings and review counts from Google. Use them to compare places. Open a result and click 'View on Maps' for full reviews.",
    "Ratings and review counts appear on each restaurant card on Find Food. Search your craving and location to see options sorted by relevance; then pick by rating and distance.",
]


def get_ai_response(message: str) -> str:
    """Keyword and pattern-based chat: cuisines, dishes, diets, occasions, mood, app help, location and small talk."""
    if not message or not message.strip():
        return "Please type a message! I'm here to help with food ideas and finding restaurants."

    text = message.strip().lower()

    # Greetings
    if re.search(r"\b(hi|hey|hello|hey there|good morning|good afternoon|good evening|good night|yo|sup)\b", text):
        return random.choice(GREETINGS)

    # Thanks / bye
    if re.search(r"\b(thanks|thank you|bye|goodbye)\b", text):
        return random.choice(THANKS_BYE)

    # Help
    if re.search(r"\b(help|what can you do|how does this work|how do i)\b", text):
        return random.choice(HELP_RESPONSES)

    # App / what is Dishcovery
    if re.search(r"\b(what is dishcovery|what is this (app|site|website)|what does this (app|site) do|how does find food work)\b", text):
        return random.choice(APP_RESPONSES)

    # "Near me" / "around here"
    if re.search(r"\b(near me|around me|close by|nearby)\b", text):
        return random.choice(NEAR_ME_RESPONSES)

    # "Recommend" / "suggest"
    if re.search(r"\b(recommend|suggest|what do you suggest)\b", text):
        return random.choice(RECOMMEND_RESPONSES)

    # "Where can I find" / "best place" / "any good"
    if re.search(r"\b(where can i find|best place|any good (places?|restaurants?)?|good (place|restaurant|spot)s?\s+(for|to)\b|where'?s (a )?good)\b", text):
        return random.choice(WHERE_BEST_RESPONSES)

    # "Never mind" / "no thanks" / "cancel"
    if re.search(r"\b(never mind|nevermind|no thanks|no thank you|cancel|forget it|nvm)\b", text):
        return random.choice(NEVERMIND_RESPONSES)

    # Ratings / reviews
    if re.search(r"\b(rating|ratings|review|reviews|stars?|how good)\b", text):
        return random.choice(RATING_RESPONSES)

    # "What should I eat" / "what to eat"
    if re.search(r"\b(what should i eat|what to eat|what can i eat|not sure what to eat)\b", text):
        return random.choice(WHAT_TO_EAT_RESPONSES)

    # Mood (tired, lazy, bored, stressed)
    if re.search(r"\b(tired|lazy|bored|stressed|can't be bothered)\b", text):
        return random.choice(MOOD_RESPONSES)

    # Small talk (how are you, what's up, ok, cool, nice, sure)
    if re.search(r"\b(how are you|what'?s up|how'?s it going|ok|okay|cool|nice|sure|alright|got it|sounds good)\b", text):
        return random.choice(SMALL_TALK_RESPONSES)

    # Confused / can't decide / nothing
    if re.search(r"\b(what\s*$|huh|idk|i don'?t know|don'?t know|can'?t decide|nothing|no idea)\b", text) or text in ("what", "idk", "nothing"):
        return random.choice(CONFUSED_RESPONSES)

    # Location (in London, in NYC, etc.)
    if re.search(r"\b(in|near)\s+(london|nyc|new york|manchester|birmingham|leeds|glasgow|edinburgh|dublin|paris|berlin|amsterdam|tokyo|sydney|la|los angeles|bristol|liverpool|sheffield|belfast|cardiff|cambridge|oxford|brighton|boston|chicago|miami|san francisco|sf|seattle|toronto|vancouver|melbourne|auckland|singapore|hong kong|dubai|madrid|barcelona|rome|milan|munich|copenhagen|stockholm|oslo|brussels|vienna|prague|lisbon|athens|istanbul|mumbai|delhi|bangkok|seoul)\b", text):
        return random.choice(LOCATION_RESPONSES)

    # Food keywords (cuisines, dishes, diets)
    for keyword, response in FOOD_KEYWORDS.items():
        if keyword in text:
            return response

    # Extra cuisines not in FOOD_KEYWORDS
    extra_cuisines = [
        "american", "british", "spanish", "turkish", "lebanese", "moroccan", "ethiopian",
        "nigerian", "caribbean", "brazilian", "peruvian", "indonesian", "malaysian",
        "pakistani", "bangladeshi", "sri lankan", "nepalese", "afghan", "persian", "iraqi",
        "egyptian", "south african", "ghanaian", "kenyan", "jamaican", "trinidadian",
        "argentine", "colombian", "chilean", "cuban", "puerto rican", "filipino", "polish",
        "russian", "ukrainian", "georgian", "armenian", "cajun", "creole", "hawaiian",
    ]
    for c in extra_cuisines:
        if c in text:
            return f"Great choice! Search for '{c}' on our Find Food page to discover {c.capitalize()} restaurants near you."

    return random.choice(DEFAULT_RESPONSES)
