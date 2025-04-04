#Based on Foxes and Rabbits script by H. Sayama, Introduction to the Modeling and Analysis of Complex Systems.
# Open SUNY Textbooks, 2015. [Online]. Available: https://knightscholar.geneseo.edu/oer-ost/14
#Implements a spacial Iterated Prisoner's Dilemma model. See R. Axelrod and W. D. Hamilton,
# “The evolution of cooperation,” Science, vol. 211, no. 4489, pp. 1390–1396, 1981, doi: 10.1126/science.7466396.

import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
from matplotlib.lines import Line2D

####################################################################################################
# Constant definitions
####################################################################################################

ATTACK = 1
FARM = 0
INTERACT_RANGE = 0.02
REPRODUCE_SCORE = 100
MAX_AGENTS = 600
BASE_SCORE = 50

X_LIM = .57
Y_LIM = .57

SCORE_MATRIX = [[(3,3),(-5,5)], [(5,-5),(0,0)]]

####################################################################################################
# Parent class for all agents
####################################################################################################

class Group:
    max_id = 0 #What ID numbers have been issued?
    def __init__(self, x, y, speed, color):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.id = Group.max_id #Issue an ID
        Group.max_id += 1 #Increment the next ID to be issued
        self.memory = {} #Empty dictionary
        self.my_actions_memory = {} #Empty dictionary
        self.score = BASE_SCORE #Start with >0 score to avoid instant starvation
        self.avg_move = .5
        self.weight = 1

    def interact(self, other, score_log):
        own_move = self.next_move(other.id)
        other_move = other.next_move(self.id)

        self.score += SCORE_MATRIX[own_move][other_move][0]
        score_log[self.__class__.color][-1] += SCORE_MATRIX[own_move][other_move][0]

        other.score += SCORE_MATRIX[own_move][other_move][1]
        score_log[other.__class__.color][-1] += SCORE_MATRIX[own_move][other_move][1]
        
        self.record_moves(own_move, other.id, other_move)
        other.record_moves(other_move, self.id, own_move)
    def record_moves(self, my_move, id_num, move):
        #Note: Making a list of past moves
        if id_num in self.memory.keys():
            self.memory[id_num].append(move)
            self.my_actions_memory[id_num].append(my_move)
        else:
            self.memory[id_num] = [move]
            self.my_actions_memory[id_num] = [my_move]
        if my_move == ATTACK and move == ATTACK: return
        self.avg_move = ((self.avg_move*self.weight)+my_move)/(self.weight+1)
        self.weight += 1
        
####################################################################################################
# Agent classes
####################################################################################################

#The "Always Defect" strategy
# It always Attacks the other agent, regardless of what the other agent does.
class Raider(Group):
    color = "#000000"
    shape = "." #Small dot
    def __init__(self, x,y):
        super().__init__(x,y,.02,__class__.color)

    def next_move(self, other_id):
        return ATTACK
    
#The "Always Cooperate" strategy
# It always Farms, regardless of what the other agent does.
class Farmer(Group):
    color = "#010101"
    shape = "s" #Square
    def __init__(self, x,y):
        super().__init__(x,y,.01,__class__.color)

    def next_move(self, other_id):
        return FARM

#The classic "Solution to the Prisoner's Dilemma" strategy
# It starts by cooperating, and then does whatever the other agent did last time.
class TitTat(Group):
    color = "#020202"
    shape = "*" #Star
    def __init__(self, x,y):
        super().__init__(x,y,.01,__class__.color)

    def next_move(self, other_id):
        if other_id not in self.memory.keys():
            return FARM
        else:
            return self.memory[other_id][-1]

class Test(Group):
    color = "tab:blue"  # Assign a unique color for Reactive agents
    shape = "*" #Star
    
    def __init__(self, x, y, initial_coop_prob=1, coop_after_coop_prob=1, coop_after_defect_prob=0):
        """
        Initialize a Reactive agent with specific probabilities.
        
        :param x: Initial x-coordinate of the agent
        :param y: Initial y-coordinate of the agent
        :param initial_coop_prob: Probability of cooperating in the first round
        :param coop_after_coop_prob: Probability of cooperating after opponent cooperates
        :param coop_after_defect_prob: Probability of cooperating after opponent defects
        """
        super().__init__(x, y, 0.01, __class__.color)
        self.y = initial_coop_prob
        self.p = coop_after_coop_prob
        self.q = coop_after_defect_prob

    def next_move(self, other_id):
        """
        Decide the next move based on the opponent's previous move and the agent's strategy probabilities.
        
        :param other_id: The ID of the opponent
        :return: FARM (0) if cooperating, ATTACK (1) if defecting
        """
        if other_id not in self.memory:
            # First round: decide based on initial cooperation probability
            return FARM if random.random() < self.y else ATTACK
        
        # Check the opponent's last move
        last_move = self.memory[other_id][-1]
        if last_move == FARM:
            # Opponent cooperated: decide based on p
            return FARM if random.random() < self.p else ATTACK
        else:
            # Opponent defected: decide based on q
            return FARM if random.random() < self.q else ATTACK
