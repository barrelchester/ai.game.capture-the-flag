import pygame_utils as pyg


#human controlled or AI Agent controlled player classes

class Player():
    def __init__(self, sprite, team, tile_speeds, config):
        #wads are the keyboard directions for up, left, right, down
        #grab is for getting the flag, tag is for tagging an opponent, revive is for helping a teammate
        self.actions = ['w', 'a', 'd', 's', 'grab', 'tag', 'revive']
        self.speed_terr = {v:k for k,v in self.config.terrain_speeds.items()}
        
        #configured values
        self.max_speed = config.player_max_speed
        self.max_energy = config.player_max_energy
        self.min_energy = config.player_min_energy
        
        self.sprite = sprite
        self.team = team
        self.tile_speeds = tile_speeds
        
        #current status
        self.speed = self.max_speed
        self.energy = self.max_energy
        self.has_flag = False
        self.is_incapacitated = False
        
        self.x = 0
        self.y = 0
        
    
    def update(self, frame):
        action = self.get_action()
        
        new_x, new_y = self.x, self.y
        
        #move right
        if action=='d':
            pyg.changeSpriteImage(self.sprite, 0*8+frame)    
            new_x += self.speed
            
        #move down
        elif action=='s'
            pyg.changeSpriteImage(self.sprite, 1*8+frame)    
            new_y += self.speed
            
        #move left
        elif action=='a':
            pyg.changeSpriteImage(self.sprite, 2*8+frame)    
            new_x -= self.speed
            
        #move up
        elif action=='w':
            pyg.changeSpriteImage(self.sprite, 3*8+frame)
            new_y -= self.speed
            
        #stay still
        else:
            pyg.changeSpriteImage(self.sprite, 1 * 8 + 5)
            
        tile_col = math.floor(new_x // self.config.terrain_tile_size)
        tile_row = math.floor(new_y // self.config.terrain_tile_size)
        speed = int(self.tile_speeds[tile_row, tile_col])
        
        if speed:
            #for debugging
            if speed != self.speed:
                print('player moved from %s to %s' % (self.speed_terr[self.speed], self.speed_terr[speed]))
                
            self.speed = speed
            self.x = new_x
            self.y = new_y
            
            pyg.moveSprite(self.sprite, self.x, self.y)
            
        
    def get_action(self):
        pass
    
    
    
class HumanPlayer(Player):
    def __init__(self, sprite, team, tile_speeds, config):
        super().__init__(sprite, team, tile_speeds, config)
        
        
    def get_action(self):
        new_x, new_y = self.x, self.y
        
        #move right
        if pyg.keyPressed("d"):
            return 'd'
            
        #move down
        elif pyg.keyPressed("s"):
            return 's'
            
        #move left
        elif pyg.keyPressed("a"):
            return 'a'
            
        #move up
        elif pyg.keyPressed("w"):
            return 'w'
    
    
    
class AgentPlayer(Player):
    def __init__(self, sprite, team, tile_speeds, config):
        super().__init__(sprite, team, tile_speeds, config)
    
        
    def get_action(self):
        return 'a'