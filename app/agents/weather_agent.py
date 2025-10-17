
class WeatherAgent:
    def run(self, location: str):
        return {
            "provider": "stub",
            "location": location,
            "temp_c": 27.0,
            "summary": "Partly cloudy",
            "humidity": 0.68,
        }
