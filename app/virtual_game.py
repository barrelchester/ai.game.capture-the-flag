import random
import numpy as np


class VirtualMap():
    def __init__(self, config, allow_barriers=False):
        self.players = []
        
        self.tile_speeds = np.load(config.map_default_speed_array)
        
        #we're not learning at tile level so remove obstacles
        if not allow_barriers:
            for i in range(1, self.tile_speeds.shape[0]-1):
                for j in range(1, self.tile_speeds.shape[1]-1):
                    if self.tile_speeds[i,j]==0:
                        self.tile_speeds[i,j]=1
        idx = np.where(self.tile_speeds==0)
        self.not_allowed = list(zip(idx[0].tolist(), idx[1].tolist())) 
        
        self.middle_tile = self.tile_speeds.shape[1]//2
        
        #flags
        blue_flag_x = 5
        col_speeds = self.tile_speeds[:, blue_flag_x]
        idx = np.where(col_speeds > 0)[0].tolist()
        blue_flag_y = random.choice(idx[2:-2])
        self.blue_flag_xy = (blue_flag_x, blue_flag_y)
        if config.verbose:
            print('blue flag xy', self.blue_flag_xy)
        
        red_flag_x = self.tile_speeds.shape[1] - blue_flag_x
        col_speeds = self.tile_speeds[:, red_flag_x]
        idx = np.where(col_speeds > 0)[0].tolist()
        red_flag_y = random.choice(idx[2:-2])
        self.red_flag_xy = (red_flag_x, red_flag_y)
        if config.verbose:
            print('red flag xy', self.red_flag_xy)
        
        self.blue_flag_area = [(x,y) for x in range(self.blue_flag_xy[0]-2, self.blue_flag_xy[0]+3) for y in range(self.blue_flag_xy[1]-2, self.blue_flag_xy[1]+3)]
        self.red_flag_area = [(x,y) for x in range(self.red_flag_xy[0]-2, self.red_flag_xy[0]+3) for y in range(self.red_flag_xy[1]-2, self.red_flag_xy[1]+3)]
        self.blue_flag_in_play = False
        self.red_flag_in_play = False
        
        
    def get_closest_player_by_team(self, player, team):
        best_dist=float('inf')
        best_player = None
        x1, y1 = player.xy
        
        for other_player in self.players:
            if other_player.player_idx==player.player_idx or not other_player.team==team:
                continue
                
            x2, y2 = other_player.xy
            dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            if dist<best_dist:
                best_player = other_player
                
        return best_player
    
    
    def get_closest_player_to_xy_by_team(self, player, xy, team):
        best_dist=float('inf')
        best_player = None
        x1, y1 = xy
        for other_player in self.players:
            if other_player.player_idx==player.player_idx or not other_player.team==team:
                continue
                
            x2, y2 = other_player.xy
            dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            if dist<best_dist:
                best_player = other_player
                
        return best_player
    
    
    def get_closest_incapacitated_player_by_team(self, player, team):
        best_dist=float('inf')
        best_player = None
        x1, y1 = player.xy
        
        for other_player in self.players:
            if other_player.player_idx==player.player_idx or not other_player.team==team or not other_player.is_incapacitated:
                continue
                
            x2, y2 = other_player.xy
            dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
            if dist<best_dist:
                best_player = other_player
                
        return best_player
    
    
    #copied from Player
    def get_direction_to_xy(self, xy1, xy2):
        x1,y1 = xy1
        x2,y2 = xy2
        delta_x, delta_y = x2 - x1, y2 - y1
        if abs(delta_x)>abs(delta_y):
            return 'a' if delta_x<0 else 'd'
        else:
            return 'w' if delta_y<0 else 's'
        
        
    def get_direction_away_from(self, xy1, xy2):
        x1,y1 = xy1
        x2,y2 = xy2
        delta_x, delta_y = x1 - x2, y1 - y2
        if abs(delta_x)<abs(delta_y):
            return 'a' if delta_x<0 else 'd'
        else:
            return 'w' if delta_y<0 else 's'
        
        
    def go_between(self, xy1, xy2, xy3):
        x2,y2 = xy2
        x3,y3 = xy3
        midx, midy = x2 + ((x3 - x2)/2), y2 + ((y3 - y2)/2)
        return self.get_direction_to_xy(xy1, (midx, midy))
    
        
        
