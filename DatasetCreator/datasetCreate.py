import cv2
import numpy as np
import random
import os
import pandas as pd
from generate_tfrecord import createTFRecord
import json

class DatasetCreate:

    outputPath = 'out'
    outputPathTraining = os.path.join( outputPath, 'train')
    outputPathTest = os.path.join( outputPath, 'test')
    inputImagePath = os.path.join('..', 'PatternImages')
    inputJsonProperties = os.path.join(inputImagePath,'properties.json')
    images_list = []
    fileList = []
    tagLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self):
        self.checkFolder()
        self.readJsonProperties()
        self.fileList = [f for f in os.listdir(self.inputImagePath) if f.endswith('.jpg')] 


    def saveCsv(self, outputFile):
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        df = pd.DataFrame(self.images_list, columns=column_name)
        df.to_csv(outputFile, index=None)

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

    def initialize(self, imageFile, outputPath, outputFile):
        width = random.randint(300,1000)
        height = random.randint(300,1000)

        imagen = cv2.imread(os.path.join(self.inputImagePath, imageFile))

        self.addText(imagen, imageFile)



        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        blank_image = np.zeros((height,width), np.uint8)
        blank_image[:,:] = 255

        #print(random.randint(1,101))

        y_offset = random.randint(0,blank_image.shape[0] - imagen.shape[0])
        x_offset = random.randint(0,blank_image.shape[1] - imagen.shape[1])

        #img = cv2.add(blank_image, imagen) 
        print(imagen.shape)
        print(blank_image.shape)
        blank_image[y_offset:y_offset+imagen.shape[0], x_offset:x_offset+imagen.shape[1]] = imagen

        #print(type(imagen))
        #cv2.imshow("prueba", blank_image)
        #cv2.waitKey(0)
        self.addImageToList(outputFile, width, height, os.path.splitext(os.path.basename(imageFile))[0], x_offset, y_offset, x_offset+imagen.shape[1], y_offset+imagen.shape[0])

        cv2.imwrite(os.path.join(outputPath, outputFile), blank_image)
        return

    def checkFolder(self):
        if not os.path.exists(self.outputPath):
            os.mkdir(self.outputPath)
        if not os.path.exists(self.outputPathTraining):
            os.mkdir(self.outputPathTraining)
        if not os.path.exists(self.outputPathTest):
            os.mkdir(self.outputPathTest)

    def readJsonProperties(self):
        with open(self.inputJsonProperties) as json_file:  
            self.originProperties = json.load(json_file)

    def createDataset(self, iterations, outputPath, outputhFileRecord):
        self.images_list = []
        for index in range(1,iterations):
            for file in self.fileList:
                dc.initialize(file, outputPath, str(index) + file )
        
        dc.saveCsv(os.path.join(outputPath, 'annotations.csv'))
        createTFRecord(outputhFileRecord, outputPath, os.path.join(outputPath, 'annotations.csv') )
       

if __name__ == '__main__':
    try:        
        print('Creating dataset...')
        dc = DatasetCreate()
 
        # Generating training dataset
        dc.createDataset(10, dc.outputPathTraining, os.path.join(dc.outputPath, 'train.record'))

        # Generating test dataset
        dc.createDataset(5, dc.outputPathTest, os.path.join(dc.outputPath, 'test.record'))

      

    except ValueError:
        print(ValueError)
