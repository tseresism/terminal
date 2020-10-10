import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.cannon = False
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, FACTORY, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP, BORDER_LENGTH
        WALL = config["unitInformation"][0]["shorthand"]
        FACTORY = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        BORDER_LENGTH = 28
        # This is a good place to do initial setup
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        #game_state.attempt_spawn(DEMOLISHER, [[24, 10]], 3)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    
    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        # First, place basic defenses
        gamelib.debug_write("we have ",game_state.get_resource(1,0), "MP")
        #self.i_dont_think_so(game_state)
        #dirty play time
        
        if (game_state.turn_number > 3 and (game_state.contains_stationary_unit([25,13]) ///
        and game_state.contains_stationary_unit([25,14]) and AlgoStrategy.opponent_walls(game_state) > BORDER_LENGTH-3)) or self.cannon:
            #self.bunker_bust(game_state)
            self.cannon = True
            self.build_defences(game_state)
            if  game_state.get_resource(1,0) >40:
                #self.prep_cannon(game_state)
                #self.fire_cannon(game_state)

                 

        else:    
            self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        #self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with interceptors and wait to see enemy's base
        #if game_state.turn_number < 5:
         #   self.stall_with_interceptors(game_state)
          #  print("weak")
        #else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our demolishers to attack them at long range.
        #if self.detect_enemy_unit(game_state, unit_type=None, valid_x=#None, valid_y=[14, 15]) > 10:
        #        #self.demolisher_line_strategy(game_state)
        #    scout_spawn_location_options = [[13, 0], [14, 0]]
        #    game_state.attempt_spawn(DEMOLISHER, [[13, 0]], 1000)
        #else:
            # They don't have many units in the front so lets figure out their least defended area and send Scouts there.

            # Only spawn Scouts every other turn
            # Sending more at once is better since attacks can only hit a single scout at a time
        #    if game_state.turn_number % 2 == 1:
                # To simplify we will just check sending them from back left and right
        #        scout_spawn_location_options = [[13, 0], [14, 0]]
        #        best_location = self.least_damage_spawn_location(game_state, scout_spawn_location_options)
        #        game_state.attempt_spawn(SCOUT, best_location, 1000)
        #    else:
            scout_spawn_location_options = [[13, 0], [14, 0]]
            if game_state.turn_number < 2:
                game_state.attempt_spawn(INTERCEPTOR, [[20, 6]], 2)
                game_state.attempt_spawn(INTERCEPTOR, [[7, 6]], 1)
                game_state.attempt_spawn(INTERCEPTOR, [[9, 4]], 1)

            #if game_state.turn_number > 5:
            #    game_state.attempt_spawn(INTERCEPTOR, [[13, 0]], 1)

            if game_state.turn_number == 2:
                game_state.attempt_spawn(SCOUT, scout_spawn_location_options, 1000)

            if game_state.turn_number % 3:
                game_state.attempt_spawn(SCOUT, scout_spawn_location_options, 1000)

    #count the number of stationary units in row with y coordinate 14. This is the enemy's border.
    def opponent_walls(self,game_state):
        count = 0
        for x in range(0,27):
            if game_state.contains_stationary_unit([x,14]):
                count+=1

        return count

    #To avoid spaghetti code that's impossible to maintain, here is a parser. Any time you want to build something, 
    #Run it by the parser to make sure 1 part of the code isn't interfering with another part's strateg
    def build_parsed(self,game_state,building_list):
        if self.cannon:
            for item in building_list:
                if item in [[26,13],[27,13],[26,12],[25,12],[24,12],[24,11],[23,11]]:
                    building_list.remove(item)



        return building_list



    #This is a bit convoluted but essentially if our opponent has walled off a corner of their map we can drop our defenses and target that. Not exactly a weakpoint but should be a surprise. 
    def fire_cannon(self,game_state):
        path = game_state.find_path_to_edge(self,[13,0])
        gamelib.debug_write("Taking path to try and destroy enemy:",path)
        for item in path:
            if item[1] < 14:
                path.remove(item)
        if len(path) < 1:
            gamelib.debug_write("we can't fire our cannon")
        else:
            if game_state.get_resource(1,0) >40:
                gamelib.debug_write("FIRE!")
                game_state.attempt_spawn(SCOUT, scout_spawn_location_options, 1000)

    #We are going to remove our own defenses on the right hand corner to fire off a killing blow
    def prep_cannon(self,game_state):
        cannon_barrel = [[26,13],[27,13],[26,12],[25,12],[24,12],[24,11],[23,11]]
        game_state.attempt_remove(cannon_barrel)


    #One neat trick is building a wall across the entire map and then dropping 1 wall when you've ammassed an army. We can counter by blocking their door
    def i_dont_think_so(self,game_state):
        for x in range(0,26):
            gamelib.debug_write("x is ",x)
            #gamelib.debug_write("whatever i'm reading is ",game_state.game_map[0,13])
            if game_state.game_map[x][0].pending_removal == True and x < 26:

                gamelib.debug_write("opponent is removing: ", x,",14 from the map")
                game_state.attempt_spawn(WALL,[x,13])
                game_state.attempt_upgrade([x,13])

                game_state.attempt_spawn(TURRET,[x,12])
                game_state.attempt_upgrade([x,12])

            if self.game_map[x,13][0].pending_removal == True:
                gamelib.debug_write("we are removing: ", x,",13 from the map (this is working!)")




    def bunker_bust(self, game_state):
        self.count += 1            
        game_state.attempt_remove([[27,13],[26,13],[26,12]])
        if game_state.contains_stationary_unit([27,13]) == 0:
            if game_state.get_resource(1,0) >15:
                game_state.attempt_spawn(SCOUT,[27,13],int(game_state.get_resource(1,0)-5))
                game_state.attempt_spawn(SCOUT,[13,0],5)
                
            
            
        blocking_locations = [[12,2],[23,12]]
        game_state.attempt_spawn(WALL,blocking_locations)
        turret_locations = [[1, 12]]
        game_state.attempt_spawn(TURRET, turret_locations)

        secondary_wall_locations = [[0,13],[2,11],[25,11],[3,10],[24,10],[23,9],[4,9],[22,8],[5,8],[6,7],[21,7]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)

        turret_locations = [[13, 3], [14, 3], [18, 7], [9, 7]]
        game_state.attempt_spawn(TURRET, turret_locations)
        secondary_wall_locations = [[7,6],[20,6],[8,5],[19,5],[9,4],[18,4],[10,3],[17,3],[16,2],[11,2],[12,1],[15,1]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)
        #wall_locations = [[8, 12], [19, 12]]
        #game_state.attempt_spawn(WALL, wall_locations)
    
            #secondary_wall_locations = [[13,3],[14,3],[12,4],[15,4],[11,5],[16,5],[17,6],[10,6],[18,7],[9,7],[19,8],[8,8],[20,9],[7,9],[21,10],[6,10]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)
        secondary_wall_locations = [[22,11],[5,11],[4,12]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)
        turret_locations = [[1, 13], [25,13],[2,13]]
        game_state.attempt_spawn(TURRET, turret_locations)

        defense_strongpoints = [[0,13]]
        game_state.attempt_upgrade(defense_strongpoints)
        # Lastly, if we have spare SP, let's build some Factories to generate more resources
        defense_strongpoints = [[0,13],[1,13],[25,13],[24,13],[2,13],[3,13],[23,13],[4,13],[22,13],[5,13],[21,13],[6,13],[20,13],[7,13]]
        game_state.attempt_spawn(WALL,defense_strongpoints)
        turret_locations = [[19, 13],[2,13],[25,13]]
        game_state.attempt_spawn(TURRET, turret_locations)
        game_state.attempt_upgrade(turret_locations)
        secondary_wall_locations = [[15,4],[16,5],[17,6],[10,6],[11,5],[12,4],[19,8],[20,9],[21,10]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)
        factory_locations = [[13, 10], [14, 10], [13, 9], [14, 9],[13,8],[14,8],[13,7],[14,7],[13,6],[14,6]]
    
    
        game_state.attempt_spawn(FACTORY, factory_locations)       

    def spawn_then_upgrade(self,game_state,coord, build):
        if(game_state.attempt_spawn(build,coord) | game_state.attempt_upgrade(coord)):
            return True


    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place turrets that attack enemy units
        #friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        #for coord in friendly_edges:
        #    for unit in game_state.game_map[coord]:
        #        if unit.unit_type == WALL and unit.health < 35:
        #            game_state.attempt_upgrade(coord)


        #starter turrent defense

        turret_locations = [[5, 11], [22, 11], [11,11],[15,11]]
        for location in turret_locations:
            AlgoStrategy.spawn_then_upgrade(self,game_state, location,TURRET)


        factory_locations = [[13,2],[14,2],[13,3],[14,3],[13,4],[14,4],[13,5],[14,5],[13,6],[14,6],[13,7],[14,7],[12,7],[11,7],[11,6],[15,7],[15,6],[15,5]]
        idx = 0
        while(game_state.get_resource(SP) > 12 and idx < len(factory_locations)):

            if(AlgoStrategy.spawn_then_upgrade(self,game_state, factory_locations[idx],FACTORY)):
                break
            idx+=1




        secondary_wall_locations = [[0,13],[27,13],[1,12],[26,12],[2,11],[25,11],[3,11],[24,11],[4,11],[23,11]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)

        turret_locations = [[22, 11], [5, 11]]
        game_state.attempt_spawn(TURRET, turret_locations)
        game_state.attempt_upgrade(turret_locations)

        secondary_wall_locations = [[24,11],[3,11]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)
        #wall_locations = [[8, 12], [19, 12]]
        #game_state.attempt_spawn(WALL, wall_locations)

        #secondary_wall_locations = [[13,3],[14,3],[12,4],[15,4],[11,5],[16,5],[17,6],[10,6],[18,7],[9,7],[19,8],[8,8],[20,9],[7,9],[21,10],[6,10]]
        #game_state.attempt_spawn(WALL,secondary_wall_locations)

        secondary_wall_locations = [[6,11],[7,11],[8,11],[9,11],[10,11],[11,11],[12,11],[13,11],[14,11],[15,11],[16,11],[17,11],[18,11],[19,10],[20,9]]
        game_state.attempt_spawn(WALL,secondary_wall_locations)

        factory_locations = [[4,9], [23,9]]
        for location in factory_locations:
            AlgoStrategy.spawn_then_upgrade(self,game_state,location,FACTORY)

        turret_locations = [[21, 11], [2,12]]
        game_state.attempt_spawn(TURRET, turret_locations)
        game_state.attempt_upgrade(turret_locations)

        
        factory_locations = [[13, 10], [14, 10], [13, 9], [14, 9],[13,8],[14,8],[13,7],[14,7],[13,6],[14,6]]


        for location in factory_locations:
            AlgoStrategy.spawn_then_upgrade(self,game_state,location,FACTORY)

        

    

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build turret one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1]+1]
            game_state.attempt_spawn(TURRET, build_location)

    def stall_with_interceptors(self, game_state):
        """
        Send out interceptors at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)
        
        # Remove locations that are blocked by our own structures 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)
        
        # While we have remaining MP to spend lets send out interceptors randomly.
        while game_state.get_resource(MP) >= game_state.type_cost(INTERCEPTOR)[MP] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]
            
            game_state.attempt_spawn(INTERCEPTOR, deploy_location)
            """
            We don't have to remove the location since multiple mobile 
            units can occupy the same space.
            """

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [WALL, TURRET, FACTORY]
        cheapest_unit = WALL
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.MP] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[game_state.MP]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our demolisher from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn demolishers next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