class VirtualPlayer():
    def __init__(self, team, idx, the_map, xy):
        self.team = team
        self.player_idx = idx
        self.the_map = the_map
        self.has_flag = False
        self.is_incapacitated = False
        self.incapacitated_countdown = 0
        self.in_enemy_territory = False
        self.in_flag_area = False
        self.xy = xy
        self.prev_dir = random.choice(['a','w','s','d'])
        #for penalties
        self.got_tagged = False
        self.got_tagged_with_flag = False
        self.tagged = False
        self.tagged_flag_holder = False
        self.teammate_got_flag = False
        self.opponent_got_flag = False
        self.lost = False
        self.won = False
        
        
        
class VirtualGame():
    def __init__(self, config):
        self.verbose = config.verbose
        self.the_map = VirtualMap(config)
        if self.verbose:
            print('Map size: ', self.the_map.tile_speeds.shape)
        team_size = config.blue_team_size
        
        #put players in the map
        side = self.the_map.tile_speeds.shape[1]//3
        for team in ['blue', 'red']:
            if team=='blue':
                idx = np.where(self.the_map.tile_speeds[:,:side]>0)
            else:
                idx = np.where(self.the_map.tile_speeds[:,(side*2):]>0)
                idx = (idx[0], idx[1] + np.ones_like(idx[1]) * (side*2))
            allowed_init_tiles = list(zip(idx[0].tolist(), idx[1].tolist()))
            random.shuffle(allowed_init_tiles)
        
            for i in range(team_size):
                y, x = allowed_init_tiles.pop()
                if self.verbose:
                    print('%s player %d at (%d, %d)' % (team, i, x, y))
                player = VirtualPlayer(team, i, self.the_map, (x, y))
                self.the_map.players.append(player)
                
        #rewards
        #movement reward is speed value - 5
        self.stationary_reward = -5
        
        self.got_tagged_reward = -20
        self.got_tagged_with_flag_reward = -100
        self.tagged_reward = 20
        self.tagged_flag_holder_reward = 100
        
        self.revived_teammate_reward = 25
        self.got_flag_reward = 50
        self.teammate_got_flag_reward = 5 #30
        self.opponent_got_flag_reward = -5 #-30
        
        self.lost_reward = -500 #-1000
        self.lost_teammate_reward = -10 #-50
        self.won_reward = 500 #1000
        self.won_teammate_reward = 10 #50
        
        if self.verbose:
            for r in range(self.the_map.tile_speeds.shape[0]):
                row=[]
                for c in range(self.the_map.tile_speeds.shape[1]):
                    s = str(self.the_map.tile_speeds[r,c])
                    if self.the_map.blue_flag_xy==(c,r):
                        s = 'BF'
                    elif self.the_map.red_flag_xy==(c,r):
                        s = 'RF'
                    for player in self.the_map.players:
                        if player.xy==(c,r):
                            s = 'B-%d' % player.player_idx if player.team=='blue' else 'R-%d' % player.player_idx
                            break
                    row.append(s)
                print(',   '.join(row))
                    
            
    def step(self, player, hla):
        if self.verbose:
            print('%s player %d (has flag: %s) at %s has HLA %s' % (player.team, player.player_idx, 
                                                                      player.has_flag, str(player.xy), hla))
                
        #execute a game step for a player using high level action and policy
        opponent_team = 'red' if player.team=='blue' else 'blue'
        
        if player.is_incapacitated:
            player.incapacitated_countdown -= 1
            #is countdown over?
            if player.incapacitated_countdown<=0:
                if self.verbose:
                    print('\tno longer incapacitated')
                player.is_incapacitated = False
            else:
                if self.verbose:
                    print('\tstill incapacitated for %d rounds' % (player.incapacitated_countdown))
            return self.stationary_reward, False
                            
        action = self.__hla_to_direction(player, hla)
        if self.verbose:
            print('\tlow level action %s' % (action))
                
        #apply direction if possible
        player_x, player_y = player.xy
        new_xy = player.xy
        speed = 0
        #tile speeds is row by col, which equals y by x
        if action=='w' and (player_y-1, player_x) not in self.the_map.not_allowed:
            new_xy = (player_x, player_y-1)
            speed = self.the_map.tile_speeds[player_y-1, player_x]
        elif action=='s' and (player_y+1, player_x) not in self.the_map.not_allowed:
            new_xy = (player_x, player_y+1)
            speed = self.the_map.tile_speeds[player_y+1, player_x]
        elif action=='a' and (player_y, player_x-1) not in self.the_map.not_allowed:
            new_xy = (player_x-1, player_y)
            speed = self.the_map.tile_speeds[player_y, player_x-1]
        elif action=='d' and (player_y, player_x+1) not in self.the_map.not_allowed:
            new_xy = (player_x+1, player_y)
            speed = self.the_map.tile_speeds[player_y, player_x+1]
        
        
        #if the player didn't move
        if not speed:
            if self.verbose:
                print('\tspeed is 0')
            return self.stationary_reward, False
        
        
        #update position
        player.xy = new_xy
        if self.verbose:
            print('\tnew position: %s, speed %d' % (str(player.xy), speed))
            
        if player.team=='blue':
            if player.xy[0]>self.the_map.middle_tile and not player.in_enemy_territory:
                if self.verbose:
                    print('\tplayer entered enemy territory')
                player.in_enemy_territory=True
            elif player.xy[0]<self.the_map.middle_tile and player.in_enemy_territory:
                if self.verbose:
                    print('\tplayer exitted enemy territory')
                player.in_enemy_territory=False
        if player.team=='red':
            if player.xy[0]<self.the_map.middle_tile and not player.in_enemy_territory:
                if self.verbose:
                    print('\tplayer entered enemy territory')
                player.in_enemy_territory=True
            elif player.xy[0]>self.the_map.middle_tile and player.in_enemy_territory:
                if self.verbose:
                    print('\tplayer exitted enemy territory')
                player.in_enemy_territory=False
                
        
        #player won
        if player.team=='blue' and player.has_flag and new_xy in self.the_map.blue_flag_area:
            for other_player in self.the_map.players:
                if other_player.player_idx==player.player_idx:
                    continue
                if other_player.team==opponent_team:
                    other_player.lost = True
                else:
                    other_player.won = True
            #add rewards for other players AFTER the end signal is sent in order to award/penalize all players
            if self.verbose:
                print('\tplayer won')
            return self.won_reward, True
        elif player.team=='red' and player.has_flag and new_xy in self.the_map.red_flag_area:
            for other_player in self.the_map.players:
                if other_player.player_idx==player.player_idx:
                    continue
                if other_player.team==opponent_team:
                    other_player.lost = True
                else:
                    other_player.won = True
            if self.verbose:
                print('\tplayer won')
            return self.won_reward, True
        
        
        #player got flag
        if new_xy==self.the_map.red_flag_xy and player.team=='blue' and not self.the_map.red_flag_in_play:
            player.has_flag = True
            self.the_map.red_flag_in_play = True
            for other_player in self.the_map.players:
                if other_player.player_idx==player.player_idx:
                    continue
                if other_player.team==opponent_team:
                    other_player.opponent_got_flag = True
                else:
                    other_player.teammate_got_flag = True
            if self.verbose:
                print('\tplayer got flag')
            return self.got_flag_reward, False
        
        if new_xy==self.the_map.blue_flag_xy and player.team=='red' and not self.the_map.blue_flag_in_play:
            player.has_flag = True
            self.the_map.blue_flag_in_play = True
            for other_player in self.the_map.players:
                if other_player.player_idx==player.player_idx:
                    continue
                if other_player.team==opponent_team:
                    other_player.opponent_got_flag = True
                else:
                    other_player.teammate_got_flag = True
            if self.verbose:
                print('\tplayer got flag')
            return self.got_flag_reward, False
        
        
        #player tagged someone
        for other_player in self.the_map.players:
            #skip self
            if other_player.player_idx==player.player_idx:
                continue
                
            if not other_player.xy==new_xy:
                continue
                
            if other_player.team==opponent_team and not other_player.is_incapacitated:
                #you tagged other player
                if other_player.in_enemy_territory or other_player.has_flag:
                    other_player.is_incapacitated = True
                    other_player.incapacitated_countdown = 5
                    if other_player.has_flag:
                        other_player.has_flag = False
                        other_player.got_tagged_with_flag = True
                        if other_player.team=='blue':
                            self.the_map.red_flag_in_play = False
                        else:
                            self.the_map.blue_flag_in_play = False
                        if self.verbose:
                            print('\tplayer tagged flag carrier %s-%d' % (other_player.team, other_player.player_idx))
                        return self.tagged_flag_holder_reward, False
                    else:
                        other_player.got_tagged = True
                        if self.verbose:
                            print('\tplayer tagged %s-%d' % (other_player.team, other_player.player_idx))
                        return self.tagged_reward, False
                #other player tagged you
                elif player.in_enemy_territory or player.has_flag:
                    player.is_incapacitated = True
                    player.incapacitated_countdown = 5
                    if player.has_flag:
                        #so other player gets rewarded
                        other_player.tagged_flag_holder = True
                        player.has_flag = False
                        if player.team=='blue':
                            self.the_map.red_flag_in_play = False
                        else:
                            self.the_map.blue_flag_in_play = False
                        if self.verbose:
                            print('\tother player tagged flag carrier %s-%d' % (player.team, player.player_idx))
                        return self.got_tagged_with_flag_reward, False
                    other_player.tagged = True
                    if self.verbose:
                        print('\tother player tagged %s-%d' %(player.team, player.player_idx))
                    return self.got_tagged_reward, False
            #revived teammate?
            elif other_player.team==player.team and other_player.is_incapacitated:
                other_player.is_incapacitated = False
                other_player.incapacitated_countdown = 0
                if self.verbose:
                    print('\tplayer revived %s-%d' % (other_player.team, other_player.player_idx))
                return self.revived_teammate_reward, False
            
        #player just moved
        return -1, False
    
    
    #copied from policy agent
    def __hla_to_direction(self, player, hla):
        action = ''
        team = 'blue' if player.team=='blue' else 'red'
        opponent_team = 'red' if player.team=='blue' else 'blue'
        xy1 = player.xy
        
        if hla=='wait':
            return ''
        elif hla=='random':
            if random.randint(1,20) == 1:
                player.prev_dir = random.choice(['a','w','s','d'])
            action = player.prev_dir
        elif hla=='go_opponent_flag':
            xy2 = self.the_map.red_flag_xy if team=='blue' else self.the_map.blue_flag_xy
            action = self.the_map.get_direction_to_xy(xy1, xy2)
        elif hla=='go_team_flag_area':
            xy2 = self.the_map.blue_flag_xy if team=='blue' else self.the_map.red_flag_xy
            action = self.the_map.get_direction_to_xy(xy1, xy2)
        elif hla=='go_opponent_flag_carrier':
            for other_player in self.the_map.players:
                if not (other_player.team==opponent_team and other_player.has_flag):
                    continue
                action = self.the_map.get_direction_to_xy(xy1, other_player.xy)
                break
            #opponent is no longer carrying flag and the HLA got thru
            if not action:
                action = random.choice(['a','w','s','d'])
        elif hla=='go_nearest_opponent':
            other_player = self.the_map.get_closest_player_by_team(player, opponent_team)
            action = self.the_map.get_direction_to_xy(xy1, other_player.xy)
        elif hla=='go_nearest_teammate':
            other_player = self.the_map.get_closest_player_by_team(player, team)
            action = self.the_map.get_direction_to_xy(xy1, other_player.xy)
        elif hla=='go_nearest_incapacitated_teammate':
            other_player = self.the_map.get_closest_incapacitated_player_by_team(player, team)
            if other_player==None:
                #teammate is no longer incapacitated and the HLA got thru
                action = random.choice(['a','w','s','d'])
            else:
                action = self.the_map.get_direction_to_xy(xy1, other_player.xy)
        elif hla=='gaurd_nearest_teammate':
            other_player = self.the_map.get_closest_player_by_team(player, team)
            opponent_player = self.the_map.get_closest_player_to_xy_by_team(player, other_player.xy, opponent_team)
            action = self.the_map.go_between(player.xy, other_player.xy, opponent_player.xy)
        elif hla=='gaurd_teammate_flag_carrier':
            for other_player in self.the_map.players:
                if not (other_player.team==player.team and other_player.has_flag):
                    continue
                opponent_player = self.the_map.get_closest_player_to_xy_by_team(player, other_player.xy, opponent_team)
                action = self.the_map.get_direction_to_xy(opponent_player.xy, other_player.xy)
                break
            #teammate is no longer carrying flag and the HLA got thru
            if not action:
                action = random.choice(['a','w','s','d'])
        elif hla=='gaurd_team_flag_area':
            xy2 = self.the_map.blue_flag_xy if team=='blue' else self.the_map.red_flag_xy
            other_player = self.the_map.get_closest_player_to_xy_by_team(player, xy2, opponent_team)
            action = self.the_map.go_between(player.xy, other_player.xy, xy2)
        elif hla=='guard_opponent_flag_area':
            xy2 = self.the_map.red_flag_xy if team=='blue' else self.the_map.blue_flag_xy
            other_player = self.the_map.get_closest_player_to_xy_by_team(player, xy2, opponent_team)
            action = self.the_map.go_between(player.xy, other_player.xy, xy2)
        elif hla=='run_away_from_nearest_opponent':
            other_player = self.the_map.get_closest_player_by_team(player, opponent_team)
            action = self.the_map.get_direction_away_from(xy1, other_player.xy)
        elif hla=='run_away_from_opponents_centroid':
            xs, ys = [],[]
            for other_player in self.the_map.players:
                if not other_player.team==opponent_team:
                    continue
                xs.append(other_player.xy[0])
                ys.append(other_player.xy[1])
            mean_xy = (sum(xs)/len(xs), sum(ys)/len(ys))
            action = self.the_map.get_direction_away_from(xy1, mean_xy)
            
        return action
    
    