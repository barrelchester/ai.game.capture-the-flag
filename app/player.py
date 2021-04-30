import random
import pygame_utils as pyg
from navigation import Navigation


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
        self.goals = ['opponent_flag', 'team_flag_area', 'opponent_flag_area']
        self.current_goal = 'opponent_flag'
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
            delta = (self.half_size, 0)

        # move down
        elif action == 's':
            pyg.changeSpriteImage(self.sprite, 1 * 8 + frame)
            new_y += self.speed
            delta = (0, self.half_size)

        # move left
        elif action == 'a':
            pyg.changeSpriteImage(self.sprite, 2 * 8 + frame)
            new_x -= self.speed
            delta = (-self.half_size, 0)

        # move up
        elif action == 'w':
            pyg.changeSpriteImage(self.sprite, 3 * 8 + frame)
            new_y -= self.speed
            delta = (0, -self.half_size)

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
        if self.nav_type=='astar':
            path = self.navigation.a_star((self.x, self.y), xy)
            return path
        elif self.nav_type=='bfs':
            path = self.navigation.breadth_first((self.x, self.y), xy)
            return path
        elif self.nav_type=='dfs':
            path = self.navigation.breadth_first((self.x, self.y), xy)
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

            self.goal_actions = [self.prev_dir]
            if self.config.verbose:
                print('%s player %d is blocked, trying different way: %s' % (self.team, self.player_idx, self.goal_actions))

            return self.goal_actions.pop()
        

        # head to flag home area if has flag and not already heading there
        if self.has_flag:
            
            #recalc directions if out of directions OR if this is a new state and therefore new goal
            if not self.goal_actions or not self.current_goal=='team_flag_area':
                self.current_goal='team_flag_area'

                if self.team == 'blue':
                    self.goal_actions = self.get_direction_to_xy(self.the_map.blue_flag_xy)
                else:
                    self.goal_actions = self.get_direction_to_xy(self.the_map.red_flag_xy)

                if self.config.verbose:
                    print('%s player %d heading to flag area: %s' % (self.team, self.player_idx, self.goal_actions))
                    
        #flag has priority
        else:
            # the flag is being run by a red opponent, try to tag them
            if self.team == 'blue' and self.the_map.blue_flag_in_play:
                
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


            # the flag is being run by a blue opponent, try to tag them
            if self.team == 'red' and self.the_map.red_flag_in_play:
                if not self.goal_actions or not self.current_goal=='chase_opponent':
                    self.current_goal='chase_opponent'

                    agent_info = self.the_map.agent_info['blue']
                    for idx, info in agent_info.items():
                        if info['has_flag']:
                            #we specifically want manhattan directions because the opponent's position is changing
                            self.goal_actions = self.get_manhattan_direction_to_xy(info['xy'])

                            if self.config.verbose:
                                print('%s player %d heading to tag opponent %d: %s' % (self.team, self.player_idx, idx, self.goal_actions))


            # head to red flag, if flag is in play it still may appear back there when a player is tagged
            if self.team == 'blue' and not self.the_map.red_flag_in_play:
                if not self.goal_actions or not self.current_goal=='opponent_flag':
                    self.current_goal='opponent_flag'

                    self.goal_actions = self.get_direction_to_xy(self.the_map.red_flag_xy)

                    if self.config.verbose:
                        print('%s player %d heading to flag: %s' % (self.team, self.player_idx, self.goal_actions))

            # head to blue flag
            elif self.team == 'red' and not self.the_map.blue_flag_in_play:
                if not self.goal_actions or not self.current_goal=='opponent_flag':
                    self.current_goal='opponent_flag'

                    self.goal_actions = self.get_direction_to_xy(self.the_map.blue_flag_xy)

                    if self.config.verbose:
                        print('%s player %d heading to flag: %s' % (self.team, self.player_idx, self.goal_actions))

                
        if self.goal_actions:
            action = self.goal_actions.pop()
        else:
            print('No directions to return! returning previous direction')
            action = self.prev_dir
            
        return action

    
    
class HighLevelPlanningAgentPlayer(AgentPlayer):
    '''
    Intelligent model-based agent that transforms percepts into high level states
    and strategically chooses a high level plan in response. 
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)

        
    def get_action(self):
        '''Get action based on current state and current goal, change goal if state changed'''
        pass
    
    
    
    
class ReinforcementLearningAgentPlayer(AgentPlayer):
    '''
    Intelligent model-based agent that transforms percepts into high level states
    and chooses a high level plan in response by utilizing a trained q-value table. 
    '''
    def __init__(self, x, y, idx, team, nav_type, the_map, config):
        super().__init__(x, y, idx, team, nav_type, the_map, config)

        
    def get_action(self):
        '''Get action based on current state and current goal, change goal if state changed'''
        pass
    
    
