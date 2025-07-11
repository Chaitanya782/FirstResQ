# 🌺 AI-Powered First-Aid Assistant

A Retrieval-Augmented Generation (RAG) system built with Gemini Flash 1.5, LangChain, FAISS, and Serper.dev to provide accurate, cited, and fast first-aid advice for medical symptom queries.

---

## 📁 Project Structure

```
project-root/
├── src/                        # Core modules
│   ├── triage_module.py       # Symptom classification (fallback + Gemini)
│   ├── data_aggregator.py     # Concurrent local + web evidence retriever
│   ├── embed_local_corpus.py  # Embed the local corpus
│   ├── local_retriever.py     # FAISS index interface
│   ├── web_retriever.py       # Serper + Gemini query optimizer
│   ├── relevance_ranker.py    # Keyword-based fusion + citation labeling
│   ├── answer_generator.py    # Gemini-based final answer engine
├── data/                      # FAISS index, JSONs, test corpora
├── tests/                     # Pytest-based evaluations
│   └── test_external_cases.py
├── streamlit_app.py           # Optional local UI (Streamlit)
├── requirements.txt           # All dependencies
├── .env.example               # Sample environment file
├── architecture.png           # System diagram
├── performance.md             # Latency + accuracy results
└── README.md                  # You are here
```

---

## 🚀 How to Run

### 🔧 1. Setup Environment

```bash
pip install -r requirements.txt
cp .env.example .env  # Fill with your API keys
```

### 🔑 Required Keys in `.env`

```
GEMINI_API_KEY=your-google-key
SERPER_KEY=your-serper-api-key
```

### 🧠 2. Build or Load FAISS Index (Optional)

```bash
python scripts/build_faiss.py  # if index not prebuilt
```

### 🧪 3. Run External Evaluation

```bash
python tests/test_external_cases.py
```

### 🖥️ 4. Launch the UI

```bash
streamlit run streamlit_app.py
```

---

## 🧱 Architecture Overview

**Pipeline:**

1. Symptom query classified via `triage_module.py`
2. Local RAG (FAISS) + Web search run in parallel
3. Evidence ranked using keyword match + domain priority
4. Gemini prompt constructed with citations (\[1], \[2], ...)
5. Output generated, wrapped, and rendered with source links

---

## 💡 Design Choices

| Area         | Decision                                                                  |
| ------------ | ------------------------------------------------------------------------- |
| Model        | Gemini Flash 1.5 (`gemini-2.5-flash`) for fast and factual generation     |
| Retrieval    | LangChain + FAISS for fast in-memory RAG; Serper.dev for live fallback    |
| Concurrency  | `ThreadPoolExecutor` used over `asyncio` for simplicity with blocking I/O |
| Prompt Style | Structured, warm tone, ≤ 250 words, always includes disclaimer            |
| Citations    | Gemini uses \[1], \[2], mapped to real sources with links post-generation |

---

## 📊 Performance Summary

| Metric                        | Result             |
| ----------------------------- | ------------------ |
| Total Tests Run               | 10                 |
| Correct Triage Classification | 9 / 10 ✅           |
| Useful First-Aid Advice       | 10 / 10 ✅          |
| Citations Present             | 10 / 10 ✅          |
| Under 250 Words               | 10 / 10 ✅          |
| Disclaimer Present            | 10 / 10 ✅          |
| Average Latency               | 15.77 sec          |
| Average Token Usage (est.)    | \~182 tokens/query |
| Overall Pass Rate             | ✅ **90%**          |

---

## ⚠️ Known Limitations

* Fallback rule-based triage is limited by static keyword matching.
* Citations must be manually reviewed to ensure clinical relevance.
* Web sources may include non-medical blogs or lower-trust domains.
* No critical alerting mechanism for red-flag terms (like unconscious).
* Token usage and latency may vary slightly per query.

---

## 🤝 Credits

* Gemini Flash 1.5
* LangChain + FAISS
* Serper.dev for Google search
* OpenAI-style citation patterns

---

## 📜 License

MIT (modify as needed for academic use)

---

**Built with care for better, faster medical guidance. Not a substitute for professional care.**
