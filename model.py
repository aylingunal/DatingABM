
import networkx as nx
import random
import matplotlib.pyplot as plt
import math


class Person:
    # set init parameters
    def __init__(self, id):
        # set default params
        self.id = id
        self.relationship_status = 'single'
        self.available_actions = {'commit':.4,'dump':.6}
        self.popularity = .5
        self.partner = -1 # if non-neg, then in relationship
        # set any randomizable or otherwise configurable parameters
        self.set_personality()

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
        self.experiment = args['Experiment']
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
    
    # add random subset of nodes to online dating pool
    def online_dating_pool(self):
        perc_od = .3
        num_od = math.ceil(perc_od*(len(self.graph.nodes)))
        return random.sample(self.graph.nodes, num_od)

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
    def is_compatible(self, node1, node2, threshold):
        pers_score1 = node1.personality_type
        pers_score2 = node2.personality_type
        if abs(pers_score1 - pers_score2) <= threshold:
            return True
        return False
    

    # run the episode
    def begin_episode(self):
        # get folks that are online dating
        od_pool = self.online_dating_pool()

        rels_per_timestep = []
        edge_relationships = []
        for timestep in range(self.totaltimesteps):
            # record relationships per timestep
            rels_cur_timestep = 0
            for node in self.graph.nodes:
                node = nx.get_node_attributes(self.graph, "person_obj")[node]
                if (((node.id, node.partner) not in edge_relationships) and 
                    ((node.partner,node.id) not in edge_relationships) and
                    (node.relationship_status=='relationship')):
                   # edge_relationships.append((node.id, node.partner))
                    rels_cur_timestep += 1
            rels_per_timestep.append(rels_cur_timestep)

            print('timestep ', timestep, '...')
            for node in self.graph.nodes:
                node = nx.get_node_attributes(self.graph, "person_obj")[node]
              #  print(node.relationship_status, ' ', node.id, node.partner)
                ### if node is NOT in a relationship
                if node.relationship_status == 'single':

                    ### set up the pool of nodes that target node could date
                    dating_pool = [x for x in self.graph.neighbors(node.id)]
                    # if we're allowing for 2nd degree connections:
                    for neighbor in self.graph.neighbors(node.id):
                        dating_pool.extend(self.graph.neighbors(neighbor))

                    # if relevant, open pool up to those in online dating
                    if self.experiment['OnlineDating']==True:
                        dating_pool.extend(od_pool)

                    # remove duplicates
                    dating_pool = set(dating_pool)
                    # remove non-single nodes
                    dating_pool = [x for x in dating_pool if nx.get_node_attributes(self.graph, "person_obj")[x].relationship_status=='single']
                    
                    ### find compatible potentials
                    for candidate in dating_pool:
                        candidate = nx.get_node_attributes(self.graph, "person_obj")[candidate]
                        # first check for personality compatibility
                        if self.is_compatible(node, candidate, threshold=5):
                            # now check for probability of starting a relationship
                            if random.choices([True,False], weights=[self.gamestartprob,1-self.gamestartprob],k=1) == [True]:
                                # now let's see if the two get involved!
                                node_commit = False
                                candidate_commit = False
                                if random.choices([True,False], weights=[node.available_actions['commit'],node.available_actions['dump']],k=1) == [True]:
                                    node_commit = True
                                if random.choices([True,False], weights=[candidate.available_actions['commit'],candidate.available_actions['dump']],k=1) == [True]:
                                    candidate_commit = True
                                # if both commit, (1) date; (2) increase their probs of committing again
                                if node_commit and candidate_commit:
                                    # update relationship
                                    node.relationship_status = 'relationship'
                                    node.partner = candidate.id
                                    candidate.relationship_status = 'relationship'
                                    candidate.partner = node.id
                                    edge_attributes = {(node, candidate):{'relationship':True,
                                                                        'relationship_time':1}}
                                    nx.set_edge_attributes(self.graph, edge_attributes) 

                                    
                                    # update strategies
                                    node.available_actions['commit'] = (1 - node.available_actions['commit'])/2 + node.available_actions['commit'] # TODO --> maybe make this a function of relationship_time?
                                    node.available_actions['dump'] = 1 - node.available_actions['commit']
                                    candidate.available_actions['commit'] = (1 - candidate.available_actions['commit'])/2 + candidate.available_actions['commit'] # TODO --> maybe make this a function of relationship_time?
                                    candidate.available_actions['dump'] = 1 - candidate.available_actions['commit']
                                # if one commits and one dumps, (1) decrease committers' prob of committing 
                                if node_commit and not candidate_commit:
                                    # update strategies
                                    node.available_actions['commit'] = node.available_actions['commit'] - (1 - node.available_actions['commit'])/4 # TODO --> maybe make this a function of relationship_time?
                                    node.available_actions['dump'] = 1 - node.available_actions['commit']
                                if not node_commit and candidate_commit:
                                    # update strategies
                                    candidate.available_actions['commit'] = candidate.available_actions['commit'] - (1 - candidate.available_actions['commit'])/4 # TODO --> maybe make this a function of relationship_time?
                                    candidate.available_actions['dump'] = 1 - candidate.available_actions['commit']
                                # if both dump, do nothing
                else:
                    # get partner and then determine if they commit again, or dump
                    partner = nx.get_node_attributes(self.graph, "person_obj")[node.partner]
                    node_commit = False
                    partner_commit = False
                    if random.choices([True,False], weights=[node.available_actions['commit'],node.available_actions['dump']],k=1) == [True]:
                        node_commit = True
                    if random.choices([True,False], weights=[partner.available_actions['commit'],partner.available_actions['dump']],k=1) == [True]:
                        partner_commit = True
                    # update strategies accordingly
                    if node_commit and partner_commit:
                        # increase both's commitment probabilities by 50% 
                        node.available_actions['commit'] = (1 - node.available_actions['commit'])/2 + node.available_actions['commit'] # TODO --> maybe make this a function of relationship_time?
                        node.available_actions['dump'] = 1 - node.available_actions['commit']
                        partner.available_actions['commit'] = (1 - partner.available_actions['commit'])/2 + partner.available_actions['commit'] # TODO --> maybe make this a function of relationship_time?
                        partner.available_actions['dump'] = 1 - partner.available_actions['commit']
                    else: 
                        # if one commits and one dumps, (1) decrease committers' prob of committing (2) update relationship
                        if node_commit and not partner_commit:
                            # update strategies
                            node.available_actions['commit'] = .3#node.available_actions['commit'] - (1 - node.available_actions['commit'])/4 # TODO --> maybe make this a function of relationship_time?
                            node.available_actions['dump'] = .7 #1 - node.available_actions['commit']
                            partner.available_actions['commit'] = .5
                            partner.available_actions['dump'] = .5
                        if not node_commit and partner_commit:
                            # update strategies
                            node.available_actions['commit'] = .5
                            node.available_actions['dump'] = .5
                            partner.available_actions['commit'] = .3 #partner.available_actions['commit'] - (1 - partner.available_actions['commit'])/4 # TODO --> maybe make this a function of relationship_time?
                            partner.available_actions['dump'] = .7 #1 - partner.available_actions['commit']
                        if not node_commit and not partner_commit:
                            # update strategies
                            node.available_actions['commit'] = .5
                            node.available_actions['dump'] = .5
                            partner.available_actions['commit'] = .5
                            partner.available_actions['dump'] = .5

                        # update relationship status
                        edge_attributes = {(node, partner):{'relationship':False,
                                                             'relationship_time':0}}
                        nx.set_edge_attributes(self.graph, edge_attributes)
                        # update the nodes
                        node.partner = -1
                        partner.partner = -1
                        node.relationship_status = 'single'
                        partner.relationship_status = 'single'

        plt.plot(rels_per_timestep)
        plt.xlabel('Timesteps')
        plt.ylabel('Percent Relationships')
        plt.show()

        # visualize end graph
        # nx.draw(self.graph)
        # plt.show()
        # get stats on relationships
        edge_relationships = []
        non_relationships = 0

        for node in self.graph.nodes:
            node = nx.get_node_attributes(self.graph, "person_obj")[node]
            if (((node.id, node.partner) not in edge_relationships) and 
                ((node.partner,node.id) not in edge_relationships) and
                (node.relationship_status=='relationship')):
                edge_relationships.append((node.id, node.partner))
            else:
                non_relationships += 1

        print('total non-relatinoships: ', non_relationships)
        print('total relationships: ', len(edge_relationships))

        return non_relationships, len(edge_relationships), len(self.graph.edges)


def main():
    # initialize the game (update params as needed, rn debugging)
    args = { 'NetworkInfo':
                {'Population': 100,#,100,
                'cur_id_num': 0},
        'EpisodeInfo': {
            'TotalTimesteps':1000,#200,
            'GameStartProbability':.85
        },
        'Experiment': {
            'OnlineDating':False,
            'CultureValues':True
        }
    }

    num_episodes = 1000
    total_nonrelationships = 0
    total_relationships = 0
    total_edges = 0
    for i in range(num_episodes):
        new_game = DatingGame(args)
        # initialize relationship
        new_game.set_relationships(init_degs=10)
        # begin the game!
        nonrels, rels, num_edges = new_game.begin_episode()
        total_nonrelationships += nonrels
        total_relationships += rels
        total_edges += num_edges

    print('avg total edges: ', (total_nonrelationships+total_relationships)/num_episodes)
    print('avg total relationships: ', (total_relationships)/num_episodes)
    print('avg total edges: ', total_edges/num_episodes)


if __name__=='__main__':
    main()

