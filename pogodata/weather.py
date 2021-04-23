from .objects import GameMasterObject


class Weather(GameMasterObject):
    def __init__(self, icon, template, entry, wid):
        super().__init__(wid, template, entry)
        self.type_boosts = []
        self.__icon = icon

    @property
    def icon_url(self):
        return self.__icon.weather(self)


def _make_weather_list(pogodata):
    pogodata.weather = []
    wather_enum = pogodata.get_enum("WeatherCondition")
    for _, entry in pogodata.get_gamemaster(r"^WEATHER_AFFINITY_.*", "weatherAffinities"):
        template = entry["weatherCondition"]
        weather = Weather(pogodata.icon, template, entry, wather_enum.get(template))
        weather.name = pogodata.get_locale("weather_" + template)
        for boost_type in entry["pokemonType"]:
            type_ = pogodata.get_type(template=boost_type)
            weather.type_boosts.append(type_)
        pogodata.weather.append(weather)
