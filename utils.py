import re
from typing import Dict, Tuple, Optional
from langchain.schema import BaseMessage

# Sentiment analysis keywords
SENTIMENT_KEYWORDS = {
    'positive': ['happy', 'good', 'great', 'excited', 'grateful', 'blessed'],
    'negative': ['sad', 'depressed', 'anxious', 'stressed', 'overwhelmed', 'hopeless'],
    'neutral': ['okay', 'fine', 'normal', 'alright']
}

CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'self-harm', 'cut myself', 'end my life',
    'overdose', 'die', 'dead', 'no reason to live', 'better off dead'
]

def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis"""
    text_lower = text.lower()
    pos_count = sum(1 for word in SENTIMENT_KEYWORDS['positive'] if word in text_lower)
    neg_count = sum(1 for word in SENTIMENT_KEYWORDS['negative'] if word in text_lower)
    
    if neg_count > pos_count:
        return "😢 Negative"
    elif pos_count > neg_count:
        return "😊 Positive"
    else:
        return "😐 Neutral"

def detect_crisis_keywords(text: str) -> bool:
    """Detect crisis indicators"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CRISIS_KEYWORDS)

def calculate_risk_score(text: str) -> float:
    """Calculate risk score (0.0 = low, 1.0 = high)"""
    text_lower = text.lower()
    
    # Crisis keywords (high weight)
    crisis_count = sum(1 for word in CRISIS_KEYWORDS if word in text_lower)
    
    # Negative sentiment
    neg_words = sum(1 for word in SENTIMENT_KEYWORDS['negative'] if word in text_lower)
    
    # Length factor (longer = more serious?)
    length_factor = min(len(text.split()) / 50, 0.3)
    
    risk_score = (crisis_count * 0.4 + neg_words * 0.1 + length_factor) / max(1, len(text.split()))
    return min(risk_score, 1.0)

def generate_counseling_response(
    llm, user_input: str, sentiment: str, risk_score: float
) -> str:
    """Generate context-aware counseling response"""
    try:
        # Enhanced prompt with context
        context_prompt = f"""
        Context: User sentiment={sentiment}, risk_score={risk_score:.2f}
        User: {user_input}
        
        Respond with:
        1. VALIDATION ("I hear you...")
        2. EMPATHY ("That must be really difficult")
        3. GENTLE guidance (CBT techniques)
        4. ACTIONABLE steps
        5. If risk > 0.7: CRISIS RESOURCES
        """
        
        response = llm.invoke(context_prompt)
        return response
        
    except Exception as e:
        return f"I hear you're feeling {sentiment.lower()}. That sounds challenging. Would you like to talk more about what's been going on? I'm here to listen ❤️"

def get_crisis_resources() -> str:
    """Emergency resources markdown"""
    return """
    **🚨 EMERGENCY - Call NOW:**
    
    **USA**: 988
    **UK**: 116 123  
    **Australia**: 13 11 14
    **Canada**: 1-833-456-4566
    **India**: 9152987821
    
    **You are NOT alone. Help is available 24/7**
    """
