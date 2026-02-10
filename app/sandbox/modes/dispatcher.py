from app.core.dispatcher.dispatcher import dispatch
from app.sandbox.modes.base import ModeResult


def _parse_command(raw: str):
    """
    Parses:
        "get_or_create_security symbol=AAPL"
    into:
        ("get_or_create_security", {"symbol": "AAPL"})
    """
    parts = raw.split()
    command = parts[0]
    args = {}

    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            args[k] = v

    return command, args


async def dispatcher_mode(command: str, state) -> ModeResult:
    # --- mode exit ---
    if command in {"back", "exit", "quit"}:
        return ModeResult(
            next_mode="command",
            output="⬅️ Back to command mode"
        )

    # --- parse ---
    try:
        cmd, args = _parse_command(command)
    except Exception as e:
        return ModeResult(output=f"❌ Parse error: {e}")

    # --- dispatch to core ---
    result = await dispatch(cmd, **args)

    if not result.ok:
        return ModeResult(output=f"❌ {result.error}")

    return ModeResult(
        output=str(result.value) if result.value is not None else None
    )
