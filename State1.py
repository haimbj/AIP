import random
import copy
import numpy as np
import Show1
import matplotlib.pyplot as plt	
import thread
import time
import threading

# setting room's size
heightInput = ""
widthInput = ""
while not heightInput in range(4,20):
    try:
        heightInput = int(raw_input("Enter the height of the room between 4 to 20 (walls included): "))
    except:
        print "You have to insert a number between 4 to 20."
        continue
while not widthInput in range(4,20):
    try:
        widthInput = int(raw_input("Enter the width of the room between 4 to 20 (walls included): "))
    except:
        print "You have to insert a number between 4 to 20."
        continue



###################################################################################################################################
#####################################################---For Debug ---##############################################################
# T-1 old imp 0- new imp
T = 1
#our policy-2 class policy- 1
choose_pol = 2
#debug will print the policies and the values to the files
debug = 1
###################################################################################################################################
###################################################################################################################################
pre = dict()
prob = dict()

room = []
roomHeight = heightInput # walls included
roomWidth = widthInput # walls included
OPS = ["up", "down", "left", "right", "clean", "pick", "putInBasket", "random", "idle"] # optional actions for the agent to take
ROBOT_POSITION = 2, 1 # initial agent's position in the room. Can be changed.
BASKET_POSITION = [1, 2] # initial basket's position in the room. Can be changed.

# rewards for the various actions
CLEANING_CREDIT = 10.
PICKING_CREDIT = 5.
PUTTING_CREDIT = 20.
MOVE_COST = 1.
GAMMA = 0.9 # discount factor

# the i-j cell in the transition probability matrix indicates the probability to do action j given that the chosen action is i
# the matrix is ordered according to the order in the variable OPS
TRAN_PROB_MAT = [[0.8, 0, 0.1, 0.1, 0, 0, 0, 0, 0],
                 [0, 0.8, 0.1, 0.1, 0, 0, 0, 0, 0],
                 [0.1, 0.1, 0.8, 0, 0, 0, 0, 0, 0],
                 [0.1, 0.1, 0, 0.8, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0.8, 0, 0, 0, 0.2],
                 [0, 0, 0, 0, 0, 0.8, 0, 0, 0.2],
                 [0, 0, 0, 0, 0, 0, 0.8, 0, 0.2],
                 [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0, 0.125],
                 [0, 0, 0, 0, 0, 0, 0, 0, 1]]

def initRoom():
    "initialize the room according the given input."
    for i in range(roomHeight):
        newRow = [0] * roomWidth
        room.append(newRow)
    for i in range(1, roomHeight - 1):
        for j in range(1, roomWidth - 1):
            room[i][j] = 1
    # Obstacles might be added by putting '0' in the requested cell in the variable room.

    room[ROBOT_POSITION[0]][ROBOT_POSITION[1]] = 9  # initializing robot's location
    room[BASKET_POSITION[0]][BASKET_POSITION[1]] = 2  # initializing basket's location

def printRoom(r):
    'prints the current room (given as r) representation (for debugging)'
    for i in range((len(r))):
        print r[i]

def scatteringStains():
    "scattering numOfStains stains randomly"
    i = 1
    while i <= numOfStains:
        num1 = random.randint(1, roomHeight - 2)
        num2 = random.randint(1, roomWidth - 2)
        if room[num1][num2] == 1:
            room[num1][num2] = 8
            i += 1

def scatteringFruits():
    "scattering numOfFruits fruits randomly"
    i = 1
    while i <= numOfFruits:
        num1 = random.randint(1, roomHeight - 2)
        num2 = random.randint(1, roomWidth - 2)
        if room[num1][num2] == 1:
            room[num1][num2] = random.randint(3, 5)
            i += 1

