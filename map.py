from PIL import Image
from copy import copy


class Layer:
    """ A layer or image layer holds an image and can perform operations on the image
    Filters can be applied to an image through the add_filter method, a filter should be a function which takes an image and returns an image. The filters are applied to the image in the same order as they are added. 
    """
    def __init__(self, image: Image.Image):
        self.img = image.convert("RGBA")
        self.filters = []; self.reset_filters()
        self.mask = Image.new("L", self.image.size, (1,))
    
    
    def reset_filters(self):
        self.filters = [lambda img: img]
    
        
    def load_image(self, image: Image.Image):
        self.img = copy(image)
    
    
    def load_image_from_path(self, path: str):
        self.img = Image.open(path)
    
    
    def put_filter(self, filter_func: function):
        self.filter = filter_func
    
    
    def apply_filters(self):
        for filter in self.filters:
            self.image = filter(self.image)
        self.reset_filters
    
    
    def get_image(self, filter = True, mask = True) -> Image.Image:
        image: Image.Image = copy(self.image)
        
        if mask:
            image.putalpha(self.mask)
        
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
        
    