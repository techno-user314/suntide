import "./sun.js";
import { getNextTides } from "./tides.js";

export async function getSunTideData(date, timeOfDay) {
  const sunrise = date.sunrise();
  const sunset = date.sunset();

  // --- Suntime data ---
  const daylightDuration = sunset - sunrise;

  const yesterday = new Date(date);
  yesterday.setDate(date.getDate() - 1);

  const yesterdaySunrise = yesterday.sunrise();
  const yesterdaySunset = yesterday.sunset();
  const yesterdayDuration = yesterdaySunset - yesterdaySunrise;

  const daylightDifference = daylightDuration - yesterdayDuration;

  // --- Tides for all station IDs ---
  const stationIds = [9466477, 9465831, 8467373];
  const tidesByStation = {};
  for (const id of stationIds) {
    tidesByStation[id] = await getNextTides(id, date, timeOfDay);
  }

  return {
    sunrise,
    sunset,
    daylightDuration,
    daylightDifference,
    tides: tidesByStation
  };
}
