#generate a game map and it's attributes

class MapGenerator():
    def __init__(self, config):
        #map generation can be parameterized
        
        self.default_map_path = self.map_default_path
        self.terrain_tiles_path = config.map_terrain_tiles_path
        
        
    def generate_map(self):
        pass
    