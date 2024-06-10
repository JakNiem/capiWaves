import os
import shutil
import random
from site import execsitecustomize
import numpy as np
import pandas as pd
import sys

from datetime import datetime

import math

import matplotlib.pyplot as plt
import csv
import re

import seaborn as sns



dirList = os.listdir('.')
folders = [f for f in dirList if os.path.isdir(f)]
print(f'folders found: {folders}')


# folders = ['T0.7_d18_x128_forcedWave']
print(f'folders selected: {folders}')

if not os.path.exists('./img/'): os.mkdir('./img/')

for folder in folders:
    imgFolder = os.path.join('./img/', f'{folder}_surfaceHeatmap')
    if not os.path.exists(imgFolder): os.mkdir(imgFolder)
    print(f'folder: {folder}')
    
    dirList = os.listdir(folder)
    scalarSamples = [f for f in dirList if 'CapiSampling_TS' in f]
    scalarSamples.sort()
    # print(dirList)
    if len(scalarSamples) == 0:
        print(f'no relevant files found in folder {folder}.')
    else:
        print(f"folder: {folder}")
        for sample in scalarSamples:
            print(f'sample: {sample}')
            filePath = os.path.join(folder, sample)
            sampledf = pd.read_csv(filePath, delimiter='\s+', index_col='x')

            leftDF = sampledf[sampledf['yIndex']==0]
            leftDF = leftDF.drop(['yIndex'], axis=1)

            rightDF = sampledf[sampledf['yIndex']==1]
            rightDF = rightDF.drop(['yIndex'], axis=1)

            plt.rcParams['figure.figsize'] = [12, 6]
            plt.subplot(1, 2, 1) # row 1, col 2 index 1
            ax = sns.heatmap(leftDF,annot=True, square=True, vmin=0, vmax=.5)
            plt.subplot(1, 2, 2) # row 1, col 2 index 2
            ax = sns.heatmap(rightDF,annot=True, square=True, vmin=0, vmax=.5) #, vmin=0, vmax=.8
            plt.savefig(os.path.join(imgFolder, f'{folder}_{sample}.jpg'))
            plt.close()
    

