import json


def create_webhook() -> dict:
    webhook = {
        'name': input("Type a webhook 'name' value: ") or "Custom Webhook",
        'url': input("Type a webhook 'url' value: ") or "https://discord.com/api/webhooks/RANDOM_STRING/RANDOM_STRING",
        'notifications': {
            "title": input("Type a custom 'title' value for notifications (Enter to skip): "),
            "description": input("Type a custom 'description' value for notifications (Enter to skip): "),
        }
    }

    show_category = input("Type an integer for the 'show_category' value for notifications (Enter for 0): ")
    webhook['notifications']['show_category'] = int(show_category) if show_category else 0

    show_downloads = input("Type an integer for the 'show_downloads' value for notifications (Enter for 0): ")
    webhook['notifications']['show_downloads'] = int(show_downloads) if show_downloads else 0

    show_leechers = input("Type an integer for the 'show_leechers' value for notifications (Enter for 0): ")
    webhook['notifications']['show_leechers'] = int(show_leechers) if show_leechers else 0

    show_published = input("Type an integer for the 'show_published' value for notifications (Enter for 0): ")
    webhook['notifications']['show_published'] = int(show_published) if show_published else 0

    show_seeders = input("Type an integer for the 'show_seeders' value for notifications (Enter for 0): ")
    webhook['notifications']['show_seeders'] = int(show_seeders) if show_seeders else 0

    show_size = input("Type an integer for the 'show_size' value for notifications (Enter for 0): ")
    webhook['notifications']['show_size'] = int(show_size) if show_size else 0

    return webhook


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
