import os
import random
import re


"""
Some functions for getting data from Hearts of Iron 4 files.

Sample calls:
generate_rgb(".../map/definition.csv")
world_population(".../history/states")
population_by_country(".../history/states")
"""


def world_population(dir: str):
    """Calculates and prints out the world population."""

    total_population = 0

    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, encoding="utf8") as file:
                for line in file:
                    if line.strip().startswith("manpower"):
                        population = re.search("[0-9]+", line)[0]
                        total_population += int(population)

    print(f"The world population is {total_population:,}.")


def population_by_country(dir: str, sort_by: str = None, reverse: bool = False):
    """
    Calculates and prints out population for each country
    at the start of the game.
    """

    def sort_by_population(country):
        return countries[country]

    countries = {}

    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, encoding="utf8") as file:
                for line in file:
                    if line.strip().startswith("owner"):
                        country = re.search("[A-Z]{3}", line)[0]
                    if line.strip().startswith("manpower"):
                        population = re.search("[0-9]+", line)[0]
                if country not in countries:
                    countries[country] = 0
                countries[country] += int(population)

    for country in sorted(countries, key=sort_by, reverse=reverse):
        print(f"{country}: {countries[country]:,}.")


def get_used_colors(dir: str):
    with open(dir) as file:
        colors = []
        for line in file:
            contents = line.split(";")
            colors.append([contents[1], contents[2], contents[3]])

    return colors


def generate_rgb(dir: str):
    colors = get_used_colors(dir)
    color = list(random.randint(0, 255) for i in range(3))

    while color in colors:
        color = list(random.randint(0, 255) for i in range(3))

    return color
