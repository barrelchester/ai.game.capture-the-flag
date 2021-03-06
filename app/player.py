import random
import numpy as np

import pygame_utils as pyg

from navigation import Navigation
from high_level_policy import HighLevelPolicy


# human controlled or AI Agent controlled player classes

class Player():
    '''
    Base player functionality and helper methods
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        '''
        x,y - the player/agent sprite starting location on the map
        idx - the player index (unique per team)
        team - blue or red
        nav_type - navigation algorithm: ['direct', 'bfs', 'dfs', 'astar']
        the_map - a reference to the global map with speeds, flag locations, player locations
        config - configurable settings
        '''
        self.config = config
        self.nav_type = nav_type
        self.navigation = Navigation(the_map)
        
        # list of actions for current goal
        self.goal_actions = []
        
        
        # needed for preventing sprite from overlapping a 0 speed location
        self.half_size = config.terrain_tile_size // 2

        # w,a,d,s are the keyboard directions for up, left, right, down
        self.actions = ['w', 'a', 'd', 's']

        # for debugging
        self.speed_terr = {v: k for k, v in self.config.terrain_speeds.items()}

        self.player_idx = idx
        self.team = team
        self.the_map = the_map
        self.sprite = None

        # current status
        self.speed = self.config.player_max_speed
        self.has_flag = False
        self.is_incapacitated = False
        self.incapacitated_countdown = 0
        self.in_enemy_territory = False
        self.in_flag_area = False

        self.x = x
        self.y = y
        self.tile_col, self.tile_row = self.the_map.xy_to_cr(x, y)
        self.blocked_countdown = 0
        
        
    def update(self, frame):
        # get movement action based on map, players, flag percepts
        action = self.get_action()

        # center of sprite, before moving the sprite test to see if the position is legal
        new_x, new_y = self.x, self.y

        # for checking sprite overlap of 0 speed area, only one side needs to be checked
        delta = (0, 0)

        # regardless of legality of move, animate the sprite

        # move right
        if action == 'd':
            pyg.changeSpriteImage(self.sprite, 0 * 8 + frame)
            new_x += self.speed
            # new_x is center of sprite, adding half size in movement direction prevents overlap 0 speed tile
            #delta = (self.half_size, 0)

        # move down
        elif action == 's':
            pyg.changeSpriteImage(self.sprite, 1 * 8 + frame)
            new_y += self.speed
            #delta = (0, self.half_size)

        # move left
        elif action == 'a':
            pyg.changeSpriteImage(self.sprite, 2 * 8 + frame)
            new_x -= self.speed
            #delta = (-self.half_size, 0)

        # move up
        elif action == 'w':
            pyg.changeSpriteImage(self.sprite, 3 * 8 + frame)
            new_y -= self.speed
            #delta = (0, -self.half_size)

        # stay still
        else:
            pyg.changeSpriteImage(self.sprite, 1 * 8 + 5)

        # only allow movement if not incapacitated
        if not self.is_incapacitated:
            # determine which tile/grid of the map would this put the player in
            tile_col, tile_row = self.the_map.xy_to_cr(new_x + delta[0], new_y + delta[1])

            speed = self.the_map.get_speed(tile_col, tile_row)

            self.in_enemy_territory = self.the_map.in_enemy_territory(self.team, tile_col)
            self.in_flag_area = self.the_map.in_flag_area(self.team, tile_col, tile_row)

            if speed:
                self.blocked_countdown = 0

                # for debugging
                if self.config.verbose and speed != self.speed:
                    print('%s player %d moved from %s to %s, speed=%d, yx=(%d, %d), rc=(%d, %d)' % (
                        self.team, self.player_idx,
                        self.speed_terr[self.speed], self.speed_terr[speed], speed, new_y, new_x, tile_row, tile_col))

                self.speed = speed
                self.x = new_x
                self.y = new_y

                # update global map with change in position
                self.the_map.agent_info[self.team][self.player_idx]['xy'] = (new_x, new_y)

                pyg.moveSprite(self.sprite, self.x, self.y)
            else:
                self.blocked_countdown = 20
            
            #update global map with change in position
            self.the_map.agent_info[self.team][self.player_idx]['xy'] = (new_x, new_y)

            pyg.moveSprite(self.sprite, self.x, self.y)
            

    def get_action(self):
        if self.actions:
            return self.actions.pop()

    
    def update_sprite(self, sprite):
        pyg.hideSprite(self.sprite)
        self.sprite = sprite
        pyg.moveSprite(self.sprite, self.x, self.y, centre=True)
        pyg.showSprite(self.sprite)
        
        
    def get_direction_to_xy(self, xy):
        #if close, use manhattan always
        if max(abs(xy[0] - self.x), abs(xy[1] - self.y)) <= (self.the_map.tile_size*3):
            x,y = xy
            delta_x, delta_y = x - self.x, y - self.y
            if abs(delta_x)>abs(delta_y):
                return ['a'] if delta_x<0 else ['d']
            else:
                return ['w'] if delta_y<0 else ['s']
            
        if self.nav_type=='astar':
            path = self.navigation.a_star((self.x, self.y), xy)
            path = list(reversed(path))
            return path
        elif self.nav_type=='bfs':
            path = self.navigation.breadth_first((self.x, self.y), xy)
            path = list(reversed(path))
            return path
        elif self.nav_type=='dfs':
            path = self.navigation.depth_first((self.x, self.y), xy)
            path = list(reversed(path))
            return path
        else:
            x,y = xy
            delta_x, delta_y = x - self.x, y - self.y
            if abs(delta_x)>abs(delta_y):
                return ['a'] if delta_x<0 else ['d']
            else:
                return ['w'] if delta_y<0 else ['s']
            
            
    def get_manhattan_direction_to_xy(self, xy):
        x,y = xy
        delta_x, delta_y = x - self.x, y - self.y
        if abs(delta_x)>abs(delta_y):
            return ['a'] if delta_x<0 else ['d']
        else:
            return ['w'] if delta_y<0 else ['s']
        
        
    def get_manhattan_direction_away_from(self, xy):
        x,y = xy
        delta_x, delta_y = self.x - x, self.y - y
        if abs(delta_x)<abs(delta_y):
            return ['a'] if delta_x<0 else ['d']
        else:
            return ['w'] if delta_y<0 else ['s']
        
        
    def go_between(self, xy1, xy2):
        x1,y1 = xy1
        x2,y2 = xy2
        midx, midy = x1 + ((x2 - x1)/2), y1 + ((y2 - y1)/2)
        return self.get_direction_to_xy((midx, midy))

        
    def get_closest_player_info_by_team(self, team):
        best_dist=float('inf')
        best_info = {}
        
        for idx, info in self.the_map.agent_info[team].items():
            if idx==self.player_idx:
                continue
                
            x, y = info['xy']
            dist = np.sqrt((self.x - x)**2 + (self.y - y)**2)
            if dist<best_dist:
                best_info = info
                
        return best_info
    
    
    def get_closest_player_info_to_xy_by_team(self, xy, team):
        best_dist=float('inf')
        best_info = {}
        x1, y1 = xy
        for idx, info in self.the_map.agent_info[team].items():
            if idx==self.player_idx:
                continue
                
            x2, y2 = info['xy']
            dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            if dist<best_dist:
                best_info = info
                
        return best_info
    
    
    def get_closest_incapacitated_player_info_by_team(self, team):
        best_dist=float('inf')
        best_info = {}
        
        for idx, info in self.the_map.agent_info[team].items():
            if idx==self.player_idx:
                continue
                
            if not info['is_incapacitated']:
                continue
                
            x, y = info['xy']
            dist = np.sqrt((self.x - x)**2 + (self.y - y)**2)
            if dist<best_dist:
                best_info = info
                
        return best_info


    
class HumanPlayer(Player):
    '''
    Simple wrapper around keyboard controls
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)
        # load sprites
        # there are flag holding, nonflag holding, and incapacitated sprites for blue player (human), blue agent, red agent
        # current sprite may change to flag holding or incapacitated sprite
        self.default_sprite = pyg.makeSprite(self.config.blue_player_sprite_path, 32)
        self.holding_flag_sprite = pyg.makeSprite(self.config.blue_player_with_flag_sprite_path, 32)
        self.incapacitated_sprite = pyg.makeSprite(self.config.blue_player_incapacitated_sprite_path, 32)

        self.sprite = self.default_sprite

        pyg.moveSprite(self.sprite, x, y, centre=True)
        pyg.showSprite(self.sprite)

        
    def get_action(self):
        new_x, new_y = self.x, self.y

        # move right
        if pyg.keyPressed("d"):
            return 'd'

        # move down
        elif pyg.keyPressed("s"):
            return 's'

        # move left
        elif pyg.keyPressed("a"):
            return 'a'

        # move up
        elif pyg.keyPressed("w"):
            return 'w'

        

