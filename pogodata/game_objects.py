class GameObject:
    def __init__(self, id_, template):
        self.id = id_
        self.template = template
        self.name = "?"
    
    def __str__(self):
        return self.template

class GameMasterObject(GameObject):
    def __init__(self, id_, template, gamemaster_entry, settings_name):
        super().__init__(id_, template)
        self.raw = gamemaster_entry.get("data", {}).get(settings_name, {})

def __make_gameobject_list(pogodata, enum, locale_key):
    types = []
    for template, id_ in pogodata.get_enum(enum).items():
        type_ = GameObject(id_, template)
        type_.name = pogodata.get_locale(locale_key.format(template=template))
        types.append(type_)
    return types

def make_type_list(pogodata):
    return __make_gameobject_list(pogodata, "HoloPokemonType", "{template}")

def make_item_list(pogodata):
    return __make_gameobject_list(pogodata, "Item", "{template}_name")
