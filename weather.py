import requests

class City:
    def __init__(self, name, lat, lon, units="metric"):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.units = units
        self.get_data()

    def get_data(self):
        try:
            response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?units={self.units}&lat={self.lat}&lon={self.lon}&appid=373a3596cda75a2542ec9a5e58ad6cef")
            response_json = response.json()
            self.response_json = response_json
            self.temp = self.response_json["main"]["temp"]
            self.temp_min = self.response_json["main"]["temp_min"]
            self.temp_max = self.response_json["main"]["temp_max"]
        except:
            print("An error occurred while fetching the weather data.")

    def temp_print(self):
        units_symbol = "° C" 
        if self.units == "imperial":
            units_symbol = "° F"
        print(f"In {self.name} it is currently {self.temp}{units_symbol}")
        print(f"Today's Low: {self.temp_min}{units_symbol}")
        print(f"Today's High: {self.temp_max}{units_symbol}")

my_city = City("Tokyo", 35.6762, 139.6503)
my_city.temp_print()

vacation_city = City("Paris", 48.8566, 2.3522, units="imperial")
vacation_city.temp_print()
