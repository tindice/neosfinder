#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np, Image
import os
from astrotools import *
import datetime as dt
t0 = dt.datetime.now()
fitfolder = '../Descargas/suleika/'
pngfolder = "./equalized"

def getbbox(array, thr=0):
	yy, xx = np.where(array > thr) # 
	BB = (yy.min(), yy.max(), xx.min(), xx.max())
	return (BB[1]-BB[0], BB[3]-BB[2])
	
e = Image.open("/home/rodolfo/neosfinder/1 a 041.png")
png = np.asarray(e)
refsy, refsx = FindRefs(png)
TODO: Recorrer segun nuevo FindRefs:
	
for box in refs:
	if box[2] < 150: # descartar poco luminosas
		continue # --> next box
	dt = 1
	a = png[box[1]-dt:box[1]+dt+1, box[0]-dt:box[0]+dt+1]
	shape = a.shape
	while getbbox(a) == shape:
		dt += 1
	print "shape", shape
	print "bbox", getbbox(a)
	print
	
