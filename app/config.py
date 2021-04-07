#store config values (paths, defaults, various constants, etc.) as properties in the Config class
import os


class Config():
    def __init__(self):
        #constants
        
        self.map_border_size = 20
        self.terrain_tile_size = 20
        self.flag_area_size = 100
        
        self.screen_width = self.terrain_tile_size*40 + self.map_border_size*2
        self.screen_height = self.terrain_tile_size*30 + self.map_border_size*2
        
        
        #for pygame display
        self.game_name = 'Capture the Flag'
        #TODO
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
        
        
        #map paths
        self.maps_path = '%s/maps' % self.resources_path
        self.map_default_path = '%s/map_840_640.png' % self.maps_path
        #a matrix of speeds associated with each terrain tile in the default map
        self.map_default_speed_array = '%s/map_speed_840_640.npy' % self.maps_path
        self.map_terrain_tiles_path = '%s/terrain_tiles' % self.maps_path
        
        
        #sprite paths
        self.sprites_path = '%s/sprites' % self.resources_path
        
        #flags
        self.blue_flag_sprite_path = '%s/blue_flag_%d.png' % (self.sprites_path, self.terrain_tile_size)
        self.red_flag_sprite_path = '%s/red_flag_%d.png' % (self.sprites_path, self.terrain_tile_size)
        
        #players and agents with and without flags
        self.blue_player_sprite_path = '%s/blue_player.gif' % self.sprites_path
        self.blue_player_with_flag_sprite_path = '%s/blue_player_with_flag.gif' % self.sprites_path
        self.blue_player_incapacitated_sprite_path = '%s/blue_player_incapacitated.gif' % self.sprites_path
        
        self.blue_agent_sprite_path = '%s/blue_agent.gif' % self.sprites_path
        self.blue_agent_with_flag_sprite_path = '%s/blue_agent_with_flag.gif' % self.sprites_path
        self.blue_agent_incapacitated_sprite_path = '%s/blue_agent_incapacitated.gif' % self.sprites_path
        
        self.red_agent_sprite_path = '%s/red_agent.gif' % self.sprites_path
        self.red_agent_with_flag_sprite_path = '%s/red_agent_with_flag.gif' % self.sprites_path
        self.red_agent_incapacitated_sprite_path = '%s/red_agent_incapacitated.gif' % self.sprites_path
        
        #sounds
        self.sounds_path = '%s/sounds' % self.resources_path
        
        #music
        #no copyright - Jeremy Blake 'Powerup!'
        self.default_game_music = '%s/game_music.mp3' % self.sounds_path
        self.end_game_music = '%s/end_game_music.mp3' % self.sounds_path
        
        self.grabbed_flag_sound = '%s/yeehaa.mp3' % self.sounds_path
        self.incapacitated_sound = '%s/incapacitated.mp3' % self.sounds_path
        self.dropped_flag_sound = '%s/boing.mp3' % self.sounds_path
        self.tagged_sound = '%s/whip_slap.mp3' % self.sounds_path
        self.revived_sound = '%s/revived.mp3' % self.sounds_path
        self.tagged_flag_carrier_sound = '%s/slap_bonk.mp3' % self.sounds_path
        self.victory_sound = '%s/victory.mp3' % self.sounds_path

        #various defaults for instantiating objects
        
        #pygame related
        
        
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
        self.blue_team_size = 5
        self.red_team_size = 5
        
        #player/agent
        self.player_max_speed = 10
        self.player_max_energy = 100
        self.player_min_energy = 10
        
        #terrain
        self.terrain_speeds = {'lake':0, 'swamp':6, 'plain':10, 'hill':4, 'mountain':2}

        
        
        #TODO - menu items
        self.menu_path = '%s/menu' % self.resources_path
        self.menu_background_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_game_mode_select_image_path  = '%s/menu_mode_select.png' % self.menu_path
        self.menu_team_size_select_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_regenerate_map_button_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_start_game_button_image_path = '%s/menu_background.png' % self.menu_path
        self.menu_map_display_image_path = '%s/menu_map_display.png' % self.menu_path