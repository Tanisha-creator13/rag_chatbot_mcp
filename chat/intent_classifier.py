import re

class IntentClassifier:
    def classify(self, query: str) -> str:
        query = query.lower()
        
        # Define intents using regex patterns
        patterns = {
            "greeting": r"\b(hi|hello|hey|good morning|good evening|what's up|how are you)\b",
            "thanks": r"\b(thanks|thank you|thankyou|appreciate it)\b",
            "goodbye": r"\b(bye|goodbye|see you|later)\b",
            "faq": r"\b(what|where|when|why|how|explain|tell me)\b",
        }
        
        for intent, pattern in patterns.items():
            if re.search(pattern, query):
                return intent
        return "other"