import json

import gspread
from configparser import ConfigParser
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from oauth2client.service_account import ServiceAccountCredentials
from urllib import parse, request, error

from weather_codes import weather_codes

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']


class ShouldIWearASweatshirtApp(App):
    def build(self):
        return MyBoxLayout()

    def send_to_drive(self, content: str):
        try:
            gc = gspread.service_account(filename='client_secret.json')
            wks = gc.open("shouldiwear_data").sheet1
            wks.append_row(content.split(','))

        except Exception as ex:
            print(ex)

    # Weather API methods
    def get_current_weather(self):
        def get_api_key():
            config = ConfigParser()
            config.read('secrets.ini')
            return config['openweather']['api_key']

        def build_weather_query(city: str):
            api_key = get_api_key()
            encoded_city = parse.quote_plus(city)

            URL = 'https://api.openweathermap.org/data/2.5/weather'
            url = f'{URL}?q={encoded_city}&units=metric&lang=pl&appid={api_key}'

            return url

        city = self.root.ids.city_input.text
        query = build_weather_query(city)
        weather_data = ''

        try:
            response = request.urlopen(query)
            data = response.read()
            weather_data = json.loads(data)

        except error.HTTPError as http_error:
            match http_error.code:
                case 401:
                    weather_data = 'No weather access. The API key may be expired.'
                case 404:
                    weather_data = f'No weather found for the city: {city}.'

        except json.JSONDecodeError:
            weather_data = 'Cannot parse server response.'

        if type(weather_data) == dict:
            weather_code = weather_data['weather'][0]['id']
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            temp_min = weather_data['main']['temp_min']
            temp_max = weather_data['main']['temp_max']
            pressure = weather_data['main']['pressure']
            humidity = weather_data['main']['humidity']
            visibility = weather_data['visibility']
            wind_speed = weather_data['wind']['speed']
            wind_deg = weather_data['wind']['deg']
            clouds = weather_data['clouds']['all']
            day_of_year = datetime.now().timetuple().tm_yday
            seconds_since_midnight = (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0,
                                                                              microsecond=0)).total_seconds()

            output_text = ''
            output_text = output_text + (f'weather_code: {weather_code} {weather_codes[str(weather_code)]}\n')
            output_text = output_text + (f'temp: {temp}\n')
            output_text = output_text + (f'feels_like: {feels_like}\n')
            output_text = output_text + (f'temp_min: {temp_min}\n')
            output_text = output_text + (f'temp_max: {temp_max}\n')
            output_text = output_text + (f'pressure: {pressure}\n')
            output_text = output_text + (f'humidity: {humidity}\n')
            output_text = output_text + (f'visibility: {visibility}\n')
            output_text = output_text + (f'wind_speed: {wind_speed}\n')
            output_text = output_text + (f'wind_deg: {wind_deg}\n')
            output_text = output_text + (f'clouds: {clouds}\n')
            output_text = output_text + (f'day_of_year: {day_of_year}\n')
            output_text = output_text + (f'seconds_since_midnight: {seconds_since_midnight}')

            self.root.ids.data_label.text = output_text

            return [weather_code,
                    temp,
                    feels_like,
                    temp_min,
                    temp_max,
                    pressure,
                    humidity,
                    visibility,
                    wind_speed,
                    wind_deg,
                    clouds,
                    day_of_year,
                    seconds_since_midnight]

    def update_choice_label(self, choice):
        choice_code = self.convert_choice_str_to_code(choice)
        self.root.ids.choice_label.text = f'Wybrano: {choice}\nKod: {choice_code}'

    def convert_choice_str_to_code(self, choice: str):
        if 'bluza i kurtka' in choice:
            return 2
        elif 'bluza lub kurtka' in choice:
            return 1
        elif 'bez bluzy' in choice:
            return 0

    def get_choice(self):
        return self.root.ids.choice_label.text

    def send_data(self):
        weather_data = self.get_current_weather()
        choice_code = self.convert_choice_str_to_code(self.get_choice())

        text_to_save = f'{", ".join(str(x) for x in weather_data)}, {choice_code}'

        print(text_to_save)
        self.send_to_drive(text_to_save)


class MyBoxLayout(BoxLayout):
    pass


if __name__ == '__main__':
    ShouldIWearASweatshirtApp().run()
