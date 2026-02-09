# app/controller.py

import asyncio
from app.sandbox.control import stop_event
from app.sandbox.input_loop import input_loop
from app.sandbox.storage import clear_file


async def run_app(state):
    task = asyncio.create_task(input_loop(state))

    await stop_event.wait()

    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    clear_file()
    state.items.clear()

    print("✅ Shutdown complete")
