import pandas as pd
import json
import re
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------
# 2. AI REASONING LAYER
# ---------------------------------------------------------

class AIReasoningLayer:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        # Event dictionary to map natural language concepts to structured interests/categories
        self.event_dictionary = {
            "cleanliness drive": ["Environment"],
            "medical camp": ["Health"],
            "teaching": ["Education", "Youth"],
            "disaster relief": ["Disaster Response"],
            "peace march": ["Peace", "Youth"]
        }
    
    def process_user_input(self, text_input):
        """
        Main pipeline for processing user input into structured parameters.
        Includes:
        - LLM Intent & Entity Extraction (simulated here for demonstration)
        - Event Dictionary Lookup
        - Constraint Inference
        """
        print(f"Processing Input: '{text_input}'")
        
        # 2a. LLM Intent & Entity Extraction
        entities = self._llm_extract_entities(text_input)
        
        # 2b. Event Dictionary Lookup
        inferred_interests = []
        for keyword, interests in self.event_dictionary.items():
            if keyword in text_input.lower():
                inferred_interests.extend(interests)
        
        if not inferred_interests and "event_type" in entities:
             # Fallback lookup
             for keyword, interests in self.event_dictionary.items():
                if keyword in entities["event_type"].lower():
                    inferred_interests.extend(interests)

        # 2c. Constraint Inference
        constraints = self._infer_constraints(entities, inferred_interests)
        
        return constraints

    def _llm_extract_entities(self, text):
        """
        Simulates an LLM call parsing the request into entities.
        In a real scenario, this would use google-generativeai, OpenAI, etc.
        """
        # Mocking an LLM response based on expected inputs
        text_lower = text.lower()
        entities = {}
        
        # Simple heuristic extraction for demonstration
        if "cleanliness drive" in text_lower:
            entities["event_type"] = "cleanliness drive"
        elif "medical" in text_lower:
             entities["event_type"] = "medical camp"
        
        if "pittsburgh" in text_lower:
            entities["location"] = "Pittsburgh"
            
        return entities

    def _infer_constraints(self, entities, inferred_interests):
        """
        Combines extracted entities and dictionary lookups into solid constraints
        for the Retrieval stage.
        """
        constraints = {
            "max_distance_km": 50, # Default assumption: 50km
            "required_interests": inferred_interests,
            "max_age": None,
            "min_physical_score": 5 # Default
        }
        
        # Infering extra constraints
        if "cleanliness drive" in entities.get("event_type", ""):
            # Cleanliness drives require some physical activity, maybe limit age or require high physical score
            constraints["max_age"] = 60
            constraints["min_physical_score"] = 6
            constraints["max_distance_km"] = 40 # People might not travel too far for it
        
        print("Inferred Constraints:", json.dumps(constraints, indent=2))
        return constraints
        
    def apply_feedback(self, constraints, feedback_text):
        """
        4. FEEDBACK LOOP
        Takes user feedback, parses intent, and updates the structured semantic constraints natively.
        """
        print(f"\n[FEEDBACK] Evaluating Constraint Rule: '{feedback_text}'")
        text_lower = feedback_text.lower()
        
        # Check for max age constraint using regex
        age_match = re.search(r'max(?:imum)?\s*age\s*(?:should\s*be|is|=)?\s*(\d+)', text_lower)
        if age_match:
            constraints["max_age"] = int(age_match.group(1))
            print(f">> Learned Semantic Constraint: Updated max_age to {constraints['max_age']}.")
            
        is_negation = any(neg in text_lower for neg in ["do not", "don't", "exclude", "no ", "without"])
        
        categories = {
            "youth": "Youth",
            "health": "Health", 
            "peace": "Peace",
            "environment": "Environment",
            "disaster": "Disaster Response"
        }
        
        for kw, category in categories.items():
            if kw in text_lower:
                if is_negation:
                    if "excluded_interests" not in constraints:
                        constraints["excluded_interests"] = []
                    if category not in constraints["excluded_interests"]:
                        constraints["excluded_interests"].append(category)
                    print(f">> Learned Semantic Constraint: Excluded '{category}' interest.")
                    
                    if category in constraints.get("required_interests", []):
                        constraints["required_interests"].remove(category)
                else:
                    if "required_interests" not in constraints:
                        constraints["required_interests"] = []
                    if category not in constraints["required_interests"]:
                        constraints["required_interests"].append(category)
                    print(f">> Learned Semantic Constraint: Required '{category}' interest added.")

        print("Updated Constraints:", json.dumps(constraints, indent=2))
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

def main():
    dataset_csv = "volunteers_dataset.csv"
    
    # 1. User Input
    user_request_1 = "I want to invite people for a cleanliness drive in Pittsburgh."
    
    # 2. AI Reasoning
    reasoning = AIReasoningLayer(dataset_csv)
    structured_params = reasoning.process_user_input(user_request_1)
    
    # 3. Retrieval & Ranking
    matcher = VolunteerMatcher(dataset_csv)
    
    candidates = matcher.semantic_retrieval(structured_params)
    print(f"\nCandidates after Semantic Retrieval: {len(candidates)}")
    
    ranked_candidates = matcher.predictive_ranking(candidates)
    
    top_n = 5
    print(f"\n--- TOP {top_n} RECOMMENDED VOLUNTEERS ---")
    print(ranked_candidates[['Volunteer_ID', 'Age', 'Distance_KM', 'Interests', 'ML_Score']].head(top_n))

    # 4. Feedback Loop (Model Interaction Simulation)
    # Simulating a user clicking "❌ Refine & Retrain" and typing "Must include Youth interest"
    feedback_input = "Must include Youth interest"
    
    # Update AI parameters natively (Compassion for semantic update arrow)
    updated_params = reasoning.apply_feedback(structured_params, feedback_input)
    
    # Step 3 Loop: Re-run with the updated constraints
    refined_candidates = matcher.semantic_retrieval(updated_params)
    refined_ranked = matcher.predictive_ranking(refined_candidates)
    
    print(f"\nCandidates after Applying Feedback: {len(refined_candidates)}")
    print(f"\n--- TOP {top_n} RECOMMENDATIONS (REFINED) ---")
    print(refined_ranked[['Volunteer_ID', 'Age', 'Distance_KM', 'Interests', 'ML_Score']].head(top_n))

if __name__ == "__main__":
    main()
