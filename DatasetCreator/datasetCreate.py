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
                text_file.writelines('  id: '+str(i + 1)+'\n')
                text_file.writelines('  name: \''+property['name'].split('.')[0]+'\'\n')
                text_file.writelines('}\n\n')
               

if __name__ == '__main__':
    try:        
        print('Creating dataset...')
        dc = DatasetCreate(os.path.join('..', 'PatternImages'), 'out')

        # Generating training dataset
        dc.generateDataset(100, dc.outputPathTraining, os.path.join(dc.outputPath, 'train.record'))

        # Generating test dataset
        dc.generateDataset(10, dc.outputPathTest, os.path.join(dc.outputPath, 'test.record'))

        dc.generatePbtxt()

    except Exception as e:
        print('Error: ' + str(e))
        traceback.print_exc()

