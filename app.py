import json
import pprint

from configparser import ConfigParser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from urllib import parse, request, error



class ShouldIWearASweatshirtApp(App):
    def build(self):
        return MyBoxLayout()

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

        self.root.ids.data_label.text = pprint.pformat(weather_data, indent=4, sort_dicts=False)
        return weather_data


    def update_choice_label(self, choice):
        self.root.ids.choice_label.text = 'Wybrano: ' + choice

    def send_data(self):
        weather_data = self.get_current_weather()
        pprint.pp(weather_data)



class MyBoxLayout(BoxLayout):
    pass


if __name__ == '__main__':
    ShouldIWearASweatshirtApp().run()