"""
Contains all the settings.

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

# What year to generate information for
YEAR = 2025

# What location to get sunrise/set times for
SUN_LOC = [
   60.48,  # Latitude coordinates for Bethel, AK
  -161.46  # Longitude coordinates for Bethel, AK
]

# NOAA station ID's that determine where tides are pulled from
LOCATIONS = [
  9466477, # NOAA station ID for Bethel, AK,
  9465831, # NOAA station ID for Quinhagak, AK,
  8467373  # NOAA station ID for Togaik, AK
]