def userScatterring(num, str):
    "this function allows the user to scatter the stains and fruits as he wishes."
    scatteringCounter = 0
    while scatteringCounter < num:
        try:
            if str == "stain":
                inpStr = "Choose x-coordinate for the next stain: "
            else:
                inpStr = "Choose x-coordinate for the next fruit: "
            xCo = int(raw_input(inpStr))

            if not xCo in range(1, roomWidth - 1):
                print "x has to be a number between 1 to ", roomWidth - 1
                continue

            if str == "stain":
                inpStr = "Choose y-coordinate: "
            else:
                inpStr = "Choose y-coordinate: "
            yCo = int(raw_input(inpStr))

            if not yCo in range(1, roomHeight - 1):
                print "y has to be a number between 1 to ", roomHeight - 1
                continue

            if room[yCo][xCo] == 1:
                if str == "stain":
                    room[yCo][xCo] = 8
                else:
                    room[yCo][xCo] = random.randint(3, 5)
                scatteringCounter += 1
                printRoom(room)
            else:
                print "The cell (", xCo, ",", yCo, ") does not contain '1'. Choose another cell."

        except:
            print "Insert a number between 1 to ", roomHeight - 1, " for x and between 1 to ", roomWidth - 1, " for y."

initRoom()

# determining the number of empty cells to occupy with stains/fruits and scattering them in the room
numOfStainsAndFruitsIsOK = False
numOfZeroes = 0
for i in range(roomHeight):
    for j in range(roomWidth):
        if room[i][j] == 0:
            numOfZeroes += 1
numOfStains = -1
numOfFruits = -1
while not numOfStainsAndFruitsIsOK:
    while not numOfStains in range(0,numOfZeroes):
        try:
            numOfStains = int(raw_input("How many stains would you like to scatter? "))
            if numOfStains > numOfZeroes:
                print "You can scatter only ", numOfZeroes, " stains."
        except:
            print "Wrong Input, please try again."
            continue
    while not numOfFruits in range(0,numOfZeroes):
        try:
            numOfFruits = int(raw_input("How many fruit would you like to scatter? "))
            if numOfFruits > numOfZeroes:
                print "You can scatter only ", numOfZeroes, " fruits."
        except:
            print "Wrong Input, please try again."
            continue
    if numOfStains + numOfFruits < numOfZeroes:
        numOfStainsAndFruitsIsOK = True
    else:
        numOfStains = 0
        numOfFruits = 0
        print "You can scatter only ", numOfZeroes, " stains and fruits totally. Lets try again."
whoScatters = ""
while not whoScatters in ["y", "n"]:
    try:
        whoScatters = raw_input("Would you like to decide the locations of the stains and fruits? (y/n) ")
    except:
        print 'The answer has to be "y" for yes or "n" for no.'
        continue
if whoScatters == "n":
    scatteringStains()
    scatteringFruits()
else:
    print "\nThe room situation is currently this:\n"
    printRoom(room)
    print "\nLets choose the location for the stains and the fruits.\n" \
          "You can choose any cell which contains '1'."
    userScatterring(numOfStains, "stain")
    userScatterring(numOfFruits, "fruit")

def getProbSAS(state1, state2, action):
    """"given state1 and action, returns the probability to reach state2
        in case that action is 'random' the function returns -1
        if state1 is a final state, than it leads by any action to itself in probability 1"""
    if action == 'random':
        return -1.0
    actionIndex = OPS.index(action)
    possibleActionsIndices = [numOp for numOp in range(len(OPS)) if TRAN_PROB_MAT[actionIndex][numOp] > 0]
    sum = 0.0
    for numOp in possibleActionsIndices:
        if state1.actualNextState(OPS[numOp]).hash == state2.hash:
            sum += TRAN_PROB_MAT[actionIndex][numOp]
    return sum

