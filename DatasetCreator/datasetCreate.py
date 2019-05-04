import cv2
import numpy as np
import random
import os
import pandas as pd
from generate_tfrecord import createTFRecord
import json
import traceback
from diagram import Diagram

class DatasetCreate:

    images_list = []
    fileList = []
    tagLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self, inputImagePath, output):
        self.outputPath = output
        self.outputPathTraining = os.path.join(output, 'train')
        self.outputPathTest = os.path.join(output, 'test')
        self.inputImagePath = inputImagePath
        self.inputJsonProperties = os.path.join(inputImagePath,'properties.json')
        self.checkFolder()
        self.fileList = [f for f in os.listdir(self.inputImagePath) if f.endswith('.jpg')] 
        self.readJsonProperties()


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

   

    def generate(self, imageFile, outputPath, outputFile):
        width = random.randint(300,1000)
        height = random.randint(300,1000)

        imagen = cv2.imread(os.path.join(self.inputImagePath, imageFile))

        #Add text component
        #self.addText(imagen, imageFile)

        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        blank_image = np.zeros((height,width), np.uint8)
        blank_image[:,:] = 255

        #Random change brightness
        imagen = self.changeBrigthness(imagen, random.randint(0,100))

        #Random resize image component
        condition = True
        while condition:
            resizeFactor = random.uniform(0.5, 1.5)
            imagen = cv2.resize(imagen,None,fx=resizeFactor,fy=resizeFactor)
            condition = (blank_image.shape[0] - imagen.shape[0])  < 0 or (blank_image.shape[1] - imagen.shape[1]) < 0

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

    def changeBrigthness(self, image, value):
        return  np.where((255 - image) < value, 255,image+value)

    def checkFolder(self):
        if not os.path.exists(self.outputPath):
            os.mkdir(self.outputPath)
        if not os.path.exists(self.outputPathTraining):
            os.mkdir(self.outputPathTraining)
        if not os.path.exists(self.outputPathTest):
            os.mkdir(self.outputPathTest)

    def generateDataset(self, diagramNumber, outputPath, outputhFileRecord):
        self.images_list = []
        for i in range(1,diagramNumber + 1):
            diagram = Diagram('diagram'+str(i)+'.jpg', self.originProperties)
            diagram.generateImage()
            diagram.save(outputPath)
            self.images_list = self.images_list + diagram.images_list

        self.saveCsv(os.path.join(outputPath, 'annotations.csv'))
        createTFRecord(outputhFileRecord, outputPath, os.path.join(outputPath, 'annotations.csv'), self.originProperties )

    def readJsonProperties(self):
        with open(self.inputJsonProperties) as json_file:  
            self.originProperties = json.load(json_file)

    def generatePbtxt(self):
        with open(os.path.join(self.outputPath, 'label_map.pbtxt'), "w") as text_file:
            for i, property in enumerate([f for f in self.originProperties if f['isComponent'] == True]):
                text_file.writelines('item {\n')
                text_file.writelines('  id: '+str(i)+'\n')
                text_file.writelines('  name: \''+property['name'].split('.')[0]+'\'\n')
                text_file.writelines('}\n\n')
               

if __name__ == '__main__':
    try:        
        print('Creating dataset...')
        dc = DatasetCreate(os.path.join('..', 'PatternImages'), 'out')

        # Generating training dataset
        dc.generateDataset(200, dc.outputPathTraining, os.path.join(dc.outputPath, 'train.record'))

        # Generating test dataset
        dc.generateDataset(50, dc.outputPathTest, os.path.join(dc.outputPath, 'test.record'))

        dc.generatePbtxt()

    except Exception as e:
        print('Error: ' + str(e))
        traceback.print_exc()

