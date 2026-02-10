from app.sandbox.utility.dispatcher_mode import handle_dispatcher
from app.sandbox.modes.base import ModeResult


async def dispatcher_mode(command: str, state) -> ModeResult:
    try:
        result = await handle_dispatcher(command)

        if result == "exit_dispatcher":
            return ModeResult(next_mode="command", output="⬅️ Back to command mode")

        return ModeResult(output=str(result) if result is not None else None)

    except Exception as e:
        return ModeResult(output=f"🚨 Dispatcher error: {e}")