class State:
    "This class represents a specific state of the game - contains all parameters to fully characterize specific situation"

    def __init__(self):
        self.stateRoom = [[ROBOT_POSITION[0], ROBOT_POSITION[1]]]  # list of lists: list of robot coordinates, stains list, fruit list and num of carried fruits
        stains = []
        fruits = []
        carriedFruits = 0  # num of fruits the robot is holding
        for i in range(len(room)):
            for j in range(len(room[0])):
                if room[i][j] == 8:
                    stains.append([i, j])
                if room[i][j] in [3, 4, 5]:
                    fruits.append([i, j])
        self.stateRoom.append(stains)
        self.stateRoom.append(fruits)
        self.stateRoom.append(carriedFruits)
        self.hash = repr(self.stateRoom)  # each stateRoom has a unique string to represent it
        self.end = len(self.stateRoom[1]) == 0 and len(self.stateRoom[2]) == 0 and self.stateRoom[3] == 0

    def isEnd(self):
        "checks if self is a state when all stains are cleaned and all fruits are in the basket"
        self.end = len(self.stateRoom[1]) == 0 and len(self.stateRoom[2]) == 0 and self.stateRoom[3] == 0
        return self.end

    def nextState(self, op):
        """givan a state and an operation to apply, computes the actual action taken, 
            and returns the next room's state after applying the actual action"""
        global TRAN_PROB_MAT
        actionIndex = OPS.index(op)
        sample = np.random.uniform(0.000000001, 1.)
        sumProb = 0
        for i in range(len(OPS)):
            sumProb += TRAN_PROB_MAT[actionIndex][i]
            if sumProb > sample:
                realActionIndex = i
                break
        actualOp = OPS[realActionIndex]
        if not self.legalOp(actualOp):
            actualOp = "idle"
        newState = State()
        newState.stateRoom = copy.deepcopy(self.stateRoom[:])  # deep copy
        if actualOp == "up":
            newState.stateRoom[0][0] = self.stateRoom[0][0] - 1
        elif actualOp == "down":
            newState.stateRoom[0][0] = self.stateRoom[0][0] + 1
        elif actualOp == "left":
            newState.stateRoom[0][1] = self.stateRoom[0][1] - 1
        elif actualOp == "right":
            newState.stateRoom[0][1] = self.stateRoom[0][1] + 1
        elif actualOp == "clean":  # remove a stain from the current position only if there's a stain there
            if self.stateRoom[0] in self.stateRoom[1]:
                index = self.stateRoom[1].index(self.stateRoom[0])
                newState.stateRoom[1] = newState.stateRoom[1][0:index] + newState.stateRoom[1][index + 1:]
                newState.end = newState.isEnd()
            else:
                return self
        elif actualOp == "pick":  # pick a fruit from the current position only if there's a fruit there
            if self.stateRoom[0] in self.stateRoom[2]:
                index = self.stateRoom[2].index(self.stateRoom[0])
                newState.stateRoom[2] = newState.stateRoom[2][0:index] + newState.stateRoom[2][index + 1:]
                newState.stateRoom[3] += 1
                newState.end = newState.isEnd()
            else:
                return self
        elif actualOp == "putInBasket":  # legalOp prevents putInBasket not in the basket
            newState.stateRoom[3] = 0
            newState.end = newState.isEnd()
        elif actualOp == "idle":
            return self
        elif actualOp == "random":
            legalOps = [op for op in OPS if self.legalOp(op)]
            return self.nextState(np.random.choice(legalOps))
        newState.hash = repr(newState.stateRoom)
        return newState

    def actualNextState(self, op):
        """givan a state and an operation to apply, returns the next room's state if this action will be applied"""
        if not self.legalOp(op):
            op = "idle"
        newState = State()
        newState.stateRoom = copy.deepcopy(self.stateRoom[:])  # deep copy
        if op == "up":
            newState.stateRoom[0][0] = self.stateRoom[0][0] - 1
        elif op == "down":
            newState.stateRoom[0][0] = self.stateRoom[0][0] + 1
        elif op == "left":
            newState.stateRoom[0][1] = self.stateRoom[0][1] - 1
        elif op == "right":
            newState.stateRoom[0][1] = self.stateRoom[0][1] + 1
        elif op == "clean":  # remove a stain from the current position only if there's a stain there
            if self.stateRoom[0] in self.stateRoom[1]:
                index = self.stateRoom[1].index(self.stateRoom[0])
                newState.stateRoom[1] = newState.stateRoom[1][0:index] + newState.stateRoom[1][index + 1:]
                newState.end = newState.isEnd()
            else:
                return self
        elif op == "pick":  # pick a fruit from the current position only if there's a fruit there
            if self.stateRoom[0] in self.stateRoom[2]:
                index = self.stateRoom[2].index(self.stateRoom[0])
                newState.stateRoom[2] = newState.stateRoom[2][0:index] + newState.stateRoom[2][index + 1:]
                newState.stateRoom[3] += 1
                newState.end = newState.isEnd()
            else:
                return self
        elif op == "putInBasket":  # legalOp prevents putInBasket not in the basket
            newState.stateRoom[3] = 0
            newState.end = newState.isEnd()
        elif op == "idle":
            return self
        elif op == "random":
            legalOps = [op for op in OPS if self.legalOp(op)]
            return self.actualNextState(np.random.choice(legalOps))
        newState.hash = repr(newState.stateRoom)
        return newState

  
    def legalOp(self, op):
        "given an action, returns true iff the action can be done in this (self) state"
        if op == "idle":
            return True
        if self.isEnd():
            return False
        row_positionOfRobot = self.stateRoom[0][0]
        col_positionOfRobot = self.stateRoom[0][1]
        occupied = [0, 7, 10]  # these numbers represent wall, basket, cabinet and man appropriately
        if op == "up" and room[row_positionOfRobot - 1][col_positionOfRobot] not in occupied:
            return True
        elif op == "down" and room[row_positionOfRobot + 1][col_positionOfRobot] not in occupied:
            return True
        elif op == "left" and room[row_positionOfRobot][col_positionOfRobot - 1] not in occupied:
            return True
        elif op == "right" and room[row_positionOfRobot][col_positionOfRobot + 1] not in occupied:
            return True
        elif op == "pick":
            return True
        elif op == "clean":
            return True
        elif op == "putInBasket" and self.stateRoom[0] == BASKET_POSITION:
            return True
        return False



