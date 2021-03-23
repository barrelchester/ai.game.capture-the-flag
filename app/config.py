#store config values (paths, defaults, various constants, etc.) as properties in the Config class
import os


class Config():
    def __init__(self):
        #constants
        
        #for pygame display
        self.game_name = 'Capture the Flag'
        self.game_description = ''
        self.game_rules = ''
        
        #for pygame display radio button
        self.game_mode_play = 'play'
        self.game_mode_observe = 'observe'
        
        #team related
        self.team1_name = 'blue_team'
        self.team2_name = 'red_team'
        self.team1_flag = 'blue_flag'
        self.team2_flag = 'red_flag'
        
        #terrain related
        self.terrain_plain = 'plain'
        self.terrain_swamp = 'swamp'
        self.terrain_hill = 'hill'
        self.terrain_mountain = 'mountain'
        self.terrain_chasm = 'chasm'
        self.terrain_lake = 'lake'
        
        
        #project paths
        self.app_path = '../app'
        self.resources_path = '%s/resources' % self.app_path
        
        self.game_icon_image_path = '%s/icon.png' % self.resources_path
        self.game_background_image_path = '%s/background.png' % self.resources_path
        self.team1_wins_screen = '%s/team1_wins_background.png' % self.resources_path
        self.team2_wins_screen = '%s/team2_wins_background.png' % self.resources_path
        
        #menu items
        self.menu_path = '%s/menu' % self.resources_path
        self.menu_background_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_game_mode_select_image_path  = '%s/menu_mode_select.png' % self.menu_path
        self.menu_team_size_select_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_regenerate_map_button_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_start_game_button_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_map_display_image_path = '%s/menu_map_display.png' % self.menu_path
        
        self.maps_path = '%s/maps' % self.resources_path
        self.map_default_path = '%s/default_map.png' % self.maps_path
        self.map_terrain_tiles_path = '%s/terrain_tiles' % self.maps_path
        
        
        self.sprites_path = '%s/sprites' % self.resources_path
        self.team1_player_sprite_path = '%s/team1_player_sprite.png' % self.sprites_path
        self.team1_agent_sprite_path = '%s/team1_agent_sprite.png' % self.sprites_path
        self.team1_flag_sprite_path = '%s/team1_flag_sprite.png' % self.sprites_path
        
        self.team2_player_sprite_path = '%s/team2_player_sprite.png' % self.sprites_path
        self.team2_agent_sprite_path = '%s/team2_agent_sprite.png' % self.sprites_path
        self.team2_flag_sprite_path = '%s/team2_flag_sprite.png' % self.sprites_path
        
        
        #various defaults for instantiating objects
        
        #pygame related
        self.screen_width = 1200
        self.screen_height = 700
        #slow the update rate to avoid burning up CPU
        self.game_frame_rate = 30
        self.menu_frame_rate = 10
        #transition time in seconds between initiating start of the game and the game running
        self.game_start_countdown = 3
        #transition time in seconds between ending the game and the winning team screen display
        self.game_end_countdown = 3
        #amount of time in seconds to show the winning team screen before going back to the menu
        self.game_winning_screen_countdown = 10
        
        #game play
        self.team1_size = 6
        self.team2_size = 6
        
        #player/agent
        self.player_max_speed = 10
        self.player_max_energy = 100
        self.player_min_energy = 10
        
        #terrain
        self.terrain_tile_size = 30
        self.terrain_speeds = {'lake':0, 'swamp':7, 'plain':10, 'hill':5, 'mountain':3}
        
        
        
        
