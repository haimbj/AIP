import Tkinter as tk
import numpy as np
import copy
import time

ROOM = []
INIT_ROOM = []
ROOM_HEIGHT = 0
ROOM_WIDTH = 0
COLOR_DICT = {0: "black", 0.5:"gray", 1: "white", 2: "basket", 3: "banana", 4: "strawberry", 5: "grapes", 6: "kettle",
             7: "cabinet", 8: "stain", 9: "robot", 10:"man", 11:"empty_cup", 12:"full_cup"}
OPS = []
TRAN_PROB_MAT = []
OBJECT_IN_ROBOT_POSITION = 1
ALL_STATES = dict()
CURRENT_STATE = []
INIT_STATE = []
POLICY = dict()
NUM_OF_PICKED_FRUITS = 0
root = tk.Tk()
root.title("Brafman's Project")
c = tk.Canvas(root, height=50 * (ROOM_HEIGHT + 3), width= 50 * (ROOM_WIDTH+2), bg='white', bd=0)
ROBOT_BAR = []
BASKET_BAR = []
FIRST_SHOW = True
FINAL_STATE = ""
RESET = False

def showRoom(room, policy, allStates, initialState, operations, tranProbMat):
    global ROOM, INIT_ROOM, ROOM_HEIGHT, ROOM_WIDTH, OPS, TRAN_PROB_MAT, ALL_STATES, CURRENT_STATE, INIT_STATE, POLICY, c, FIRST_SHOW, FINAL_STATE
    ROOM = room
    INIT_ROOM = copy.deepcopy(room)
    ROOM_HEIGHT = len(room)
    ROOM_WIDTH = len(room[0])
    OPS = operations
    TRAN_PROB_MAT = tranProbMat
    CURRENT_STATE = initialState
    INIT_STATE = copy.deepcopy(initialState)
    ALL_STATES = allStates
    POLICY = policy
    c = tk.Canvas(root, height=50 * (ROOM_HEIGHT + 3), width=50 * (ROOM_WIDTH+2), bg='white', bd=0)


    # creating grid
    for i in range(0, 50 * ROOM_WIDTH, 50):
        c.create_line([(i, 0), (i, 50 * ROOM_HEIGHT)])
    for i in range(0, 50 * ROOM_HEIGHT, 50):
        c.create_line([(0, i), (50 * ROOM_WIDTH, i)])

    # by pressing: 'r' the game is stopped (restarted)
    #              'n' we see what the policy orders to do in the next step
    #              'p' shows a full episode
    root.bind('<r>', restart)
    root.bind('<n>', nextMove)
    root.bind('<p>', playEpisode)

    for i in range(ROOM_HEIGHT):
        for j in range(ROOM_WIDTH):
            if room[i][j] == 7 and room[i][j + 1] != 7: # preventing drawing cabinet twice
                continue
            if room[i][j] == 10 and room[i + 1][j] != 10: # preventing drawing man twice
                continue
            createImage(room[i][j], i, j, c)
    createImage(9, ROOM_HEIGHT, 0, c)
    createImage(2, ROOM_HEIGHT + 1, 0, c)
    for i in range(ROOM_WIDTH):
        createImage(0.5, ROOM_HEIGHT + 2, i, c)

    coords1 = (1, 50 * ROOM_HEIGHT + 100, 100, 50 * ROOM_HEIGHT + 199)
    coords2 = (100, 50 * ROOM_HEIGHT + 100, 200, 50 * ROOM_HEIGHT + 199)
    coords3 = (200, 50 * ROOM_HEIGHT + 100, 300, 50 * ROOM_HEIGHT + 199)

    item1 = c.create_rectangle(coords1, outline="black", fill="red")
    item4 = c.create_text(50, 50 * ROOM_HEIGHT + 125, fill="black", font="Times 14 italic bold", text="restart")
    c.tag_bind(item1, "<1>", restart)
    c.tag_bind(item4, "<1>", restart)

    item2 = c.create_rectangle(coords2, outline="black", fill="yellow")
    item5 = c.create_text(150, 50 * ROOM_HEIGHT + 125, fill="black", font="Times 14 italic bold", text="next move")
    c.tag_bind(item2, "<1>", nextMove)
    c.tag_bind(item5, "<1>", nextMove)

    item3 = c.create_rectangle(coords3, outline="black", fill="green")
    item6 = c.create_text(250, 50 * ROOM_HEIGHT + 125, fill="black", font="Times 14 italic bold", text="play episode")
    c.tag_bind(item3, "<1>", playEpisode)
    c.tag_bind(item6, "<1>", playEpisode)

    if FIRST_SHOW:
        c.delete()
    FIRST_SHOW = False
    c.pack()
    root.mainloop()

def createImage(imageNum, row, col, c):
    "paints the image imageName in [row][col] square."
    if imageNum in [0, 1]:
        c.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=COLOR_DICT[imageNum])
    elif imageNum == 0.5:
        c.create_rectangle(col * 50, row * 50, (col + 1) * 50, (row + 1) * 50, fill=COLOR_DICT[imageNum], outline = COLOR_DICT[0.5])
    elif imageNum == 0.99:
        c.create_rectangle(col * 50, row * 50 + 1, (col + 1) * 50, (row + 1) * 50 - 1, fill=COLOR_DICT[1], outline = COLOR_DICT[1])
    else:
        filename = tk.PhotoImage(file="gif_pictures/" + COLOR_DICT[imageNum] + ".gif")
        if imageNum == 7:  # cabinet takes two spots
            image = c.create_image(col * 50 + 50, row * 50 + 25, image=filename)
        elif imageNum == 10:  # man takes two spots
            image = c.create_image(col * 50 + 25, row * 50 + 50, image=filename)
        else:
            image = c.create_image(col * 50 + 25, row * 50 + 25, image=filename)
        if imageNum == 9:  # robot => therefore the position update
            currentPosition = row, col
        label = tk.Label(image=filename)
        label.image = filename