def newPolicyCalculate (p,vt):
		
	h = []
	for state in allStates.keys():
		h.append((0.02,state))
		if allStates[state].isEnd():
			end = state
			h.append((1,end))

	epsilon = 0.01
	gama = 0.9
	k = max(h)
	h.remove(k)
	stop = 0
	while k[0] > epsilon and len(h)>=0:
		f.write (str(k[0]))

		state = k[1]
		f.write ("the state is\n")
		f.write(state)
		statehash = k[1]
		state = allStates[state]
		if state.isEnd():
			result = 0
		else:	
			result =  valueChecker(state,p[statehash],vt,gama)
		diff = abs (result-vt[statehash])
		vt[statehash] = result
		for element in pre[statehash]:
			found = 0
			for x in h:
				if x[1] == element:
					found = 1	
					value = prob[(element,statehash)]*diff
					value = max(value, x[0])
					x = (value,x[1])
			if found == 0:
				value = prob[(element,statehash)]*diff
				h.append((value,element))
		if len(h) !=0:
			k = max(h)
			h.remove(k)
	return vt
			


def new_Value_iteration (vt):
	h = [] 
	for state in allStates.keys():
		if allStates[state].isEnd():
			end = state
			vt[end] = 400
			h.append((100,end))

	epsilon = 0.001
	gama = 0.9
	k = max(h)
	h.remove(k)
	while k[0] > epsilon and len(h)>=0:
		statehash = k[1]
		state = allStates[statehash]
		if state.isEnd():
			maxValue = 0
		else:		
			maxValue = -500 # initial max values
			if debug == 1:
				g.write ("statring new cal\n")
			for act in OPS:
				if state.legalOp(act):
					result =  valueChecker(state,act,vt,gama)
					if maxValue < result:
							maxValue = result	
		diff = abs(maxValue-vt[statehash])
		vt[statehash] = maxValue
		if debug == 1:
			print "the max Value :",maxValue
		for element in pre[statehash]:
			found = 0
			for x in h:
				if x[1] == element:
					found = 1	
					value = prob[(element,statehash)] * diff
					new_x = (max(x[0],value),x[1])
					h = [y for y in h if y[1] != x[1]]
					h.append(new_x)
			if found == 0:
				value = prob[(element,statehash)] * diff
				h.append((value,element))
		if len(h) !=0:
			k = max(h)
			h.remove(k)
	return vt
			
