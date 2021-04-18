import random
import pygame_utils as pyg



#human controlled or AI Agent controlled player classes

class Player():
    def __init__(self, x, y, idx, team, the_map, config):
        '''
        x,y - the player/agent sprite starting location on the map
        team - blue or red
        the_map - a reference to the global map with speeds, flag locations, player locations
        config - configurable settings
        '''
        self.config = config
        
        #w,a,d,s are the keyboard directions for up, left, right, down
        self.actions = ['w', 'a', 'd', 's']
        
        #for debugging
        self.speed_terr = {v:k for k,v in self.config.terrain_speeds.items()}
        
        #configured values
        
        #TODO - implement variable default speeds so some players are naturally faster
        #self.max_speed = self.config.player_max_speed
        
        #TODO implement energy countdown to promote teamwork through revivals
        #self.max_energy = self.config.player_max_energy
        #self.min_energy = self.config.player_min_energy
        #self.energy = self.config.player_max_energy
        
        self.player_idx = idx
        self.team = team
        self.the_map = the_map
        self.sprite = None
        
        #current status
        self.speed = self.config.player_max_speed
        self.has_flag = False
        self.is_incapacitated = False
        self.incapacitated_countdown = 0
        self.in_enemy_territory = False
        self.in_flag_area = False
        
        self.x = x
        self.y = y
        self.tile_col, self.tile_row = self.the_map.xy_to_cr(x, y)
        
    
    def update(self, frame):
        #get movement action based on map, players, flag percepts
        action = self.get_action()
        
        #first test to see if the action is legal
        new_x, new_y = self.x, self.y
        
        #regardless of legality of move, animate the sprite
        
        #move right
        if action=='d':
            pyg.changeSpriteImage(self.sprite, 0*8+frame)    
            new_x += self.speed
            
        #move down
        elif action=='s':
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
            
        #only allow movement if not incapacitated
        if not self.is_incapacitated:
            #determine which tile/grid of the map would this put the player in    
            tile_col, tile_row = self.the_map.xy_to_cr(new_x, new_y)

            speed = self.the_map.get_speed(tile_col, tile_row)

            self.in_enemy_territory = self.the_map.in_enemy_territory(self.team, tile_col)
            self.in_flag_area = self.the_map.in_flag_area(self.team, tile_col, tile_row)

            if speed:
                #for debugging
                if self.config.verbose and speed != self.speed:
                    print('%s player %d moved from %s to %s' % (self.team, self.player_idx, self.speed_terr[self.speed], self.speed_terr[speed]))

                self.speed = speed
                self.x = new_x
                self.y = new_y

                pyg.moveSprite(self.sprite, self.x, self.y)
            
        
    def get_action(self):
        pass
    
    
    def update_sprite(self, sprite):
        pyg.hideSprite(self.sprite)
        self.sprite = sprite
        pyg.moveSprite(self.sprite, self.x, self.y, centre=True)
        pyg.showSprite(self.sprite)
        
    
    
class HumanPlayer(Player):
    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)
        #load sprites
        #there are flag holding, nonflag holding, and incapacitated sprites for blue player (human), blue agent, red agent
        #current sprite may change to flag holding or incapacitated sprite
        self.default_sprite = pyg.makeSprite(self.config.blue_player_sprite_path, 32)
        self.holding_flag_sprite = pyg.makeSprite(self.config.blue_player_with_flag_sprite_path, 32)
        self.incapacitated_sprite = pyg.makeSprite(self.config.blue_player_incapacitated_sprite_path, 32)
                                                   
        self.sprite = self.default_sprite
        
        pyg.moveSprite(self.sprite, x, y, centre=True)
        pyg.showSprite(self.sprite)
        
        
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
    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)
        self.prev_dir = 'a' if team=='red' else 'd'
        
        #load sprites
        #there are flag holding, nonflag holding, and incapacitated sprites for blue player (human), blue agent, red agent
        #current sprite may change to flag holding or incapacitated sprite
        if team=='blue':
            self.default_sprite = pyg.makeSprite(self.config.blue_agent_sprite_path, 32)
            self.holding_flag_sprite = pyg.makeSprite(self.config.blue_agent_with_flag_sprite_path, 32)
            self.incapacitated_sprite = pyg.makeSprite(self.config.blue_agent_incapacitated_sprite_path, 32)
        else:
            self.default_sprite = pyg.makeSprite(self.config.red_agent_sprite_path, 32)
            self.holding_flag_sprite = pyg.makeSprite(self.config.red_agent_with_flag_sprite_path, 32)
            self.incapacitated_sprite = pyg.makeSprite(self.config.red_agent_incapacitated_sprite_path, 32)
            
        self.sprite = self.default_sprite
        
        pyg.moveSprite(self.sprite, x, y, centre=True)
        pyg.showSprite(self.sprite)
        
        
    def get_action(self):
        if random.randint(1,20) == 1:
            self.prev_dir = random.choice(['a','w','s','d'])
            
        return self.prev_dir
    
    