import asyncio
from core.orchestrator import Orchestrator
from voice.tts_stream import warmup_async

async def main():
    bot = Orchestrator()

    await warmup_async()
    
    print("\nDell Manual Voice RAG ready, Ask questions. \n")
    while True:
        try:
            q = input("user: ").strip()
        except EOFError:
            print("\nSession ended.")
            break
        if not q:
            continue
        if q.lower() in ["exit", "quit"]:
            break

        try:
            await bot.handle_voice_query(q)
        except Exception as e:
            print(f"[error] {e}")


        
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# from core.orchestrator import Orchestrator

# async def main():
#     orch = Orchestrator()

#     user_query = "My server shows error 43 and the seconnd light is blinking"

#     print("user:", user_query)
#     print("-" * 60)

#     await orch.handle_query(user_query)

# if __name__ == "__main__":
#     asyncio.run(main())