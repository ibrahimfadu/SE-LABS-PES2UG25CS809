def clean_dish_name(name):
    """
    Removes chef's-special markers and title-cases the dish name.
    Rejects invalid types and empty dish names.
    """
    if not isinstance(name, str):
        raise TypeError("Dish name must be a string")

    name = name.strip()

    for ch in ['*', '#', '~']:
        name = name.replace(ch, '')

    name = name.strip()

    if not name:
        raise ValueError("Dish name cannot be empty")

    return name.title()


def parse_item_prices(text):
    """
    Parses comma-separated prices into a list of non-negative integers.
    """
    if not isinstance(text, str):
        raise TypeError("Prices must be provided as a string")

    if not text.strip():
        raise ValueError("Price list cannot be empty")

    prices = []

    for price in text.split(','):
        price = price.strip()

        if not price:
            raise ValueError("Price cannot be empty")

        try:
            value = int(price)
        except ValueError:
            raise ValueError("Prices must be valid whole numbers")

        if value < 0:
            raise ValueError("Prices cannot be negative")

        prices.append(value)

    return prices


def split_amount(text):
    """
    Splits TOTAL/PEOPLE and calculates each person's share.
    """
    if not isinstance(text, str):
        raise TypeError("Bill details must be a string")

    parts = text.split('/')

    if len(parts) != 2:
        raise ValueError("Format must be TOTAL/PEOPLE")

    try:
        total = int(parts[0].strip())
        people = int(parts[1].strip())
    except ValueError:
        raise ValueError("Total and people must be whole numbers")

    if total < 0:
        raise ValueError("Total cannot be negative")

    if people <= 0:
        raise ValueError("Number of people must be positive")

    return total // people


def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    print("Dish name:", clean_dish_name(value))

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    print("Item prices:", parse_item_prices(value))

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    print("Each person pays:", split_amount(value))


if __name__ == "__main__":
    main()