def getAllStatesImpl(currentState, allStates):
    "a recursive function to build the data structure allStates"
    global FINAL_STATE
    for i in sorted(OPS):
        if currentState.legalOp(i):
            newState = currentState.actualNextState(i)
            
            if newState.hash not in allStates.keys():  # maybe it's better to use hash function in order to construct allStates
                allStates[newState.hash] = newState
                if not newState.isEnd():
                    getAllStatesImpl(newState, allStates)



def fillPre():
	f = open('groups', 'w')
	for state in allStates.keys():
		pre[state] = []

	for state in allStates.keys():
		currentState = allStates[state]
		for act in OPS:
			for a in OPS:
				p = TRAN_PROB_MAT[OPS.index(act)][OPS.index(a)]
				s_prime = currentState.actualNextState(a)
				s_prime_hash = s_prime.hash
				if (state,s_prime_hash) not in prob.keys():
					prob[(state,s_prime_hash)] = p
				else:
					prob[(state,s_prime_hash)] = prob[(state,s_prime_hash)] + p
				if state not in pre[s_prime_hash]:
					pre[s_prime_hash].append(state)

	for state in allStates.keys():
		f.write("\nstate report:\n")
		for element in pre[state]:
			f.write	(element)
			f.write("\n")
			f.write(str(prob[(element,state)]))
			prob[(element,state)] = prob[(element,state)]
				
	f.write ("\noutput of pre array:")
	for state in sorted(allStates.keys()):
		f.write ("\n\n\nstate is:")
		f.write(state)	
		f.write("\n")
		f.write("is this end?\n")
		f.write(str(allStates[state].isEnd()))
		for element in pre[state]:
			f.write("\n")
			f.write	(element)
			f.write("\n")


def getAllStates():
    "building the data structure of all the states"
    currentState = State()
    allStates = dict()
    allStates[currentState.hash] = currentState
    getAllStatesImpl(currentState, allStates)
    return allStates
allStates = getAllStates()


def calculate_policy_value(p):
	gama = 0.9
	epsilon = 0.01
	con = 1
	vt = {}
	vt1 = {}

	for key in allStates.keys():
		vt[key] = 0
		vt1[key] = 0 

	while con:
		con = 0
		for stateHash in allStates.keys():
			state = allStates[stateHash]
			result = valueChecker(state,p[stateHash],vt,gama)
			vt1[stateHash] = result

		for key in sorted(allStates.keys()):
			if debug == 1:			
				print "vt is ", vt[key], "\nvt1 is ", vt1[key]
				print abs(vt[key] - vt1[key]),"\n"
			if abs(vt[key] - vt1[key]) > epsilon:
				con = 1
			vt[key] = vt1[key] 
	return vt1


def calculate_value_iteration():
	gama=0.9
	con = 1
	vt = {}
	vt1 = {}
	epsilon = 0.01
	for key in allStates.keys():
		vt[key] = -100
		vt1[key] = -100


	#iteration for the next times
	while con:
		#print "entry to the loop\n"
		con = 0
		for stateHash in allStates.keys():
			if debug == 1:
				g.write ("\n\n\n********The stateHash is")
				g.write(str(stateHash))
			state = allStates[stateHash]
			maxValue = -10000.000000 # initial max value 
			for act in OPS:
				if state.legalOp(act):
					result =  valueChecker(state,act,vt,gama)
					if debug == 1:
						g.write ("\naction is")
						g.write (act)
						g.write ("\nresult is")
						g.write (str(result))
						g.write ("\nmaxValue is")
						g.write (str(maxValue))
						if maxValue == result:
							g.write("Python is idiot\n")
					if maxValue < result:
						maxValue = result
						if debug == 1:
							g.write("the condition happened\n")
			vt1[stateHash] = maxValue
			if debug == 1:
				g.write ("\nmaxValue is")
				g.write (str(maxValue))


		for key in sorted(allStates.keys()):
			if debug == 1:			
				print "vt is ", vt[key], "\nvt1 is ", vt1[key]
				print abs(vt[key] - vt1[key]),"\n"
			if abs(vt[key] - vt1[key]) > epsilon:
				con = 1
			vt[key] = vt1[key] 
		#break
	return vt1

