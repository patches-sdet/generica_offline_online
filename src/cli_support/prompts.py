def prompt_int(prompt, *, minimum=0, maximum=None):
    while True:
        raw = input(prompt).strip()

        if not raw.isdigit():
            print("Enter a whole number.")
            continue

        value = int(raw)

        if value < minimum:
            print(f"Value must be at least {minimum}.")
            continue

        if maximum is not None and value > maximum:
            print(f"Value must be no more than {maximum}.")
            continue

        return value


def choose_from_mapping(prompt, options_dict):
    while True:
        choice = input(prompt).strip().lower()
        if choice in options_dict:
            return options_dict[choice]
        print("Invalid choice. Try again.")


def confirm(prompt="Confirm? (y/n): "):
    return input(prompt).strip().lower() == "y"


def prompt_nonempty(prompt: str, retry_prompt: str) -> str:
    value = input(prompt).strip()
    while not value:
        value = input(retry_prompt).strip()
    return value
