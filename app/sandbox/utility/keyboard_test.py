# app/sandbox/keyboard_test.py

import asyncio
from app.sandbox.state import AppState
from app.sandbox.storage import load_items, save_items
from app.sandbox.control import stop_event


async def command_listener(state: AppState):
    print("⌨️ Command listener started")

    loop = asyncio.get_running_loop()

    while not stop_event.is_set():
        command = await loop.run_in_executor(None, input, "> ")

        if command == "exit":
            print("🚪 Exit requested from command listener")
            stop_event.set()
            return

        if command == "begin":
            state.items = load_items()
            state.active = True
            print("▶️ Session started")

        elif command.startswith("add "):
            state.items.append(command[4:])

        elif command == "end":
            save_items(state.items)
            state.items.clear()
            state.active = False
