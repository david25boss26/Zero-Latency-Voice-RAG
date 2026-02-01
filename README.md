# Zero-Latency-Voice-RAG
Real-Time Voice-Based Retrieval-Augmented Generation for Technical Support

#📌 Project Overview
This project implements a Zero-Latency Voice-Driven Retrieval-Augmented Generation (RAG) system designed to simulate a real-world technical support assistant for enterprise hardware manuals (e.g., Dell PowerEdge servers).

The system supports:

🎙️ Real-time voice input (ASR simulation)

⚡ Speculative retrieval while the user is still speaking

📚 Hybrid document search (FAISS + BM25)

🧠 Cross-encoder reranking

🗣️ Natural spoken responses using TTS

#🧠 Methodology
1️⃣ Problem Framing

Traditional RAG systems suffer from:

High latency

Blocking pipelines

Slow first token response

Poor conversational handling

This project solves that by introducing:

✅ Parallel execution
✅ Speculative retrieval
✅ Streaming input handling
✅ Voice-first interaction design



⏱️ Optimized Time-To-First-Byte (TTFB)

The goal is to minimize perceived latency while maintaining high answer accuracy.

#2️⃣ System Design Philosophy

The system is built around three principles:

⚡ 1. Parallelism Over Sequential Processing

Instead of:
User speaks → ASR → Retrieval → LLM → TTS

We do:
User speaks
   ↓
ASR streaming ──────┐
                     ├── Retrieval starts early
                     └── TTS prepares response

#🧠 2. Hybrid Retrieval for Accuracy
Single retrieval methods fail in edge cases.
So we use:

FAISS → semantic similarity

BM25 → keyword matching

Cross-Encoder → deep reranking

This ensures:
High recall
High precision
Robust performance on technical text

#🗣️ 3. Voice-First Output Design
Instead of dumping raw text:

Sentences are shortened
Technical terms are normalized
Output is optimized for speech clarity
Example:
PCIe → P C I express
iDRAC → eye-drack

#⚙️ Technical Architecture

User Voice
   ↓
ASR (Streaming)
   ↓
Speculative RAG Trigger
   ↓
Hybrid Search (FAISS + BM25)
   ↓
Cross-Encoder Reranking
   ↓
LLM Answer Generation
   ↓
Speech Optimization
   ↓
Text-to-Speech Output


#🧩 Component Breakdown
#📁 ingest/
File Purpose: 
parse_pdf.py -> Extracts text from manuals 
chunker.py -> Splits text into semantic chunks
build_index.py -> Builds FAISS + BM25 index

#📁 rag/
File Purpose: 
vector_search.py -> FAISS-based retrieval 
bm25_search.py -> Keyword search
reranker.py -> Cross-encoder ranking
hybrid.py -> Combines all retrieval logic

#📁 voice/
File Purpose:
asr_stream.py -> Simulates streaming ASR
tts_stream.py -> Async TTS using pyttsx3

#📁 core/
File Purpose: 
orchestrator.py -> Controls entire pipeline

#📄 demo.py
Entry point for running the system.

#🧠 Core Logic Explained
🔹 Speculative RAG
As soon as 4–5 words are detected:
RAG pipeline starts
Retrieval happens before user finishes speaking
Reduces perceived latency

🔹 Query Rewriting
Handles follow-ups like:
“What about the second one?”
“And that error?”

Uses:
Previous user query
Last retrieved documents

🔹 Reranking
Uses:
cross-encoder/ms-marco-MiniLM-L-6-v2
To score (query, passage) relevance accurately.

🔹 LLM Prompt Control
LLM is constrained to:
Use only retrieved context
Avoid hallucination
Answer in 2–4 short sentences
Be voice-friendly



#🧪 Setup Instructions
#✅ Step 1: Clone Repository
git clone https://github.com/david25boss26/Zero-Latency-Voice-RAG.git
cd Zero-Latency-Voice-RAG


#✅ Step 2: Create Virtual Environment
python -m venv venv
venv\Scripts\activate


#✅ Step 3: Install Dependencies
pip install -r requirements.txt


#✅ Step 4: Build Index
cd ingest
python chunker.py
python build_index.py


#✅ Step 5: Run System
python demo.py


#🎤 Example Interaction
User: my server shows error 46 and second light blinking

[ASR partial] my server shows
⚡ starting speculative RAG...

AI:
Error code 46 usually indicates a hardware communication issue.
The blinking second LED suggests a component initialization failure.
I recommend checking the system logs or reseating the affected module.


🚀 Performance Highlights
MetricResultTTFB~600–800 msRetrievalParallelResponseStreamingAccuracyHigh (reranked)Voice LatencyLow

👨‍💻 Author
David Sharma
AI Systems | Voice AI | Retrieval Engineering
GitHub:
👉 https://github.com/david25boss26

✅ Final Notes
This project demonstrates:

Real-world RAG design
Low-latency AI systems
Production-grade architecture
Voice-first AI interaction
Advanced async orchestration



