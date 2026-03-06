import re
import random

FOOD_KEYWORDS = {
    "pizza": "Pizza is a great choice! Try searching for 'pizza' on our Find Food page to discover nearby pizzerias. Classic toppings like margherita or pepperoni never disappoint.",
    "sushi": "Sushi lovers, unite! Search for 'sushi' to find Japanese restaurants near you. Don't forget to try salmon nigiri or a fresh roll.",
    "vegan": "Going vegan? Search for 'vegan' to find plant-based restaurants. Many spots now offer amazing vegan bowls, burgers and desserts.",
    "burger": "Burgers are always a crowd-pleaser! Search 'burger' or 'burgers' to find the best spots. Consider trying a local craft burger joint.",
    "tacos": "Tacos for the win! Search 'tacos' for authentic Mexican spots. Carnitas, al pastor and fish tacos are must-tries.",
    "indian": "Indian food offers amazing flavors! Search 'Indian' for curry houses and tandoori spots. Butter chicken and naan are classics.",
    "chinese": "Craving Chinese? Search 'Chinese' for nearby options. Dim sum, fried rice and Peking duck are popular choices.",
    "italian": "Italian cuisine never disappoints. Search 'Italian' for pasta, risotto and wood-fired pizzas.",
    "thai": "Thai food brings bold flavors! Search 'Thai' for pad thai, green curry and tom yum soup.",
    "breakfast": "Breakfast is the most important meal! Search 'breakfast' or 'brunch' for cafes and diners.",
    "healthy": "Eating healthy? Search 'healthy' or 'salad' for lighter options. Many restaurants now offer nutritious bowls.",
    "spicy": "Love spice? Search for 'spicy' or try cuisines like Thai, Indian or Mexican for bold flavors.",
}

GREETINGS = [
    "Hi! I'm your Dishcovery food assistant. Ask me about cuisines, dishes or diets or head to Find Food to search restaurants near you!",
    "Hello! What are you in the mood for? I can suggest cuisines or help you find restaurants. Try 'Find Food' to search by location.",
]

HELP_RESPONSES = [
    "I can help with food recommendations! Try asking about a cuisine (e.g. pizza, sushi, vegan) or use our Find Food page to search restaurants near your location.",
    "Ask me things like 'Where can I find good pizza?' or 'What's good for a vegan diet?' I'll point you in the right direction.",
]

DEFAULT_RESPONSES = [
    "That sounds interesting! Try using our Find Food page to search for restaurants near you. Enter what you're craving and we'll show you nearby options.",
    "I'd love to help! Head to the Find Food page, enter your craving (e.g. pizza, tacos, vegan) and we'll find spots near your location.",
]


def get_ai_response(message: str) -> str:
    """Generate a simple keyword-based response for the chat widget."""
    if not message or not message.strip():
        return "Please type a message! I'm here to help with food recommendations."

    text = message.strip().lower()

    # Greetings
    if re.search(r"\b(hi|hey|hello|hey there)\b", text):
        return random.choice(GREETINGS)

    # Help
    if re.search(r"\b(help|what can you do|how does this work)\b", text):
        return random.choice(HELP_RESPONSES)

    # Check for food keywords
    for keyword, response in FOOD_KEYWORDS.items():
        if keyword in text:
            return response

    # Cuisine mentions
    cuisines = ["mexican", "japanese", "korean", "mediterranean", "greek", "french"]
    for c in cuisines:
        if c in text:
            return f"Great choice! Search for '{c}' on our Find Food page to discover {c.capitalize()} restaurants near you."

    return random.choice(DEFAULT_RESPONSES)