#old implementation - we need to test it if it brings quicker results!!

    
def valueChecker(state,act,vt,gama):
	summ = 0.0
	if debug == 1:
		g.write("\n\nchecking this state:\n")
		g.write(state.hash)
		g.write("\n\nchecking this act:\n")
		g.write(act)
	for a in OPS:
		p = TRAN_PROB_MAT[OPS.index(act)][OPS.index(a)]
		s_prime = state.actualNextState(a)	
		summ += vt[s_prime.hash]*p
		if debug == 1:
			g.write("\nthe action is\n")
			g.write(a)
			g.write ("\nin P:")
			g.write(str(p))
			g.write ("\nwe will be in the following state: ")
			g.write (str(s_prime.hash))	
			g.write ("\nvalue of next state is: ")
			g.write (str( vt[s_prime.hash]))	
			g.write ("\nwe add to sum: ")
			g.write (str(vt[s_prime.hash]*p))	
	if debug == 1:
		g.write("\n\nsumm is\n")
		g.write(str(summ))
		g.write("\ngama is\n")
		g.write(str(gama))
		g.write("\ngama*summ is\n")
		g.write(str(gama*summ))
		g.write("\ngama*summ + reward is\n")
		g.write(str(gama*summ+ computeExpectedReward (state,act)))
	return gama*summ + computeExpectedReward (state,act)




def computeExpectedReward(state, action):
	"""given a state and an action that the robot tried to do (and not necessarily succeeded), returns the expectation of the received reward trying this action"""
	reward = 0
	for op in OPS: 
		opProb = TRAN_PROB_MAT[OPS.index(action)][OPS.index(op)]
		reward += opProb * computeReward(state, op)
	
	return reward



def computeReward(state, action):
    """this function computes the reward of doing an action in a specific state (given that the robot succeeded to make it, 
        i.e. this is the actual action taken)"""
    if action == "pick" and state.stateRoom[0] in state.stateRoom[2]:
        return PICKING_CREDIT - MOVE_COST
    if action == "clean" and state.stateRoom[0] in state.stateRoom[1]:
        return CLEANING_CREDIT - MOVE_COST
    elif action == "putInBasket":
        return PUTTING_CREDIT * state.stateRoom[3] - MOVE_COST
    return - MOVE_COST




# initial policy
policy = dict()
for key in allStates.keys():
    num = -1
    while num == -1:
        num = random.randint(0, len(OPS) - 1)
        if OPS[num] in ["random","pick","putInBasket","idle","clean"]:
            num = -1
    policy[key] = OPS[num]
    if allStates[key].isEnd():
        policy[key] = "idle"




# initial policy
if choose_pol == 1:
	
	policy = dict()
	for key in allStates.keys():
	    num = -1
	    while num == -1:
	        num = random.randint(0, len(OPS) - 1)
	        if OPS[num] in ["random","pick","putInBasket","idle","clean"]:
	            num = -1
	  #  policy[key] = OPS[num]
	    policy[key] = OPS[8]
	    if allStates[key].isEnd():
	        policy[key] = "idle"

