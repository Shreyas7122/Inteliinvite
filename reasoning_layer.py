import pandas as pd
import json
import re
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from typing import Dict, Any, List

# Ollama integration with graceful fallback
try:
    import ollama
    OLLAMA_AVAILABLE = True
    print("✅ Ollama library loaded successfully.")
except ImportError:
    print("⚠️ Ollama not installed. Run: pip install ollama")
    OLLAMA_AVAILABLE = False


class AIReasoningLayer:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        
        # Semantic Event Dictionary (core of your semantic engineering layer)
        self.event_dictionary = {
            "cleanliness drive": ["Environment"],
            "cleanup": ["Environment"],
            "medical camp": ["Health"],
            "teaching": ["Education", "Youth"],
            "disaster relief": ["Disaster Response"],
            "peace march": ["Peace", "Youth"]
        }
        
        # LLM Configuration
        self.llm_model = "llama3.2"   # Recommended: llama3.2, gemma2:9b, qwen2.5:7b
        self.use_ollama = OLLAMA_AVAILABLE

    def process_user_input(self, text_input: str) -> Dict[str, Any]:
        """
        Main Semantic Engineering Pipeline:
        1. LLM Intent & Entity Extraction
        2. Event Dictionary Semantic Lookup
        3. Constraint Inference
        """
        print(f"🔍 Processing Input: '{text_input}'")
        
        # 1. LLM-based extraction (with fallback)
        entities = self._llm_extract_entities(text_input)
        
        # 2. Semantic lookup from event dictionary
        inferred_interests = self._lookup_event_interests(text_input, entities)
        
        # 3. Build structured constraints for retrieval & ranking
        constraints = self._infer_constraints(entities, inferred_interests)
        
        return constraints

    def _llm_extract_entities(self, text: str) -> Dict[str, Any]:
        """Real LLM extraction using Ollama. Falls back to heuristic if Ollama fails."""
        if not self.use_ollama:
            return self._heuristic_fallback(text)

        try:
            system_prompt = """
You are an expert Semantic Engineer for a volunteer matching system.
Extract structured information from the user request.

Return ONLY a valid JSON object with these exact keys:
- event_type: string (e.g. "cleanliness drive", "medical camp", "teaching")
- location: string or null
- other_entities: list of strings

Be precise, consistent, and do not add extra text.
"""

            response = ollama.chat(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": f"User request: {text}"}
                ],
                format="json"
            )
            
            entities = json.loads(response['message']['content'])
            print(f"✅ Ollama extracted entities: {entities}")
            return entities

        except Exception as e:
            print(f"⚠️ Ollama error: {e}. Falling back to heuristic extraction.")
            return self._heuristic_fallback(text)

    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        """Robust heuristic fallback when Ollama is unavailable or fails."""
        text_lower = text.lower()
        entities: Dict[str, Any] = {
            "event_type": None,
            "location": None,
            "other_entities": []
        }

        # Event type detection
        for keyword in self.event_dictionary.keys():
            if keyword in text_lower:
                entities["event_type"] = keyword
                break

        # Location detection (expand as needed)
        if "pittsburgh" in text_lower:
            entities["location"] = "Pittsburgh"

        return entities

    def _lookup_event_interests(self, text: str, entities: Dict) -> List[str]:
        """Semantic lookup using event dictionary (OR logic across keywords)."""
        text_lower = text.lower()
        inferred: List[str] = []

        for keyword, interests in self.event_dictionary.items():
            if keyword in text_lower:
                inferred.extend(interests)

        # Fallback using LLM-extracted event_type
        if not inferred and entities.get("event_type"):
            event_type = str(entities["event_type"]).lower()
            for keyword, interests in self.event_dictionary.items():
                if keyword in event_type:
                    inferred.extend(interests)

        return list(dict.fromkeys(inferred))  # Remove duplicates while preserving order

    def _infer_constraints(self, entities: Dict, inferred_interests: List[str]) -> Dict[str, Any]:
        """Infer final structured constraints for semantic retrieval + ML ranking."""
        constraints = {
            "max_distance_km": 50,
            "required_interests": inferred_interests[:],
            "excluded_interests": [],
            "max_age": None,
            "min_age": None,
            "min_physical_score": 5,
            "location": entities.get("location")
        }

        # Domain-specific rules (Cleanliness drive example)
        event_type = str(entities.get("event_type", "")).lower()
        if "cleanliness" in event_type or "cleanup" in event_type:
            constraints.update({
                "max_age": 60,
                "min_physical_score": 6,
                "max_distance_km": 40
            })

        print("✅ Inferred Constraints:")
        print(json.dumps(constraints, indent=2))
        return constraints

    def apply_feedback(self, constraints: Dict, feedback_text: str) -> Dict:
        """Dynamic Feedback Loop - Updates semantic constraints from natural language feedback."""
        print(f"\n🔄 [FEEDBACK] Processing: '{feedback_text}'")
        text_lower = feedback_text.lower().strip()

        # Max age update
        max_age_pattern = r'(?:(?:max|maximum|less\s*than|under|below|<)[^0-9]*age|age[^0-9]*(?:max|maximum|less|under|below|<))[^0-9]*(\d+)|(?:(?:max|maximum|less\s*than|under|below|<)[^0-9]*(\d+)[^0-9]*age)'
        max_age_match = re.search(max_age_pattern, text_lower)
        if max_age_match:
            constraints["max_age"] = int(max_age_match.group(1) or max_age_match.group(2))
            print(f"   → Updated max_age → {constraints['max_age']}")

        # Min age update
        min_age_pattern = r'(?:(?:min|minimum|more\s*than|greater\s*than|above|over|>)[^0-9]*age|age[^0-9]*(?:min|minimum|more|greater|above|over|>))[^0-9]*(\d+)|(?:(?:min|minimum|more\s*than|greater\s*than|above|over|>)[^0-9]*(\d+)[^0-9]*age)'
        min_age_match = re.search(min_age_pattern, text_lower)
        if min_age_match:
            constraints["min_age"] = int(min_age_match.group(1) or min_age_match.group(2))
            print(f"   → Updated min_age → {constraints['min_age']}")

        # Interest management (support negation)
        is_negation = any(word in text_lower for word in ["not", "don't", "exclude", "no ", "without", "avoid"])

        categories = {
            "youth": "Youth",
            "health": "Health",
            "peace": "Peace",
            "environment": "Environment",
            "disaster": "Disaster Response",
            "education": "Education"
        }

        for kw, category in categories.items():
            if kw in text_lower:
                if is_negation:
                    if "excluded_interests" not in constraints:
                        constraints["excluded_interests"] = []
                    if category not in constraints["excluded_interests"]:
                        constraints["excluded_interests"].append(category)
                    constraints["required_interests"] = [i for i in constraints.get("required_interests", []) if i != category]
                    print(f"   → Excluded interest: {category}")
                else:
                    if "required_interests" not in constraints:
                        constraints["required_interests"] = []
                    if category not in constraints["required_interests"]:
                        constraints["required_interests"].append(category)
                    print(f"   → Required interest added: {category}")

        print("✅ Updated Constraints:")
        print(json.dumps(constraints, indent=2))
        return constraints


