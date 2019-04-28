import numpy as np
import random
import cv2

class Diagram:
    minCells = 5
    maxCells = 30
    minCellSize = 70
    maxCellSize = 150   
    blank_image = None
    numComponentPercent = 0.3

    def __init__(self):
        self.cellSize = random.randint(self.minCellSize,self.maxCellSize)
       
        self.numXCell = random.randint(self.minCells,self.maxCells)
        self.numYCell = random.randint(self.minCells,self.maxCells)

    def generateBaseDiagram(self):
        self.blank_image = np.zeros((self.cellSize * self.numXCell ,self.cellSize * self.numYCell), np.uint8)
        self.blank_image[:,:] = 255

    def generateComponents(self):
        for element in range(0, self.numXCell * self.numYCell * self.numComponentPercent):
            print(element)

if __name__ == '__main__':
    d = Diagram()
    d.generateBaseDiagram()

    cv2.imshow("Black Image", d.blank_image)
    cv2.waitKey(0)


    