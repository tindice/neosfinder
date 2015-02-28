#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''  Busco Refs en fits.
	Alinear xor los png equalizados
'''
print "processing ..."

import numpy as np
from PIL import Image, ImageOps
import os
from astrotools import *

fitfolder = '../Descargas/suleika/'
pngfolder = "./equalized/"
#~ n, cant = 0, 0
cant = 0
#~ Ref = None
# Recorrer imagenes FIT -------------------------------
filelist = os.listdir(fitfolder[:-1])
totalfiles = len(filelist)
for filename in sorted(filelist):
	if filename[-4:] != ".fit": continue
	cant += 1
	f = fitfolder+filename
	boxes = 8
	if cant > 1: prevrefs = refs
	# Buscar los puntos mas luminosos ---------
	refs = FindRefs(f,boxes)
	for pt in range(0,len(refs)):
		ptx = refs[pt][0]
		pty = refs[pt][1]
	
	#~ e = Image.fromarray(np.flipud(pngarray)).convert("L")
	#~ imout = ImageOps.equalize(e)	
	#~ imout.save("out_%s.png" %(filename[-7:-4]))
	#~ print cant, refs
	
	# Uso primera imagen como base para alinear -----------
	if cant == 1: 
		data = Getdata(f)
		pngsum = Fit2png(data).astype(np.uint8)
		continue		# ---------------------------------
	
	# Buscar desplazamientos mas probables -----------------
	dx, dy = [], []
	for p in range(0,len(refs)):
		dx.append(refs[p][0]-prevrefs[p][0])
		dy.append(refs[p][1]-prevrefs[p][1])
	#^bins = [-1.5,-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5]
	bins = np.arange(-10,15,0.5)
	hx = np.histogram(dx,bins=bins)[0]
	#~ print hx
		# Elegir el mejor dx ---------------------
	xd = []
	for n in range(0,len(hx)):
		if hx[n] != 0:
			xd.append(int(0.5+bins[n]))
			
		# Ensayo alineaciones -------------
	data = Getdata(f)
	png = Fit2png(data).astype(np.uint8)
	for n in range(0,len(xd)):
		ali = np.maximum(Shift(pngsum,dx=xd[n]), png)
		lumi = ali.mean()
		if n==0 or lumi < lumin:
			lumin = lumi
			bestx = xd[n]
		# ahora para dy -------------
	hy = np.histogram(dy,bins=bins,range=(-4.0,4.0))[0]
	yd = []
	for n in range(0,len(hy)):
		if hy[n] != 0:
			yd.append(int(0.5+bins[n]))
			
	for n in range(0,len(yd)):
		ali = np.maximum(Shift(pngsum,dx=bestx,dy=yd[n]), png)
		lumi = ali.mean()
		if n==0 or lumi < lumin:
			lumin = lumi
			besty = yd[n]
	# Alineamos ----------------------------------
	pngsum = np.maximum(Shift(pngsum,bestx,besty), png)
		
		
			

	#~ Choosebest(pngsum,bins,histo)
	#~ Pause()
	#~ arg = histo.argmax()
	#~ conf = 100*histo[arg]/boxes**2 
	#~ if conf < 50: 
		#~ print "\rWarning: en %s hay conf(x)=%i." %(filename,conf)
		#~ continue
	#~ Dx = int(0.5+bins[arg])
	#~ histo = np.histogram(dy,bins=bins,range=(-4.0,4.0))[0]
	#~ conf = 100*histo[arg]/boxes**2 
	#~ if conf < 50: 
		#~ print "\rWarning: en %s hay conf(y)=%i." %(filename,conf)
		#~ continue
	#~ Dy = int(0.5+bins[arg])
#~ 
	#~ data = Getdata(f)
	#~ png = Fit2png(data).astype(np.uint8)
	#~ pngsum = np.maximum(Shift(pngsum,Dx,Dy), png)
	#~ pngsum = Shift(pngsum,-Dx,-Dy).__xor__(png)
	#~ fitsum = Shift(fitsum.astype(np.uint16),Dx,Dy) ^ data  # xor
	#~ print data
	#~ print pngsum
	#~ print np.amax(pngsum)
	#~ Pause()
	#~ prevrefs = FindRefs(pngsum)
	prevrefs = refs
	update_progress(cant,totalfiles)
	#~ if cant == 110: break

#~ e = Image.fromarray(np.flipud(png))
e = Image.fromarray(pngsum)
#~ e = ImageOps.equalize(e)	
e.save("out_0 a %i.png" %(cant) )
	
	
	
	#~ cant += 1
	#~ imin = Image.open(folder+"/"+filename).convert("L")
	#~ refs, array = FindRefs(imin,cros=True)
	#~ 
	#~ imout = Image.fromarray(array)
	#~ imout.save("out_%s.png" %(filename[-7:-4]))
	#~ raw_input("pausa")
	#################################################
	
	#~ if Ref == None:
		#~ Ref = refs
		#~ a = array
		#~ prevDist = Distances(refs)
	#~ else:
		#~ actDist = Distances(refs)
		#~ print prevDist
		#~ print actDist
		#~ raw_input("Enter")
		#~ prevDist = actDist
		
		
		
		#~ if Ref[0] in refs:
			#~ a = a.__xor__(array)
			#~ n += 1
#~ imout = Image.fromarray(a)
#~ imout.save("out.png")
#~ print "%i imágenes superpuestas de %i procesadas." %(n,cant)
#~ imout.save("out_%s.png" %(filename[-7:-4]))
	
	
	

	
