"""
The sunrise_set function defined here is a Python adaption of the
JavaScript library for predicting sunrise and sunset times,
created by Triggertrap Ltd. and found here:
https://github.com/Triggertrap/sun-js/blob/master/sun.js

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
import math
from datetime import datetime, timedelta

def sunrise_set(lat, long, date, sunrise:bool, zenith=90.8333, tz_offset=0):
    tz_offset = timedelta(hours=tz_offset)
    degrees_per_hour = 360 / 24

    def sinDeg(deg):
        return math.sin( math.radians(deg) )

    def cosDeg(deg):
        return math.cos( math.radians(deg) )

    def tanDeg(deg):
        return math.tan( math.radians(deg) )

    def acosDeg(x):
        return math.acos(x) * 360.0 / (2 * math.pi)

    def asinDeg(x):
        return math.asin(x) * 360.0 / (2 * math.pi)

    hours_from_meridian = long / degrees_per_hour
    day_of_year = date.timetuple().tm_yday

    if sunrise:
        approx_time_days = day_of_year + ((6 - hours_from_meridian) / 24)
    else:
        approx_time_days = day_of_year + ((18.0 - hours_from_meridian) / 24)

    sun_mean_anomaly = (0.9856 * approx_time_days) - 3.289

    sun_longitude = sun_mean_anomaly + (1.916 * sinDeg(sun_mean_anomaly))
    sun_longitude += (0.020 * sinDeg(2 * sun_mean_anomaly)) + 282.634
    sun_longitude =  sun_longitude % 360

    ascension = 0.91764 * tanDeg(sun_longitude)
    right_ascension = 360 / (2 * math.pi) * math.atan(ascension)
    right_ascension = right_ascension % 360

    l_quadrant = int(sun_longitude / 90) * 90
    ra_quadrant = int(right_ascension / 90) * 90
    right_ascension = right_ascension + (l_quadrant - ra_quadrant)
    right_ascension /= degrees_per_hour

    sin_dec = 0.39782 * sinDeg(sun_longitude)
    cos_dec = cosDeg(asinDeg(sin_dec))
    cos_local_hour_angle = (cosDeg(zenith) - sin_dec*sinDeg(lat)) / (cos_dec * cosDeg(lat))

    local_hour_angle = acosDeg(cos_local_hour_angle)

    if sunrise:
        local_hour_angle = 360 - local_hour_angle

    local_hour = local_hour_angle / degrees_per_hour

    local_mean_time = local_hour + right_ascension - (0.06571 * approx_time_days) - 6.622

    time = local_mean_time - (long / degrees_per_hour)
    time = time % 24

    midnight = date.replace(hour=0, minute=0, second=0)

    new_time = midnight + timedelta(hours=time) + tz_offset
    new_time = new_time.time()
    new_dtime = datetime(year=date.year, month=date.month, day=date.day,
                         hour=new_time.hour, minute=new_time.minute, second=new_time.second)

    return new_dtime
