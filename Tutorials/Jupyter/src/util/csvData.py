# -*- coding: utf-8 -*-
"""
Generically extract the header and data from any lab instrument in csv format

Created on Tue Jun 20 15:30:05 2017
@author: dan.boschen

Updated on Fri Jun 30 14:13:00 2017
@author: josh.wilkins
"""

import numpy as np

class csvData(object):
    '''
    Importer for csv files with formt:
    Input, Ouput1, Output2, Output3, ...
    '''
    
    def __init__(self, fileName):
        # Extracts the header and stores the filePath
        self.fileName = fileName
        self.head = self.__getHeader() # Extract header (Array)
        
    def __getHeader(self):
        # Returns Header in Array Format
        
        head = []
        with open(self.fileName) as dataFile:
            for line in dataFile:
                if (line[0].isdigit() or line[0] == '-' or line[0] == '+'):
                    try:
                        float(line.split(',')[0]) # For the cases formatted as such: '123 ABC, DEF'
                        break
                    except:
                        pass
                else:
                    head.append(line.strip('\n'))
        return head

    def getDataGen(self):
        # Returns generator for input/output data pairs
        
        with open(self.fileName) as dataFile:
            for line in dataFile:
                line = line.strip()
                if (line[0].isdigit() or line[0] == '-' or line[0] == '+'):
                    try:
                        dataPair = [float(x) for x in line.split(',') if x != '']
                        yield dataPair
                    except:
                        pass

    def getData(self):
        # Returns array of input & output data arrays
        
        dataGen = self.getDataGen()
        out = np.array([test for test in dataGen])
        # out = [ [Input Values], [Output1 Values], [Output2 Values], ... ]
        # Inputs = out[:,0] --- Outputs1 = out[:,1] --- Outputs2 = out[:,2] --- etc
        return out

