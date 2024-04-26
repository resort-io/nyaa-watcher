import json


def create_watchlist() -> dict:
    watchlist = {}

    name = input("Type a watchlist 'name' value (Enter to skip): ")
    if name:
        watchlist['name'] = name

    tags = []
    while True:
        tag = input("Type a watchlist 'tag' value (Enter to skip): ")
        if not tag:
            break
        tags.append(tag)
    if tags:
        watchlist['tags'] = tags

    regexes = []
    while True:
        regex = input("Type a watchlist 'regex' value (Enter to skip): ")
        if not regex:
            break
        regexes.append(regex)
    if regexes:
        watchlist['regex'] = regexes

    ex_regexes = []
    while True:
        ex_regex = input("Type a watchlist 'exclude_regex' value (Enter to skip): ")
        if not ex_regex:
            break
        ex_regexes.append(ex_regex)
    if ex_regexes:
        watchlist['exclude_regex'] = ex_regexes

    webhooks = []
    while True:
        webhook = input("Type a Discord webhook 'name' value (Enter to skip): ")
        if not webhook:
            break
        webhooks.append(webhook)
    if webhooks:
        watchlist['webhooks'] = webhooks

    return watchlist


def create_subscription() -> dict:
    print()

    subscription = {
        'username': input("Enter Nyaa username: "),
        'rss': input("Enter the Nyaa RSS URL: "),
        'watchlist': [create_watchlist()]
    }

    while True:
        print()
        repeat = input(f"Add another watchlist for {subscription.get('username')}? (y/n): ")
        if "y" not in repeat.lower():
            break
        subscription['watchlist'].append(create_watchlist())

    return subscription


def main():
    print("~~~ Nyaa Watcher: Subscriptions JSON Generator ~~~")

    subscriptions = {
        'interval_sec': int(input("Enter an integer for the interval: ")),
        'subscriptions': [create_subscription()]
    }

    while True:
        repeat = input("Add another subscription? (y/n): ")
        if "y" not in repeat.lower():
            break
        subscriptions['subscriptions'].append(create_subscription())

    print(f"\n~~~ subscriptions.json ~~~\n{json.dumps(subscriptions, indent=4)}")


if __name__ == "__main__":
    main()
