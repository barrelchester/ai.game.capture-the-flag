import sys, os, random
import numpy as np
from PIL import Image, ImageDraw


#sample usage of this class:

#config = Config()
#map_gen = MapGenerator(config)
#tile_size=20   #tiles are in resources/maps/terrain_tiles, choose an existing size, 20 or 30 fit well
#tile_cols, tile_rows = 40, 30
#the_map, map_speeds = map_gen.generate_map(pixel_dims=(tile_size*tile_cols, tile_size*tile_rows), save_path=config.maps_path)



class MapGenerator():
    '''Generates a random map composed of terrain tiles and a border, as well as a matrix
    of the speeds associated with the different terrain tiles.'''
    
    def __init__(self, config, seed=42):
        '''config provides the necessary paths and map parameters'''
        self.maps_path = config.maps_path
        self.map_terrain_tiles_path = config.map_terrain_tiles_path
        self.terrain_tile_size = config.terrain_tile_size
        self.terrain_speeds = config.terrain_speeds
        self.map_border_size = config.map_border_size
        
        self.perlin_noise_generator = PerlinNoise(seed)
        
        
    def generate_map(self, pixel_dims, save_path):
        '''Generate a map roughly the size of the provided pixel dimensions, modulus the tile size.'''
        tiles = self.__load_terrain_tiles()
        if not tiles:
            print('Tiles of size %d not found in %s' % (self.terrain_tile_size, self.terrain_tiles_path))
            return
        
        borders, corners = self.__load_boarder_tiles()
        
        tile_cols = pixel_dims[0]//self.terrain_tile_size
        tile_rows = pixel_dims[1]//self.terrain_tile_size
        
        #perlin outputs a square so select the max dimension
        perlin_dim = max(tile_rows, tile_cols)
        
        #this sized chunk will be used to calculate terrain type to paste
        perlin_avg_over = 5
        
        #generate perlin noise
        noise = self.perlin_noise_generator.generate_noise(perlin_dim*perlin_avg_over, 
                                            num_octaves=4, persistence=0.5, grid_size=(50,50))
        
        #create the map and speed matrix
        the_map, map_speeds = self.__render_map(tiles, borders, corners, tile_rows, tile_cols, perlin_avg_over, noise)
        
        map_path = '%s/map_%d_%d.png' % (save_path, 
                                       tile_cols*self.terrain_tile_size + self.map_border_size*2, 
                                       tile_rows*self.terrain_tile_size + self.map_border_size*2)
        print('saving map and map speeds array', map_path)
        the_map.save(map_path)
        np.save(map_path.replace('map_', 'map_speed_').replace('.png', ''), map_speeds)
        
        the_map.close()
        
        for im in tiles.values():
            im.close()
            im = None
        for im in borders:
            im.close()
            im = None
        for im in corners:
            im.close()
            im = None
            
        return map_speeds, map_path
            
        
    def __render_map(self, tiles, borders, corners, tile_rows, tile_cols, perlin_avg_over, noise):
        the_map = Image.new('RGB', (tile_cols*self.terrain_tile_size + 2*self.map_border_size, 
                                    tile_rows*self.terrain_tile_size + 2*self.map_border_size))

        #add borders
        self.__add_borders(the_map, borders, corners, tile_rows, tile_cols)
        
        #store mapping of terrain to associated speeds for this map - include borders (+2)
        map_speeds = np.zeros((tile_rows+2, tile_cols+2))
        print(map_speeds.shape)

        #set thresholds for determining which terrain type to use based on mean perlin sample
        min_val = noise.min()
        thr = (noise.max() - min_val)//len(self.terrain_speeds)
        terr_thresholds = {'lake':(min_val + thr*1),
                          'swamp':(min_val + thr*2),
                          'plain':(min_val + thr*3),
                          'hill':(min_val + thr*4),
                          'mountain':(min_val + thr*5)}
        
        #take a chunk of perlin noise, map terrain type to it, paste it in the image
        y_off = 0
        for i in range(tile_cols):
            x_off = 0
            for j in range(tile_rows):
                chunk = noise[y_off:y_off+perlin_avg_over, x_off:x_off+perlin_avg_over]
                
                #this makes things a little less smooth
                r = random.choice([1,2,3])
                if r==1:
                    m = chunk.min()
                if r==2:
                    m = chunk.mean()
                if r==3:
                    m = chunk.max()

                #Lakes should have a clear border, no blending
                if m < terr_thresholds['lake']:
                    rot=random.choice([0,90,180,270])

                    the_map.paste(tiles['lake'].rotate(rot), (i*self.terrain_tile_size + self.map_border_size, 
                                                              j*self.terrain_tile_size + self.map_border_size))
                    #plus 1 for the borders
                    map_speeds[j+1,i+1] = self.terrain_speeds['lake']
                    
                #swamps
                elif m < terr_thresholds['swamp']:
                    rot=random.choice([0,90,180,270])

                    the_map.paste(tiles['swamp'].rotate(rot), (i*self.terrain_tile_size + self.map_border_size, 
                                                               j*self.terrain_tile_size + self.map_border_size))
                    map_speeds[j+1,i+1] = self.terrain_speeds['swamp']
                    
                #plains - can blend with swamps
                elif m < terr_thresholds['plain']:
                    alpha = (m - terr_thresholds['swamp']) / (terr_thresholds['plain'] - terr_thresholds['swamp'])
                    land = Image.blend(tiles['plain'], tiles['swamp'], alpha=alpha*0.5)

                    rot=random.choice([0,90,180,270])

                    the_map.paste(land.rotate(rot), (i*self.terrain_tile_size + self.map_border_size, 
                                                     j*self.terrain_tile_size + self.map_border_size))
                    map_speeds[j+1,i+1] = self.terrain_speeds['plain']
                    
                #hills blend with plain
                elif m < terr_thresholds['hill']:
                    alpha = (m - terr_thresholds['plain']) / (terr_thresholds['hill'] - terr_thresholds['plain'])
                    land = Image.blend(tiles['hill'], tiles['plain'], alpha=alpha*0.5)

                    rot=random.choice([0,90,180,270])

                    the_map.paste(land.rotate(rot), (i*self.terrain_tile_size + self.map_border_size, 
                                                     j*self.terrain_tile_size + self.map_border_size))
                    map_speeds[j+1,i+1] = self.terrain_speeds['hill']
                    
                #mountain blend with hills
                elif m < terr_thresholds['mountain']:
                    alpha = (m - terr_thresholds['hill']) / (terr_thresholds['mountain'] - terr_thresholds['hill'])
                    land = Image.blend(tiles['mountain'], tiles['hill'], alpha=alpha*0.5)

                    rot=random.choice([0,90,180,270])

                    the_map.paste(land.rotate(rot), (i*self.terrain_tile_size + self.map_border_size, 
                                                     j*self.terrain_tile_size + self.map_border_size))
                    map_speeds[j+1,i+1] = self.terrain_speeds['mountain']
                    
                #unblended mountain
                else:
                    rot=random.choice([0,90,180,270])
                    the_map.paste(tiles['mountain'].rotate(rot), (i*self.terrain_tile_size + self.map_border_size, 
                                                                  j*self.terrain_tile_size + self.map_border_size))
                    map_speeds[j+1,i+1] = self.terrain_speeds['mountain']
                    
                x_off+=perlin_avg_over
                
            y_off+=perlin_avg_over
    
        return the_map, map_speeds
    
    
    def __add_borders(self, the_map, borders, corners, tile_rows, tile_cols):
        the_map.paste(random.choice(corners), (0, 0))
        for i in range(tile_cols):
            the_map.paste(random.choice(borders), (self.map_border_size + i*self.terrain_tile_size, 0))
        
        the_map.paste(random.choice(corners).rotate(270), (self.map_border_size + tile_cols*self.terrain_tile_size, 0))
        for i in range(tile_rows):
            the_map.paste(random.choice(borders).rotate(270), (self.map_border_size + tile_cols*self.terrain_tile_size, 
                                                              self.map_border_size + i*self.terrain_tile_size))
        
        the_map.paste(random.choice(corners).rotate(180), (self.map_border_size + tile_cols*self.terrain_tile_size,
                                                           self.map_border_size + tile_rows*self.terrain_tile_size))
        for i in range(tile_cols):
            the_map.paste(random.choice(borders).rotate(180), (self.map_border_size + i*self.terrain_tile_size, 
                                                              self.map_border_size + tile_rows*self.terrain_tile_size))
            
        the_map.paste(random.choice(corners).rotate(90), (0, self.map_border_size + tile_rows*self.terrain_tile_size))
        for i in range(tile_rows):
            the_map.paste(random.choice(borders).rotate(90), (0, self.map_border_size + i*self.terrain_tile_size))
        
    
    def __load_terrain_tiles(self):
        tiles = {}
        for terr_type in self.terrain_speeds:
            p = '%s/%s_tile_%d.png' % (self.map_terrain_tiles_path, terr_type, self.terrain_tile_size)
            if os.path.exists(p):
                tiles[terr_type] = Image.open(p)
                
        return tiles
    
    
    def __load_boarder_tiles(self):
        borders=[]
        corners=[]
        
        size = '_%d.png' % self.map_border_size
        for fn in os.listdir(self.maps_path):
            if fn.startswith('border') and size in fn:
                borders.append(Image.open('%s/%s' % (self.maps_path, fn)))
            elif fn.startswith('corner') and size in fn:
                corners.append(Image.open('%s/%s' % (self.maps_path, fn)))
                
        return borders, corners
    

    