def restart(event):
    print "Reseting game"
    global ROOM, INIT_ROOM, CURRENT_STATE, INIT_STATE, OBJECT_IN_ROBOT_POSITION, ROBOT_BAR, BASKET_BAR, NUM_OF_PICKED_FRUITS, RESET
    ROOM = copy.deepcopy(INIT_ROOM)
    CURRENT_STATE = copy.deepcopy(INIT_STATE)
    OBJECT_IN_ROBOT_POSITION = 1
    ROBOT_BAR = []
    BASKET_BAR = []
    NUM_OF_PICKED_FRUITS = 0
    RESET = True
    for i in range(ROOM_HEIGHT):
        for j in range(ROOM_WIDTH):
            if ROOM[i][j] == 0:
                createImage(0, i, j, c)
            else:
                createImage(1, i, j, c)
    for i in range(ROOM_HEIGHT):
        for j in range(ROOM_WIDTH):
            if ROOM[i][j] == 7 and ROOM[i][j + 1] != 7: # preventing drawing cabinet twice
                continue
            if ROOM[i][j] == 10 and ROOM[i + 1][j] != 10: # preventing drawing man twice
                continue
            createImage(ROOM[i][j], i, j, c)
    createImage(9, ROOM_HEIGHT, 0, c)
    createImage(2, ROOM_HEIGHT + 1, 0, c)
    for i in range(ROOM_WIDTH - 1):
        createImage(0.99, ROOM_HEIGHT, i + 1, c)
        createImage(0.99, ROOM_HEIGHT + 1, i + 1, c)

def nextMove(event):
    takeNextMove()

def takeNextMove():
    global CURRENT_STATE, POLICY
    print(POLICY[CURRENT_STATE.hash])
    actionIndex = OPS.index(POLICY[CURRENT_STATE.hash])
    sample = np.random.uniform(0.000000001, 1.)
    sumProb = 0
    for i in range(len(OPS)):
        sumProb += TRAN_PROB_MAT[actionIndex][i]
        if sumProb > sample:
            realActionIndex = i
            break
    if CURRENT_STATE.legalOp(OPS[realActionIndex]):
        executeAction(OPS[realActionIndex])
        CURRENT_STATE = CURRENT_STATE.actualNextState(OPS[realActionIndex])
    return

def playEpisode(event):
    global CURRENT_STATE, POLICY, FINAL_STATE, RESET
    while True:
        if RESET == True:
            RESET = False
            break
        takeNextMove()
        c.update()
        time.sleep(1)
        if CURRENT_STATE.isEnd():
            break

def executeAction(action):

    if action in ["up", "down", "left", "right"]:
        moveRobot(action, CURRENT_STATE.stateRoom[0][0], CURRENT_STATE.stateRoom[0][1])
    elif action in ["clean", "pick", "putInBasket"]:
        nonMoveAction(CURRENT_STATE.stateRoom[0][0], CURRENT_STATE.stateRoom[0][1], action)

def moveRobot(direction, row, col):
    global ROOM, OBJECT_IN_ROBOT_POSITION, c
    createImage(OBJECT_IN_ROBOT_POSITION, row, col, c)
    ROOM[row][col] = OBJECT_IN_ROBOT_POSITION
    if direction == "up":
        OBJECT_IN_ROBOT_POSITION = ROOM[row - 1][col]
        ROOM[row - 1][col] = 9
        createImage(9, row - 1, col, c)
    elif direction == "down":
        OBJECT_IN_ROBOT_POSITION = ROOM[row + 1][col]
        ROOM[row + 1][col] = 9
        createImage(9, row + 1, col, c)
    elif direction == "left":
        OBJECT_IN_ROBOT_POSITION = ROOM[row][col - 1]
        ROOM[row][col - 1] = 9
        createImage(9, row, col - 1, c)
    elif direction == "right":
        OBJECT_IN_ROBOT_POSITION = ROOM[row][col + 1]
        ROOM[row][col + 1] = 9
        createImage(9, row, col + 1, c)

def nonMoveAction(row, col, action):
    global OBJECT_IN_ROBOT_POSITION, NUM_OF_PICKED_FRUITS, ROBOT_BAR, BASKET_BAR
    if (action == "pick" and OBJECT_IN_ROBOT_POSITION not in [3,4,5]) or (action == "clean" and OBJECT_IN_ROBOT_POSITION != 8):
        return
    if action in ["clean", "pick"]:
        createImage(1, row, col, c)
        createImage(9, row, col, c)
    if action == "pick":
        NUM_OF_PICKED_FRUITS += 1
        ROBOT_BAR.append(OBJECT_IN_ROBOT_POSITION)
        createImage(OBJECT_IN_ROBOT_POSITION, ROOM_HEIGHT, NUM_OF_PICKED_FRUITS, c)
    OBJECT_IN_ROBOT_POSITION = 1
    if action == "putInBasket":
        OBJECT_IN_ROBOT_POSITION = 2
        numOfObjects = len(ROBOT_BAR)
        for object in range(numOfObjects):
            BASKET_BAR.append(ROBOT_BAR[object])
        ROBOT_BAR = []
        NUM_OF_PICKED_FRUITS = 0
        #erasing robot's bar
        c.create_rectangle(50, ROOM_HEIGHT * 50 + 1, (ROOM_WIDTH) * 50, (ROOM_HEIGHT + 1) * 50, fill=COLOR_DICT[1], outline="white")
        for object in range(len(BASKET_BAR)): #creating basket bar
            createImage(BASKET_BAR[object], ROOM_HEIGHT + 1, object + 1, c)