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
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    def _condition_json_to_list(self):

        file_path = 'E:\ResQ\FirstResQ\data\conditions.json'
        with open(file_path, 'r') as file:
            data = json.load(file)
        flat_list = [f"{category} - {subcategory}" for category, sublist in data.items() for subcategory in sublist]
        return flat_list

    def classify_sympton(self, symptom_text: str) -> str:
        text = symptom_text.lower()

        rules = {
            "Diabetes - Hypoglycaemia": ["shaky", "sweating", "low sugar", "55 mg/dl", "glucometer"],
            "Diabetes - Ketoacidosis": ["thirsty", "acid", "ketones", "dka"],
            "Diabetes - Gestational": ["pregnant", "gestational", "130 mg/dl", "fasting"],
            "Diabetes - Type 1": ["type 1", "insulin dependent"],
            "Diabetes - Type 2": ["type 2", "non insulin"],
            "Cardiac - Myocardial infarction": ["chest pain", "left arm", "aspirin", "crushing"],
            "Cardiac - Angina": ["tightness", "relieved by rest", "exertion", "chest discomfort"],
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

        # Find top scoring condition
        top_condition = max(scores, key=scores.get)

        if scores[top_condition] == 0:
            return "Unknown"

        return top_condition

    def gemini_fallback(self, symptom_text:str) -> str:
        conditions=self._condition_json_to_list()

        prompt=f""""
        You are a medical triage assistant.
        Based on the patient's symptom description, infer the most likely medical emergency condition.
        Choose the best match only from the list below. If multiple could match, return the most urgent one.
        Do not explain. Respond only with the condition name.
        
        Symptom:
        {symptom_text}
        
        Condition List:
        {conditions}
        
        """

        response = self.model.generate_content(prompt)

        return response.text

    def classify_symptom(self, symptom_text):
        Condition=self.classify_sympton(symptom_text)
        if Condition == "Unknown":
            try:
                Condition = self.gemini_fallback(symptom_text)
            except Exception as e:
                print(f"Gemini failed: {e}")
                Condition = "Unknown"
        return Condition






if __name__ == "__main__":
    triag=traiger()
    query= "Im shaky sweating, and my glucometer reads 55 mg/dL"
    print(triag.classify_symptom(query))