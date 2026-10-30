import datetime
import requests
from PIL import Image, ImageDraw, ImageFont

# Souradnice Duchcov
LAT = 50.6033
LON = 13.7456
CITY_NAME = "DUCHCOV"

def get_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,surface_pressure"
        f"&hourly=temperature_2m,precipitation_probability"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset"
        f"&timezone=Europe%2FPrague&forecast_days=4"
    )
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

def weather_desc(code):
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        95: "Thunderstorm"
    }
    return mapping.get(code, "Variable")

def create_image(data):
    width, height = 600, 800
    img = Image.new("L", (width, height), color=255)
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()

    curr = data.get("current", {})
    daily = data.get("daily", {})
    hourly = data.get("hourly", {})

    temp_now = round(curr.get("temperature_2m", 0))
    feels_like = round(curr.get("apparent_temperature", 0))
    hum = curr.get("relative_humidity_2m", 0)
    wind = round(curr.get("wind_speed_10m", 0))
    press = round(curr.get("surface_pressure", 1013))
    w_code = curr.get("weather_code", 0)
    condition = weather_desc(w_code)

    now = datetime.datetime.now()
    datum_str = now.strftime("%A, %B %d, %Y")
    cas_str = now.strftime("%H:%M")

    # Horni lista
    draw.text((25, 20), datum_str.upper(), fill=0, font=font)
    draw.text((520, 20), cas_str, fill=0, font=font)
    draw.line([(25, 45), (575, 45)], fill=0, width=2)

    # Aktualni stav
    draw.text((25, 60), f"WEATHER STATION - {CITY_NAME}", fill=0, font=font)
    draw.text((25, 95), f"TEMPERATURE: {temp_now} C  (Feels like: {feels_like} C)", fill=0, font=font)
    draw.text((25, 125), f"CONDITION:   {condition.upper()}", fill=0, font=font)
    draw.text((25, 155), f"WIND: {wind} km/h   |   HUMIDITY: {hum} %   |   PRESSURE: {press} hPa", fill=0, font=font)

    sunrise = daily.get("sunrise", ["--:--"])[0].split("T")[-1]
    sunset = daily.get("sunset", ["--:--"])[0].split("T")[-1]
    draw.text((25, 185), f"SUNRISE: {sunrise}   |   SUNSET: {sunset}", fill=0, font=font)

    draw.line([(25, 220), (575, 220)], fill=0, width=2)

    # Hodinova predpoved
    draw.text((25, 235), "NEXT 10 HOURS FORECAST:", fill=0, font=font)

    h_temps = hourly.get("temperature_2m", [])[:10]
    h_precip = hourly.get("precipitation_probability", [])[:10]

    col_w = 54
    start_x = 28
    for i in range(min(10, len(h_temps))):
        x = start_x + (i * col_w)
        h_time = f"+{i+1}h"
        t_val = f"{round(h_temps[i])}C"
        p_val = f"{h_precip[i]}%"
        
        draw.text((x, 265), h_time, fill=0, font=font)
        draw.text((x, 290), t_val, fill=0, font=font)
        draw.text((x, 315), p_val, fill=0, font=font)

    draw.line([(25, 345), (575, 345)], fill=0, width=2)

    # Denni predpoved
    draw.text((25, 360), "DAILY OUTLOOK:", fill=0, font=font)

    d_max = daily.get("temperature_2m_max", [])
    d_min = daily.get("temperature_2m_min", [])
    d_codes = daily.get("weather_code", [])

    for day_idx in range(1, min(4, len(d_max))):
        target_date = now + datetime.timedelta(days=day_idx)
        den_nazev = target_date.strftime("%A, %b %d")
        t_max = round(d_max[day_idx])
        t_min = round(d_min[day_idx])
        den_stav = weather_desc(d_codes[day_idx])

        y_offset = 390 + (day_idx - 1) * 115
        
        draw.rectangle([(25, y_offset), (575, y_offset + 95)], outline=0, width=2)
        draw.text((45, y_offset + 18), den_nazev.upper(), fill=0, font=font)
        draw.text((45, y_offset + 48), f"Condition: {den_stav}", fill=0, font=font)
        draw.text((380, y_offset + 30), f"MAX: {t_max} C  /  MIN: {t_min} C", fill=0, font=font)

    # Paticka
    draw.line([(25, 755), (575, 755)], fill=0, width=1)
    draw.text((25, 768), "Updated via GitHub Actions | Open-Meteo API", fill=0, font=font)

    img.convert("L").save("weather.png", "PNG")

if __name__ == "__main__":
    w_data = get_weather()
    create_image(w_data)
