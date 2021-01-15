# PogoData

PogoData is a Python module that allows developers to easily integrate up-to-date Pokémon GO data in their projects. This includes all kinds of info about Pokémon, Raids, Grunts, Moves, Types or Items. It gets that data from the [Protos](https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/base.proto), [GameMaster](https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json), [APK text files](https://github.com/PokeMiners/pogo_assets/tree/master/Texts/Latest%20APK/JSON) and [my pogoinfo repo](https://github.com/ccev/pogoinfo/).

### `pip install pogodata`

## Quick Guide

This is a guide on how to use this module. A proper wiki will follow.

### Initializing

Everything happens within the PogoData class. You can import it and initialize with a language, which must be one of [these](https://github.com/PokeMiners/pogo_assets/tree/master/Texts/Latest%20APK/JSON). Default is `english`

```py
>>> from pogodata import PogoData
>>> data = PogoData(language="german")
```

If your script is running 24/7, you might want to stay updated and reload data every so often. You can do that with `PogoData.reload()`, which also accepts a language.

```py
>>> data.reload(language="english")
```

### Fetching specific data

#### In-game objects

For most objects, there's a `PogoData.get_xxx()` function. They all work the same: You give it an attribute and its value of an object you're looking for and get one that matched this search. Below is a list of objects and their attributes you can refer to.

If nothing is found, `None` is being returned.

```py
>>> data.get_item(id=1).name
'Poké Ball'

>>> data.get_type(template="GRASS").id
12
# Type templates are saved as `POKEMON_TYPE_XXX` but the function also accepts just XXX
    
>>> data.get_move(name="Ice Punch").template
'ICE_PUNCH'
```

##### Pokémon

Since there can be multiple forms of a Pokémon (e.g. Venusaur, Shadow Venusaur, Clone Venusaur, Mega Venusaur), there's an `get_all` options, if you want to get a list with all Pokémon that match your search.

```py
>>> mons = data.get_mon(get_all=True, id=3)
>>> [(m.template, m.name) for m in mons]
[('VENUSAUR', 'Venusaur'), ('VENUSAUR', 'Mega Venusaur'), ('VENUSAUR_COPY_2019', 'Venusaur'), ('VENUSAUR_NORMAL', 'Venusaur'), ('VENUSAUR_NORMAL', 'Mega Venusaur'), ('VENUSAUR_PURIFIED', 'Venusaur'), ('VENUSAUR_PURIFIED', 'Mega Venusaur'), ('VENUSAUR_SHADOW', 'Venusaur')]

>>> data.get_mon(id=3).template
'VENUSAUR'
```

Additionally, ever since Shadow Forms have been released, some Pokémon's default forms are `0`, while others have the `NORMAL` type, which gives them an unique Form ID. The PokeMiners would call this the Shadow Treatment, that some Pokémon receive.

Using `PogoData.get_default_mon()` you can get the default form used by the game.

```py
>>> data.get_default_mon(name="Bidoof").form
0
>>> data.get_default_mon(name="Venusaur").form
169
# Venusaur's template would be 'VENUSAUR_NORMAL'
```

#### Raw

If you want to get raw Proto Enums, Gamemaster entries or locale data, you can use `PogoData.get_enum()`, `PogoData.get_gamemaster()` and `PogoData.get_locale()`.
