import numpy as np
from map_generator import MapGenerator


class TheMap():
    def __init__(self, config, new_map=False):
        self.config = config
        self.border_size = self.config.map_border_size
        self.tile_size = self.config.terrain_tile_size
        
        #make the map and get the terrain speeds associated with the map
        if new_map:
            if self.config.verbose:
                print('Creating new map')
            tile_cols, tile_rows = 40, 30
            pixel_dims = (self.tile_size * tile_cols, self.tile_size * tile_rows)
            self.tile_speeds, self.map_path = MapGenerator(self.config, seed=13).generate_map(pixel_dims, 
                                                                        save_path = self.config.maps_path)
        else:
            if self.config.verbose:
                print('Using default map')
            self.map_path = self.config.map_default_path
            self.tile_speeds = np.load(self.config.map_default_speed_array)
            
        self.middle_tile = self.tile_speeds.shape[1]//2
            
        self.blue_flag_tile = (0,0)
        self.blue_flag_area_tiles = []
        self.red_flag_tile = (0,0)
        self.red_flag_area_tiles = []
        
        self.player_tile = (0,0)
        self.blue_agent_tiles = []
        self.red_agent_tiles = []
        
        
    def set_flag_location(self, team, flag_x, flag_y):
        flag_c, flag_r = self.xy_to_cr(flag_x, flag_y)
        
        if team=='blue':
            self.blue_flag_tile = (flag_r, flag_c)
        else:
            self.red_flag_tile = (flag_r, flag_c)
        
        #get tiles in flag area
        flag_area_border_tiles = ((self.config.flag_area_size//self.tile_size) // 2) - 1
        for r in range(flag_r - flag_area_border_tiles, flag_r + flag_area_border_tiles + 1):
            for c in range(flag_c - flag_area_border_tiles, flag_c + flag_area_border_tiles + 1):
                if team=='blue':
                    self.blue_flag_area_tiles.append((r, c))
                else:
                    self.red_flag_area_tiles.append((r, c))
                    
        if self.config.verbose:
            print('%s flag is on %s, %s, in area %s' % (team, flag_r, flag_c, 
                    str(self.blue_flag_area_tiles) if team=='blue' else str(self.red_flag_area_tiles)))
                    
        
    def get_not_allowed_tiles(self):
        idx = np.where(self.tile_speeds==0)
        
        return list(zip(idx[0].tolist(), idx[1].tolist()))
    
    
    def xy_to_cr(self, x, y):
        return x // self.config.terrain_tile_size, y // self.config.terrain_tile_size
        
        
    def get_speed(self, tile_col, tile_row):
        return int(self.tile_speeds[tile_row, tile_col])
    
    
    def in_enemy_territory(self, team, tile_col):
        if team=='blue':
            return tile_col > self.middle_tile
        else:
            return tile_col < self.middle_tile
        
        
    def in_flag_area(self, team, tile_col, tile_row):
        if team=='blue':
            return (tile_row, tile_col) in self.blue_flag_area_tiles
        else:
            return (tile_row, tile_col) in self.red_flag_area_tiles
        