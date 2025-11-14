/*
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
*/

class APIFailure extends Error {}

function formatDate(dt) {
    if (!(dt instanceof Date)) {
        throw new Error("'date_start' and 'date_end' must be Date objects.");
    }

    const yyyy = dt.getFullYear();
    const mm = String(dt.getMonth() + 1).padStart(2, '0');
    const dd = String(dt.getDate()).padStart(2, '0');
    return `${yyyy}${mm}${dd}`;
}

async function getTides(stationId, dateStart, dateEnd) {
    const dstart = formatDate(dateStart);
    const dend = formatDate(dateEnd);

    const params = {
        begin_date: dstart,
        end_date: dend,
        station: String(stationId),
        product: "predictions",
        datum: "MLLW",
        interval: "hilo",
        units: "english",
        time_zone: "lst_ldt",
        application: "SunTide-DevMode",
        format: "json"
    };

    // Build query string
    const queryString = new URLSearchParams(params).toString();

    const url = `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?${queryString}`;
    const response = await fetch(url);

    if (!response.ok) {
        throw new APIFailure("Unable to retrieve data from API");
    }

    const data = await response.json();
    return data.predictions;
}