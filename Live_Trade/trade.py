import threading


class InputReader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.user_input = None

    def run(self):
        self.user_input = input("Enter something: ")


timeout_seconds = 5
input_reader = InputReader()
input_reader.start()
input_reader.join(timeout_seconds)
if input_reader.is_alive():
    print(f"\nNo input received. Using default: default_value")
    user_input = "default_value"
else:
    user_input = input_reader.user_input.strip()
print(f"You entered: {user_input}")
