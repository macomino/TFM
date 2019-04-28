import numpy as np
import random
import cv2
import os
import glob
import traceback
import json

class Diagram:
    minCells = 5
    maxCells = 30
    minCellSize = 70
    maxCellSize = 150   
    blank_image = None
    numComponentPercent = 0.1
    patternsPath = os.path.join('..', 'PatternImages')
    inputJsonProperties = os.path.join(patternsPath,'properties.json')
    tagLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    diagramName = ''

    def __init__(self, diagramName):
        self.cellSize = random.randint(self.minCellSize,self.maxCellSize)
        self.images_list = []
        self.numXCell = random.randint(self.minCells,self.maxCells)
        self.numYCell = random.randint(self.minCells,self.maxCells)
        self.readJsonProperties()
        self.diagramName = diagramName

    def generateBaseDiagram(self):
        print('Diagram size: Cell size: '+str(self.cellSize)+ ' numCells: '+str(self.numXCell)+ ','+str(self.numYCell))
        self.blank_image = np.zeros((self.cellSize * self.numYCell ,self.cellSize * self.numXCell), np.uint8)
        self.blank_image[:,:] = 255

    def generateComponents(self):
        for element in range(0, int(self.numXCell * self.numYCell * self.numComponentPercent)):
                x = random.randint(1,self.numXCell - 2) * self.cellSize
                y = random.randint(1,self.numYCell - 2) * self.cellSize
                print('Coor: '+str(x)+','+str(y))

                patternImage, imageName = self.getRandomPatternimage()
                patternImage = self.resizeImagePattern(patternImage)
                self.blank_image[y:y+patternImage.shape[0], x:x+patternImage.shape[1]] = patternImage
                self.addImageToList(self.diagramName, self.cellSize * self.numXCell, self.cellSize * self.numYCell, os.path.splitext(imageName)[0], x, y, x+patternImage.shape[1], y+patternImage.shape[0])



        

    def getRandomPatternimage(self):
        files = glob.glob(os.path.join(self.patternsPath, '*.jpg'))
        imageFile = files[random.randint(0, len(files) - 1)]

        patternImage = cv2.imread(imageFile)
        patternImage = cv2.cvtColor(patternImage, cv2.COLOR_BGR2GRAY)
        patternImage = self.addText(patternImage, os.path.basename(imageFile))
        return patternImage, os.path.basename(imageFile)

    def addText(self, image, imageFile):
        property = [f for f in self.originProperties if f['name'] == imageFile]

        if len(property) > 0:
            for t in property[0]['texts']:
                X = t['X']
                Y = t['Y']
                length = t['length']
                fontSize = t['fontSize']

                font                   = cv2.FONT_HERSHEY_PLAIN
                bottomLeftCornerOfText = (X,Y)
                fontScale              = fontSize
                fontColor              = (0,0,0)
                lineType               = 2

                cv2.putText(image,''.join([random.choice(self.tagLetters) for f in range(1,length)]), 
                    bottomLeftCornerOfText, 
                    font, 
                    fontScale,
                    fontColor,
                    lineType)
        return image

    def resizeImagePattern(self, image):
        width, height = image.shape[:2]
        if width > height:
            resizeFactor = self.cellSize / width
        else:
            resizeFactor = self.cellSize / height

        return cv2.resize(image,None,fx=resizeFactor,fy=resizeFactor)

    def addImageToList(self, filename, width, height, clase, xmin, ymin, xmax, ymax):
        value = (filename,
                int(width),
                int(height),
                clase,
                int(xmin),
                int(ymin),
                int(xmax),
                int(ymax)
                )
        self.images_list.append(value)

    def readJsonProperties(self):
        with open(self.inputJsonProperties) as json_file:  
            self.originProperties = json.load(json_file)

    def save(self, outputhPath):
        cv2.imwrite(os.path.join(outputhPath, self.diagramName), self.blank_image)

    def generateImage(self):
        self.generateBaseDiagram()
        self.generateComponents()


if __name__ == '__main__':
    d = Diagram('diagram1')
    d.generateImage()

    cv2.imwrite('prueba.jpg', d.blank_image)

    cv2.imshow("Black Image", d.blank_image)
    cv2.waitKey(0)




    