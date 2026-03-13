import json, os
from dataclasses import asdict
from src.application.character_creation import create_character
from src.presentation.character_sheet import debug_print_character
from src.domain.race import RACES

PERSISTENCE_DIR = "src/persistence"

def main():
    print("=== Tabletop RPG Character Creator ===\n")

    # Ask for the character name
    char_name = input("Enter character name: ").strip()
    while not char_name:
        char_name = input("Please enter a valid character name: ").strip()

    # Display available races
    print("\nAvailable races:")
    for race_name in RACES.keys():
        print(f"- {race_name}")

    # Ask for the race choice
    race_name = input("\nChoose a race from the list above: ").strip()
    while race_name not in RACES:
        race_name = input("Invalid race. Please choose a valid race: ").strip()

    # Create the character using character_creation.py
    character = create_character(char_name, race_name)

    # Print the character sheet
    print("\n=== Character Created ===\n")
    debug_print_character(character)

    os.makedirs(PERSISTENCE_DIR, exist_ok=True)
    filename = f"{char_name.replace(' ', '_').lower()}_character.json"
    filepath = os.path.join(PERSISTENCE_DIR, filename)

    data = asdict(character)
    data.pop("pool_manager", None)

    with open(filepath, "w") as f:
        json.dump(asdict(character), f, indent=4)
        print(f"\nCharacter saved to: {filename}")

if __name__ == "__main__":
    main()
