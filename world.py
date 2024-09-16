from math import dist, pi, tan
import random
# random.seed(0)

from PIL import Image, ImageDraw, ImageOps

from consts import *
from continent import Continent

# When generating the mask make sure the continents "loop" around the edges of the map
# I think you can draw/paste the mask outside of the image bounds, it's probably not too difficult to get a "negative" coordinate

class World:
    def __init__(self, name):
        self.name = name
        self.continents = []

    
    def add_continent(self, continent, coordinates = None):
        if coordinates:
            self.continents.append((continent, coordinates))
            return True
        elif len(self.continents) == 0:
            # First continent, just place it in the center
            self.continents.append((continent, (WORLD_WIDTH * 0.5, WORLD_HEIGHT * 0.5)))
            return True
        else:
            # Randomly generate coordinates
            # if the random number is too close to an existing continent, try again
            for _ in range(100):
                x = (random.random() * 0.8 + 0.1) * WORLD_WIDTH
                y = (random.random() * 0.8 + 0.1) * WORLD_HEIGHT
                
                # Check if the continent overlaps with any existing continents
                for c, coord in self.continents:
                    if (x - coord[0])**2 + (y - coord[1])**2 < (c.radius + continent.radius)**2:
                        break
                else:
                    self.continents.append((continent, (x, y)))
                    return True
                
        return False
    
    
    class _Point:
        def __init__(self, x:int|float, y:int|float, r:float):
            self.x = x
            self.y = y
            self.r = r
            
        def center_distance(self, other) -> float:
            return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
        
        
        def max_radius(self, other) -> float:
            return self.center_distance(other) - other.r
    
    
    def continental_drift_generation(self):
        """ Generates continents by simulating continental drift."""
        
        # Generate a field of points
        # A little bit of overlap is ok, but we want to avoid large overlaps
        # Randomly placed points have too much overlap, and checking for that is expensive.
        # We can make it easier by placing points on a grid, then calculating how large they can be without overlapping.
        
        # Make the grid of points (radius = 0)
        num_points_x = 40
        num_points_y = 20
        ordered_points = [
            World._Point(x,y,0.1) 
            for y in range(num_points_y)
            for x in range(num_points_x)
        ]
        
        # Shuffle the points so we process them in a random order
        shuffled_points = ordered_points.copy()
        random.shuffle(shuffled_points)
        
        # Calculate the maximum radius for each point
        for i, point in enumerate(shuffled_points):
            # Check distance to neighboring points
            min_radius = WORLD_HEIGHT
            for (x_dif, y_dif) in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]: # Check the 8 nearest neighbors
                # calc ordered index
                x, y = point.x + x_dif, point.y + y_dif
                index = int(x + y * num_points_x)
                if index < 0 or index >= len(ordered_points):
                    continue
                neighbor = ordered_points[index]
                min_radius = min(min_radius, point.max_radius(neighbor))
            min_radius = max(min_radius, 0.1)
            
            # Now randomly set the radius without going over the maximum possible without overlap
            point.r = min_radius * random.random()
            
            # shrink the radius for points near the edge
            dist = (
                (2*point.x/num_points_x - 1)**2
                + (2*point.y/num_points_y- 1)**2
            )**0.5
            if dist > 1:
                k = (num_points_x + num_points_y) / 2
                point.r /= (dist*k) - k + 1
            
            # Add a little randomness to the position
            point.x += random.random() * 0.4 - 0.2
            point.y += random.random() * 0.4 - 0.2
        
        # show_points(ordered_points, num_points_x, num_points_y)
        
        point_sets = [(
            ordered_points, # points
            num_points_x / 2, num_points_y / 2, # center
            1.0, # weight
            0.0, 0.0 # drift
            )]
        n_cuts = random.randint(3, 8)
        # Cut the field into n pieces
        for _ in range(n_cuts):
            # Select a point_set weighted by the number of points
            # Total weight is 1
            r = random.random()
            i = 0
            while r > point_sets[i][3]:
                r -= point_sets[i][3]
                i += 1
            
            point_set = point_sets.pop(i)
            # First find a random line that cuts the field roughly in half
            # equation of a line: y = mx + b
            # To cut in half first find the center of the field
            center = point_set[1], point_set[2]
            # Now define a random angle
            angle = random.random() * 2 * pi
            m = tan(angle)
            # Now find b
            b = center[1] - m * center[0]
            line = lambda x: m * x + b
            # Create a second similar line
            angle2 = angle + pi/2 + random.random()*pi/4
            m2 = tan(angle2)
            b2 = center[1] - m2 * center[0]
            line2 = lambda x: m2 * x + b2
            
            # show the line
            # image = Image.new('L', (num_points_x * 100, num_points_y * 100), (0,))
            # draw = ImageDraw.Draw(image)
            # draw.line((0, line(0)*100, num_points_x*100, line(num_points_x)*100), fill=(255,), width=3)
            # draw.line((0, line2(0)*100, num_points_x*100, line2(num_points_x)*100), fill=(255,), width=3)
            # image.show()
            
            # Now split the field into two sets of points
            lhs, rhs = [], []
            lhs_center = (0, 0)
            rhs_center = (0, 0)
            direction1 = 1 if random.random() > 0.5 else -1
            direction2 = 1 if random.random() > 0.5 else -1
            for point in point_set[0]:
                if (
                    point.y*direction1 > line(point.x)*direction1 and
                    point.y*direction2 > line2(point.x)*direction2
                ):
                    lhs.append(point)
                    lhs_center = (lhs_center[0] + point.x, lhs_center[1] + point.y)
                else:
                    rhs.append(point)
                    rhs_center = (rhs_center[0] + point.x, rhs_center[1] + point.y)
                    
            if len(lhs) == 0 or len(rhs) == 0:
                # This cut was not useful, try again
                point_sets.append(point_set)
                continue
            
            lhs_center = (lhs_center[0] / len(lhs), lhs_center[1] / len(lhs))
            rhs_center = (rhs_center[0] / len(rhs), rhs_center[1] / len(rhs))
            
            lhs_weight = len(lhs) / len(ordered_points)
            rhs_weight = len(rhs) / len(ordered_points)
            
            lhs_drift = (
                (lhs_center[0] - point_set[1]) * lhs_weight * n_cuts,
                (lhs_center[1] - point_set[2]) * lhs_weight * n_cuts
            )
            rhs_drift = (
                (rhs_center[0] - point_set[1]) * rhs_weight * n_cuts,
                (rhs_center[1] - point_set[2]) * rhs_weight * n_cuts
            )
            
            point_sets.append((lhs, *lhs_center, lhs_weight, *lhs_drift))
            point_sets.append((rhs, *rhs_center, rhs_weight, *rhs_drift))
        
        # Now turn each piece into a continent
        n = 0
        for point_set, center_x, center_y, _, drift_x, drift_y in point_sets:
            
            center_x = (center_x-num_points_x/2)/num_points_x
            center_y = (center_y-num_points_y/2)/num_points_y
            
            p = []
            for point in point_set: # scale the points between -0.9 and 0.9
                p.append((
                    (2*point.x/num_points_x-1) * 0.9,
                    (2*point.y/num_points_y-1) * 0.9,
                    2*point.r/(num_points_x+num_points_y)
                    ))
            c = Continent(str(n:=n+1), WORLD_HEIGHT//4, p)
            
            # calculate drift
            drift_factor = (0.5*WORLD_WIDTH, 0.5*WORLD_HEIGHT)
            # move the continent in the direction of it's center relative to the center of the world
            drift_x = drift_x/num_points_x * WORLD_WIDTH
            drift_y = drift_y/num_points_y * WORLD_HEIGHT
            drift_factor = 1, 0.5
            pos = (
                WORLD_WIDTH//2 + drift_x * drift_factor[0],
                WORLD_HEIGHT//2 + drift_y * drift_factor[1]
                )
            
            self.add_continent(c, pos)
        
        return 
    
    
    def mask_and_height_map(self, scale = 10):
        """ Generates a mask and height map of the world
        
        scale is km per pixel: Lower values will result in a more detailed map but will take longer to generate
        """
        # Earth has an equatorial circumference of 40,075 km and polar circumference of 40,008 km
        # Let's assume the world is a perfect sphere with a circumference of 40,000 km
        # The height of the map will therefore be 20,000 km and the width 40,000 km or a 2:1 ratio (ignoring distortion due to curvature) 
        
        width = int(WORLD_WIDTH / scale)
        height = int(WORLD_HEIGHT / scale)
        mask = Image.new('LA', (width, height), (0,))
        height_map = Image.new('LA', (width, height), (0,))
        
        # Draw each continent
        for continent, coordinates in self.continents:
            m, h_map = continent.mask_and_height_map(scale)
            
            x, y = coordinates
            x = int(x / scale)
            y = int(y / scale)
            r = int(continent.radius / scale) # Is this still correct? I've changed a lot, TODO: check
            mask.paste(m, (x - r, y - r), m)
            height_map.paste(h_map, (x - r, y - r), h_map)
            
            # Continents can sit on the edge of the map, so we need to draw them extra times to ensure they loop around
            mask.paste(m, (x - r + width, y - r), m)
            height_map.paste(h_map, (x - r + width, y - r), h_map)
            mask.paste(m, (x - r - width, y - r), m)
            height_map.paste(h_map, (x - r - width, y - r), h_map)
        
        return mask, height_map
            
            
def show_points(points, num_points_x, num_points_y):
    # display the points
        image = Image.new('L', (num_points_x * 100, num_points_y * 100), (0,))
        draw = ImageDraw.Draw(image)
        for point in points:
            x, y = point.x * 100, point.y * 100
            r = point.r * 100
            if r > 0:
                draw.ellipse(
                    (x - r, y - r,
                     x + r, y + r),
                    outline=(255,)
                )
            else:
                r = abs(r)
                draw.ellipse(
                    (x - r, y - r,
                    x + r, y + r),
                    fill=(128,)
                )
        image.show()