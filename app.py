import json
from datetime import datetime, timezone
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "data" / "entries.json"


def load_entries(file_path=DATA_FILE):
    if not file_path.exists():
        return []

    with file_path.open("r", encoding="utf-8") as data_file:
        entries = json.load(data_file)

    required_fields = {"id", "title", "content", "created_at"}
    if not isinstance(entries, list) or any(
        not isinstance(entry, dict)
        or not required_fields.issubset(entry)
        or not isinstance(entry["id"], int)
        or isinstance(entry["id"], bool)
        or entry["id"] < 1
        or any(
            not isinstance(entry[field], str)
            for field in required_fields - {"id"}
        )
        for entry in entries
    ):
        raise ValueError("The data file does not contain a valid list of entries.")

    return entries


def save_entries(entries, file_path=DATA_FILE):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as data_file:
        json.dump(entries, data_file, ensure_ascii=False, indent=2)
        data_file.write("\n")


def next_entry_id(entries):
    return max((entry["id"] for entry in entries), default=0) + 1


def make_entry(title, content, entry_id):
    title = title.strip()
    content = content.strip()
    if not title:
        raise ValueError("Title cannot be empty.")
    if not content:
        raise ValueError("Information cannot be empty.")
    if not isinstance(entry_id, int) or isinstance(entry_id, bool) or entry_id < 1:
        raise ValueError("ID must be a positive integer.")

    return {
        "id": entry_id,
        "title": title,
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def show_entries(entries):
    if not entries:
        print("\nNo saved information yet.")
        return

    print()
    for entry in entries:
        print(f"[{entry['id']}] {entry['title']} ({entry['created_at']})")
        print(f"  {entry['content']}")


def find_entries(entries, query):
    query = query.casefold()
    return [
        entry
        for entry in entries
        if query in entry["title"].casefold()
        or query in entry["content"].casefold()
    ]


def run():
    print("Info Vault")
    while True:
        print("\n1. Add information")
        print("2. List saved information")
        print("3. Search")
        print("4. Delete information")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            title = input("Title: ")
            content = input("Information: ")
            entries = load_entries()
            entry = make_entry(title, content, next_entry_id(entries))
            entries.append(entry)
            save_entries(entries)
            print(f"Saved as [{entry['id']}].")
        elif choice == "2":
            show_entries(load_entries())
        elif choice == "3":
            query = input("Search for: ").strip()
            show_entries(find_entries(load_entries(), query))
        elif choice == "4":
            entries = load_entries()
            show_entries(entries)
            if not entries:
                continue
            entry_id = input(
                "\nID to delete (integer, or leave blank to cancel): "
            ).strip()
            if not entry_id:
                continue
            try:
                entry_id = int(entry_id)
            except ValueError:
                print("Please enter a valid integer ID.")
                continue
            matching = [entry for entry in entries if entry["id"] == entry_id]
            if not matching:
                print("No entry found with that ID.")
                continue
            if input(f"Delete '{matching[0]['title']}'? (y/N): ").strip().casefold() == "y":
                entries.remove(matching[0])
                save_entries(entries)
                print("Entry deleted.")
        elif choice == "5":
            print("Goodbye.")
            return
        else:
            print("Please choose an option from 1 to 5.")


if __name__ == "__main__":
    try:
        run()
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise SystemExit(f"Info Vault could not continue: {error}") from error
