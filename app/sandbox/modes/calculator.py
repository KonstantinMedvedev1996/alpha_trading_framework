from app.sandbox.utility.calculator import handle_calculator
from app.sandbox.modes.base import ModeResult


async def calculator_mode(command: str, state) -> ModeResult:
    result = handle_calculator(command)

    if result == "exit_calc":
        return ModeResult(next_mode="command", output="⬅️ Back to command mode")

    return ModeResult()
