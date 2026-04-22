import re
import numpy as np
from typing import Tuple, Dict, Any

def analyze_text(text: str) -> float:
    """Analyze text for risk indicators (0.0 = low, 1.0 = high)"""
    text_lower = text.lower()
    
    # High-risk keywords (weighted)
    high_risk_keywords = [
        'suicide', 'kill myself', 'self-harm', 'cut myself', 'end it all',
        'overdose', 'die', 'dead', 'hopeless', 'worthless'
    ]
    
    medium_risk_keywords = [
        'depressed', 'anxious', 'panic', 'overwhelmed', 'alone', 'empty'
    ]
    
    # Count matches
    high_count = sum(1 for word in high_risk_keywords if word in text_lower)
    medium_count = sum(1 for word in medium_risk_keywords if word in text_lower)
    
    # Simple risk scoring
    risk_score = (high_count * 0.3 + medium_count * 0.1) / max(len(text.split()), 1)
    return min(risk_score, 1.0)

def predict_from_form(
    age: int, 
    gender: str, 
    family_history: str, 
    work_interfere: str,
    sleep_quality: int = 5,
    mood_score: int = 5
) -> str:
    """Simple rule-based prediction (replace with ML model)"""
    try:
        # Convert categorical to numeric
        gender_score = 0.5 if gender == "Female" else 0.3
        family_score = 0.7 if family_history == "Yes" else 0.2
        
        interfere_scores = {
            "Never": 0.1, "Rarely": 0.3, "Sometimes": 0.5, "Often": 0.7, "Always": 0.9
        }
        
        # Composite score
        total_score = (
            (age / 100) * 0.1 +
            gender_score * 0.2 +
            family_score * 0.3 +
            interfere_scores[work_interfere] * 0.3 +
            ((10 - sleep_quality) / 10) * 0.2 +
            ((10 - mood_score) / 10) * 0.2
        )
        
        if total_score > 0.65:
            return "HIGH RISK - Needs Immediate Treatment"
        elif total_score > 0.45:
            return "MEDIUM RISK - Professional Support Recommended"
        else:
            return "LOW RISK - Continue Self-Care"
            
    except:
        return "Model Not Loaded"
