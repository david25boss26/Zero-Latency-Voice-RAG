import asyncio

async def asr_stream_simulator(full_text: str):
    words = full_text.split()
    current = []

    for w in words:
        current.append(w)
        await asyncio.sleep(0.15)
        yield " ".join(current)

async def asr_final(full_text: str):
    await asyncio.sleep(0.2)
    return full_text