####################################################################################################
# Function definitions
####################################################################################################

def observe(agents, init_list):
    '''function for displaying the world'''
    if(len(agents) <= 0): return
    plt.figure()#Begin a new plot
    for ag in agents:
        plt.plot(ag.x,ag.y,ag.__class__.shape,color = ag.color)
        plt.xlim(0,X_LIM)
        plt.ylim(0,Y_LIM)
        plt.axis('off')
        #add key
        plt.legend([Line2D([], [], color='black', marker=t[0].shape, linestyle='None') for t in init_list], [t[0].__name__ for t in init_list], loc='upper right')

    pdf.savefig()#write the plot out as a page in the pdf
    plt.close()#close the plot

def update(agents, score_log):
    #Don't move them in the same order every time
    random.shuffle(agents)
    #Move all agents
    for ag in agents:
        #agent moves
        ag.x += random.uniform(-1*ag.speed, ag.speed)
        ag.y += random.uniform(-1*ag.speed, ag.speed)

        #The agent might now be outside the field, so check and re-set position
        while ag.x >= X_LIM:
            ag.x -= X_LIM
        while ag.x < 0:
            ag.x += X_LIM
        while ag.y >= Y_LIM:
            ag.y -= Y_LIM
        while ag.y < 0:
            ag.y += Y_LIM
    #All agents interact with neighbors
    for ag in agents:
        for nb in agents:
            if ag is nb: continue
            if abs(ag.x - nb.x) < INTERACT_RANGE and abs(ag.y - nb.y) < INTERACT_RANGE:
                    ag.interact(nb, score_log)
    #Agents with negative scores die, agents with strongly positive socres may reproduce
    numFarmers = 0
    for ag in agents:
        if ag.avg_move <= .5:
            numFarmers += 1
    for ag in agents:
        ag.score -= 1 #Score decreases over time
        if ag.score < 0:
            agents.remove(ag)
        elif ag.score > REPRODUCE_SCORE:
            if ag.avg_move > .5 or random.random() < (1 - numFarmers/MAX_AGENTS):
                agents.append(type(ag)(ag.x, ag.y))
                ag.score = BASE_SCORE
            else:
                ag.score = REPRODUCE_SCORE #Cap the score

def log(agents, init_list, logdict, score_log):
    for t in init_list:
        logdict[t[0].color].append(0)
    for ag in agents:
        logdict[ag.__class__.color][-1] += 1
    for c in score_log.keys():
        score_log[c].append(score_log[c][-1])

####################################################################################################
# Primary model run function
####################################################################################################

def model_run(num):
    init_list = [(Farmer, 50), (Test, 50), (Raider, 100)]
    agents = []
    for t in init_list:
        for i in range(t[1]):
            x = random.random()*X_LIM
            y = random.random()*Y_LIM
            agents.append(t[0](x,y))

    logdict = {}
    total_score_log_dict = {}
    for t in init_list:
        logdict[t[0].color] = [t[1]]
        total_score_log_dict[t[0].color] = [0]
    #Do a bunch of updates
    for i in range(100):
        print(num, "-", i)
        update(agents, total_score_log_dict)
        if i % 5 == 0:#One observation every 50 updates
            observe(agents, init_list)
            log(agents, init_list, logdict, total_score_log_dict)

    for c in logdict.keys():
        times = [t for t in range(0, len(logdict[c]))]
        plt.plot(times, logdict[c], '-', color=c)
        plt.legend([t[0].__name__ for t in init_list])
    pdf.savefig()#write the plot out as a page in the pdf
    plt.close()#close the plot

    for c in total_score_log_dict.keys():
        times = [t for t in range(0, len(total_score_log_dict[c]))]
        plt.plot(times, total_score_log_dict[c], '-', color=c)
    pdf.savefig()#write the plot out as a page in the pdf
    plt.close()#close the plot

####################################################################################################
# Script begins here
####################################################################################################

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
str_current_datetime = str(current_datetime)

file_name = "gameTheory"+str_current_datetime+".pdf"
pdf = PdfPages(file_name)
for i in range(2):
    model_run(i)

pdf.close()