# ---------------------------------------------------------
# 3. RETRIEVAL & RANKING STAGE
# ---------------------------------------------------------
class VolunteerMatcher:
    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)
        self.model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        self.label_encoders = {}
        self._train_model()
        
    def _train_model(self):
        """Trains the ML model on the dataset using dummy columns."""
        # Dummy columns matching the architecture: Attendance Rate, Physical Activity Score, Membership Type
        # (Using Volunteer dataset equivalents)
        X = self.df[['Attendance_Rate', 'Physical_Score', 'Membership_Status', 'Past_Events', 'Distance_KM']].copy()
        y = self.df['Likelihood_to_Attend']
        
        # Encode Membership_Status
        le = LabelEncoder()
        X['Membership_Status'] = le.fit_transform(X['Membership_Status'])
        self.label_encoders['Membership_Status'] = le
        
        self.model.fit(X, y)
        print(">> XGBoost Predictive ML Model trained successfully.")

    def semantic_retrieval(self, constraints):
        """
        Simulates a Vector Database / Semantic Document Search retrieval
        using deterministic filtering based on parameters.
        """
        filtered_df = self.df.copy()
        
        # Filter by max Distance
        if constraints.get("max_distance_km"):
            filtered_df = filtered_df[filtered_df['Distance_KM'] <= constraints['max_distance_km']]
            
        # Filter by max Age
        if constraints.get("max_age"):
            filtered_df = filtered_df[filtered_df['Age'] <= constraints['max_age']]
            
        # Filter by min Age
        if constraints.get("min_age"):
            filtered_df = filtered_df[filtered_df['Age'] >= constraints['min_age']]
            
        # Filter by physical score
        if constraints.get("min_physical_score"):
            filtered_df = filtered_df[filtered_df['Physical_Score'] >= constraints['min_physical_score']]
            
        # Filter by required Interests (simulating semantic matched categories)
        if constraints.get("required_interests"):
            # Check if any of the required interests are in the user's interests (separated by |)
            interest_pattern = '|'.join(constraints['required_interests'])
            filtered_df = filtered_df[filtered_df['Interests'].str.contains(interest_pattern, case=False, na=False)]
            
        # Filter out excluded Interests
        if constraints.get("excluded_interests"):
            exclude_pattern = '|'.join(constraints['excluded_interests'])
            filtered_df = filtered_df[~filtered_df['Interests'].str.contains(exclude_pattern, case=False, na=False)]
            
        return filtered_df
        
    def predictive_ranking(self, candidates_df):
        """
        Uses Predictive ML Model ranking (XGBoost) to score candidates.
        """
        if candidates_df.empty:
            return candidates_df
            
        # Prepare features for candidates
        X_candidates = candidates_df[['Attendance_Rate', 'Physical_Score', 'Membership_Status', 'Past_Events', 'Distance_KM']].copy()
        
        le = self.label_encoders['Membership_Status']
        # Map known labels
        X_candidates['Membership_Status'] = X_candidates['Membership_Status'].map(
            lambda s: le.transform([s])[0] if s in le.classes_ else -1
        )
        
        # Calculate ML Score via XGBoost prediction
        # Output limits depending on target representation
        candidates_df['ML_Score'] = self.model.predict(X_candidates)
        
        # Sort by best rank
        ranked_df = candidates_df.sort_values(by="ML_Score", ascending=False)
        return ranked_df

# For testing
if __name__ == "__main__":
    # Test the reasoning layer
    reasoning = AIReasoningLayer("volunteers_dataset.csv")
    
    test_input = "I want to invite people for a cleanliness drive in Pittsburgh."
    params = reasoning.process_user_input(test_input)
    
    feedback = "Must include Youth interest and max age should be 55"
    updated = reasoning.apply_feedback(params, feedback)
    
    print("\n✅ Reasoning Layer test completed successfully!")