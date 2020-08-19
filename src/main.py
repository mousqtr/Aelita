from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
import numpy as np
import csv

confVars = """
win-size 1280 720
window-title Titre
undecorated false
show-frame-rate-meter true
show-scene-graph-analyzer-meter 1
sync-video 1
"""

loadPrcFileData("", confVars)

# Inputs map
keyMap = {
    "left": False,
    "right": False,
    "down": False
}


# Function that updates the input map
def updateKeyMap(key, state):
    keyMap[key] = state


class Disc:
    def __init__(self, disc, color):
        self.disc = disc
        self.color = color
        self.disc.setTexture(color)
        self.disc.setPos(0, 0, 7.5)
        self.disc.setScale(0.75, 0.75, 0.75)


class Connect4(ShowBase):
    def __init__(self):
        super().__init__()

        # Inputs management
        self.accept("arrow_left", updateKeyMap, ["left", True])
        self.accept("arrow_left-up", updateKeyMap, ["left", False])
        self.accept("arrow_right", updateKeyMap, ["right", True])
        self.accept("arrow_right-up", updateKeyMap, ["right", False])
        self.accept("arrow_down", updateKeyMap, ["down", True])
        self.accept("arrow_down-up", updateKeyMap, ["down", False])

        # General settings
        self.disable_mouse()
        self.set_background_color(1, 1, 0.9)

        # Grid management
        self.grid = self.loader.loadModel("../models/grille")
        self.grid.reparentTo(self.render)
        self.blue_grid = self.loader.loadTexture("../tex/blue_plastic.jpg")
        self.grid.setTexture(self.blue_grid)
        self.grid.setHpr(90, 0, 0)
        self.grid.setScale(1, 1, 1)
        self.grid.setPos(0, 40, -6.5)
        self.axes_H = [-6, -4, -2, 0, 2, 4, 6]
        self.axes_V = [5, 3, 1, -1, -3, -5]
        self.column = 3
        self.line = 5

        # Discs management
        self.red_texture = self.loader.loadTexture("../tex/red_plastic.jpg")
        self.yellow_texture = self.loader.loadTexture("../tex/yellow_plastic.jpg")
        self.discs = []
        for i in range(0, 43):
            self.disc = self.loader.loadModel("../models/jeton")
            self.disc.reparentTo(self.render)
            if i % 2 == 0:
                self.color_disc = Disc(self.disc, self.red_texture)
            else:
                self.color_disc = Disc(self.disc, self.yellow_texture)
            self.discs.append(self.color_disc)

        self.round = 0
        self.speed = 20

        self.discs[self.round].disc.setPos(0, 40, 7.5)
        self.movement_V = False
        self.movement_H = False

        # Grid content
        self.gridContent = np.zeros((6, 7))
        self.gridContent2 = np.zeros(6*7)

        # Read csv file cases
        self.results = []
        with open("../csv/cases.csv") as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # change contents to floats
            for row in reader:  # each row is a list
                self.results.append(row)
        #print(self.results)

        # Addition of an update function
        self.taskMgr.add(self.mainloop, "mainloop")


    # Fonction d'actualisation
    def mainloop(self, task):
        dt = globalClock.getDt()
        # print(self.gridContent)

        pos = self.discs[self.round].disc.getPos()
        #pos.z = 7.5


        # left clic
        if keyMap["left"] and self.column != 0 and not self.movement_V:
            keyMap["left"] = False
            self.column -= 1
            self.movement_H = True

        # right clic
        if keyMap["right"] and self.column != 6 and not self.movement_V:
            keyMap["right"] = False
            self.column += 1
            self.movement_H = True

        # down clic
        if keyMap["down"] and self.gridContent[0][self.column] == 0 and not self.movement_V:
            keyMap["down"] = False

            # Compute new position
            line_fixed = False
            self.line = 5
            while line_fixed == False and self.line >= 0 :
                if self.gridContent[self.line][self.column] != 0:
                    self.line -= 1
                else :
                    line_fixed = True
            self.movement_V = True

            # check if there is a victory or not
            victory = self.check_victory()
            if victory == 1:
                print("Red victory")
            if victory == 2:
                print("Yellow victory")

        if self.movement_V and pos.z != self.axes_V[self.line]:
            pos.z -= 0.5
            self.discs[self.round].disc.setPos(pos)

        # prepare next disc
        if self.movement_V and pos.z == self.axes_V[self.line]:
            pos.z = self.axes_V[self.line]
            self.line = 0
            self.discs[self.round].disc.setPos(pos)
            self.round += 1
            self.discs[self.round].disc.setPos(0, 40, 7.5)
            self.movement_V = False
            self.column = 3


        if self.movement_H:
            pos.x = self.axes_H[self.column]
            self.discs[self.round].disc.setPos(pos)
            self.movement_H = False

        return task.cont

    def check_victory(self):
        if self.round % 2 == 0:
            disc_type = 1
        else:
            disc_type = 2
        self.gridContent[self.line][self.column] = disc_type
        self.gridContent2[7 * self.line + self.column] = disc_type

        for i in range(69):
            for j in range(4):
                if self.results[i][j] == 7 * self.line + self.column:
                    if (self.gridContent2[int(self.results[i][0])] == disc_type) and (
                            self.gridContent2[int(self.results[i][1])] == disc_type) and (
                            self.gridContent2[int(self.results[i][2])] == disc_type) and (
                            self.gridContent2[int(self.results[i][3])] == disc_type):
                        return disc_type
        return 0


# Boucle principal
game = Connect4()
game.run()