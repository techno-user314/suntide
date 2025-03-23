"""
Retrieves all the settings from the user.

Copyright (C) 2025  Zach Harwood

This file is part of SunTide

SunTide is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from datetime import datetime

def init():
    welcome = """
    This is SunTide: A script to generate spreadsheets of data containing
    day-by-day tide predictions and daylight information for a given year.
    Copyright 2025, Zach Harwood.
    """
    print(welcome)

def get_year():
    this_year = datetime.now().year
    while True:
        print(f"Type 'this' to retrieve data for this year ({this_year}), ", end="")
        print(f"type 'next' to retrieve data for next year ({this_year + 1})")
        user_says = input("Which year (this/next)? ")
        if user_says.lower() == "this":
            print(f"Fetching data for {this_year}")
            return this_year
        elif user_says.lower() == "next":
            print(f"Fetching data for {this_year+1}...")
            return this_year+1
