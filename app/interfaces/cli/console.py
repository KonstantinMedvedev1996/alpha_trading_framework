# interfaces/console.py

import asyncio
from app.core.dispatcher.dispatcher import dispatch

async def console_loop():
    print("Async console ready. Type 'exit' to quit.")

    while True:
        raw = await asyncio.to_thread(input, "> ")

        if raw in {"exit", "quit"}:
            break

        try:
            parts = raw.split()
            cmd = parts[0]
            args = dict(p.split("=") for p in parts[1:])

            result = await dispatch(cmd, **args)
            print(result)

        except Exception as e:
            print(f"Error: {e}")
