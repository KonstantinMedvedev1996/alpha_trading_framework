from app.sandbox.storage import load_items, save_items
from app.sandbox.modes.base import ModeResult


async def file_mode(command: str, state) -> ModeResult:
    if command == "load":
        state.items = load_items()
        return ModeResult(output="📂 Items loaded")

    if command.startswith("add "):
        value = command[4:]
        state.items.append(value)
        return ModeResult(output=f"✅ Added: {value}")

    if command == "list":
        return ModeResult(output=f"📋 {state.items}")

    if command == "save":
        save_items(state.items)
        return ModeResult(output="💾 Items saved")

    if command in {"back", "exit"}:
        return ModeResult(next_mode="command", output="⬅️ Back to command mode")

    return ModeResult(output="❓ Unknown file command")
