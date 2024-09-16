from PIL import Image

from continent import Continent
from world import World
from consts import *

w = World('Testworld')

c1 = Continent('Testmerica', 2200)
# c2 = Continent('Testope', 1800)
# c3 = Continent('Testralia', 1600)
# c4 = Continent('Testfrica', 3100)

w.add_continent(c1)
# w.add_continent(c2)
# w.add_continent(c3)
# w.add_continent(c4)

# mask, height_map = w.mask_and_height_map()
# mask.show()
# height_map.show()

w = World('Testworld')
w.continental_drift_generation()
mask, height_map = w.mask_and_height_map()

image = Image.new('RGB', mask.size, (0, 0, 0))
image.paste(mask, (0, 0))
image.show()