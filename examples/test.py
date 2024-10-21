from PIL import Image

from continent import Continent
from world import World
from map import Map, Layer
from consts import *

# w = World('Testworld')

# c1 = Continent('Testmerica', 2200)
# c2 = Continent('Testope', 1800)
# c3 = Continent('Testralia', 1600)
# c4 = Continent('Testfrica', 3100)

# w.add_continent(c1)
# w.add_continent(c2)
# w.add_continent(c3)
# w.add_continent(c4)

# mask, height_map = w.mask_and_height_map()
# mask.show()
# height_map.show()

w = World('Testworld')
w.continental_drift_generation()
# w.add_continent(c4, (WORLD_WIDTH, WORLD_HEIGHT//2))
mask, height_map = w.mask_and_height_map()

mask_img = Image.new('RGB', mask.size, (0, 0, 0))
mask_img.paste(mask, (0, 0))
mask_img.show()

# Create a new map object
map = Map()
map.add_layer_bottom(Image.open('images/test_image.png'))
map.layers[0].mask = mask
map.layers[0].cover = Layer.Cover.STRETCH
image = map.get_image()
image.show()

