import random
import heapq
import pygame_utils as pyg


# human controlled or AI Agent controlled player classes

class Player():
    def __init__(self, x, y, idx, team, the_map, config):
        '''
        x,y - the player/agent sprite starting location on the map
        team - blue or red
        the_map - a reference to the global map with speeds, flag locations, player locations
        config - configurable settings
        '''
        self.config = config

        # needed for preventing sprite from overlapping a 0 speed location
        self.half_size = config.terrain_tile_size // 2

        # w,a,d,s are the keyboard directions for up, left, right, down
        self.actions = ['w', 'a', 'd', 's']

        # for debugging
        self.speed_terr = {v: k for k, v in self.config.terrain_speeds.items()}

        # configured values

        # TODO - implement variable default speeds so some players are naturally faster
        # self.max_speed = self.config.player_max_speed

        # TODO implement energy countdown to promote teamwork through revivals
        # self.max_energy = self.config.player_max_energy
        # self.min_energy = self.config.player_min_energy
        # self.energy = self.config.player_max_energy

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
    Moves around randomly
    '''

    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)
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


class GreedyGoalAgentPlayer(AgentPlayer):
    '''
    If the flag is not in play head directly for it
    If player has the flag head directly for flag area
    If opponent has flag head directly toward them
    '''

    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)

    def get_action(self):
        action = ''

        # if blocked going direct way, try going a random direction for a while
        if self.blocked_countdown:
            if self.blocked_countdown == 20:
                dirs = ['a', 'w', 's', 'd']
                dirs.remove(self.prev_dir)
                self.prev_dir = random.choice(dirs)

            self.blocked_countdown -= 1

            if random.randint(1, 10) == 1:
                self.prev_dir = random.choice(['a', 'w', 's', 'd'])

            action = self.prev_dir
            if self.config.verbose:
                print('%s player %d is blocked, trying different way: %s' % (self.team, self.player_idx, action))

            return action

        # head to flag home area
        if self.has_flag:
            if self.team == 'blue':
                action = self.__get_direction_to_xy(self.the_map.blue_flag_xy)
            else:
                action = self.__get_direction_to_xy(self.the_map.red_flag_xy)
            if self.config.verbose:
                print('%s player %d heading to flag area: %s' % (self.team, self.player_idx, action))
            return action

        # the flag is being run by an opponent, try to tag them
        if self.the_map.blue_flag_in_play and self.team == 'blue':
            agent_info = self.the_map.agent_info['red']
            for idx, info in agent_info.items():
                if info['has_flag']:
                    action = self.__get_direction_to_xy(info['xy'])
                    if self.config.verbose:
                        print('%s player %d heading to tag opponent %d: %s' % (self.team, self.player_idx, idx, action))
            return action
        if self.the_map.red_flag_in_play and self.team == 'red':
            agent_info = self.the_map.agent_info['blue']
            for idx, info in agent_info.items():
                if info['has_flag']:
                    action = self.__get_direction_to_xy(info['xy'])
                    if self.config.verbose:
                        print('%s player %d heading to tag opponent %d: %s' % (self.team, self.player_idx, idx, action))
            return action

        # head to flag
        if self.team == 'blue' and not self.the_map.red_flag_in_play:
            action = self.__get_direction_to_xy(self.the_map.red_flag_xy)
            if self.config.verbose:
                print('%s player %d heading to flag: %s' % (self.team, self.player_idx, action))
        elif self.team == 'red' and not self.the_map.blue_flag_in_play:
            action = self.__get_direction_to_xy(self.the_map.blue_flag_xy)
            if self.config.verbose:
                print('%s player %d heading to flag: %s' % (self.team, self.player_idx, action))

        return action

    def __get_direction_to_xy(self, xy):
        x, y = xy
        delta_x, delta_y = x - self.x, y - self.y
        if abs(delta_x) > abs(delta_y):
            return 'a' if delta_x < 0 else 'd'
        else:
            return 'w' if delta_y < 0 else 's'


class PriorityQueue:
    """
      Citation: Berkeley AI course, Homework 1 from this class

      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)


class AStarAgentPlayer(GreedyGoalAgentPlayer):
    """
    This Agent follows a learned high-level policy to determine its actions
    """

    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)

        self.goals = ['opponent_flag', 'team_flag_area', 'opponent_flag_area']  # other...
        self.current_goal = 'opponent_flag'
        goal_location = the_map.red_flag_xy if team == 'blue' else the_map.blue_flag_xy
        self.current_path = self.__a_star((x, y), goal_location)

    def get_action(self):
        action = ''

        if self.is_incapacitated:
            return ''

        # if blocked going direct way, try going a random direction for a while
        if self.blocked_countdown:
            if self.blocked_countdown == 20:
                dirs = ['a', 'w', 's', 'd']
                dirs.remove(self.prev_dir)
                self.prev_dir = random.choice(dirs)

            self.blocked_countdown -= 1

            if random.randint(1, 10) == 1:
                self.prev_dir = random.choice(['a', 'w', 's', 'd'])

            action = self.prev_dir
            if self.config.verbose:
                print('%s player %d is blocked, trying different way: %s' % (self.team, self.player_idx, action))

            return action

        # recalc A* due to goal change
        if self.has_flag:
            if not self.current_goal == 'team_flag_area':
                self.current_goal = 'team_flag_area'
                goal_location = self.the_map.blue_flag_xy if self.team == 'blue' else self.the_map.red_flag_xy
                self.current_path = self.__a_star((self.x, self.y), goal_location)
            if self.config.verbose:
                print('%s player %d heading to flag area: %s' % (self.team, self.player_idx, action))
        else:
            # the flag is being run by an opponent, try to tag them
            if self.the_map.blue_flag_in_play and self.team == 'blue':
                agent_info = self.the_map.agent_info['red']
                for idx, info in agent_info.items():
                    if info['has_flag']:
                        action = self.__get_direction_to_xy(info['xy'])
                        if self.config.verbose:
                            print('%s player %d heading to tag opponent %d: %s' % (
                                self.team, self.player_idx, idx, action))
                return action
            if self.the_map.red_flag_in_play and self.team == 'red':
                agent_info = self.the_map.agent_info['blue']
                for idx, info in agent_info.items():
                    if info['has_flag']:
                        action = self.__get_direction_to_xy(info['xy'])
                        if self.config.verbose:
                            print('%s player %d heading to tag opponent %d: %s' % (
                                self.team, self.player_idx, idx, action))
                return action

        if self.current_path:
            action = self.current_path.pop()
        else:
            # default action - head directly toward opponent flag area
            if self.has_flag:
                goal_location = self.the_map.red_flag_xy if self.team == 'red' else self.the_map.blue_flag_xy
            else:
                goal_location = self.the_map.red_flag_xy if self.team == 'blue' else self.the_map.blue_flag_xy
            action = self.__get_direction_to_xy(goal_location)

        return action

    def __get_direction_to_xy(self, xy):
        x, y = xy
        delta_x, delta_y = x - self.x, y - self.y
        if abs(delta_x) > abs(delta_y):
            return 'a' if delta_x < 0 else 'd'
        else:
            return 'w' if delta_y < 0 else 's'

    def get_action_path(self, goal, successor_to_parent_map):
        path = [goal[1]]
        parent = successor_to_parent_map[goal]
        while parent is not None:
            if parent[1] is not None:
                path.insert(0, parent[1])
            parent = successor_to_parent_map[parent]
        return path

    def __a_star(self, xy1, xy2):
        """Search the node that has the lowest combined cost and heuristic first."""
        xy1 = self.the_map.xy_to_cr(xy1[0], xy1[1])
        xy2 = self.the_map.xy_to_cr(xy2[0], xy2[1])
        successor_to_parent_map = {}
        start_state = xy1
        successor_to_parent_map[(start_state, None)] = None  # (Successor, Action) -> (Parent, Action)
        open = PriorityQueue()
        open.update((start_state, None), 0)
        closed = []
        while not open.isEmpty():
            current_state, action_to_current_state = open.pop()
            if current_state == xy2:
                return self.get_action_path((current_state, action_to_current_state), successor_to_parent_map)
            if current_state not in closed:
                if current_state == start_state:
                    current_cost = 0
                else:
                    current_cost = len(self.get_action_path((current_state, action_to_current_state),
                                                            successor_to_parent_map))
                for successor_state, action, step_cost in self.get_successors(current_state):
                    cost = current_cost + step_cost + self.cartesian_distance(current_state, successor_state)
                    open.update((successor_state, action), cost)
                    if successor_state not in closed:
                        successor_to_parent_map[(successor_state, action)] = (current_state, action_to_current_state)
            closed.append(current_state)
        return []

    def get_successors(self, current_state):
        successors = []
        step_cost = 1
        # State to the north
        if current_state[0] > 0:
            successors.append(((current_state[0] - 1, current_state[1]), "w", step_cost))
        # State to the south
        if current_state[0] < self.the_map.tile_speeds.shape[0]:
            successors.append(((current_state[0] + 1, current_state[1]), "s", step_cost))
        # State to the east
        if current_state[1] < self.the_map.tile_speeds.shape[1]:
            successors.append(((current_state[0], current_state[1] + 1), "d", step_cost))
        # State to the west
        if current_state[1] > 0:
            successors.append(((current_state[0], current_state[1] - 1), "a", step_cost))
        return successors

    def cartesian_distance(self, current_state, successorState):
        return (((successorState[0] - current_state[0]) ** 2) + ((successorState[1] - current_state[1]) ** 2)) ** .5

class BreadthFirstAgentPlayer(GreedyGoalAgentPlayer):
    """
    This Agent follows a learned high-level policy to determine its actions
    """

    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)

        self.goals = ['opponent_flag', 'team_flag_area', 'opponent_flag_area']  # other...
        self.current_goal = 'opponent_flag'
        goal_location = the_map.red_flag_xy if team == 'blue' else the_map.blue_flag_xy
        self.current_path = self.breath_first((x, y), goal_location)

    def get_action(self):
        action = ''

        if self.is_incapacitated:
            return ''

        # if blocked going direct way, try going a random direction for a while
        if self.blocked_countdown:
            if self.blocked_countdown == 20:
                dirs = ['a', 'w', 's', 'd']
                dirs.remove(self.prev_dir)
                self.prev_dir = random.choice(dirs)

            self.blocked_countdown -= 1

            if random.randint(1, 10) == 1:
                self.prev_dir = random.choice(['a', 'w', 's', 'd'])

            action = self.prev_dir
            if self.config.verbose:
                print('%s player %d is blocked, trying different way: %s' % (self.team, self.player_idx, action))

            return action

        # recalc A* due to goal change
        if self.has_flag:
            if not self.current_goal == 'team_flag_area':
                self.current_goal = 'team_flag_area'
                goal_location = self.the_map.blue_flag_xy if self.team == 'blue' else self.the_map.red_flag_xy
                self.current_path = self.breath_first((self.x, self.y), goal_location)
            if self.config.verbose:
                print('%s player %d heading to flag area: %s' % (self.team, self.player_idx, action))
        else:
            # the flag is being run by an opponent, try to tag them
            if self.the_map.blue_flag_in_play and self.team == 'blue':
                agent_info = self.the_map.agent_info['red']
                for idx, info in agent_info.items():
                    if info['has_flag']:
                        action = self.__get_direction_to_xy(info['xy'])
                        if self.config.verbose:
                            print('%s player %d heading to tag opponent %d: %s' % (
                                self.team, self.player_idx, idx, action))
                return action
            if self.the_map.red_flag_in_play and self.team == 'red':
                agent_info = self.the_map.agent_info['blue']
                for idx, info in agent_info.items():
                    if info['has_flag']:
                        action = self.__get_direction_to_xy(info['xy'])
                        if self.config.verbose:
                            print('%s player %d heading to tag opponent %d: %s' % (
                                self.team, self.player_idx, idx, action))
                return action

        if self.current_path:
            action = self.current_path.pop()
        else:
            # default action - head directly toward opponent flag area
            if self.has_flag:
                goal_location = self.the_map.red_flag_xy if self.team == 'red' else self.the_map.blue_flag_xy
            else:
                goal_location = self.the_map.red_flag_xy if self.team == 'blue' else self.the_map.blue_flag_xy
            action = self.__get_direction_to_xy(goal_location)

        return action

    def __get_direction_to_xy(self, xy):
        x, y = xy
        delta_x, delta_y = x - self.x, y - self.y
        if abs(delta_x) > abs(delta_y):
            return 'a' if delta_x < 0 else 'd'
        else:
            return 'w' if delta_y < 0 else 's'

    def get_action_path(self, goal, successor_to_parent_map):
        path = [goal[1]]
        parent = successor_to_parent_map[goal]
        while parent is not None:
            if parent[1] is not None:
                path.insert(0, parent[1])
            parent = successor_to_parent_map[parent]
        return path

    def breath_first(self, xy1, xy2):
        """Search the node that has the lowest combined cost and heuristic first."""
        xy1 = self.the_map.xy_to_cr(xy1[0], xy1[1])
        xy2 = self.the_map.xy_to_cr(xy2[0], xy2[1])
        successor_to_parent_map = {}
        start_state = xy1
        successor_to_parent_map[(start_state, None)] = None  # (Successor, Action) -> (Parent, Action)
        open = PriorityQueue()
        open.update((start_state, None), 0)
        closed = []
        while not open.isEmpty():
            current_state, action_to_current_state = open.pop()
            if current_state == xy2:
                return self.get_action_path((current_state, action_to_current_state), successor_to_parent_map)
            if current_state not in closed:
                for successor_state, action, step_cost in self.get_successors(current_state):
                    open.update((successor_state, action), 0)
                    if successor_state not in closed:
                        successor_to_parent_map[(successor_state, action)] = (current_state, action_to_current_state)
            closed.append(current_state)
        return []

    def get_successors(self, current_state):
        successors = []
        step_cost = 1
        # State to the north
        if current_state[0] > 0:
            successors.append(((current_state[0] - 1, current_state[1]), "w", step_cost))
        # State to the south
        if current_state[0] < self.the_map.tile_speeds.shape[0]:
            successors.append(((current_state[0] + 1, current_state[1]), "s", step_cost))
        # State to the east
        if current_state[1] < self.the_map.tile_speeds.shape[1]:
            successors.append(((current_state[0], current_state[1] + 1), "d", step_cost))
        # State to the west
        if current_state[1] > 0:
            successors.append(((current_state[0], current_state[1] - 1), "a", step_cost))
        return successors

    def cartesian_distance(self, current_state, successorState):
        return (((successorState[0] - current_state[0]) ** 2) + ((successorState[1] - current_state[1]) ** 2)) ** .5


class Stack:
    """
    Citation: Berkeley AI course, Homework 1 from this class
    A container with a last-in-first-out (LIFO) queuing policy.
    """

    def __init__(self):
        self.list = []

    def push(self, item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0


class DepthFirstAgentPlayer(GreedyGoalAgentPlayer):
    """
    This Agent follows a learned high-level policy to determine its actions
    """

    def __init__(self, x, y, idx, team, the_map, config):
        super().__init__(x, y, idx, team, the_map, config)

        self.goals = ['opponent_flag', 'team_flag_area', 'opponent_flag_area']  # other...
        self.current_goal = 'opponent_flag'
        goal_location = the_map.red_flag_xy if team == 'blue' else the_map.blue_flag_xy
        self.current_path = self.depth_first((x, y), goal_location)

    def get_action(self):
        action = ''

        if self.is_incapacitated:
            return ''

        # if blocked going direct way, try going a random direction for a while
        if self.blocked_countdown:
            if self.blocked_countdown == 20:
                dirs = ['a', 'w', 's', 'd']
                dirs.remove(self.prev_dir)
                self.prev_dir = random.choice(dirs)

            self.blocked_countdown -= 1

            if random.randint(1, 10) == 1:
                self.prev_dir = random.choice(['a', 'w', 's', 'd'])

            action = self.prev_dir
            if self.config.verbose:
                print('%s player %d is blocked, trying different way: %s' % (self.team, self.player_idx, action))

            return action

        # recalc A* due to goal change
        if self.has_flag:
            if not self.current_goal == 'team_flag_area':
                self.current_goal = 'team_flag_area'
                goal_location = self.the_map.blue_flag_xy if self.team == 'blue' else self.the_map.red_flag_xy
                self.current_path = self.depth_first((self.x, self.y), goal_location)
            if self.config.verbose:
                print('%s player %d heading to flag area: %s' % (self.team, self.player_idx, action))
        else:
            # the flag is being run by an opponent, try to tag them
            if self.the_map.blue_flag_in_play and self.team == 'blue':
                agent_info = self.the_map.agent_info['red']
                for idx, info in agent_info.items():
                    if info['has_flag']:
                        action = self.__get_direction_to_xy(info['xy'])
                        if self.config.verbose:
                            print('%s player %d heading to tag opponent %d: %s' % (
                                self.team, self.player_idx, idx, action))
                return action
            if self.the_map.red_flag_in_play and self.team == 'red':
                agent_info = self.the_map.agent_info['blue']
                for idx, info in agent_info.items():
                    if info['has_flag']:
                        action = self.__get_direction_to_xy(info['xy'])
                        if self.config.verbose:
                            print('%s player %d heading to tag opponent %d: %s' % (
                                self.team, self.player_idx, idx, action))
                return action

        if self.current_path:
            action = self.current_path.pop()
        else:
            # default action - head directly toward opponent flag area
            if self.has_flag:
                goal_location = self.the_map.red_flag_xy if self.team == 'red' else self.the_map.blue_flag_xy
            else:
                goal_location = self.the_map.red_flag_xy if self.team == 'blue' else self.the_map.blue_flag_xy
            action = self.__get_direction_to_xy(goal_location)

        return action

    def __get_direction_to_xy(self, xy):
        x, y = xy
        delta_x, delta_y = x - self.x, y - self.y
        if abs(delta_x) > abs(delta_y):
            return 'a' if delta_x < 0 else 'd'
        else:
            return 'w' if delta_y < 0 else 's'

    def get_action_path(self, goal, successor_to_parent_map):
        path = [goal[1]]
        parent = successor_to_parent_map[goal]
        while parent is not None:
            if parent[1] is not None:
                path.insert(0, parent[1])
            parent = successor_to_parent_map[parent]
        return path

    def depth_first(self, xy1, xy2):
        """Search the node that has the lowest combined cost and heuristic first."""
        xy1 = self.the_map.xy_to_cr(xy1[0], xy1[1])
        xy2 = self.the_map.xy_to_cr(xy2[0], xy2[1])
        successor_to_parent_map = {}
        start_state = xy1
        successor_to_parent_map[(start_state, None)] = None  # (Successor, Action) -> (Parent, Action)
        open = Stack()
        open.push((start_state, None))
        closed = []
        while not open.isEmpty():
            current_state, action_to_current_state = open.pop()
            if current_state == xy2:
                return self.get_action_path((current_state, action_to_current_state), successor_to_parent_map)
            if current_state not in closed:
                for successor_state, action, step_cost in self.get_successors(current_state):
                    open.push((successor_state, action))
                    if successor_state not in closed:
                        successor_to_parent_map[(successor_state, action)] = (current_state, action_to_current_state)
            closed.append(current_state)
        return []

    def get_successors(self, current_state):
        successors = []
        step_cost = 1
        # State to the north
        if current_state[0] > 0:
            successors.append(((current_state[0] - 1, current_state[1]), "w", step_cost))
        # State to the south
        if current_state[0] < self.the_map.tile_speeds.shape[0]:
            successors.append(((current_state[0] + 1, current_state[1]), "s", step_cost))
        # State to the east
        if current_state[1] < self.the_map.tile_speeds.shape[1]:
            successors.append(((current_state[0], current_state[1] + 1), "d", step_cost))
        # State to the west
        if current_state[1] > 0:
            successors.append(((current_state[0], current_state[1] - 1), "a", step_cost))
        return successors

    def cartesian_distance(self, current_state, successorState):
        return (((successorState[0] - current_state[0]) ** 2) + ((successorState[1] - current_state[1]) ** 2)) ** .5
