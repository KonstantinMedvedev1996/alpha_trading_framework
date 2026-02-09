# app/input_loop.py

import asyncio
from app.sandbox.control import stop_event
from app.sandbox.utility.calculator import handle_calculator
from app.sandbox.storage import load_items, save_items


async def input_loop(state):
    print("⌨️ Input loop started")
    loop = asyncio.get_running_loop()

    while not stop_event.is_set():
        try:
            command = await loop.run_in_executor(None, input, "> ")
        except EOFError:
            stop_event.set()
            break

        # -------- COMMAND MODE --------
        if state.mode == "command":
            if command == "begin":
                state.items = load_items()
                state.active = True
                print("▶️ Session started")

            elif command.startswith("add "):
                if not state.active:
                    print("⚠️ Session not started. Type 'begin'")
                else:
                    value = command[4:]
                    state.items.append(value)
                    print(f"✅ Added: {value}")

            elif command == "list":
                if not state.active:
                    print("⚠️ Session not started. Type 'begin'")
                else:
                    print("📋", state.items)

            elif command == "end":
                if not state.active:
                    print("⚠️ No active session")
                else:
                    save_items(state.items)
                    state.items.clear()
                    state.active = False
                    print("⏹ Session ended")

            elif command == "calc":
                state.mode = "calculator"
                print("🧮 Calculator mode")

            elif command == "exit":
                stop_event.set()

            else:
                print("❓ Unknown command")

        # -------- CALCULATOR MODE --------
        elif state.mode == "calculator":
            result = handle_calculator(command)

            if result == "exit_calc":
                state.mode = "command"
                print("⬅️ Back to command mode")