class PerlinNoise(object):
    '''
    PerlinNoise: An implementation typically involves three steps: defining a grid of random gradient vectors, computing the
    dot product between the gradient vectors and their offsets, and interpolation between these values.

    Define an n-dimensional grid where each grid intersection has associated with it a fixed random n-dimensional unit-length
    gradient vector, except in the one dimensional case where the gradients are random scalars between -1 and 1.

    For working out the value of any candidate point, first find the unique grid cell in which the point lies.
    Then the 2^n corners of that cell, and their associated gradient vectors, are identified.
    Next, for each corner, an offset vector is calculated, being the displacement vector from the candidate point to that corner.

    For each corner, we take the dot product between its gradient vector and the offset vector to the candidate point.
    This dot product will be zero if the candidate point is exactly at the grid corner.
    '''
    
    def __init__(self, seed=0):
        self.rand_seed = seed
            

    def generate_noise(self, dim, num_octaves=4, persistence=0.7, d_theta=0.05, grid_size=(100,100), save_image=True):
        self.d_theta = d_theta
        self.grid_size = grid_size
        
        if self.rand_seed:
            np.random.seed(self.rand_seed)
        
        self.grads = np.random.uniform(-1, 1, (dim, dim, 2))
        
        norm = np.sqrt(np.sum(self.grads**2, 2))
        
        self.grads[:,:,0] /= norm
        self.grads[:,:,1] /= norm
        
        cos_t = np.cos(self.d_theta)
        sin_t = np.sin(self.d_theta)
        
        d0 = cos_t*self.grads[:,:,0] - sin_t*self.grads[:,:,1]
        d1 = sin_t*self.grads[:,:,0] + cos_t*self.grads[:,:,1]

        self.grads[:,:,0] = d0
        self.grads[:,:,1] = d1

        m=np.zeros((dim, dim))
        for y in range(dim):
            for x in range(dim):
                pt = self.__perlin_octaves(x, y, num_octaves, persistence)
                m[y, x]=pt
                
        m += abs(m.min())
        m = (m * 255)/m.max()
        m = m.astype('uint8')
        
        if save_image:
            im = Image.new("L", (dim, dim))
            im = Image.fromarray(m, 'L')
            path='perlin_oct%d_pers%.1f_grid%dx%d.png' % (num_octaves, persistence, self.grid_size[0], self.grid_size[1])
            print('saving', path)
            im.save(path)
        
        return m
            
        
    def __perlin_octaves(self, x, y, num_octaves, pers):
        total=0
        freq=1
        amp=1
        max_val=0
        for i in range(num_octaves):
            total += self.__perlin(x*freq, y*freq) * amp
            max_val += amp
            amp *= pers
            freq *= 2
        return total/max_val

    
    def __perlin(self, x, y):
        #id grid this point is in
        px1=int(x/self.grid_size[0])
        px2=px1+1
        py1=int(y/self.grid_size[1])
        py2=py1+1

        #range 0-1
        xingrid = (x%self.grid_size[0]) / self.grid_size[0]
        yingrid = (y%self.grid_size[1]) / self.grid_size[1]

        #distance vectors
        distx1y1 = np.array([xingrid, yingrid])    #0,0
        distx1y2 = np.array([xingrid, yingrid-1])  #0,1
        distx2y1 = np.array([xingrid-1, yingrid])  #1,0
        distx2y2 = np.array([xingrid-1, yingrid-1])#1,1

        gradx1y1 = self.grads[px1, py1]
        gradx1y2 = self.grads[px1, py2]
        gradx2y1 = self.grads[px2, py1]
        gradx2y2 = self.grads[px2, py2]
        
        x1y1dot = np.dot(gradx1y1, distx1y1)
        x1y2dot = np.dot(gradx1y2, distx1y2)
        x2y1dot = np.dot(gradx2y1, distx2y1)
        x2y2dot = np.dot(gradx2y2, distx2y2)
        
        #smoothed coords rel to grid
        cx=self.smoothstep(xingrid)
        cy=self.smoothstep(yingrid)
        
        #lin interpolate using smoothed coords
        xy1interp = self.linear_interp(x1y1dot, x2y1dot, cx)
        xy2interp = self.linear_interp(x1y2dot, x2y2dot, cx)
        interp = self.linear_interp(xy1interp, xy2interp, cy)
            
        return interp
    
    
    def smoothstep(self, t): #6t^5-15t^4+10t^3
        return t*t*t*(t*(t*6-15)+10)

    
    def linear_interp(self, x0, x1, w):
        return x0 + w * (x1 - x0)

