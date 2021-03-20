from config import Config
import utils as utils
import pygame_utils as pyg



class Menu():
    def __init__(self, config, map_generator):
        self.config = config
        
        #holds a generated map, can replace generated map with .generate_map()
        self.map_generator = map_generator
        
        #create menu for getting user input
        
    def get_values(self):
        '''When Start Game button is pressed, returns dict of values populated from the menu.'''
        return

    
    
# class for game status window next to map
class GameStatusWindow():
    def __init__(self):
        pass
    def display(self):
        pass
    
    
    
#class for map GUI elements
class GameMapWindow():
    def __init__(self, game_status_window):
        pass
    def display(self):
        pass
    

    
class Game():
    def __init__(self, config):
        self.config = config
        
        #instantiate pygame objects using game vars from config
        pyg.screenSize(config.screen_width, config.screen_height)
        
        pyg.setIcon(config.game_icon_image_path)
        pyg.setWindowTitle(config.game_name)
        pyg.setBackgroundImage(config.game_background_image_path)
        
        # menu
        
        # map may be regenerated in menu, so access map_generator through menu object
        
        
    def play(self):
        #main game loop
        while True:
            #wait for values from the menu - currently includes game_mode, team_size, player_team
            
            #update background with generated map accessible through the menu
            
            #create player and agents
            
            #update sprites according to their actions
            
            #check for win
            break
            
        #shut down game
        

if __name__=='__main__':
    config = Config()
    game = Game(config)
    game.play()