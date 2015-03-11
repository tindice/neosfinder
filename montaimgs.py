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
import cclabel as ccl

fitfolder = os.path.expanduser('~/Descargas/suleika/')

pngfolder = "./equalized/"
cant = 0
totalx, totaly = 0,0
# Recorrer imagenes FIT -------------------------------
filelist = sorted(os.listdir(fitfolder[:-1]))
totalfiles = len(filelist)
shiftlog = open("./shift.log", "w")

t0 = dt.datetime.now()
#~ exclude = Checkfits(fitfolder, filelist, log=False)
exclude = []
print"Checkfits: ", dt.datetime.now()-t0

t0 = dt.datetime.now()
print "processing %s*.fit files..." %(fitfolder)
for filename in filelist:
    if filename[-7:-4]=="040": break    # <--- PRIMERAS 40
    
    update_progress(cant,totalfiles)
    if filename[-4:] != ".fit" or filename in exclude:
        shiftlog.write("%s\t --- Excluded ---\n" %(filename+spc))
        continue        # -- next file
    cant += 1
    f = fitfolder+filename
    # Uso primera imagen como base para alinear -----------
    if cant == 1: 
        spc = " " * (len(filename) - 4)
        shiftlog.write("File%s\t dx\t dy\tadx\tady\n" %(spc))
        data = Getdata(f)
        pngsum = Fit2png(data,i0=100,sharp=2.2).astype(np.uint8)
        refsy, refsx = FindRefs(data)
        continue        # -- next file
        
    data = Getdata(f)
    prevrefsy = refsy
    prevrefsx = refsx
    refsy, refsx = FindRefs(data)
    #~ print prevrefsx
    #~ print refsx
    # Buscar desplazamientos relativos -----------------
    dx = refsx-prevrefsx
    #~ print dx
    dy = refsy-prevrefsy
    # Quitando repetidos ------------
    dx = np.unique(dx)
    print
    print dx
    dy = np.unique(dy)
    print dy
    # Elegir el mejor dy ensayando alineaciones------
    Height, Width = data.shape
    png = Fit2png(data,i0=100,sharp=2.2).astype(np.uint8)
    lumin = 4000000000
    maskmin = min(set(dy))
    maskmax = max(set(dy))
    mpngsum = pngsum.copy()
    mpngsum[:totaly+maskmax,:] =0 NO !!!!! Pensarlo mejor
    for n in set(dy):
		shpng = Shift(png,dy=-totaly-n)
        ali = np.maximum(shpng, pngsum)
        lumi = ali.sum(dtype=np.uint32)
        if lumi < lumin:
            lumin = lumi
            besty = dy[n]
    print "besty = %i con lumi=%i" %(besty,lumin)
	
    # ahora para dx -------------
    lumin = 4000000000
    for n in set(dx):
        ali = np.maximum(Shift(png,dx=-totalx-dx[n],dy=-totaly-besty), pngsum)
        lumi = ali.sum(dtype=np.uint32)
        if lumi < lumin:
            lumin = lumi
            bestx = dx[n]
    print "bestx = %i con lumi=%i" %(bestx,lumin)
            
    # y otra vez para dy -------------
    lumin = 4000000000
    for n in set(dy):
        ali = np.maximum(Shift(png,dx=-totaly-bestx, dy=-totaly-dy[n]), pngsum)
        lumi = ali.sum(dtype=np.uint32)
        if lumi < lumin:
            lumin = lumi
            besty = dy[n]
    print "besty = %i con lumi=%i" %(besty,lumin)
    Pause("dx")
    
    # Check Out of Field:       
    if abs(totalx+bestx) >Width/2 or abs(totaly+besty) >Height/2:
        shiftlog.write("%s\t %i\t %i\t %i\t %i Field Out.\n" %(filename,bestx,besty,totalx,totaly))
        continue        # -- next file
            
    totalx += bestx     # acumulo desplazamientos absolutos:
    totaly += besty
    shiftlog.write("%s\t %i\t %i\t %i\t %i\n" %(filename,bestx,besty,totalx,totaly))
    # Alineamos ----------------------------------
    pngsum = np.maximum(Shift(png,-totalx,-totaly), pngsum)
        
e = Image.fromarray(pngsum)
e.save("out_1 a %s.png" %(filename[-7:-4]) )
print"Saving sample: ", dt.datetime.now()-t0

e_bw = ccl.bw(e)
#~ a_bw = np.array(e_bw)
(labels, output_img) = ccl.run(e_bw)
#~ output_img.show()
vals = labels.values()
#~ print set(vals)
#~ histo = list([(x, vals.count(x)) for x in set(vals)])
histo = list([(x, vals.count(x)) for x in set(vals)])
histo = sorted(histo,key=lambda x: x[1])
print histo
for lbl in range(len(histo)-1,-1,-1): # orden de tamaño descendente
    Comp = ccl.findcomponent(labels,lbl)  # lista de pixels del componente lbl
    xx, yy = [], []
    for (x,y) in Comp:
        xx.append(x)
        yy.append(y)
    x0 = min(xx)
    x1 = max(xx)
    y0 = min(yy)
    y1 = max(yy)
    if (x1-x0+y1-y0) < 10: continue # Descarto componentes pequeños.
    if (pngsum[y0,x0]<190 and pngsum[y0,x1]<190 and
        pngsum[y1,x0]<190 and pngsum[y1,x1]<190): continue # Descarto componentes redondos.
    print pngsum[y0:y1+1,x0:x1+1]
    Pause()
shiftlog.close()        
            