class AgentPlayer(Player):
    '''
    Agent base - moves around randomly
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)
        self.prev_dir = 'a' if team == 'red' else 'd'

        # load sprites
        # there are flag holding, nonflag holding, and incapacitated sprites for blue player (human), blue agent, red agent
        # current sprite may change to flag holding or incapacitated sprite
        if team == 'blue':
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
        if random.randint(1, 20) == 1:
            self.prev_dir = random.choice(['a', 'w', 's', 'd'])

        return self.prev_dir


    
class ReflexAgentPlayer(AgentPlayer):
    '''
    Intelligent model-based reflex agent following these rules:
    
    If the flag is not in play head directly for it
    If player has the flag head directly for flag area
    If opponent has flag head directly toward them
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)
        self.goals = ['go_team_flag_area', 'chase_opponent', 'go_opponent_flag']
        self.current_goal = 'go_opponent_flag'
        
        
    def get_action(self):
        '''Get action based on current state and current goal, change goal if state changed'''
        # if blocked going direct way, try going a random direction for a while
        if self.blocked_countdown:
            if self.blocked_countdown == 20:
                dirs = ['a', 'w', 's', 'd']
                dirs.remove(self.prev_dir)
                self.prev_dir = random.choice(dirs)

            self.blocked_countdown -= 1

            if random.randint(1, 10) == 1:
                self.prev_dir = random.choice(['a', 'w', 's', 'd'])

            if self.config.verbose:
                print('%s player %d is blocked, trying different way: %s' % (self.team, self.player_idx, self.prev_dir))

            return self.prev_dir
        

        # head to flag home area if has flag and not already heading there
        if self.has_flag:
            
            #recalc directions if out of directions OR if this is a new state and therefore new goal
            if not self.goal_actions or not self.current_goal=='go_team_flag_area':
                self.current_goal='go_team_flag_area'

                if self.team == 'blue':
                    #do I need to reverse these?
                    self.goal_actions = self.get_direction_to_xy(self.the_map.blue_flag_xy)
                else:
                    self.goal_actions = self.get_direction_to_xy(self.the_map.red_flag_xy)

                if self.config.verbose:
                    print('%s player %d heading to flag area: %s' % (self.team, self.player_idx, self.goal_actions))
                    
        #flag has priority
        else:
            # the flag is being run by a red opponent, try to tag them
            if self.team == 'blue':
                if self.the_map.blue_flag_in_play:
                
                    #recalc directions if out of directions OR if this is a new state and therefore new goal
                    if not self.goal_actions or not self.current_goal=='chase_opponent':
                        self.current_goal='chase_opponent'

                        agent_info = self.the_map.agent_info['red']
                        for idx, info in agent_info.items():
                            if info['has_flag']:
                                #we specifically want manhattan directions because the opponent's position is changing
                                self.goal_actions = self.get_manhattan_direction_to_xy(info['xy'])

                                if self.config.verbose:
                                    print('%s player %d heading to tag opponent %d: %s' % (self.team, self.player_idx, idx, self.goal_actions))
                                break
                #go to opp flag area to wait
                else:
                    if not self.goal_actions or not self.current_goal=='go_opponent_flag':
                        self.current_goal='go_opponent_flag'

                        self.goal_actions = self.get_direction_to_xy(self.the_map.red_flag_xy)

                        if self.config.verbose:
                            print('%s player %d heading to flag: %s' % (self.team, self.player_idx, self.goal_actions))

            # the flag is being run by a blue opponent, try to tag them
            else:
                if self.the_map.red_flag_in_play:
                    if not self.goal_actions or not self.current_goal=='chase_opponent':
                        self.current_goal='chase_opponent'

                        agent_info = self.the_map.agent_info['blue']
                        for idx, info in agent_info.items():
                            if info['has_flag']:
                                #we specifically want manhattan directions because the opponent's position is changing
                                self.goal_actions = self.get_manhattan_direction_to_xy(info['xy'])

                                if self.config.verbose:
                                    print('%s player %d heading to tag opponent %d: %s' % (self.team, self.player_idx, idx, self.goal_actions))
                                break
                else:
                    if not self.goal_actions or not self.current_goal=='go_opponent_flag':
                        self.current_goal='go_opponent_flag'

                        self.goal_actions = self.get_direction_to_xy(self.the_map.blue_flag_xy)

                        if self.config.verbose:
                            print('%s player %d heading to flag: %s' % (self.team, self.player_idx, self.goal_actions))

                
        if self.goal_actions:
            action = self.goal_actions.pop()
        else:
            tfip = self.the_map.blue_flag_in_play if self.team == 'blue' else self.the_map.red_flag_in_play
            ofip = self.the_map.blue_flag_in_play if self.team == 'red' else self.the_map.red_flag_in_play
            print('No directions to return! curgoal: %s, team: %s, incap: %s, hasflag: %s, teamflaginplay: %s, oppflaginplay: %s' % (
                self.current_goal, self.team, self.is_incapacitated, self.has_flag, tfip, ofip))
            action = self.prev_dir
            
        return action

    
    
