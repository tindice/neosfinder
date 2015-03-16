#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''  Busco Refs en fits.
    Alinear xor los png equalizados
'''
print "processing ..."

import numpy as np
from numpy.lib.stride_tricks import as_strided
from PIL import Image #, ImageOps
import os, datetime as dt
from astrotools import *
import cclabel as ccl
from recognize import recognize, stamptext

fitfolder = os.path.expanduser('~/Descargas/suleika_2/')

tmpfolder = "./tmp/"
cant = 0
#~ totalx, totaly = 0,0
# Recorrer imagenes FIT -------------------------------
filelist = sorted(os.listdir(fitfolder[:-1]))

shiftlog = open("./shift.log", "w")

t0 = dt.datetime.now()
#~ exclude = Checkfits(fitfolder, filelist, log=False)
exclude = []
print"Checkfits: ", dt.datetime.now()-t0

t0 = dt.datetime.now()
print "processing %s*.fit files..." %(fitfolder)
for filename in filelist:
    if filename[-7:-4]=="040": break    # <--- PRIMERAS 40
    
    update_progress(cant,len(filelist))
    if filename[-4:] != ".fit" or filename in exclude:
        shiftlog.write("%s\t --- Excluded ---\n" %(filename+spc))
        continue        # -- next file
    cant += 1
    f = fitfolder+filename
    meta, data = Getdata(f)
    # Uso primera imagen como base para alinear -----------
    if cant == 1: 
        pngsum = Fit2png(data,i0=100,sharp=2.2)
        png1 = pngsum.copy()
        refs1 = FindRefs(data)
        if len(os.listdir(tmpfolder[:-1])) > 0: # si aun tengo las png
            pngsum = "%sSuma.png" %(tmpfolder)
            break
        metadict = {filename : meta}
        print metadict[filename]
        filename1 = filename
        spc = " " * (len(filename) - 4)
        shiftlog.write("File%s\t adx\tady\n" %(spc))
        continue        # -- next file
        
    #~ prevrefs = refs
    metadict[filename] = meta
    refs = FindRefs(data)
    
    png = Fit2png(data,i0=100,sharp=2.2)
    tn = ChooseBestAlign(pngsum,png,refs1-refs)
    
    #~ # Check Out of Field:       
    #~ if abs(totalx+bestx) >Width/2 or abs(totaly+besty) >Height/2:
        #~ shiftlog.write("%s\t %i\t %i\t %i\t %i Field Out.\n" %(filename,bestx,besty,totalx,totaly))
        #~ continue        # -- next file
    shiftlog.write("%s\t  %i\t %i\n" %(filename,tn[1],tn[0]))
    png = Shift(png,dy=tn[0],dx=tn[1])
    # Alineamos ----------------------------------
    pngsum = np.maximum(png, pngsum)
    #~ print type(pngsum)
    #~ Pause()
    e = Image.fromarray(png)
    stamptext(e, (10, 10), metadict[filename][0][:10]+"  "+metadict[filename][0][11:], color=120)
    e.save("%sframe_%s.png" %(tmpfolder, filename[-7:-4]) )

if type(pngsum) != type('str'): # si aun no existe Suma
    s = Image.fromarray(pngsum)
    #~ desde = 
    #~ hasta = metadict[filename][0]
    #~ stamptext(e, (10, 20), "to   "+hasta )
    print"Saving sample: ", dt.datetime.now()-t0
    s.save("%sSuma.png" %(tmpfolder) )

shiftlog.close()        

# Buscamos neos --------------------------------
yx = recognize(pngsum)[0]
#   Lo marcamos:
green = png1.copy()
green[yx[0]-10:yx[1]+10, yx[2]-10] = 100
green[yx[0]-10:yx[1]+10, yx[3]+10] = 100
green[yx[0]-10, yx[2]-10:yx[3]+10] = 100
green[yx[1]+10, yx[2]-10:yx[3]+10] = 100

r = b = Image.fromarray(png1)
g = Image.fromarray(green)
im = Image.merge("RGB", (r,g,b))
stamptext(im, (yx[2]-20, yx[0]-25), "Suleika")
#~ im.show()
im.save(tmpfolder+"tmp.png")
os.system("eog %stmp.png"%(tmpfolder)) 
            

