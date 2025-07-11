import time
import json
import pytest

from src.answer_generator import AnswerGenerator

# Test queries with expected condition keywords
test_cases = [
    ("I’m sweating, shaky, and my glucometer reads 55 mg/dL—what should I do right now?", "Diabetes - Hypoglycaemia"),
    ("My diabetic father just became unconscious; we think his sugar crashed. What immediate first-aid should we give?", "Diabetes - Hypoglycaemia"),
    ("A pregnant woman with gestational diabetes keeps getting fasting readings around 130 mg/dL. What does this mean and how should we manage it?", "Diabetes - Gestational"),
    ("Crushing chest pain shooting down my left arm—do I chew aspirin first or call an ambulance?", "Cardiac - Myocardial infarction"),
    ("I’m having angina; how many nitroglycerin tablets can I safely take and when must I stop?", "Cardiac - Angina"),
    ("Grandma has chronic heart failure, is suddenly short of breath, and her ankles are swelling. Any first-aid steps before we reach the ER?", "Cardiac - Heart failure"),
    ("After working in the sun all day I’ve barely urinated and my creatinine just rose 0.4 mg/dL—could this be acute kidney injury and what should I do?", "Renal - AKI"),
    ("CKD patient with a potassium level of 6.1 mmol/L—what emergency measures can we start right away?", "Renal - Hyperkalaemia"),
    ("I took ibuprofen for back pain; now my flanks hurt and I’m worried about kidney damage—any immediate precautions?", "Renal - AKI"),
    ("Type 2 diabetic, extremely thirsty, glucose meter says ‘HI’ but urine ketone strip is negative—what’s happening and what’s the first-aid?", "Diabetes - Type 2")
]

# Store results for final report
test_results = []
total_latency = 0
total_tokens = 0

@pytest.mark.parametrize("query,expected_condition", test_cases)
def test_answer_generation(query, expected_condition):
    global total_latency, total_tokens
    ag = AnswerGenerator()

    result_data = {
        "query": query,
        "expected_condition": expected_condition,
    }

    try:
        start_time = time.time()
        final_answer, predicted_condition, evidence_used = ag.generate_answer(query)
        latency = time.time() - start_time

        triage_match = expected_condition.lower() in predicted_condition.lower()
        word_count = len(final_answer.split())
        disclaimer_ok = "educational purposes only" in final_answer.lower()
        citation_ok = any(e.get("citation_label") in final_answer for e in evidence_used)

        token_usage = len(query.split()) + word_count + 20

        result = triage_match and word_count <= 250 and disclaimer_ok and citation_ok
        status = "PASS" if result else "FAIL"

        # Store per test
        result_data.update({
            "predicted_condition": predicted_condition,
            "word_count": word_count,
            "disclaimer_present": disclaimer_ok,
            "citation_found": citation_ok,
            "latency_seconds": latency,
            "token_usage": token_usage,
            "status": status
        })

        total_latency += latency
        total_tokens += token_usage

        assert triage_match, "Triage mismatch"
        assert word_count <= 250, "Too many words"
        assert disclaimer_ok, "Missing disclaimer"
        assert citation_ok, "Missing citation"

    except Exception as e:
        result_data.update({
            "error": str(e),
            "status": "ERROR"
        })
        raise e  # Reraise for pytest to register the test as failed

    finally:
        test_results.append(result_data)


def teardown_module(module):
    # Called once after all tests
    summary = {
        "total_passed": sum(1 for r in test_results if r["status"] == "PASS"),
        "total_tests": len(test_results),
        "accuracy_percent": round(sum(1 for r in test_results if r["status"] == "PASS") / len(test_results) * 100, 2),
        "average_latency_seconds": round(total_latency / len(test_results), 2),
        "average_token_usage": round(total_tokens / len(test_results), 2),
        "known_limitations": [
            "Gemini may hallucinate slightly varied condition names.",
            "Fallback rule-based method limited by fixed keyword set.",
            "Citations must be manually validated for relevance."
        ]
    }

    final_report = {
        "test_results": test_results,
        "summary": summary
    }

    output_path = "triage_test_report.json"
    with open(output_path, "w") as f:
        json.dump(final_report, f, indent=4)

    print(f"\n📄 Test results saved to `{output_path}`\n")
