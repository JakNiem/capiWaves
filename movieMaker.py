#%% Imorts 
import os
import shutil
import random
# from site import execsitecustomize
import numpy as np
import pandas as pd
import sys

import matplotlib.pyplot as plt
import csv
import re

import imageio
import matplotlib.cm as cm
import matplotlib.animation as animation

#%% makeVid-function:
def makeVid(imgList, outpath, fps = 2):
    frames = [] # for storing the generated images
    fig = plt.figure()
    for i in range(len(imgList)):
        frames.append([plt.imshow(imgList[i], cmap=cm.Greys_r,animated=True)])

    anim = animation.ArtistAnimation(fig, frames, interval=50, blit=True,
                                    repeat_delay=1000)
    

    f = os.path.normpath(f'{outpath}.mp4')
    writergif = animation.PillowWriter(fps=fps) 
    writervideo = animation.FFMpegWriter(fps=fps) 
    # anim.save(f, writer=writergif)
    # anim.save(f)
    anim.save(f, writer=writervideo)
    plt.close() 
    return


#%% MAIN:
#  
## get directories in img folder:
imgFolder = './img/'
dirList = os.listdir(imgFolder)
folders = [f for f in dirList if os.path.isdir(os.path.join(imgFolder,f))]
imgDirList = [f for f in folders if f.startswith('T')]
imgDirList.sort()
print(f'imgDirList found: {imgDirList}')


imgDirList = ['T0.7_d18_x128_forcedWave_surfaceHeatmap']
print(f'imgDirList selected: {imgDirList}')

fps = 8
print(f'rendering with {fps} fps')

vidFolder = os.path.normpath('./video/')
if not os.path.exists(vidFolder): os.mkdir(vidFolder)

imgList = []
for imgDir in imgDirList:
    print(f'rendering from folder {imgDir} .. this may take a moment ..')
    imgDirPath = os.path.join(imgFolder, imgDir)
    imgFiles = os.listdir(imgDirPath)
    imgFiles.sort()
    for imgFile in imgFiles:
        imgFilePath = os.path.join(imgDirPath, imgFile)
        imgList.append(imageio.imread(imgFilePath))
    vidOutPath = os.path.join(vidFolder, f'{imgDir}')
    makeVid(imgList, vidOutPath, fps)
    print(f'video for {imgDir} done.')

print(f'all done.')









