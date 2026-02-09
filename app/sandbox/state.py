from asyncio import Lock

class AppState:
    def __init__(self):
        self.items = []
        self.active = False
        self.mode = "command"   # 👈 "command" | "calculator"
        self.lock = Lock()