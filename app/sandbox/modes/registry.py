from app.sandbox.modes.command import command_mode
from app.sandbox.modes.calculator import calculator_mode
from app.sandbox.modes.dispatcher import dispatcher_mode
from app.sandbox.modes.file_mode import file_mode


MODES = {
    "command": command_mode,
    "calculator": calculator_mode,
    "dispatcher": dispatcher_mode,
    "file": file_mode,
}
