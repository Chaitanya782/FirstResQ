# 🧱 Architecture of AI-Powered First-Aid Assistant

This document outlines the architecture of the First-Aid Assistant RAG system.

---

## 🔄 System Flow

```text
[ User Query ]
      ↓
Triage Classification (triage_module.py)
      ↓
+----------------------------+
| Concurrent Evidence Fetch |
+----------------------------+
       ↓                        ↓
Local FAISS Search     Web Search (Serper.dev)
(local_retriever.py)     (web_retriever.py)
       ↓                        ↓
   FAISS Chunks         Gemini Query-Optimized Search
       ↓                        ↓
   Local Evidence        Web Evidence (Top 5 results)
        \                      /
         +--------------------+
         | Evidence Aggregator|
         | (data_aggregator.py) |
         +--------------------+
                   ↓
        Keyword Relevance Ranker (relevance_ranker.py)
                   ↓
     Gemini Answer Generator (answer_generator.py)
                   ↓
     Final Answer (≤250 words + citations + disclaimer)
                   ↓
      [ Streamlit UI or CLI Output ]
```

---

## 🔧 Module Responsibilities

| Module                | Function                                                                |
| --------------------- | ----------------------------------------------------------------------- |
| `triage_module.py`    | Classifies condition using fallback rules + Gemini                      |
| `local_retriever.py`  | Loads FAISS index + retrieves k-nearest matches                         |
| `web_retriever.py`    | Builds Gemini search query → queries Serper.dev → extracts evidence     |
| `data_aggregator.py`  | Concurrently runs local + web and merges them                           |
| `relevance_ranker.py` | Scores all evidence chunks using keywords/domain heuristics             |
| `answer_generator.py` | Prompts Gemini to generate answer based on query + condition + evidence |

---

## ☁️ External Dependencies

* **Gemini Flash 1.5** — for triage + final answer generation
* **FAISS + LangChain** — for semantic local search
* **Serper.dev** — Google search API wrapper

---

## 💡 Notes

* All results are cited using \[1], \[2] style and shown in final output.
* Citations include local sentences or original URLs from web sources.
* Prompt strictly instructs Gemini not to hallucinate or fabricate sources.
* All logic is preloaded (no runtime FAISS rebuilding).
* Parallel web/local search ensures responsiveness < 15 sec total.

---

## 🧪 Future Extensions

* Add real-time alert system for red-flag cases
* Train local mini-RAG model for offline fallback
* Add PDF/Email export of answers

---

> Last updated: July 2025
