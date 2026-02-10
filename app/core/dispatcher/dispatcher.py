# core/dispatcher.py

# from app.core.commands.securities import get_or_create_security_id

# COMMANDS = {
#     "get_or_create_security": get_or_create_security_id,
# }

# async def dispatch(command: str, **kwargs):
#     if command not in COMMANDS:
#         raise ValueError(f"Unknown command: {command}")

#     handler = COMMANDS[command]
#     return await handler(**kwargs)


from app.sandbox.modes.base import DispatchResult
from app.core.commands.securities import get_or_create_security_id


COMMANDS = {
    "get_or_create_security": get_or_create_security_id,
}


async def dispatch(command: str, **kwargs) -> DispatchResult:
    handler = COMMANDS.get(command)

    if not handler:
        return DispatchResult(
            ok=False,
            error=f"Unknown command: {command}"
        )

    try:
        result = await handler(**kwargs)
        return DispatchResult(ok=True, value=result)

    except Exception as e:
        return DispatchResult(
            ok=False,
            error=str(e)
        )

