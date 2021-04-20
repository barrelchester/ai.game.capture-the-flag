import sys, random, os, math, time
import numpy as np
import pygame

#config stores constants and default settings
from config import Config
from map_generator import MapGenerator
from the_map import TheMap
from player import HumanPlayer, AgentPlayer, GreedyGoalAgentPlayer

#helpful pygame wrapper
import pygame_utils as pyg


class CaptureTheFlag():
    def __init__(self, config, new_map_seed=0):
        '''
        Load background, icon, music, sounds, create flag sprites and areas, create players
        '''
        self.config = config
        
        #sounds
        self.grabbed_flag_sound = pyg.makeSound(self.config.grabbed_flag_sound)
        self.incapacitated_sound = pyg.makeSound(self.config.incapacitated_sound)
        self.dropped_flag_sound = pyg.makeSound(self.config.dropped_flag_sound)
        self.tagged_sound = pyg.makeSound(self.config.tagged_sound)
        self.tagged_flag_carrier_sound = pyg.makeSound(self.config.tagged_flag_carrier_sound)
        self.revived_sound = pyg.makeSound(self.config.revived_sound)
        self.victory_sound = pyg.makeSound(self.config.victory_sound)
        
        #for drawing the divide and knowing when someone is off sides
        self.screen_divide_x = (self.config.screen_width//2)
        
        #stores location of terrain speeds including 0 (not allowed areas), flag location, player locations
        self.the_map = TheMap(self.config, new_map_seed)
        
        
        #set screen, title, icon, background, music
        self.__setup(self.the_map.map_path)

        
        #make flags
        self.blue_flag_sprite, self.red_flag_sprite = self.__make_flags()
        
        #update the map object with their locations
        self.the_map.set_flag_location('blue', self.blue_flag_x, self.blue_flag_y)
        self.the_map.set_flag_location('red', self.red_flag_x, self.red_flag_y)
        
        
        #make players with reference to map, and with their locations added to the map
        allowed_blue_sprite_init_tiles = self.__get_allowed_sprite_init_tiles('blue')
    
        #create user player on blue team
        self.user_player = self.__make_player(allowed_blue_sprite_init_tiles, idx=0, team='blue', agent=False)
        #set info in map
        player_info = {'xy':(self.user_player.x, self.user_player.y), 
                       'has_flag':False,
                       'is_incapacitated':False, 
                       'in_enemy_territory':False}
        self.the_map.agent_info['blue'][self.user_player.player_idx] = player_info
            
        #create other blue players
        self.blue_players = [self.user_player]
        for i in range(self.config.blue_team_size - 1):
            blue_player = self.__make_player(allowed_blue_sprite_init_tiles, idx=i+1, team='blue')
            self.blue_players.append(blue_player)
            #add player info to global map so others can access it
            player_info = {'xy':(blue_player.x, blue_player.y), 
                           'has_flag':False,
                           'is_incapacitated':False, 
                           'in_enemy_territory':False}
            self.the_map.agent_info['blue'][blue_player.player_idx] = player_info

            
        #get red side non-lake non border tile locations
        allowed_red_sprite_init_tiles = self.__get_allowed_sprite_init_tiles('red')
        
        #create red players
        self.red_players = []
        for i in range(self.config.red_team_size):
            red_player = self.__make_player(allowed_red_sprite_init_tiles, idx=i, team='red')
            self.red_players.append(red_player)
            #add player info to global map so others can access it
            player_info = {'xy':(red_player.x, red_player.y), 
                           'has_flag':False,
                           'is_incapacitated':False, 
                           'in_enemy_territory':False}
            self.the_map.agent_info['red'][red_player.player_idx] = player_info
            
        #all players
        self.players = self.blue_players + self.red_players
        
    
    def run(self):
        nextFrame = pyg.clock()
        frame = 0
        
        while True:
            #quit?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
            # We only animate our character every 80ms.
            if pyg.clock() > nextFrame:
                self.__draw_divide()
                self.__draw_flag_areas()
                # There are 8 frames of animation in each direction so the modulus 8 allows it to loop                        
                frame = (frame+1)%8                         
                nextFrame += 80 

            #execute each players action
            for player in self.players:
                player.update(frame)
            
            #game logic here
            state = self.__get_state()
            
            #handle states
            if state['blue_wins']:
                pygame.mixer.music.fadeout(1000)
                pyg.pause(1000)
                win_label = pyg.makeLabel('BLUE WINS!!!', 80, self.config.screen_width//2-200, self.config.screen_height//2-40, 
                              fontColour='blue', font='Arial', background="black")
                pyg.showLabel(win_label)
                self.end_game_music = pyg.makeMusic(self.config.end_game_music)
                pyg.playMusic()
                pyg.pause(5000)
                pygame.mixer.music.fadeout(3000)
                quit_label = pyg.makeLabel('Press Esc', 24, self.config.screen_width//2-30, self.config.screen_height//2+120, 
                              fontColour='blue', font='Arial', background="black")
                pyg.showLabel(quit_label)
                pyg.pause(3000)
                break
            elif state['red_wins']:
                pygame.mixer.music.fadeout(1000)
                pyg.pause(1000)
                win_label = pyg.makeLabel('RED WINS!!!', 80, self.config.screen_width//2-200, self.config.screen_height//2-40, 
                              fontColour='red', font='Arial', background="black")
                pyg.showLabel(win_label)
                self.end_game_music = pyg.makeMusic(self.config.end_game_music)
                pyg.playMusic()
                pyg.pause(5000)
                pygame.mixer.music.fadeout(3000)
                quit_label = pyg.makeLabel('Press Esc', 24, self.config.screen_width//2-30, self.config.screen_height//2+120, 
                              fontColour='red', font='Arial', background="black")
                pyg.showLabel(quit_label)
                pyg.pause(3000)
                break
           

            pyg.tick(10)

        pyg.endWait()
        
        
    def __get_state(self):
        '''Game logic here.'''
        state = {'blue_wins':False, 'red_wins':False}
        
        #all states can be determined by what the players are touching and where they are
        for player in self.players:
            
            #can player do anything?
            if player.is_incapacitated:
                player.incapacitated_countdown -= 1
                
                #is countdown over?
                if player.incapacitated_countdown<=0:
                    print('%s player is no longer incapacitated' % player.team)
                    self.__handle_revival(player)
                #player revived - TODO use sprite group
                elif self.__tagged_by_team_member(player):
                    print('%s player revived' % player.team)
                    self.__handle_revival(player)
                continue
                
                
            #check for win condition
            if player.has_flag and player.in_flag_area:
                if player.team=='blue':
                    print('blue wins')
                    state['blue_wins']=True
                else:
                    print('red wins')
                    state['red_wins']=True
                break
                
            
            #this player isn't touching anything
            if not pyg.allTouching(player.sprite):
                continue
                
                
            #flag grabbed?
            if not self.the_map.blue_flag_in_play and player.team=='red' and pyg.touching(player.sprite, self.blue_flag_sprite):
                print('%s player %d touched blue flag' % (player.team, player.player_idx))
                self.__handle_flag_grabbed(player, self.blue_flag_sprite)
                continue
            elif not self.the_map.red_flag_in_play and player.team=='blue' and pyg.touching(player.sprite, self.red_flag_sprite):
                print('%s player %d touched blue flag' % (player.team, player.player_idx))
                self.__handle_flag_grabbed(player, self.red_flag_sprite)
                continue
        
        
            #check for player tagged - TODO make team player sprite Groups instead of looping
            if player.in_enemy_territory or player.has_flag:
                if player.team=='blue':
                    if any([pyg.touching(player.sprite, red_player.sprite)!=None for red_player in self.red_players]):
                        print('blue player tagged')
                        self.__handle_tag(player)
                        continue
                elif player.team=='red':
                    if any([pyg.touching(player.sprite, blue_player.sprite)!=None for blue_player in self.blue_players]):
                        print('red player tagged')
                        self.__handle_tag(player)
                        continue
        
        return state
    
    
    #state actions
    
    def __handle_flag_grabbed(self, player, flag_sprite):
        pyg.playSound(self.grabbed_flag_sound)
        pyg.hideSprite(flag_sprite)
        player.has_flag = True
        player.update_sprite(player.holding_flag_sprite)
        
        #update the global map
        if player.team=='blue':
            self.the_map.red_flag_in_play = True
            self.the_map.agent_info['blue'][player.player_idx]['has_flag'] = True
        else:
            self.the_map.blue_flag_in_play = True
            self.the_map.agent_info['red'][player.player_idx]['has_flag'] = True
        
        
    def __handle_tag(self, player):
        if player.has_flag:
            pyg.playSound(self.tagged_flag_carrier_sound)
            player.has_flag = False
            
            #return flag (or drop it near them? then it will never go backwards)
            if player.team=='blue':
                pyg.moveSprite(self.red_flag_sprite, x=self.red_flag_x, y=self.red_flag_y, centre=True)
                pyg.showSprite(self.red_flag_sprite)
                
                #update the global map
                self.the_map.red_flag_in_play = False
                self.the_map.agent_info['blue'][player.player_idx]['has_flag'] = False
                self.the_map.agent_info['blue'][player.player_idx]['is_incapacitated'] = True
            else:
                pyg.moveSprite(self.blue_flag_sprite, x=self.blue_flag_x, y=self.blue_flag_y, centre=True)
                pyg.showSprite(self.blue_flag_sprite)
                
                #update the global map
                self.the_map.blue_flag_in_play = False
                self.the_map.agent_info['red'][player.player_idx]['has_flag'] = False
                self.the_map.agent_info['red'][player.player_idx]['is_incapacitated'] = True
        else:
            pyg.playSound(self.tagged_sound)
            
        pyg.playSound(self.incapacitated_sound)
        
        player.is_incapacitated = True
        #player.energy = 0
        player.update_sprite(player.incapacitated_sprite)
        player.incapacitated_countdown = 60
        
            
    def __tagged_by_team_member(self, player):
        if player.team=='blue':
            for blue_player in self.blue_players:
                #can't revive yourself!!!
                if not player==blue_player and pyg.touching(player.sprite, blue_player.sprite):
                    return True
        else:
            for red_player in self.red_players:
                if not player==red_player and pyg.touching(player.sprite, red_player.sprite):
                    return True
                
        return False
                                                            
            
    def __handle_revival(self, player):
        pyg.playSound(self.revived_sound)
        player.is_incapacitated = False
        #player.energy = self.config.player_max_energy
        player.update_sprite(player.default_sprite)
        player.incapacitated_countdown = 0
        
        #update global map
        if player.team=='blue':
            self.the_map.agent_info['blue'][player.player_idx]['is_incapacitated'] = False
        else:
            self.the_map.agent_info['red'][player.player_idx]['is_incapacitated'] = False
        
        
    def __setup(self, map_path):
        pyg.screenSize(self.config.screen_width, self.config.screen_height)
        pyg.setIcon(self.config.game_icon_image_path)
        pyg.setWindowTitle(self.config.game_name)
        
        #load the map
        pyg.setBackgroundImage(map_path)
        
        #draw dividing line
        self.__draw_divide()
        
        #music
        pyg.makeMusic(self.config.default_game_music)
        pyg.playMusic(loops=-1)
        
        
    def __draw_divide(self):
        pyg.drawLine(self.screen_divide_x-3, self.config.map_border_size,
                     self.screen_divide_x-3, self.config.screen_height - self.config.map_border_size, 
                     'blue', linewidth=3)
        
        pyg.drawLine(self.screen_divide_x, self.config.map_border_size, 
                     self.screen_divide_x, self.config.screen_height - self.config.map_border_size, 
                     'red', linewidth=3)
    
    
    def __make_flags(self):
        self.blue_flag_x, self.blue_flag_y = self.__get_flag_position(
            self.the_map, 'blue')
        self.red_flag_x, self.red_flag_y = self.__get_flag_position(
            self.the_map, 'red')
        
        self.__draw_flag_areas()
        
        blue_flag_sprite = pyg.makeSprite(self.config.blue_flag_sprite_path)
        pyg.moveSprite(blue_flag_sprite, x=self.blue_flag_x, y=self.blue_flag_y, centre=True)
        pyg.showSprite(blue_flag_sprite)
        
        red_flag_sprite = pyg.makeSprite(self.config.red_flag_sprite_path)
        pyg.moveSprite(red_flag_sprite, x=self.red_flag_x, y=self.red_flag_y, centre=True)
        pyg.showSprite(red_flag_sprite)
        
        return blue_flag_sprite, red_flag_sprite
        
        
    def __get_flag_position(self, the_map, team):
        #choose an available row along a column a set distance from the border
        pad = 20
        
        if team=='blue':
            x = the_map.border_size + self.config.flag_area_size//2 + pad
        else:
            x = self.config.screen_width - the_map.border_size - pad - self.config.flag_area_size//2
            
        flag_tile_c = x//the_map.tile_size
        
        col_speeds = the_map.tile_speeds[:, flag_tile_c]
        idx = np.where(col_speeds > 0)[0].tolist()
        
        #trim top and bottow 2 options to avoid map area going off the screen
        flag_tile_r = random.choice(idx[2:-2])
        y = flag_tile_r * the_map.tile_size
        
        return x, y

    
    def __draw_flag_areas(self):
        pyg.drawEllipse(self.blue_flag_x, self.blue_flag_y, self.config.flag_area_size, self.config.flag_area_size, 
                        colour='blue', linewidth=3)
        
        pyg.drawEllipse(self.red_flag_x, self.red_flag_y, self.config.flag_area_size, self.config.flag_area_size, 
                        colour='red', linewidth=3)
        
        
    def __get_allowed_sprite_init_tiles(self, team):
        side = self.the_map.tile_speeds.shape[1]//3
        if team=='blue':
            idx = np.where(self.the_map.tile_speeds[:,:side]>0)
        else:
            idx = np.where(self.the_map.tile_speeds[:,(side*2):]>0)
            idx = (idx[0], idx[1] + np.ones_like(idx[1]) * (side*2))
            
        allowed_init_tiles = list(zip(idx[0].tolist(), idx[1].tolist()))
        
        random.shuffle(allowed_init_tiles)
        
        return allowed_init_tiles


    def __make_player(self, allowed_sprite_init_tiles, idx=-1, team='', agent=True):
        player_r_idx, player_c_idx = allowed_sprite_init_tiles.pop()

        player_x_pos = (player_c_idx * self.config.terrain_tile_size) + self.config.terrain_tile_size//2
        player_y_pos = (player_r_idx * self.config.terrain_tile_size) + self.config.terrain_tile_size//2
        
        if self.config.verbose:
            print('%s %s on r=%s, c=%d, x=%d, y=%d' % (team, 'agent' if agent else 'player', 
                                                   player_r_idx, player_c_idx, player_x_pos, player_y_pos))

        if not agent: #this will be a different sprite
            player = HumanPlayer(player_x_pos, player_y_pos, idx, team, self.the_map, self.config)
        else:
            #player = AgentPlayer(player_x_pos, player_y_pos, idx, team, self.the_map, self.config)
            player = GreedyGoalAgentPlayer(player_x_pos, player_y_pos, idx, team, self.the_map, self.config)

        return player
    
        

if __name__=='__main__':
    print('Movement Keys: W=north, S=south, A=west, D=east') 
    config = Config(verbose=False)
    game = CaptureTheFlag(config, new_map_seed=0)
    game.run()
    