import os
import json

def log_mismatch_case(query, original_condition, verified_condition, answer, evidence_list):
    log_dir = "error_log"

    os.makedirs(log_dir, exist_ok=True)

    log_data = {
        "query": query,
        "original_condition": original_condition,
        "verified_condition": verified_condition,
        "final_answer": answer,
        "evidence_used": evidence_list
    }

    log_path = os.path.join(log_dir, "mismatches.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