elif choose_pol == 2:
	fillPre()
	vt = {}
	##print "done"
	if debug == 1:
		f = open('workfile', 'w')
		g = open('checkValue','w')
	policy = dict()
	gama = 0.9
	for key in allStates.keys(): #provide inital value for each state - the max reward from this state (as we have seen at class)
		maxReward = -100
		for action in OPS:
			if allStates[key].legalOp(action):
				reward = computeExpectedReward (allStates[key],action)
				if reward>maxReward:
					maxReward = reward
		print "max reward:",maxReward
		vt[key] = maxReward
	v_star=new_Value_iteration (vt) #new_Value_iteration(vt)
	print "finished"
	for key in sorted(allStates.keys()):
		maxValue = -10000
		chosen_action = -1	
		for action in sorted(OPS):
			if allStates[key].legalOp(action):
				result = valueChecker(allStates[key],action,v_star,gama)
				if maxValue < result:
					maxValue = result
					chosen_action = OPS.index(action)
		policy[key] = OPS[chosen_action]
		if debug == 1:
			f.write("\n\n\nfor the state")
			x = ("",key)
			f.write (str(x))
			x = ("",allStates[key])
			f.write (str(x))
			f.write ("in which:\n is this end point? ")
			f.write(str(allStates[key].isEnd()))
			f.write("\n the act which was chosen is ")
			f.write(str(OPS[chosen_action]))
			f.write("\n robot location is in ")
			x=("",allStates[key].stateRoom[0][0],allStates[key].stateRoom[0][1])
			f.write(str(x))
			f.write ("\n the reward for this act is ")
			f.write (str(computeExpectedReward(allStates[key], OPS[chosen_action])))
			f.write ("\nnumber of fruits in the hand is ")
			f.write (str(allStates[key].stateRoom[3]))
			f.write ("\nfruits array is ")
			f.write (str(allStates[key].stateRoom[2]))
			f.write ("\nthe value from this state is")
			f.write (str(v_star[key]))
			f.write ("\nlet's see what would happen if we chose other actions:\n")
			for act in OPS:
				f.write ("\nthe reward for this act is ")
				f.write (act)
				f.write (str(computeExpectedReward(allStates[key],act)))
				f.write ("\nthe value of the next state is")
				y= allStates[key]
				z = y.actualNextState(act)
				f.write(str(z.hash))
				f.write (str(v_star[z.hash]))
				#x = v_star(x)
				#f.write (str(x))
	if debug == 1:	
		f.close()
		g.close()


elif choose_pol == 3:
	fillPre()
	v_star = {}
	print "done"
	if debug == 1:
		f = open('workfile', 'w')
		g = open('checkValue','w')
	f = open('workfile', 'w')
	h = open ('followChanges','w')
	h.write("new printing")
	policy = dict()
	gama = 0.9
	epsilon = 0.01
	for key in sorted(allStates.keys()):
	    policy[key] = OPS[1]
	    if allStates[key].isEnd():
	        policy[key] = "up"
	for key in allStates.keys(): #provide inital value for each state -
		v_star[key] = -30
	v_star = newPolicyCalculate(policy,v_star)


	more_upgrade = 1
	# we dont have any policy(state) to improve
	while more_upgrade:
		more_upgrade = 0
		should_compute = 0
		for key in sorted(allStates.keys()):
			for a in OPS:
				if should_compute:
					break
				if ((not (a == policy[key])) and (allStates[key].legalOp(a)) and (v_star[key] + epsilon < valueChecker(allStates[key],a,v_star,gama))):
					h.write ("\nreplace\n")
					h.write(policy[key])
					h.write("\nwith\n")
					h.write(a)
					policy[key] = a
					should_compute = 1			
					more_upgrade = 1
			if should_compute:
				break
		if should_compute:
			v_star = newPolicyCalculate(policy,v_star)

	h.close()

initialState = State()
Show1.showRoom(room, policy, allStates, initialState, OPS, TRAN_PROB_MAT)




class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      print "Starting " + self.name
      print_values(self.name, 5, self.counter)
      print "Exiting " + self.name

def print_values(delay):
      time.sleep(delay)
      print "The average is"
      

# Create new threads
thread1 = myThread(1, "Thread-1", 1)


# Start new Threads
thread1.start()
thread2.start()
