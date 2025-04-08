import asyncio
import python_weather

async def get_weather(city):
    # Create a weather client
    async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
        forecast = await client.get(city)
        
        # Get the first forecast (today)
        first_day = forecast.forecast[0]

        print(f"📍 Location: {city}")
        print(f"📅 Date: {first_day.date}")
        print(f"🌡️ High: {first_day.high}°F / Low: {first_day.low}°F")
        print(f"🌥️ Sky: {first_day.sky_text}")

# Run it with your desired city
if __name__ == "__main__":
    city = "Champaign, IL"
    asyncio.run(get_weather(city))



    NOT WORKING