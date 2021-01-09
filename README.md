# pogodata

## Quick example
```py
from pogodata import PogoData

data = PogoData("german")
# Load data in German

greatball = data.get_item(id=2)
print(greatball.name)
# Get the item with an ID of 2 and print its name (Superball)

data.reload()
# Reload data (in English)

bulb = data.get_mon(template="BULBASAUR_NORMAL")
# Get Bulbasaur

print(bulb.name)
print([t.name for t in bulb.types])
print([m.template for m in bulb.quick_moves])
# Print Bulbasaur's name, its types and quick moves

ivy = bulb.evolutions[0]
venu = ivy.evolutions[0]
mega_venu = venu.temp_evolutions[0]
print(mega_venu.name)
# Get Venusaur by going up Bulbasaur's evolution line
# Then get Venusaur's Mega evolution and print its name
```
