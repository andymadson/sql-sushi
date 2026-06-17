"""Build the seed CSVs that every other script reads.

Run once before generating transactions. Produces:
  data/master_items.csv  -- canonical menu + per-POS aliases
  data/locations.csv     -- 6-location subset for the chapter
"""

from __future__ import annotations

import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


# (master_item_id, category, base_price_usd, clover_name, square_name, toast_name)
MENU = [
    ("SUSHI_001", "rolls", 12.00, "Tuna Roll", "tuna_roll_8pc", "Maguro Maki"),
    ("SUSHI_002", "rolls", 13.00, "Salmon Roll", "salmon_roll_8pc", "Sake Maki"),
    ("SUSHI_003", "rolls", 14.00, "Spicy Tuna Roll", "spicy_tuna_8pc", "Spicy Maguro"),
    ("SUSHI_004", "rolls", 14.50, "Spicy Salmon Roll", "spicy_salmon_8pc", "Spicy Sake"),
    ("SUSHI_005", "rolls", 16.00, "Dragon Roll", "dragon_roll_8pc", "Dragon Maki"),
    ("SUSHI_006", "rolls", 17.50, "Rainbow Roll", "rainbow_roll_8pc", "Rainbow Maki"),
    ("SUSHI_007", "rolls", 15.00, "California Roll", "cal_roll_8pc", "California Maki"),
    ("SUSHI_008", "rolls", 18.00, "Caterpillar Roll", "caterpillar_8pc", "Imomushi Maki"),
    ("SUSHI_009", "rolls", 16.50, "Philadelphia Roll", "philly_roll_8pc", "Philadelphia Maki"),
    ("SUSHI_010", "rolls", 19.00, "Volcano Roll", "volcano_roll_8pc", "Kazan Maki"),
    ("SUSHI_011", "rolls", 13.50, "Cucumber Roll", "cucumber_roll_6pc", "Kappa Maki"),
    ("SUSHI_012", "rolls", 13.50, "Avocado Roll", "avocado_roll_6pc", "Avocado Maki"),
    ("NIGIRI_001", "nigiri", 6.50, "Tuna Nigiri (2pc)", "tuna_nigiri_2", "Maguro Nigiri"),
    ("NIGIRI_002", "nigiri", 6.50, "Salmon Nigiri (2pc)", "salmon_nigiri_2", "Sake Nigiri"),
    ("NIGIRI_003", "nigiri", 7.00, "Yellowtail Nigiri (2pc)", "yellowtail_nigiri_2", "Hamachi Nigiri"),
    ("NIGIRI_004", "nigiri", 7.50, "Eel Nigiri (2pc)", "eel_nigiri_2", "Unagi Nigiri"),
    ("NIGIRI_005", "nigiri", 8.00, "Toro Nigiri (2pc)", "toro_nigiri_2", "Toro Nigiri"),
    ("NIGIRI_006", "nigiri", 5.50, "Shrimp Nigiri (2pc)", "shrimp_nigiri_2", "Ebi Nigiri"),
    ("NIGIRI_007", "nigiri", 6.00, "Octopus Nigiri (2pc)", "octopus_nigiri_2", "Tako Nigiri"),
    ("NIGIRI_008", "nigiri", 6.50, "Mackerel Nigiri (2pc)", "mackerel_nigiri_2", "Saba Nigiri"),
    ("BOWL_001", "bowls", 16.00, "Salmon Poke Bowl", "salmon_poke_bowl", "Salmon Don"),
    ("BOWL_002", "bowls", 17.00, "Tuna Poke Bowl", "tuna_poke_bowl", "Tekka Don"),
    ("BOWL_003", "bowls", 18.50, "Chirashi Bowl", "chirashi_bowl", "Chirashi"),
    ("BOWL_004", "bowls", 14.00, "Vegetable Bowl", "veggie_bowl", "Yasai Don"),
    ("BOWL_005", "bowls", 19.00, "Spicy Tuna Bowl", "spicy_tuna_bowl", "Spicy Tekka Don"),
    ("SIDE_001", "sides", 5.50, "Edamame", "edamame", "Edamame"),
    ("SIDE_002", "sides", 6.00, "Miso Soup", "miso_soup", "Miso Shiru"),
    ("SIDE_003", "sides", 7.50, "Seaweed Salad", "seaweed_salad", "Wakame Salada"),
    ("DRINK_001", "drinks", 3.50, "Green Tea", "green_tea", "Ocha"),
    ("DRINK_002", "drinks", 8.50, "Sake (small)", "sake_small", "Sake Tokkuri"),
]


# (location_id, metro, name, pos_system)
LOCATIONS = [
    (1, "Brooklyn", "SQL-Sushi Park Slope", "clover"),
    (2, "Brooklyn", "SQL-Sushi Williamsburg", "clover"),
    (3, "Bay Area", "SQL-Sushi Mission", "square"),
    (4, "Bay Area", "SQL-Sushi Berkeley", "square"),
    (5, "Austin", "SQL-Sushi South Congress", "toast"),
    (6, "Austin", "SQL-Sushi East 6th", "toast"),
]


def main() -> None:
    DATA.mkdir(exist_ok=True)

    with (DATA / "master_items.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "master_item_id",
                "category",
                "base_price_usd",
                "clover_name",
                "square_name",
                "toast_name",
            ]
        )
        writer.writerows(MENU)

    with (DATA / "locations.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["location_id", "metro", "location_name", "pos_system"])
        writer.writerows(LOCATIONS)

    print(f"wrote {len(MENU)} items to data/master_items.csv")
    print(f"wrote {len(LOCATIONS)} locations to data/locations.csv")


if __name__ == "__main__":
    main()
