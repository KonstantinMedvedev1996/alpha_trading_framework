from app.sandbox.modes.base import ModeResult


async def command_mode(command: str, state) -> ModeResult:
    if command == "calc":
        return ModeResult(
            next_mode="calculator",
            output="🧮 Calculator mode (type 'exit' to return)"
        )

    if command == "dispatch":
        return ModeResult(
            next_mode="dispatcher",
            output="🛰 Dispatcher mode (type 'back' to return)"
        )

    if command == "file":
        return ModeResult(
            next_mode="file",
            output="📂 File mode (load/add/list/save/back)"
        )

    if command == "exit":
        return ModeResult(stop=True)

    return ModeResult(output="❓ Unknown command")