class HighLevelPlanningAgentPlayer(AgentPlayer):
    '''
    Intelligent model-based agent that transforms percepts into high level states
    and strategically chooses a high level plan in response. 
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)
        self.policy = HighLevelPolicy('q.npy')
        self.prev_hls = ()
        self.prev_hla = ''
        self.prev_action = 's'
        
        
    def get_action(self):
        '''Decide high level action based on current state and current goal, change goal if state changed'''
        hls = self.policy.get_high_level_state(self, self.the_map)
        
        #only change HLA if state is different
        if hls==self.prev_hls and self.goal_actions:
            return self.goal_actions.pop()
        
        #choose best HLA
        hla = self.choose_hla(hls)
        
        if self.config.verbose and self.goal_actions:
            print('STATE CHANGE, old state %s, new state %s, new hla: %s' % (self.prev_hls, hls, hla))
        self.prev_hls = hls
        
        self.goal_actions = self.hla_to_actions(hla)
            
        if self.goal_actions:
            action = self.goal_actions.pop()
        else:
            action = self.prev_action
        
        self.prev_action = action
        
        return action
    
    
    def choose_hla(self, hls):
        hla = self.prev_hla
        
        allowed_hlas = self.policy.get_available_hlas(self, self.the_map, hls)   
        
        if sum(hls)==0 or sum(hls)==1 and hls[self.policy.high_level_states.index('self_in_enemy_territory')]:
            hla='go_opponent_flag'
            
        elif hls[self.policy.high_level_states.index('self_incapacitated')]: 
            hla='wait'
            
        elif hls[self.policy.high_level_states.index('self_has_flag')]: 
            hla='go_team_flag_area'
            
        elif hls[self.policy.high_level_states.index('team_flag_in_play')]: 
            hla='go_opponent_flag_carrier'
            
        elif hls[self.policy.high_level_states.index('nearest_teammate_incapacitated')]: 
            hla='go_nearest_incapacitated_teammate'
            
        elif not hls[self.policy.high_level_states.index('self_in_enemy_territory')]: 
            hla='go_nearest_opponent'
            
        if hla not in allowed_hlas:
            hla = 'go_opponent_flag'
            
        return hla
    
        
    def hla_to_actions(self, hla):
        opponent_team = 'red' if self.team=='blue' else 'blue'
        goal_actions = []
        
        if hla=='random':
            if random.randint(1,20) == 1:
                self.prev_dir = random.choice(['a','w','s','d'])
            goal_actions = [self.prev_dir]
            
        elif hla=='go_opponent_flag':
            xy = self.the_map.red_flag_xy if self.team=='blue' else self.the_map.blue_flag_xy
            goal_actions = self.get_direction_to_xy(xy)
            
        elif hla=='go_team_flag_area':
            xy = self.the_map.blue_flag_xy if self.team=='blue' else self.the_map.red_flag_xy
            goal_actions = self.get_direction_to_xy(xy)
            
        elif hla=='go_opponent_flag_carrier':
            for info in self.the_map.agent_info[opponent_team].values():
                if info['has_flag']:
                    goal_actions = self.get_manhattan_direction_to_xy(info['xy'])
                    
        elif hla=='go_nearest_opponent':
            info = self.get_closest_player_info_by_team(opponent_team)
            goal_actions = self.get_manhattan_direction_to_xy(info['xy'])
            
        elif hla=='go_nearest_teammate':
            info = self.get_closest_player_info_by_team(self.team)
            goal_actions = self.get_direction_to_xy(info['xy'])
            
        elif hla=='go_nearest_incapacitated_teammate':
            info = self.get_closest_incapacitated_player_info_by_team(self.team)
            goal_actions = self.get_direction_to_xy(info['xy'])
            
        elif hla=='gaurd_nearest_teammate':
            info = self.get_closest_player_info_by_team(self.team)
            opp_info = self.get_closest_player_info_to_xy_by_team(info['xy'], opponent_team)
            goal_actions = self.go_between(info['xy'], opp_info['xy'])
            
        elif hla=='gaurd_teammate_flag_carrier':
            for info in self.the_map.agent_info[self.team].values():
                if info['has_flag']:
                    goal_actions = self.get_direction_to_xy(info['xy'])
                    
        elif hla=='gaurd_team_flag_area':
            xy1 = self.the_map.blue_flag_xy if self.team=='blue' else self.the_map.red_flag_xy
            info = self.get_closest_player_info_to_xy_by_team(xy1, opponent_team)
            goal_actions = self.go_between(xy1, info['xy'])
            
        elif hla=='guard_opponent_flag_area':
            xy1 = self.the_map.red_flag_xy if self.team=='blue' else self.the_map.blue_flag_xy
            info = self.get_closest_player_info_to_xy_by_team(xy1, opponent_team)
            goal_actions = self.go_between(xy1, info['xy'])
            
        elif hla=='run_away_from_nearest_opponent':
            info = self.get_closest_player_info_by_team(opponent_team)
            goal_actions = self.get_manhattan_direction_away_from(info['xy'])
            
        elif hla=='run_away_from_opponents_centroid':
            xs, ys = [],[]
            for info in self.the_map.agent_info[opponent_team].values():
                x,y = info['xy']
                xs.append(x)
                ys.append(y)
            mean_xy = (sum(xs)/len(xs), sum(ys)/len(ys))
            goal_actions = self.get_manhattan_direction_away_from(mean_xy)
            
        return goal_actions
    
    
    
class ReinforcementLearningAgentPlayer(HighLevelPlanningAgentPlayer):
    '''
    Intelligent model-based agent that transforms percepts into high level states
    and chooses a high level plan in response by utilizing a trained q-value table. 
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)

        
    def get_action(self):
        '''Select action based on expected utility from a learned q table.'''
        hls = self.policy.get_high_level_state(self, self.the_map)

        #only change HLA if state is different
        if hls==self.prev_hls and self.goal_actions:
            return self.goal_actions.pop()
        
        hla, utility = self.policy.get_high_level_action(self, self.the_map, hls, with_probability=False)
        #if self.config.verbose:
        #print('HLA %s, Utility %.4f' % (hla, utility))
        
        if self.goal_actions: # and self.config.verbose:
            print('STATE CHANGE, old state %s, new state %s, new hla: %s, utility: %.4f' % (self.prev_hls, hls, hla, utility))
        self.prev_hls = hls
    
        self.goal_actions = self.hla_to_actions(hla)
            
        if self.goal_actions:
            action = self.goal_actions.pop()
        else:
            action = self.prev_action
            
        self.prev_action = action
            
        return action
    