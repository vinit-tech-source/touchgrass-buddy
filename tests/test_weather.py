import pytest
from httpx import Response
from app.weather import _describe_weather, parse_weather_data, WeatherInfo

class TestDescribeWeather:
    def test_temperature_descriptions(self):
        assert "freezing" in _describe_weather(-5, 0, 0)
        assert "chilly" in _describe_weather(8, 0, 0)
        assert "mild" in _describe_weather(18, 0, 0)
        assert "warm" in _describe_weather(25, 0, 0)
        assert "hot" in _describe_weather(35, 0, 0)
        assert "extremely hot" in _describe_weather(40, 0, 0)

class TestParseWeatherData:
    def test_basic_parsing(self):
        current = {
            "temperature_2m": 25.3,
            "precipitation": 0,
            "rain": 0,
            "wind_speed_10m": 12.5,
            "is_day": 1
        }
        daily = {
            "sunrise": ["2026-10-09T06:30"],
            "sunset": ["2026-10-09T18:45"]
        }
        info = parse_weather_data(current, daily)

        assert isinstance(info, WeatherInfo)
        assert info.temperature_c == 25.3
        assert info.wind_kmh == 12.5
        assert info.rain_chance == 0
        assert info.is_day is True
        assert info.sunrise_str == "06:30"
        assert info.sunset_str == "18:45"
