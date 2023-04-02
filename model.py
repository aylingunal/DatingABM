
import networkx as nx
import random
import matplotlib.pyplot as plt


class Person:
    # set init parameters
    def __init__(self, id):
        # set default params
        self.id = id
        self.relationship_status = 'single'
        self.available_actions = ['commit', 'dump']        
        self.popularity = .5
        # set any randomizable or otherwise configurable parameters
        self.set_personality()

        #### for the future ####
        # self.attributes = {'humor': True} 
        # self.preferences = {'humor': True}
        # self.history = {}
    
    # def update_available_actions(new_action_set):
    #     self.available_actions = new_action_set
    def set_personality(self):
        PERSONALITY_TYPES = 100
        self.personality_type = random.randint(0,PERSONALITY_TYPES)

class DatingGame:
    # TODO to add attributes:
    # - networkx graph with people IDs
    # - list of all IDs within the population (maybe make this a dict since people might have statuses of being within or out)

    # set default parameters
    def __init__(self):
        # initialize graph
        graph = nx.Graph()
    
    # later can make a lot of this conditional, but for now randomly
    # initialize everything
    def __init__(self, args):
        # set parameters
        self.totaltimesteps = args['EpisodeInfo']['TotalTimesteps']
        self.gamestartprob = args['EpisodeInfo']['GameStartProbability']
        self.population = args['NetworkInfo']['Population']
        self.id_num = args['NetworkInfo']['cur_id_num']
        # create the network
        self.graph = nx.Graph()
        for i in range(self.population):
            # add new id to network
            self.graph.add_node(self.id_num)
            # populate node w/ person's attributes
            new_person = Person(self.id_num)
            node_attributes = {self.id_num: {'person_obj':new_person}}
            nx.set_node_attributes(self.graph, node_attributes)
            # incremenet id_num
            self.id_num += 1

    # set relationships randomly
    def set_relationships(self, init_degs):
        for node in self.graph.nodes:
            # randomly select {init_degs} to set neighbors
            if init_degs <= len([x for x in range(init_degs) if x not in self.graph.neighbors(node)]): # todo --> not great solution but whatever
                new_neighbors = random.sample([x for x in range(init_degs) if x not in self.graph.neighbors(node)], init_degs)
                for neighbor in new_neighbors:
                    # no self-loops
                    if neighbor != node:
                        # add edge to graph
                        self.graph.add_edge(node, neighbor)
                        # initialize relationship status
                        edge_attributes = {(node, neighbor):{'relationship':False,
                                                             'relationship_time':0}}
                        nx.set_edge_attributes(self.graph, edge_attributes)

    # returns True for compatible, False for no
    def is_compatible(node1, node2, threshold):
        pers_score1 = nx.get_node_attributes(self.graph, "person_obj")[node1].personality_type
        pers_score2 = nx.get_node_attributes(self.graph, "person_obj")[node2].personality_type
        if abs(pers_score1 - pers_score2) <= threshold:
            return True
        return False

    # run the episode
    def begin_episode(self):
        for timestep in range(self.totaltimesteps):
            print('timestep ', timestep, '...')
            for node in self.graph.nodes:
                ### if node is NOT in a relationship
                if nx.get_node_attributes(self.graph, "person_obj")[node].relationship_status == 'single':
                    ### set up the pool of nodes that target node could date
                    dating_pool = [self.graph.neighbors(node)]
                    # if we're allowing for 2nd degree connections:
                    for neighbor in self.graph.neighbors(node):
                        dating_pool.extend(self.graph.neighbors(neighbor))
                    # remove duplicates
                    dating_pool = set(dating_pool)
                    ### find compatible potentials 
                    for candidate in dating_pool:
                        # first check for personality compatibility
                        if is_compatible(node, candidate):
                            # now check for probability of starting a relationship
                            if random.choices([True,False], weights=[self.gamestartprob,1-gamestartprob],k=1) == [True]:
                                # start game TODO 
                else:
                    # TODO --> get partner and then determine if they commit again, or dump

        # visualize end graph
        nx.draw(self.graph)
        plt.show()

def main():
    # initialize the game
    args = { 'NetworkInfo':
                {'Population': 20,
                'cur_id_num': 0},
        'EpisodeInfo': {
            'TotalTimesteps':10,
            'GameStartProbability':.7
        }
    }
    new_game = DatingGame(args)
    # initialize relationship
    new_game.set_relationships(init_degs=10)
    # begin the game!
    new_game.begin_episode()




if __name__=='__main__':
    main()

