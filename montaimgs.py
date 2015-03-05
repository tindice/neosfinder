#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''  Busco Refs en fits.
	Alinear xor los png equalizados
'''
print "processing ..."

import numpy as np
from PIL import Image, ImageOps
import os, datetime as dt
from astrotools import *

fitfolder = os.path.expanduser('~/Descargas/suleika/')
#~ print fitfolder

pngfolder = "./equalized/"
cant = 0
totalx, totaly = 0,0
# Recorrer imagenes FIT -------------------------------
filelist = sorted(os.listdir(fitfolder[:-1]))
totalfiles = len(filelist)
shiftlog = open("./shift.log", "w")

t0 = dt.datetime.now()
exclude = Checkfits(fitfolder, filelist)
print"Checkfits: ", dt.datetime.now()-t0

t0 = dt.datetime.now()
print "processing %s*.fit files..." %(fitfolder)
for filename in filelist:
	if filename[-7:-4]=="150": break
	update_progress(cant,totalfiles)
	if filename[-4:] != ".fit" or filename in exclude:
		shiftlog.write("%s\t --- Excluded ---\n" %(filename+spc))
		continue		# -- next file
	cant += 1
	f = fitfolder+filename
	boxes = 8
	# Uso primera imagen como base para alinear -----------
	if cant == 1: 
		spc = " " * (len(filename) - 4)
		shiftlog.write("File%s\t dx\t dy\tadx\tadyn" %(spc))
		data = Getdata(f)
		pngsum = Fit2png(data).astype(np.uint8)
		refs = FindRefs(f,boxes)
		continue		# -- next file
		
	prevrefs = refs
	# Buscar los puntos mas luminosos ---------
	refs = FindRefs(f,boxes)
	#~ if filename[-7:-4]=="041": print refs	#debug
	for pt in range(0,len(refs)):
		ptx = refs[pt][0]
		pty = refs[pt][1]
	
	# Buscar desplazamientos relativos -----------------
	dx, dy = [], []
	for p in range(0,len(refs)):
		dx.append(refs[p][0]-prevrefs[p][0])
		dy.append(refs[p][1]-prevrefs[p][1])

	# Quitando repetidos ------------
	dx = np.unique(dx)
	dy = np.unique(dy)
	
	# Elegir el mejor dx ensayando alineaciones------
	data = Getdata(f)
	Height, Width = data.shape
	png = Fit2png(data).astype(np.uint8)
	for n in range(0,len(dx)):
		ali = np.maximum(Shift(png,dx=-totalx-dx[n]), pngsum)
		lumi = ali.mean()
		if n==0 or lumi < lumin:
			lumin = lumi
			bestx = dx[n]
		# ahora para dy -------------
	for n in range(0,len(dy)):
		ali = np.maximum(Shift(png,dx=-totalx-bestx,dy=-totaly-dy[n]), pngsum)
		lumi = ali.mean()
		if n==0 or lumi < lumin:
			lumin = lumi
			besty = dy[n]
	# Check Out of Field:		
	if abs(totalx+bestx) >Width/2 or abs(totaly+besty) >Height/2:
		shiftlog.write("%s\t %i\t %i\t %i\t %i Field Out.\n" %(filename,bestx,besty,totalx,totaly))
		continue		# -- next file
			
	totalx += bestx		# acumulo desplazamientos absolutos:
	totaly += besty
	shiftlog.write("%s\t %i\t %i\t %i\t %i\n" %(filename,bestx,besty,totalx,totaly))
	# Alineamos ----------------------------------
	pngsum = np.maximum(Shift(png,-totalx,-totaly), pngsum)
		
	#~ prevrefs = refs
	e = Image.fromarray(pngsum)
	e.save("out_1 a %s.png" %(filename[-7:-4]) )
print"Saving to 150: ", dt.datetime.now()-t0

shiftlog.close()		
			

