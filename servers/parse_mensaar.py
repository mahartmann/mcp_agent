"""
Parse menu data from mensaar.de (Saarland University canteen) via the REST API.
Requires: pip install requests
"""

import argparse
import requests
from dataclasses import dataclass, field
from datetime import date as Date
# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("mensaServer")



API_BASE = "https://mensaar.de/api/2/TFtD8CTykAXXwrW4WBU4/1/de/getMenu"
DEFAULT_LOCATION = "sb"


@dataclass
class Component:
    name: str
    notices: list[str] = field(default_factory=list)

    def __str__(self):
        s = self.name
        if self.notices:
            s += f" ({', '.join(self.notices)})"
        return s


@dataclass
class Meal:
    name: str
    category: str | None = None
    components: list[Component] = field(default_factory=list)
    notices: list[str] = field(default_factory=list)
    price_student: float | None = None
    price_staff: float | None = None
    price_guest: float | None = None

    def __str__(self):
        prices = (
            f"S: {self.price_student or '?'}  "
            f"B: {self.price_staff or '?'}  "
            f"G: {self.price_guest or '?'}"
        )
        header = f"{self.category + ' ' if self.category else ''}{self.name}"
        result = f"{header}\n  Prices:     {prices}"
        if self.notices:
            result += f"\n  Notices:    {', '.join(self.notices)}"
        if self.components:
            result += "\n  Components:"
            for c in self.components:
                result += f"\n    - {c}"
        return result


def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_notice_map() -> dict[str, str]:
    """Returns a mapping of notice code -> display name."""
    base_url = "https://mensaar.de/api/2/TFtD8CTykAXXwrW4WBU4/1/de/getBaseData"
    data = fetch_json(base_url)
    return {code: info["displayName"] for code, info in data.get("notices", {}).items()}


def parse_meal(meal_data: dict, notice_map: dict[str, str]) -> Meal:
    prices = meal_data.get("prices", {})

    def fmt_price(val):
        if val is None:
            return None
        return str(val).replace(",", ".")

    def resolve(codes):
        return [notice_map.get(c, c) for c in codes]

    components = [
        Component(name=c["name"], notices=resolve(c.get("notices", [])))
        for c in meal_data.get("components", [])
    ]
    return Meal(
        name=meal_data["name"],
        notices=resolve(meal_data.get("notices", [])),
        components=components,
        price_student=fmt_price(prices.get("s")),
        price_staff=fmt_price(prices.get("m")),
        price_guest=fmt_price(prices.get("g")),
    )


@mcp.tool()
def parse_menu(
    target_date: str | None = None,
    location: str = DEFAULT_LOCATION,
) -> list[dict]:
    """
    Fetch the canteen menu from the mensaar API.

    Args:
        target_date: Date in YYYY-MM-DD format (default: today).
        location: Canteen location code, e.g. 'sb' (Saarbrücken), 'hom' (Homburg).

    Returns:
        List of meals with name, notices, components, and prices.
    """
    from datetime import date as _Date
    from dataclasses import asdict

    if target_date is not None:
        try:
            target = _Date.fromisoformat(target_date).isoformat()
        except ValueError:
            raise ValueError(f"Invalid date format '{target_date}', expected YYYY-MM-DD")
    else:
        target = _Date.today().isoformat()

    notice_map = fetch_notice_map()
    data = fetch_json(f"{API_BASE}/{location}")

    for day in data.get("days", []):
        if day.get("date", "").startswith(target):
            meals = []
            for counter in day.get("counters", []):
                for meal_data in counter.get("meals", []):
                    meals.append(asdict(parse_meal(meal_data, notice_map)))
            if meals:
                return meals

    return []


def main():
    parser = argparse.ArgumentParser(description="Parse mensaar.de canteen menu.")
    parser.add_argument(
        "--date", "-d",
        type=Date.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="Date to fetch the menu for (default: today)",
    )
    parser.add_argument(
        "--location", "-l",
        default=DEFAULT_LOCATION,
        help=f"Canteen location code (default: {DEFAULT_LOCATION})",
    )
    args = parser.parse_args()

    label = args.date.isoformat() if args.date else "today"
    print(f"Fetching menu for {label} (location: {args.location}) ...\n")

    meals = parse_menu(args.date, args.location)

    if not meals:
        print("No meals found.")
        return

    print(f"=== Menu for {label} ({len(meals)} meals) ===\n")
    for i, meal in enumerate(meals, 1):
        print(f"[{i}] {meal}\n")


if __name__ == "__main__":
    #main()
    #mcp.run(transport='streamable-http')
    mcp.run()
