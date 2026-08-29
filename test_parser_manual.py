import sys

from backend.services.query_parser import parse_query


# Force terminal output to UTF-8
sys.stdout.reconfigure(encoding="utf-8")


queries = [
    "red top under 1000",
    "black shirt",
    "blue dress below ₹2500",
    "white oversized tshirt",
    "elegant black dress under 3000",
    "cotton shirt for summer",
    "party dress between 1500 and 3000",
    "classy black dress for dinner under rs 2500",
]


for query in queries:
    intent = parse_query(query)

    print("\nQUERY:", query)
    print(intent)