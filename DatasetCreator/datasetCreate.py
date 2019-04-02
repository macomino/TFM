import cv2
import numpy as np
import random
import os
import pandas as pd

class DatasetCreate:

    outputPath = 'out'
    inputImagePath = ''
    images_list = []

    def saveCsv(self):
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        df = pd.DataFrame(self.images_list, columns=column_name)
        df.to_csv('annotations.csv', index=None)

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

    def initialize(self, imageFile, outputFile):
        width = 500
        height = 300

        imagen = cv2.imread(os.path.join(self.inputImagePath, imageFile))

        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        blank_image = np.zeros((height,width), np.uint8)
        blank_image[:,:] = 255

        print(random.randint(1,101))

        y_offset = random.randint(0,blank_image.shape[0] - imagen.shape[0])
        x_offset = random.randint(0,blank_image.shape[1] - imagen.shape[1])

        #img = cv2.add(blank_image, imagen) 
        print(imagen.shape)
        print(blank_image.shape)
        blank_image[y_offset:y_offset+imagen.shape[0], x_offset:x_offset+imagen.shape[1]] = imagen

        #print(type(imagen))
        #cv2.imshow("prueba", blank_image)
        #cv2.waitKey(0)
        self.addImageToList(outputFile, width, height, imageFile, x_offset, y_offset, x_offset+imagen.shape[1], y_offset+imagen.shape[0])

        cv2.imwrite( os.path.join(self.outputPath, outputFile) ,blank_image)
        return


if __name__ == '__main__':
    try:        
        print('Creating dataset...')
        dc = DatasetCreate()

        dc.inputImagePath = os.path.join('..','..', 'imagenesPatron')

        fileList = os.listdir(dc.inputImagePath)


        for index in range(1,10):
            for file in fileList:
                dc.initialize(file, str(index) + file)
        
        dc.saveCsv()
        
    except ValueError:
        print(ValueError)
