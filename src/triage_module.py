import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()


class traiger():
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    def _condition_json_to_list(self):

        file_path = 'E:\ResQ\FirstResQ\data\conditions.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        flat_list = [f"{category} - {subcategory}" for category, sublist in data.items() for subcategory in sublist]
        return flat_list

    def classify_issue(self, symptom_text: str):
        text = symptom_text.lower()
        rules = {
            "Diabetes - Hypoglycaemia": ["shaky", "sweating", "low sugar", "55 mg/dl", "glucometer"],
            "Diabetes - Ketoacidosis": ["thirsty", "acid", "ketones", "dka", "hi", "fruity breath"],
            "Diabetes - Gestational": ["pregnant", "gestational", "130 mg/dl", "fasting"],
            "Diabetes - Type 1": ["type 1", "insulin dependent"],
            "Diabetes - Type 2": ["type 2", "non insulin", "glucose meter", "high sugar"],
            "Cardiac - Myocardial infarction": ["chest pain", "left arm", "aspirin", "crushing", "radiating"],
            "Cardiac - Angina": ["tightness", "relieved by rest", "exertion", "chest discomfort", "angina",
                                 "nitroglycerin"],
            "Cardiac - Arrhythmia": ["flutter", "palpitations", "irregular heartbeat"],
            "Cardiac - Heart failure": ["swollen ankles", "fluid", "short of breath", "elderly"],
            "Renal - AKI": ["creatinine", "urine", "dehydration", "flank pain", "acute"],
            "Renal - CKD": ["chronic", "long-standing", "kidney disease", "creatinine high"],
            "Renal - Hyperkalaemia": ["potassium", "6.1", "ekg", "tall t wave"],
            "Renal - Dialysis crises": ["dialysis", "missed", "dry mouth", "nausea", "fatigue"]
        }

        scores = {condition: 0 for condition in rules}
        for condition, keywords in rules.items():
            for keyword in keywords:
                if keyword in text:
                    scores[condition] += 1

        max_score = max(scores.values())
        if max_score == 0:
            return "Unknown", scores

        top_conditions = [cond for cond, score in scores.items() if score == max_score]

        # If multiple conditions have the same score, let Gemini decide
        if len(top_conditions) > 1:
            return "Ambiguous", scores
        return top_conditions[0], scores

    def gemini_fallback(self, symptom_text: str) -> str:
        conditions = self._condition_json_to_list()

        prompt = f"""
        You are a medical triage assistant.
        Based on the patient's symptoms, select the most likely and urgent condition.
        Only choose from the list provided.
        Respond **only** with the exact condition name from the list.
    
        Symptoms:
        {symptom_text}
    
        Condition List:
        {conditions}
        """

        response = self.model.generate_content(prompt)
        return response.text.strip()

    def classify_symptom(self, symptom_text):
        condition, scores = self.classify_issue(symptom_text)

        if condition == "Unknown" or condition == "Ambiguous":
            try:
                condition = self.gemini_fallback(symptom_text).strip()
            except Exception as e:
                print(f"Gemini failed: {e}")
                condition = "Unknown"

        return condition


if __name__ == "__main__":
    triag=traiger()
    query= "Im shaky sweating, and my glucometer reads 55 mg/dL"
    print(triag.classify_symptom(query))