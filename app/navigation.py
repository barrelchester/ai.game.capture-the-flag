from utils import PriorityQueue, Stack



class Navigation():
    '''
    A helper class with navigation methods.
    '''
    def __init__(self, the_map):
        self.the_map = the_map
        
        
    def a_star(self, xy1, xy2):
        """Search the node that has the lowest combined cost and heuristic first."""
        tile_col1, tile_row1 = self.the_map.xy_to_cr(xy1[0], xy1[1])
        tile_col2, tile_row2 = self.the_map.xy_to_cr(xy2[0], xy2[1])
        
        successor_to_parent_map = {}
        start_state = (tile_col1, tile_row1)
        #print('x=%d, y=%d to col=%d, row=%d (map row=%d, col= %d)' % (xy1[0], xy1[1], tile_col1, tile_row1, 
        #                               self.the_map.tile_speeds.shape[0], self.the_map.tile_speeds.shape[1]))
        successor_to_parent_map[(start_state, None)] = None  # (Successor, Action) -> (Parent, Action)
        
        open_list = PriorityQueue()
        open_list.update((start_state, None), 0)
        closed = []
        
        while not open_list.isEmpty():
            current_state, action_to_current_state = open_list.pop()
            
            if current_state == (tile_col2, tile_row2):
                return self.__get_action_path((current_state, action_to_current_state), successor_to_parent_map)
            
            if current_state not in closed:
                if current_state == start_state:
                    current_cost = 0
                else:
                    current_cost = len(self.__get_action_path((current_state, action_to_current_state),
                                                               successor_to_parent_map))
                    
                for successor_state, action, step_cost in self.__get_successors(current_state):
                    cost = current_cost + step_cost + self.__cartesian_distance(current_state, successor_state)
                    
                    open_list.update((successor_state, action), cost)
                    
                    if successor_state not in closed:
                        successor_to_parent_map[(successor_state, action)] = (current_state, action_to_current_state)
                        
            closed.append(current_state)
        return []

    
    def breadth_first(self, xy1, xy2):
        """Execute a breadth first search"""
        tile_col1, tile_row1 = self.the_map.xy_to_cr(xy1[0], xy1[1])
        tile_col2, tile_row2 = self.the_map.xy_to_cr(xy2[0], xy2[1])
        
        successor_to_parent_map = {}
        start_state = (tile_col1, tile_row1)
        successor_to_parent_map[(start_state, None)] = None  # (Successor, Action) -> (Parent, Action)
        
        open_list = PriorityQueue()
        open_list.update((start_state, None), 0)
        closed = []
        
        while not open_list.isEmpty():
            current_state, action_to_current_state = open_list.pop()
            
            if current_state == xy2:
                return self.__get_action_path((current_state, action_to_current_state), successor_to_parent_map)
            
            if current_state not in closed:
                for successor_state, action, step_cost in self.__get_successors(current_state):
                    open_list.update((successor_state, action), 0)
                    
                    if successor_state not in closed:
                        successor_to_parent_map[(successor_state, action)] = (current_state, action_to_current_state)
                        
            closed.append(current_state)
            
        return []
    
    
    def depth_first(self, xy1, xy2):
        """Execute a depth first search."""
        tile_col1, tile_row1 = self.the_map.xy_to_cr(xy1[0], xy1[1])
        tile_col2, tile_row2 = self.the_map.xy_to_cr(xy2[0], xy2[1])
        
        successor_to_parent_map = {}
        start_state = (tile_col1, tile_row1)
        successor_to_parent_map[(start_state, None)] = None  # (Successor, Action) -> (Parent, Action)
        
        open_list = Stack()
        open_list.push((start_state, None))
        closed = []
        
        while not open_list.isEmpty():
            current_state, action_to_current_state = open_list.pop()
            
            if current_state == xy2:
                return self.__get_action_path((current_state, action_to_current_state), successor_to_parent_map)
            
            if current_state not in closed:
                for successor_state, action, step_cost in self.__get_successors(current_state):
                    open_list.push((successor_state, action))
                    
                    if successor_state not in closed:
                        successor_to_parent_map[(successor_state, action)] = (current_state, action_to_current_state)
                        
            closed.append(current_state)
        return []
    

    def __get_action_path(self, goal, successor_to_parent_map):
        path = [goal[1]]
        parent = successor_to_parent_map[goal]
        
        while parent is not None:
            if parent[1] is not None:
                path.insert(0, parent[1])
            parent = successor_to_parent_map[parent]
            
        return path
    

    def __get_successors(self, current_state):
        successors = []
        step_cost = 1
        
        # State to the north
        if current_state[0] > 0:
            new_x, new_y = current_state[0], current_state[1] - 1
            #in array: row (y) by column (x)
            step_cost = self.the_map.tile_speeds[new_y, new_x]
            # a barricade in this direction
            if not step_cost:
                step_cost = 1e10
                
            successors.append(((new_x, new_y), "w", step_cost))
            
        # State to the south
        if current_state[0] < self.the_map.tile_speeds.shape[0]:
            new_x, new_y = current_state[0], current_state[1] + 1
            
            step_cost = self.the_map.tile_speeds[new_y, new_x]
            if not step_cost:
                step_cost = 1e10
                
            successors.append(((new_x, new_y), "s", step_cost))
            
        # State to the east
        if current_state[1] < self.the_map.tile_speeds.shape[1]:
            new_x, new_y = current_state[0] + 1, current_state[1]
            
            step_cost = self.the_map.tile_speeds[new_y, new_x]
            if not step_cost:
                step_cost = 1e10
                
            successors.append(((new_x, new_y), "d", step_cost))
            
        # State to the west
        if current_state[1] > 0:
            new_x, new_y = current_state[0] - 1, current_state[1]
            
            step_cost = self.the_map.tile_speeds[new_y, new_x]
            if not step_cost:
                step_cost = 1e10
                
            successors.append(((new_x, new_y), "a", step_cost))
            
        return successors
    

    def __cartesian_distance(self, current_state, successorState):
        return (((successorState[0] - current_state[0]) ** 2) + ((successorState[1] - current_state[1]) ** 2)) ** .5
    