import asyncio
import time
import torch
from rag.hybrid import HybridSearch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from voice.asr_stream import asr_stream_simulator, asr_final
from voice.tts_stream import speak, warmup_async

class Orchestrator:

    def ts(start):
        return f"[{(time.time() - start):.3f}s]"
    
    def __init__(self):
        print("Loading RAG engine...")
        self.search_engine = HybridSearch()

        print("loading LLM...")
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

        self.turn_history = []
        self.last_docs = []

        warmup_async()



    def _spoken_formatter(self, text: str) -> str:
        text = text.replace("PCIe", "P C I express")
        text = text.replace("CPU", "C P U")
        text = text.replace ("BIOS", "bye-oss")
        text = text.replace("iDRAC", "eye-drack")

        sentences = [s.strip() for s in text.split('.') if s.strip()]
        return ". ".join(sentences[:4]) + "."
    
    def _rewrite_query(self, query:str) -> str:
        q = query.lower()

        if ("second one "in q) or ("2nd one" in q) or ("the second" in q):
            if len(self.last_docs) >= 2:
                anchor = (self.last_docs[1].get("text", "")[:180]).replace("\n", " ")
                return f"{query}\nReference(second item): {anchor}"
             
            
        if self.turn_history:
            prev = self.turn_history[-1]["user"]
            return f"{query}\n\nPrevious question: {prev}"
        
        return query
    
    def answer(self, query:str) -> str:
        
        rewritten = self._rewrite_query(query)

        boosted = rewritten + "detailed description recommended response action arguments severity category"

        docs = self.search_engine.search(boosted)

        if not docs:
            return "I couldn't find any relevant information fot that issue."
        
        self.last_docs = docs[:]

        filtered = [d for d in docs if len((d.get("text") or "").strip()) > 120]
        if not filtered:
            filtered = docs[:5]

        context = "\n\n".join(d["text"] for d in filtered[:3])[:1800]

        prompt = f"""
You are a Dell PowerEdge support engineer. 
task: Explain what this error code or message means and what the user should do next. 
Rules: 
- Use ONLY the context. 
- Do NOT copy raw manual text. 
- Answer in 2 to 4 short sentences. 
- If the exact meaning is not present, 

say: "I couldn't find the exact definition for that code in this manual excerpt.

context:
{context}

Question: 
{query}

Answer:
"""
        inputs = self.tokenizer(
            prompt, return_tensors="pt", max_length=512, truncation=True
        )

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=120,
                do_sample=False,
            )

        result = self.tokenizer.decode(output[0], skip_special_token=True).strip()


        
        if len(result) < 25:
            digits = "".join(c for c in query if c.isdigit())
            if digits:
                for d in filtered:
                    if digits in d.get("text", ""):
                        snip = d["text"].replace("\n", " ").strip()[:300]
                        return self._spoken_formatter(
                            "I found this in the manual: "+
                            snip
                        ) 
                    return "I couldn't find the exact definition for that code in this manual excerpt"
        return self._spoken_formatter(result)
    
    async def handle_voice_query(self, user_text: str):
        print("--------------------------------------------------")
        
        t0 = time.time()
        def ts():
            return time.perf_counter() - t0
        
        print(f"[{ts():0.3f}s] user started speaking...")

        rag_task = None
        filler_task = None
        answer_ready = False

        async def start_filler():
           
           print(f"[{ts():0.3f}s]TTFB: speaking Filler")
           await speak("let me check taht for you")

        filler_task = asyncio.create_task(start_filler())


        async for partial in asr_stream_simulator(user_text):
            print(f"[{ts():0.3f}s] [ASR partial] {partial}")

            if rag_task is None and len(partial.split()) >= 4:
                print(f"[{ts():0.3f}s] ⚡ starting speculative RAG")
                rag_task = asyncio.create_task(
                    asyncio.to_thread(self.answer, partial)
                )

        print(f"[{ts():0.3f}s] [ASR final] {user_text}")


        if rag_task is None:
            rag_task = asyncio.create_task(
                asyncio.to_thread(self.answer, user_text)
            )

        answer = await rag_task
        answer_ready = True

        if filler_task:
            try:
                await filler_task
            except:
                pass
        
        print(f"[{ts():0.3f}s] 🔊 speaking final answer")
        await speak(answer)

        self.turn_history.append({
            "user": user_text,
            "assistant": answer
        })

        print(f"[{ts():0.3f}s] done.")

                     


# BEFORE ADDING THE STREAMIN TTS THE CORE WAS THIS:

# import asyncio
# from rag.hybrid import HybridSearch
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import torch

# from voice.asr_stream import asr_stream_simulator, asr_final
# from voice.tts_stream import speak


# class Orchestrator:
#     def __init__(self):
#         print("Loading RAG engine...")
#         self.search_engine = HybridSearch()

