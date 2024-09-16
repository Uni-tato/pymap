import random
from math import pi, cos, sin
import copy

from PIL import Image, ImageDraw, ImageMorph, ImageFilter

from consts import *

# TODO:
# - manually place seeds
# - need some way to import/export the world, ideally something that a user could edit
# - calculate the "radius" of a continent, the distance from the center to the farthest point

# More complicated TODO:
# - add features to the continents:
#   - mountains
#   - rivers
#   - forests
#   - deserts
#   - cities
#   - roads
# - generate an image
# - generate a heightmap

class Continent:
    """ A large body of land with features on it
    The default radius is 2200 km, approximately the maximum radius of the united states of america (mainland).
    points is a list of tuples (x, y, size) where x and y are between -1 and 1 and size is measured in km. If left empty the points will be generated randomly
    """
    
    def __init__(self, name, radius = 2200, points:list = []):
        self.name = name
        self.radius = radius
        
        self.points = copy.deepcopy(points) # If it's not a copy then it modifies the default list which is wild and I didn't know that was a thing
        
        if len(self.points) == 0:
            self.generate_points()
            
        
    def generate_points(self, n = 300):
        relative_radius = self.radius / WORLD_HEIGHT
        for i in range(int(300 * relative_radius)): # This should be proportional to area, not radius
            r = random.gauss(0, relative_radius/2)%relative_radius
            theta = random.random() * 2 * pi
            size = abs(random.gauss(0, relative_radius/10))
            self.points.append(
                (r*cos(theta), r*sin(theta), size)
            )


    def mask_and_height_map(self, scale = 10):
        """ Generates a mask and height map of the continent
        
        scale is km per pixel: Lower values will result in a more detailed map but will take longer to generate
        """
        
        multiplier = WORLD_HEIGHT / scale
        relative_radius = self.radius / WORLD_HEIGHT
        size = int(2 * relative_radius * multiplier)
        
        image = Image.new('L', (size, size), (0,))
        draw = ImageDraw.Draw(image)
        
        # print(f"size: {size}, num_points: {len(self.points)}, points: {self.points[:5]}")
        
        # Draw the points
        for point in self.points:
            x, y = (point[0] + 1)/2 * size, (point[1] + 1)/2 * size
            # print(f"x: {x}, y: {y}")
            s = point[2] * size
            draw.ellipse(
                (x - s, y - s,
                 x + s, y + s),
                fill=(255,)
            )
        
        # Morphological operations are difficult because the image size is inconsistent
        # Generate everything at a smaller size and then scale it up?
        
        # Resize to a known size
        image = image.resize((200, 200))
        # Perform morphological closing operations
        # First create the dilation LUT
        lb = ImageMorph.LutBuilder(patterns = ["4:(.1. .0. ...)->1"])
        dilation = lb.build_lut()
        
        for i in range(4):
            _, image = ImageMorph.MorphOp(dilation).apply(image)
        
        # Now perform the erosion
        lb = ImageMorph.LutBuilder(patterns = ["4:(.0. .1. ...)->0"])
        erosion = lb.build_lut()
        
        for i in range(4):
            _, image = ImageMorph.MorphOp(erosion).apply(image)
        
        # Resize back to the original size
        image = image.resize((size, size))
        
        # Blur the image
        image = image.filter(ImageFilter.GaussianBlur(100//scale))
        # convert the image to alpha channel
        height_map = Image.new('L', (size, size), (255,))
        height_map.putalpha(image)
        # Apply a threshold
        image = image.point(lambda x: 0 if x < 128 else 255)
        mask = Image.new('L', (size, size), (255,))
        mask.putalpha(image)
        
        return mask, height_map
        

        
        
        