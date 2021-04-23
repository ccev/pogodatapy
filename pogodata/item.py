import re
from .misc import match_enum
from .objects import GameMasterObject


class Item(GameMasterObject):
    def __init__(self, icon, id_, template, gm_entry):
        super().__init__(id_, template, gm_entry)
        self.min_level = gm_entry.get("dropTrainerLevel", 0)
        self.type = None
        self.category = None
        self.food_effects = []

        self.__icon = icon

    @property
    def icon_url(self):
        return self.__icon.item(self)


def _make_item_list(pogodata):
    pogodata.items = []
    item_enum = pogodata.get_enum("Item")
    item_gm = pogodata.get_gamemaster(r"^ITEM_.*", "itemSettings")

    categories = pogodata.get_enum("HoloItemCategory", as_enum=True)
    types = pogodata.get_enum("HoloItemType", as_enum=True)
    effects = pogodata.get_enum("HoloItemEffect", as_enum=True)
    for template, entry in item_gm:
        id_ = item_enum[template]
        item = Item(pogodata.icon, id_, template, entry)

        item.type = match_enum(types, entry.get("itemType", 0))
        item.category = match_enum(categories, entry.get("category", 0))
        
        if item.type.value == 12:
            locale_key = re.sub(r"^ITEM_", "", item.template)
            locale_key = locale_key.replace("_", "")
            locale_key += ".1_title"
        else:
            locale_key = f"{template}_name"

        item.name = pogodata.get_locale(locale_key)

        raw_food_effects = entry.get("food")
        if raw_food_effects:
            effects = raw_food_effects.get("itemEffect")
            if not effects:
                continue
            for i, template in enumerate(effects):
                percent = raw_food_effects["itemEffectPercent"][i]
                item.food_effects.append((template, percent))

        pogodata.items.append(item)
