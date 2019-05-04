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
    maxCellSize = 250   
    blank_image = None
    numComponentPercent = 0.1
    patternsPath = os.path.join('..', 'PatternImages')
    inputJsonProperties = os.path.join(patternsPath,'properties.json')
    tagLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    diagramName = ''
    coordenates = []

    def __init__(self, diagramName, originProperties):
        self.cellSize = random.randint(self.minCellSize,self.maxCellSize)
        self.images_list = []
        self.numXCell = random.randint(self.minCells,self.maxCells)
        self.numYCell = random.randint(self.minCells,self.maxCells)
        self.diagramName = diagramName
        self.originProperties = originProperties

    def generateBaseDiagram(self):
        print('Diagram size: ' + str(self.numXCell) + 'x'+str(self.numYCell) +' cells | Cell size: '+str(self.cellSize))
        self.blank_image = np.zeros((self.cellSize * self.numYCell ,self.cellSize * self.numXCell), np.uint8)
        self.blank_image[:,:] = 255

    def generateComponents(self):
        for element in range(0, int(self.numXCell * self.numYCell * self.numComponentPercent)):
                x = random.randint(1,self.numXCell - 2) * self.cellSize
                y = random.randint(1,self.numYCell - 2) * self.cellSize
                
                if [x, y] in self.coordenates:
                    continue
                #print('Coor: '+str(x)+','+str(y))

                self.coordenates.append([x,y])
                patternImage, imageName, isComponent = self.getRandomPatternimage()
                patternImage = self.resizeImagePattern(patternImage)
                self.blank_image[y:y+patternImage.shape[0], x:x+patternImage.shape[1]] = patternImage
                if isComponent:
                    self.addImageToList(self.diagramName, self.cellSize * self.numXCell, self.cellSize * self.numYCell, os.path.splitext(imageName)[0], x, y, x+patternImage.shape[1], y+patternImage.shape[0])


    def getRandomPatternimage(self):
        imagesTypes = [f for f in self.originProperties]
        #files = glob.glob(os.path.join(self.patternsPath, '*.jpg'))
        imageFile = imagesTypes[random.randint(0, len(imagesTypes) - 1)]

        patternImage = cv2.imread(os.path.join(self.patternsPath, imageFile['name']))
        patternImage = cv2.cvtColor(patternImage, cv2.COLOR_BGR2GRAY)
        patternImage = self.addText(patternImage, os.path.basename(imageFile['name']))
        return patternImage, os.path.basename(imageFile['name']), imageFile['isComponent']

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

                cv2.putText(image,''.join([random.choice(self.tagLetters) for f in range(0,length)]), 
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


    def save(self, outputhPath):
        cv2.imwrite(os.path.join(outputhPath, self.diagramName), self.blank_image)

    def generateImage(self):
        self.generateBaseDiagram()
        self.generateComponents()
        self.connections()

    def connections(self):
        
        for img in self.images_list:
            distancesToOthers = []
            x = img[4]
            y = img[5]
            for imgDts in self.images_list:
                if img == imgDts:
                    continue
                xDest = imgDts[4]
                yDest = imgDts[5]

                distance = ((yDest - y) ** 2 + (xDest - x) ** 2 ) ** 0.5
                distancesToOthers.append({'image': imgDts, 'distance': distance})

            sorted_x = sorted(distancesToOthers, key=lambda kv: kv['distance'])
            self.drawLine(img, sorted_x[0]['image'])

    def drawLine(self, origin, destination):
        lineThickness = 2
        x1 = origin[4]
        y1 = origin[5]
        x2 = destination[4]
        y2 = destination[5]
        cv2.line(self.blank_image, (x1, y1), (x2, y2), (0,255,0), lineThickness)


            


if __name__ == '__main__':
    originProperties = None
    with open(os.path.join('..', 'PatternImages', 'properties.json')) as json_file:  
        originProperties = json.load(json_file)


    d = Diagram('diagram1', originProperties)
    d.generateImage()

    cv2.imwrite('prueba.jpg', d.blank_image)

    cv2.imshow("Black Image", d.blank_image)
    cv2.waitKey(0)




    