import json


def non_empty_input(prompt: str) -> str:
    while True:
        string = input(prompt)
        if string:
            return string
        print("(Error: Input cannot be empty)")


def get_integer(prompt: str) -> int:
    while True:
        integer = input(prompt)
        if integer == "":
            return 0
        if integer.isdigit() and 0 <= int(integer) <= 6:
            return int(integer)
        print("(Error: Input must be an integer from 0 to 6)")


def create_webhook() -> dict:
    webhook = {
        'name': input("Type a webhook 'name' value: ") or "Custom Webhook",
        'url': non_empty_input("Type a webhook 'url' value: "),
        'notifications': {
            "title": input("Type a custom 'title' value for notifications (Enter to skip): "),
            "description": input("Type a custom 'description' value for notifications (Enter to skip): "),
        }
    }

    while True:
        show_category = get_integer("Type an integer for the 'show_category' value for notifications (Enter for 0): ")
        webhook['notifications']['show_category'] = show_category if show_category else 0

        show_downloads = get_integer("Type an integer for the 'show_downloads' value for notifications (Enter for 0): ")
        webhook['notifications']['show_downloads'] = show_downloads if show_downloads else 0

        show_leechers = get_integer("Type an integer for the 'show_leechers' value for notifications (Enter for 0): ")
        webhook['notifications']['show_leechers'] = show_leechers if show_leechers else 0

        show_published = get_integer("Type an integer for the 'show_published' value for notifications (Enter for 0): ")
        webhook['notifications']['show_published'] = show_published if show_published else 0

        show_seeders = get_integer("Type an integer for the 'show_seeders' value for notifications (Enter for 0): ")
        webhook['notifications']['show_seeders'] = show_seeders if show_seeders else 0

        show_size = get_integer("Type an integer for the 'show_size' value for notifications (Enter for 0): ")
        webhook['notifications']['show_size'] = show_size if show_size else 0

        array = [show_category, show_downloads, show_leechers, show_published, show_seeders, show_size]
        if len(set(array)) == len(array):
            return webhook
        print("(Error: Duplicate values are not allowed for the 'show_' values)")


def main():
    print("~~~ Nyaa Watcher: Webhooks JSON Generator ~~~")

    webhooks = {
        'webhooks': [create_webhook()]
    }

    while True:
        print()
        repeat = input("Add another webhook? (y/n): ")
        if "y" not in repeat.lower():
            break
        print()
        webhooks['webhooks'].append(create_webhook())

    print(f"\n~~~ webhooks.json ~~~\n{json.dumps(webhooks, indent=4)}")


if __name__ == '__main__':
    main()