#         print("loading LLM...")
#         self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
#         self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
        
#         self.turn_history = []
#         self.last_docs = []

#     def _spoken_formatter(self, text: str) -> str:
#         text = text.replace("PCIe", "P C I express")
#         text = text.replace("CPU", "C P U")
#         text = text.replace("BIOS", "bye-oss")
#         text = text.replace("iDRAC", "eye-drack")

        
#         sentences = [s.strip() for s in text.split(".") if s.strip()]
#         return ". ".join(sentences[:4]) + "."
    
#     def _rewrite_query(self, q:str) -> str:
#         """
#         Very leightweight query rewriting for follow-ups like:
#         'and waht about the second one?'
#         """

#         q = q.lower()

#         if "second one" in q or "that one" in q:
#             if len(self.last_docs) >= 2:
#                 anchor = self.last_docs[1].get("text", "")[:180].replace("\n", " ")
#                 return f"{q}\nrefrence (second item): {anchor}"
            
#         if self.turn_history:
#             last_user = self.turn_history[-1]["user"]
#             return f"{q}\nprevios question : {last_user}"
        
#         return q
    
#     def answer(self, query: str) -> str:
        

#         boosted_query = (
#             query
#             + "message detailed description recommended response action arguments severity category"
#         )
#         docs = self.search_engine.search(query)

#         if not docs:
#             return "I could not find the relevant info for that issue"
        
#         self.last_docs = docs[:]

#         filtered = []
#         for d in docs:
#             t = (d.get("text") or "").strip()
#             if len(t) > 120:
#                 filtered.append(d)
#         if not filtered:
#             filtered = docs[:5]

#         context = "\n\n".join([d['text'] for d in filtered[:5]])
#         context = context[:1800]

#         prompt = f"""
# You are a Dell PowerEdge support engineer.
# task:

# Explain what this error code or message means and what the user should do next.

# Rules:
# - Use ONLY the context.
# - Do NOT copy raw manual text.
# - Answer in 2 to 4 short sentences.
# - If the exact meaning is not present, say:
#   "I couldn't find the exact definition for that code in this manual excerpt."

# context:
# {context}

# Question:
# {query}

# Answer:
# """.strip()
        
#         inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)

#         with torch.no_grad():
#             outputs = self.model.generate(**inputs, max_new_tokens=120,do_sample=False)

#         result = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

#         if len(result) < 25:
#             digits = "".join([c for c in query if c.isdigit()])
#             if digits:
#                 for d in filtered:
#                     if digits in d.get("text", ""):
#                         snippet = d["text"].replace("\n", " ").strip()[:320]
#                         return self._spoken_formatter(f"i found this in the manual: {snippet}")
                    
                
#         return self._spoken_formatter(
#             "I couldn't find the exact definition for that error in the manual, "
#             "but error 43 usually means a communication or hardware status issue. "
#             "I recommend checking the system logs or the front panel indicators."
#         )
    
#     async def handle_voice_query(self, user_full_text: str):
#         """✅ Task A: speculative / parallelizedpipeline:
#         -stream ASR particals
#         -start RAG prefetch early
#         -speak filler while heavy work happens
#         -speak final answer when ready"""
    
#         print("--------------------------------------------------------")
#         t0 = asyncio.get_event_loop().time()
#         print("[0.000s] user started speaking...")

#         rag_task = None
#         rag_started = False
#         started_on = ""


#         async for partial in asr_stream_simulator(user_full_text):
#             dt = asyncio.get_event_loop().time() - t0
#             print(f"[ASR partial] {partial}")

#             has_digit = any(ch.isdigit() for ch in partial)
#             if (not rag_started) and (len(partial.split()) >= 4):
#                 rag_started = True
#                 started_on = partial
#                 print("⚡ staring speculative RAG prefetch...")
#                 rag_task = asyncio.create_task(asyncio.to_thread(self.answer, partial))

#         final_text = await asr_final(user_full_text)
#         dt = asyncio.get_event_loop().time() - t0
#         print(f"[ASR final] {final_text}")

#         if rag_task is None:
#             rag_task = asyncio.create_task(asyncio.to_thread(self.answer, final_text))

#         filler_task = asyncio.create_task(speak("Let me check that for you."))
#         speculative_answer = await rag_task

        

#         if not filler_task.done():
#             filler_task.cancel()
#             try:
#                 await filler_task
#             except asyncio.CancelledError:
#                 pass
        
#         if speculative_answer is None or len(speculative_answer) < 40:
#             final_answer = await asyncio.to_thread(self.answer, final_text)
#         else:
#             final_answer = speculative_answer

#         self.turn_history.append({"user": final_text, "assistant": final_answer})

#         await speak(final_answer)
#         print("\n[done]")
