
def handle_calculator(command: str):
    if command in {"back", "exit", "quit"}:
        return "exit_calc"

    if command.startswith("add"):
        try:
            _, a, b = command.split()
            print(int(a) + int(b))
        except Exception:
            print("Usage: add <a> <b>")
        return None

    print("❓ Calculator command")
    return None