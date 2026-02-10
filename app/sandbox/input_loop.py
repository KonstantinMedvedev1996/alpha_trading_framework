import asyncio
from app.sandbox.control import stop_event
from app.sandbox.modes.registry import MODES


async def input_loop(state):
    print("⌨️ Input loop started")
    loop = asyncio.get_running_loop()

    while not stop_event.is_set():
        try:
            command = await loop.run_in_executor(None, input, "> ")
        except EOFError:
            stop_event.set()
            break

        handler = MODES.get(state.mode)

        if not handler:
            print(f"🚨 Unknown mode: {state.mode}")
            state.mode = "command"
            continue

        result = await handler(command, state)

        if result.output:
            print(result.output)

        if result.next_mode:
            state.mode = result.next_mode

        if result.stop:
            stop_event.set()
