from PIL import Image, ImageChops
from copy import copy
from enum import Enum



class Layer:
    """ A layer or image layer holds an image and can perform operations on the image
    Filters can be applied to an image through the add_filter method, a filter should be a function which takes an image and returns an image. The filters are applied to the image in the same order as they are added. 
    """
    class Cover(Enum):
        """ The cover mode of the image, how the image covers the image below it. """
        CENTER = 0
        TOP_LEFT = 1
        TOP_RIGHT = 2
        BOTTOM_LEFT = 3
        BOTTOM_RIGHT = 4
        STRETCH = 5
        TILE = 6
        FIT = 7
        FILL = 8
    
    def __init__(self, image: Image.Image):
        self.img = image.convert("RGBA")
        self.filters = []; self.reset_filters()
        self.mask = Image.new("L", self.img.size, (1,))
        self.cover = Layer.Cover.CENTER
        self.size = 1920, 1080
    
    
    def reset_filters(self):
        self.filters = [lambda img: img]
    
        
    def load_image(self, image: Image.Image):
        self.img = copy(image)
    
    
    def load_image_from_path(self, path: str):
        self.img = Image.open(path)
    
    
    def put_filter(self, filter_func):
        self.filter = filter_func
    
    
    def apply_filters(self):
        for filter in self.filters:
            self.img = filter(self.img)
        self.reset_filters
    
    
    def get_image(self, filter = True, mask = True) -> Image.Image:
        image: Image.Image = Image.new("RGBA", self.size, (0, 0, 0, 0))
        
        # Apply cover
        match self.cover:
            case Layer.Cover.CENTER:
                image.paste(self.img, (self.size[0]//2 - self.img.size[0]//2, self.size[1]//2 - self.img.size[1]//2))
            case Layer.Cover.TOP_LEFT:
                image.paste(self.img, (0, 0))
            case Layer.Cover.TOP_RIGHT:
                image.paste(self.img, (self.size[0] - self.img.size[0], 0))
            case Layer.Cover.BOTTOM_LEFT:
                image.paste(self.img, (0, self.size[1] - self.img.size[1]))
            case Layer.Cover.BOTTOM_RIGHT:
                image.paste(self.img, (self.size[0] - self.img.size[0], self.size[1] - self.img.size[1]))
            case Layer.Cover.STRETCH:
                resized_img = self.img.resize(self.size)
                image.paste(resized_img, (0, 0))
            case Layer.Cover.TILE:
                for x in range(0, self.size[0], self.img.size[0]):
                    for y in range(0, self.size[1], self.img.size[1]):
                        image.paste(self.img, (x, y))
            case Layer.Cover.FIT:
                scale = min(self.size[0] / self.img.size[0], self.size[1] / self.img.size[1])
                resized_img = self.img.resize((int(self.img.size[0] * scale), int(self.img.size[1] * scale)))
                image.paste(resized_img, (self.size[0]//2 - resized_img.size[0]//2, self.size[1]//2 - resized_img.size[1]//2))
            case Layer.Cover.FILL:
                scale = max(self.size[0] / self.img.size[0], self.size[1] / self.img.size[1])
                resized_img = self.img.resize((int(self.img.size[0] * scale), int(self.img.size[1] * scale)))
                image.paste(resized_img, (self.size[0]//2 - resized_img.size[0]//2, self.size[1]//2 - resized_img.size[1]//2))
            
            case _:
                raise ValueError("Invalid cover mode")
        
        # Apply mask
        if mask:
            mask_image = self.mask.resize(self.size)
            alpha_1 = mask_image.split()[0]
            alpha_2 = image.split()[3]
            mask_image = ImageChops.multiply(alpha_1, alpha_2)
            image.putalpha(mask_image)
        
        # Apply filters
        if filter:
            for f in self.filters:
                image = f(image)
        
        return image


class Map:
    
    def __init__(self):
        self.layers = []
    
    
    def add_layer_top(self, image: Image.Image):
        self.layers.append(Layer(image))
    
    
    def add_layer_bottom(self, image: Image.Image):
        self.layers.insert(0, Layer(image))
    
    
    def get_image(self, filter = True, mask = True) -> Image.Image:
        image = Image.new("RGBA", self.layers[0].size, (0, 0, 0, 0))
        for layer in self.layers:
            image.paste(layer.get_image(filter, mask))
        return image
    
    