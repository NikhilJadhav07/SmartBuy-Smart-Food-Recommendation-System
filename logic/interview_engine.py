import json
import os
from logic.neural_inference_engine import NeuralInferenceEngine
from logic.recommendation_engine import RecommendationEngine

class InterviewEngine:
    def __init__(self):
        # Load Questions from JSON
        self.question_db = self._load_questions()
        
        # Initialize sub-engines
        self.inference_engine = NeuralInferenceEngine()
        self.recommendation_engine = RecommendationEngine()

    def _load_questions(self):
        try:
            # Adjust path relative to where app.py runs
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, 'data', 'questions.json')
            
            if not os.path.exists(file_path):
                print(f"Questions file not found: {file_path}")
                return {"questions": {}, "flow_order": []}

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading questions: {e}")
            return {"questions": {}, "flow_order": []}

    def get_first_question(self, user=None, profile_context=None):
        """
        Determines the entry point. Uses UserMentalProfile if available.
        """
        if profile_context:
             # Use aggregated profile data
             condition = profile_context.get('dominant_condition')
             risk = profile_context.get('risk_level')
             
             if condition and risk in ['Moderate', 'High']:
                 return {
                    "id": "profile_checkin",
                    "text": f"Based on your history, I know {condition.lower()} has been a challenge. Is that weighing on you today?",
                    "type": "choice",
                    "options": ["Yes, heavily", "A little", "No, I'm okay", "It's something else"],
                    "category": condition,
                    "is_past_reference": True,
                    "next_logic": {
                        "Yes, heavily": "start", # Logic to jump to specific section could be added
                        "A little": "start",
                        "No, I'm okay": "start",
                        "It's something else": "start",
                        "default": "start"
                    }
                }

        if user and user.is_authenticated:
            # Check for high-risk conditions from last session (Fallback if no profile context passed)
            from models import AssessmentResult
            last_assessment = AssessmentResult.query.filter_by(user_id=user.id).order_by(AssessmentResult.created_at.desc()).first()
            if last_assessment and last_assessment.data:
                preds = last_assessment.data.get('predictions', [])
                if preds and preds[0]['probability'] > 60:
                    condition = preds[0]['condition']
                    return {
                        "id": "past_followup",
                        "text": f"Last time we talked, you mentioned feeling {condition.lower()}. How has that been lately?",
                        "type": "statement",
                        "category": "Follow-up",
                        "is_past_reference": True,
                        "next_logic": {"yes": "start", "no": "start", "default": "start"}
                    }

        if not self.question_db.get("flow_order"):
            return None
        start_id = self.question_db["flow_order"][0]
        return self.question_db["questions"].get(start_id)

    def get_next_question(self, current_answers, selected_regions=None, user=None, profile_context=None):
        """
        Determines the next question based on answers, selected regions, and user history.
        """
        questions = self.question_db.get("questions", {})
        selected_regions = selected_regions or []
        
        # 1. Calculate real-time scores to see if we need a "Deep Dive"
        current_results = self.inference_engine.calculate_scores(current_answers, self.question_db)
        top_prediction = current_results['predictions'][0] if current_results['predictions'] else None
        
        # 2. Identify the last answered question
        if not current_answers:
            # If user selected regions, start with the first region-specific question
            if selected_regions:
                for q_id, q_def in questions.items():
                    if q_def.get("region") == selected_regions[0]:
                        return q_def
            return self.get_first_question(user, profile_context)
             
        try:
            last_q_id = list(current_answers.keys())[-1]
            last_answer = current_answers[last_q_id]
        except (IndexError, AttributeError, KeyError):
            return self.get_first_question(user, profile_context)
        
        # Special handling for injected follow-ups
        if last_q_id in ["past_followup", "profile_checkin"]:
            # If they said "It's something else", maybe just go to start
            return questions.get("start")

        last_q_def = questions.get(last_q_id)
        if not last_q_def:
            # Might be a dynamic question not in JSON
            return questions.get("start")
            
        next_q_id = None
        
        # 3. Dynamic Branching: If a condition is spiking, prioritize it
        if top_prediction and top_prediction['probability'] > 40:
             # Check if we have more questions for this specific spiking condition
             # that haven't been asked yet
             for q_id, q_def in questions.items():
                 if q_def.get("category") == top_prediction['condition'] and q_id not in current_answers:
                     # Add an empathetic transition
                     next_q = q_def.copy()
                     next_q['empathy_prefix'] = self._get_empathy_statement(top_prediction['condition'])
                     return next_q
        
        # 3b. Profile-based Branching (if no immediate spike)
        if profile_context and not next_q_id:
             dom_condition = profile_context.get('dominant_condition')
             if dom_condition:
                 # Try to find a relevant question for their chronic condition
                 for q_id, q_def in questions.items():
                     if q_def.get("category") == dom_condition and q_id not in current_answers:
                         # Only inject occasionally or if it seems relevant (simple heuristic here)
                         import random
                         if random.random() < 0.3: # 30% chance to steer conversation to chronic issue
                             next_q = q_def.copy()
                             next_q['empathy_prefix'] = f"Given what you've faced with {dom_condition.lower()} before..."
                             return next_q

        # 3c. Region-based prioritization
        if selected_regions and not next_q_id:
            for region in selected_regions:
                for q_id, q_def in questions.items():
                    if q_def.get("region") == region and q_id not in current_answers:
                        return q_def

        # 4. Handle Standard Branching Logic
        if "next_logic" in last_q_def:
            logic = last_q_def["next_logic"]
            next_q_id = logic.get(last_answer, logic.get("default"))
        elif "next" in last_q_def:
            next_q_id = last_q_def["next"]
        
        # 5. Return the next question or None if finished
        if next_q_id and next_q_id != "finish":
            return questions.get(next_q_id)

        # 6. If the natural flow ends, check if we have other selected regions to cover
        # Find which regions we have already touched
        touched_regions = set()
        for q in current_answers:
            q_def = questions.get(q)
            if q_def and q_def.get("region"):
                touched_regions.add(q_def.get("region"))
        
        # Find the next selected region that hasn't been touched
        next_region = None
        if selected_regions:
            for region in selected_regions:
                if region not in touched_regions:
                    next_region = region
                    break
        
        # If we found a new region to switch to, find its first question
        if next_region:
            for q_id, q_def in questions.items():
                if q_def.get("region") == next_region:
                    return q_def
        
        return None

    def _get_empathy_statement(self, condition):
        import random
        statements = [
            f"I hear that you're dealing with some {condition.lower()} right now. It takes strength to talk about it.",
            f"Thank you for sharing that. Managing {condition.lower()} can be really tough.",
            f"I appreciate you being open. Let's look a bit deeper into these {condition.lower()} feelings.",
            "I'm here to listen. Tell me more about that."
        ]
        return random.choice(statements)


    def calculate_results(self, answers, user=None, symptoms=None):
        """
        Delegates to InferenceEngine and adds Recommendations.
        """
        # 1. Calculate Scores & XAI
        try:
            user_id = user.id if user and user.is_authenticated else None
            results = self.inference_engine.calculate_scores(answers, self.question_db, user_id=user_id)
        except Exception as e:
            print(f"Inference Engine Error: {e}")
            results = {"predictions": [], "status": "Green", "raw_scores": {}}
        
        # 2. Get Recommendations
        advice = []
        try:
            advice = self.recommendation_engine.get_recommendations(results.get("predictions", []))
        except Exception as e:
            print(f"Recommendation Engine Error: {e}")
            advice = ["Please consult with a professional therapist for personalized guidance."]
        
        # 3. Merge
        results["recommendations"] = advice
        
        # 4. Add user answers with questions for display
        user_answers = []
        questions = self.question_db.get("questions", {})
        for q_id, answer_value in answers.items():
            question_def = questions.get(q_id)
            if question_def:
                # Format the answer nicely
                answer_text = self._format_answer(answer_value, question_def)
                user_answers.append({
                    "question": question_def.get("question", question_def.get("text", "")),
                    "answer": answer_text
                })
        
        results["user_answers"] = user_answers

        # 5. Generate Personalized Summary
        results["personalized_summary"] = self._generate_personalized_summary(results, symptoms)
        
        return results

    def _format_answer(self, answer_value, question_def):
        """
        Format the answer value into a readable string.
        """
        # For statement questions (yes/no)
        if question_def.get("type") == "statement":
            if answer_value == "yes":
                return "Yes"
            elif answer_value == "no":
                return "No"
            elif answer_value == "dk":
                return "I'm not sure"
            return str(answer_value).capitalize()
        
        # For questions with options, find the matching option text
        if "options" in question_def:
            for opt in question_def.get("options", []):
                if isinstance(opt, dict):
                    if opt.get("value") == answer_value or opt.get("val") == answer_value:
                        return opt.get("text", str(answer_value))
        
        # Default: return the value as-is
        return str(answer_value)

    def _generate_personalized_summary(self, results, input_symptoms):
        """
        Generates a calm, non-diagnostic summary based on scored data.
        """
        import random
        
        predictions = results.get('predictions', [])
        if not predictions:
            return {
                "title": "You seem to be doing well",
                "content": "Our analysis didn't detect any significant patterns of concern based on your responses. Continue prioritizing your well-being.",
                "tips": ["Maintain your current routine", "Stay connected with friends"]
            }

        # 1. Identify Dominant Category
        top_pred = predictions[0]
        category = top_pred['condition']
        severity = top_pred['severity']
        probability = top_pred['probability']

        # 2. Key Contributing Symptoms
        # Combine input symptoms (Phase 1) and answers (Phase 2)
        contributing_factors = []
        if input_symptoms:
            contributing_factors.extend([s for s in input_symptoms if s])
        
        # Check user answers for "Yes" or high-value responses if needed, 
        # but for now we'll rely on the input_symptoms + generic "current feelings"
        
        # Limit to 3 formatted factors
        factors_text = ""
        if contributing_factors:
            selected_factors = contributing_factors[:3]
            if len(selected_factors) > 1:
                factors_text = f", specifically related to {', '.join(selected_factors[:-1])} and {selected_factors[-1]}"
            else:
                factors_text = f", specifically regarding {selected_factors[0]}"

        # 3. Pattern Description (Psychological Terms, Non-Diagnostic)
        # Templates for different categories
        patterns = {
            "Anxiety": [
                "a pattern of heightened alertness and anticipation",
                "a tendency for your mind to over-prepare for future outcomes",
                "a state of elevated nervous system arousal"
            ],
            "Depression": [
                "a pattern of reduced emotional energy",
                "a temporary withdrawal from usual interests",
                "a state of emotional conservation"
            ],
            "Burnout": [
                "signs of systemic exhaustion",
                "a natural response to prolonged high-demand situations",
                "a signal that your energy reserves are depleted"
            ],
            "Panic Disorder": [
                "intense surges of physical and emotional responsiveness",
                "a heightened sensitivity to bodily sensations"
            ],
            "Stress": [
                "a reaction to accumulating daily pressures",
                "a sign of carrying a heavy mental load"
            ],
            "General": [
                "some variations in your emotional equilibrium",
                "shifts in your usual mood patterns"
            ]
        }
        
        cat_key = category if category in patterns else "General"
        description = random.choice(patterns[cat_key])

        # 4. Construct the Narrative
        summary_text = (
            f"Based on your responses, we've noticed {description}. "
            f"This appears to be the most dominant pattern right now{factors_text}. "
            f"It's important to remember that this is a common human response, not a permanent label."
        )

        # 5. Targeted Coping Suggestions
        coping_strategies = {
            "Mild": [
                "incorporating small 5-minute improvements to your daily routine",
                "practicing mindful breathing when you feel tension rising",
                "sharing your thoughts with a friend or journal"
            ],
            "Moderate": [
                "establishing structured boundaries for rest and work",
                "using grounding techniques (like the 5-4-3-2-1 exercise) during tough moments",
                "considering a chat with a counselor to unpack these feelings"
            ],
            "High": [
                "prioritizing immediate self-care and reducing daily demands",
                "reaching out to a support professional for guided strategies",
                "accepting support from those around you as a strength, not a weakness"
            ],
            "Severe": [
                "speaking with a healthcare professional as a priority",
                "focusing strictly on essential daily tasks and rest",
                "allowing yourself to pause and seek active support"
            ]
        }
        
        severity_key = severity if severity in coping_strategies else "Moderate"
        suggestion = random.choice(coping_strategies[severity_key])
        
        return {
            "title": f"Observing {category}",
            "severity": severity,
            "content": summary_text,
            "suggestion": f"We recommend {suggestion}."
        }

