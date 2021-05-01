import os, random, itertools
import numpy as np



class HighLevelPolicy:
    '''Policy for high level states (HLS) and high level actions (HLA).'''
    def __init__(self, q_matrix_path=''):
        self.epsilon = 1e-10
        
        self.high_level_actions = [
            'wait', #if stunned
            'random', #a valid strategy
           'go_opponent_flag',  #go get the flag
           'go_team_flag_area',  #especially if you have the flag
           'go_opponent_flag_carrier', #tag flag carrier
           'go_nearest_opponent', #chase
           'go_nearest_teammate', #a good choice if you have the flag
           'go_nearest_incapacitated_teammate', #revive them
           'gaurd_nearest_teammate',  #get between nearest teammate and enemy
           'gaurd_teammate_flag_carrier', #get between flag carrying teammate and enemy
           'gaurd_team_flag_area', #get between flag area and enemy
           'guard_opponent_flag_area',  #especially if opponent is running the flag
           'run_away_from_nearest_opponent',  #if being chased
           'run_away_from_opponents_centroid' #allows skirting dangerous areas
          ]
        
        self.high_level_states = [
            'opponents_flag_in_play', 
              'team_flag_in_play', 
              'self_incapacitated', 
              'self_has_flag', 
              'self_in_enemy_territory',
              'nearest_teammate_has_flag',
              'nearest_teammate_incapacitated', 
              'nearest_opponent_has_flag',
              'nearest_opponent_incapacitated'
             ]
        
        #every possible state
        self.high_level_state_codes = [tuple([int(s) for s in seq]) for seq in itertools.product('01', repeat=len(self.high_level_states))]
        
        #if q has already been trained
        if q_matrix_path:
            print('Loading Q matrix')
            self.q = np.load(q_matrix_path)
        else:
            self.q = np.zeros((len(self.high_level_state_codes), len(self.high_level_actions)))

        self.prev_hla = 'random'
        self.prev_utility = -1.0
        
    def get_high_level_action(self, player, the_map, high_level_state, with_probability=False):
        '''Get a high level action for the player based on high level percepts'''
        #this should only be called for live players, not incapacitated players, but we'll check
        if player.is_incapacitated:
            return 'wait', -1.0
        
        #this could be a never encountered before hls, if so, just return previous hla
        if high_level_state not in self.high_level_state_codes:
            print('New state found: ', high_level_state)
            return self.prev_hla, self.prev_utility
        
        state_idx = self.high_level_state_codes.index(high_level_state)
        
        #select best action with probability proportional to utility
        action_utilities = {}
        best_hla = ''
        best_utility = -float('inf')
        
        for hla in self.get_available_hlas(player, the_map, high_level_state):
            action_idx = self.high_level_actions.index(hla)
            value = self.q[state_idx, action_idx]
            action_utilities[hla] = value
            if value>best_utility:
                best_utility=value
                best_hla=hla
        
        if with_probability:
            #normalize to positive
            min_val = min(action_utilities.values())
            action_utilities = {hla:v-min_val+self.epsilon for hla,v in action_utilities.items()}

            actions = [k for k in action_utilities.keys()]
            scale = sum(action_utilities.values())
            probs = [v/scale for v in action_utilities.values()]

            #choose HLA proportional to utility
            idx = np.random.choice(len(actions), p=probs)

            hla = actions[idx]
        else:
            hla = best_hla
            
        self.prev_hla = hla
        self.prev_utility = best_utility
        
        return hla, best_utility
    
    
    def get_high_level_state(self, player, the_map):
        '''Determine which high level state applies at this time'''
        state = [0 for i in range(len(self.high_level_states))]
        
        #if player is incapacitated, that is all that matters, this saves making pointless states
        if player.is_incapacitated:
            state[self.high_level_states.index('self_incapacitated')] = 1   
            return tuple(state)
        
        if (player.team=='blue' and the_map.red_flag_in_play) or (player.team=='red' and the_map.blue_flag_in_play):
            state[self.high_level_states.index('opponents_flag_in_play')] = 1
        if (player.team=='blue' and the_map.blue_flag_in_play) or (player.team=='red' and the_map.red_flag_in_play):
            state[self.high_level_states.index('team_flag_in_play')] = 1
        if player.has_flag:
            state[self.high_level_states.index('self_has_flag')] = 1
        if player.in_enemy_territory:
            state[self.high_level_states.index('self_in_enemy_territory')] = 1
            
        teammate_info = player.get_closest_player_info_by_team(player.team)
        if teammate_info['has_flag']:
            state[self.high_level_states.index('nearest_teammate_has_flag')] = 1
        if teammate_info['is_incapacitated']:
            state[self.high_level_states.index('nearest_teammate_incapacitated')] = 1
        
        opponent_info = player.get_closest_player_info_by_team('red' if player.team=='blue' else 'blue')
        if opponent_info['has_flag']:
            state[self.high_level_states.index('nearest_opponent_has_flag')] = 1
        if opponent_info['is_incapacitated']:
            state[self.high_level_states.index('nearest_opponent_incapacitated')] = 1
            
        return tuple(state)
            
        
    def get_available_hlas(self, player, the_map, high_level_state):
        '''Determine possible high level actions given the high level state'''
        #almost all hlas are possible except the two dependent on the flag being carried
        if player.is_incapacitated:
            return ['wait']
        
        hlas = self.high_level_actions.copy()
        hlas.remove('wait')
        hlas.remove('go_opponent_flag_carrier')
        hlas.remove('gaurd_teammate_flag_carrier')
        hlas.remove('go_nearest_incapacitated_teammate')
        
        if (player.team=='blue' and the_map.blue_flag_in_play) or (player.team=='red' and the_map.red_flag_in_play):
            hlas.append('go_opponent_flag_carrier')
        if not player.has_flag and (player.team=='blue' and the_map.red_flag_in_play) or (player.team=='red' and the_map.blue_flag_in_play):
            hlas.append('gaurd_teammate_flag_carrier')
        if high_level_state[self.high_level_states.index('nearest_teammate_incapacitated')]==1:
            hlas.append('go_nearest_incapacitated_teammate')
            
        return hlas
    
    