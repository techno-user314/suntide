"""
Function that uses the National Oceanic and Atmospheric Administration's
tide predictions API to retrieve tide predictions.

NOAA API docs:
https://api.tidesandcurrents.noaa.gov/api/prod/

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
import requests
import pandas as pd

from datetime import datetime

class APIFailure(Exception):
    pass

def get_tides(station_id, date_start, date_end):
    if not isinstance(date_start, datetime):
        raise ValueError("'date_start' parameter must be a datetime object.")
    if not isinstance(date_end, datetime):
        raise ValueError("'date_end' parameter must be a datetime object.")

    dstart = date_start.strftime('%Y%m%d')
    dend = date_end.strftime('%Y%m%d')

    # Define parameters for the request
    params = {
        "begin_date": str(dstart),
        "end_date": str(dend),
        "station": str(station_id),
        "product": "predictions",
        "datum": "MLLW",
        "interval":"hilo",
        "units": "english",
        "time_zone": "lst_ldt",
        "application": "SunTide-DevMode",
        "format": "json",
    }

    # Make the API request
    url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data["predictions"]
    else:
        raise APIFailure("Unable to retrieve data from API")
