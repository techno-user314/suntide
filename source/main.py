"""
This is SunTide: A script to generate spreadsheets of data containing
day-by-day tide predictions and daylight information for a given year.

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
from datetime import datetime, timedelta

import pandas as pd

from suntimes import sunrise_set
from tides import get_tides
from settings import YEAR, SUN_LOC, LOCATIONS

def days_in_month(year, month):
    days_in_months = [None,31,28,31,30,31,30,31,31,30,31,30,31]
    if month == 2 and (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0): return 29
    return days_in_months[month]

#Sun times
print("Calculating sun times...")
cols = ["DAY", "MONTH", "DATE",
        "SUNRISE", "SUNSET", "DUR", "DIFF", "MORE/LESS"]
sun_year = pd.DataFrame(columns=cols)
for month in range(1,13):
    for day in range(1, days_in_month(YEAR, month)+1):
        today = datetime(YEAR, month, day)

        sunrise = sunrise_set(SUN_LOC[0], SUN_LOC[1],
                              today, True, tz_offset=-9)
        sunset = sunrise_set(SUN_LOC[0], SUN_LOC[1],
                             today, False, tz_offset=-9)

        dur = sunset - sunrise
        duration = str(dur).split(":")[0] + ":" + str(dur).split(":")[1]

        yesterday = today - timedelta(days=1)
        sunrisey = sunrise_set(SUN_LOC[0], SUN_LOC[1],
                               yesterday, True, tz_offset=-9)
        sunsety = sunrise_set(SUN_LOC[0], SUN_LOC[1],
                              yesterday, False, tz_offset=-9)
        dury = sunsety - sunrisey
        diff = dur - dury
        difftype = "more"
        if diff < timedelta(0):
            diff = dury - dur
            difftype = "less"
        differance = str(diff).split(":")[1] + ":" + str(diff).split(":")[2]

        sun_year.loc[len(sun_year)] = [today.strftime("%a"),
                                       today.strftime("%B"),
                                       day,
                                       sunrise.time().strftime("%I:%M %p"),
                                       sunset.time().strftime("%I:%M %p"),
                                       duration,
                                       differance,
                                       difftype]
print(f"Saving to CSV: Suntimes {YEAR}.csv")
sun_year.to_csv(f"Suntimes {YEAR}.csv", index=False)


#Tide predictions
print("Retrieving tide predictions...")

# Pull data for tides month by month to prevent overloading the api server
month_start = [f"{YEAR}{mm:02d}01" for mm in range(1, 13)]
month_end = [f"{YEAR}{mm:02d}{days_in_month(YEAR, mm)}" for mm in range(1, 13)]
all_tides = [[] for _ in range(len(LOCATIONS))]
for start, end in zip(month_start, month_end):
    print(".", end="")
    for i in range(len(LOCATIONS)):
        all_tides[i] += get_tides(LOCATIONS[i],
                                  datetime.strptime(start, "%Y%m%d"),
                                  datetime.strptime(end, "%Y%m%d"))

# Format tides for the .csv
print("\nGenerating CSV file...")
cols = []
for loc_num in range(len(LOCATIONS)):
    idnum = loc_num + 1
    cols += [f"DATE{idnum}", f"DAY{idnum}",
             f"TYPE{idnum}", f"HEIGHT{idnum}", f"TIME{idnum}"]
tides_year = pd.DataFrame(columns=cols)

date = f"{YEAR}-01-01"

while True:
    row = []

    done_w_location = [True for _ in range(len(LOCATIONS))]
    for i, tide_list in enumerate(all_tides):
        if not tide_list:
            continue
        done_w_location[i] = (tide_list[0]["t"].split(" ")[0] != date)

    if all(done_w_location):
        date = datetime.strptime(date, "%Y-%m-%d")+timedelta(days=1)
        if date.year == YEAR+1:
            break
        date = date.strftime("%Y-%m-%d")
        continue

    for i in range(len(all_tides)):
        if not done_w_location[i]:
            tide = all_tides[i][0]
            tide_datetime_obj = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
            tide_date = tide_datetime_obj.strftime("%m-%d")
            tide_day = tide_datetime_obj.strftime("%a")
            tide_type = "High" if tide["type"] == "H" else "Low"
            tide_height = round(float(tide["v"]), 1)
            tide_time = tide_datetime_obj.strftime("%I:%M %p")
            row += [tide_date, tide_day, tide_type, tide_height, tide_time]
            all_tides[i].pop(0)
        else:
            row += ["", "", "", "", ""]

    tides_year.loc[len(tides_year)] = row
print(f"Saving to CSV: Tides {YEAR}.cv")
tides_year.to_csv(f"Tides {YEAR}.csv", index=False)
