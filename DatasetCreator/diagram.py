import numpy as np
import random
import cv2
import os
import glob
import traceback
import json
from connection import Connection

class Diagram:
    minCells = 5
    maxCells = 30
    minCellSize = 70
    maxCellSize = 350   
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
        self.coordenates = []

    def generateBaseDiagram(self):
        print(self.diagramName +' | Diagram size: ' + str(self.numXCell) + 'x'+str(self.numYCell) +' cells | Cell size: '+str(self.cellSize) + ' | numComponents: '+str(int(self.numXCell * self.numYCell * self.numComponentPercent)))
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
            propertyImg = [f for f in self.originProperties if f['name'].startswith(img[3])]
            if len(propertyImg) < 0:
                continue
            
            for connectorImg in propertyImg[0]['connectors']:
                x = img[4] + (img[6] - img[4]) * connectorImg['X']
                y = img[5] + (img[7] - img[5]) * connectorImg['Y']

                for imgDts in self.images_list:
                    if img == imgDts:
                        continue

                    propertyDts = [f for f in self.originProperties if f['name'].startswith(imgDts[3])]
                    if len(propertyDts) > 0:
                        for connector in propertyDts[0]['connectors']:
                            xDest = imgDts[4] + (imgDts[6] - imgDts[4]) * connector['X']
                            yDest = imgDts[5] + (imgDts[7] - imgDts[5]) * connector['Y']

                            distance = ((yDest - y) ** 2 + (xDest - x) ** 2 ) ** 0.5
                            distancesToOthers.append({'image': imgDts, 'distance': distance, 'connector': connector})

                if len(distancesToOthers) > 0:
                    sorted_x = sorted(distancesToOthers, key=lambda kv: kv['distance'])
                    self.drawLine(img, sorted_x[0]['image'], connectorImg, sorted_x[0]['connector'])

    def drawLine(self, origin, destination, connectorOrigin, connectorDestination):
        lineThickness = 2
        x1 = int(origin[4] + (origin[6] - origin[4]) * connectorOrigin['X'])
        y1 = int(origin[5] + (origin[7] - origin[5]) * connectorOrigin['Y'])
        x2 = int(destination[4] + (destination[6] - destination[4]) * connectorDestination['X'])
        y2 = int(destination[5] + (destination[7] - destination[5]) * connectorDestination['Y'])
        #cv2.line(self.blank_image, (x1, y1), (x2, y2), (0,255,0), lineThickness)

        connectorOrigin['RealX'] = x1
        connectorOrigin['RealY'] = y1
        connectorDestination['RealX'] = x2
        connectorDestination['RealY'] = y2
        #, connectorDestination



        connection = Connection()
        pointsList = connection.GetConnectionLine(origin, destination, connectorOrigin, connectorDestination)
        lastPoint = None
        for i, point in enumerate(pointsList):
            if i == 0:
                lastPoint = point
                continue

            cv2.line(self.blank_image, lastPoint, point, (0,255,0), lineThickness)
            lastPoint = point

          


if __name__ == '__main__':
    originProperties = None
    with open(os.path.join('..', 'PatternImages', 'properties.json')) as json_file:  
        originProperties = json.load(json_file)


    d = Diagram('diagram1', originProperties)
    d.generateImage()

    cv2.imwrite('prueba.jpg', d.blank_image)

    cv2.imshow("Black Image", d.blank_image)
    cv2.waitKey(0)




    