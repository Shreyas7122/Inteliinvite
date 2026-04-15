from flask import Flask, request, jsonify
from flask_cors import CORS
from reasoning_layer import AIReasoningLayer, VolunteerMatcher
import math

app = Flask(__name__)
CORS(app) # Allow React frontend to access the API securely

dataset_path = "volunteers_dataset.csv"
print("Initializing Logic & Training ML Model globally...")
reasoning = AIReasoningLayer(dataset_path)
matcher = VolunteerMatcher(dataset_path)

@app.route('/api/match', methods=['POST'])
def match():
    data = request.json
    sentence = data.get("sentence", "")
    feedback_rules = data.get("feedback", [])

    # 1 & 2. Intent Extraction & Constraint Inference
    structured_params = reasoning.process_user_input(sentence)

    # 4. Feedback Loop Application
    # Apply any feedback constraints iteratively
    for rule in feedback_rules:
        structured_params = reasoning.apply_feedback(structured_params, rule)

    # 3. Retrieval & Ranking Stage
    candidates_df = matcher.semantic_retrieval(structured_params)
    ranked_df = matcher.predictive_ranking(candidates_df)

    # Process Top 5 for the frontend UI format
    top_candidates = []
    if not ranked_df.empty:
        top_5 = ranked_df.head(5)
        for _, row in top_5.iterrows():
            top_candidates.append({
                "id": row['Volunteer_ID'],
                "age": int(row['Age']),
                "distance": f"{row['Distance_KM']:.2f} km",
                "interests": [str(x) for x in row['Interests'].split('|') if x],
                "score": float(row['ML_Score']) if not math.isnan(row['ML_Score']) else 0.0
            })

    # Output to the Frontend
    return jsonify({
        "inferred_constraints": structured_params,
        "total_matched": len(candidates_df),
        "candidates": top_candidates
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
