# core/dispatcher.py

from app.core.commands.securities import get_or_create_security_id

COMMANDS = {
    "get_or_create_security": get_or_create_security_id,
}

async def dispatch(command: str, **kwargs):
    if command not in COMMANDS:
        raise ValueError(f"Unknown command: {command}")

    handler = COMMANDS[command]
    return await handler(**kwargs)
