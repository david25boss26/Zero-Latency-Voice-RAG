import asyncio
import pyttsx3
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=1)

def _speak_blocking(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()

    engine.stop()
    del engine

async def speak(text: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_executor, _speak_blocking, text)

async def warmup_async():
    await speak(" ")
