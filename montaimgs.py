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
    
    update_progress(cant,len(filelist))
    if filename[-4:] != ".fit" or filename in exclude:
        shiftlog.write("%s\t --- Excluded ---\n" %(filename+spc))
        continue        # -- next file
    cant += 1
    f = fitfolder+filename
    meta, data = Getdata(f)
    size = (data.shape[1]/2, data.shape[0]/2)
    
    # Uso primera imagen como base para alinear -----------
    if cant == 1: 
        #~ pngsum = Fit2png(data,i0=100,sharp=2.2)
        pngsum = Fit2png(data)
        png1 = pngsum.copy()
        refs1 = FindRefs(data)
        if len(os.listdir(tmpfolder[:-1])) > 0: # si aun tengo las png
            pngsum = "%sSuma.png" %(tmpfolder)
            break
        metadict = {filename : meta}
        #~ print metadict[filename]
        filename1 = filename
        spc = " " * (len(filename) - 4)
        shiftlog.write("File%s\t adx\tady\n" %(spc))
        continue        # -- next file
        
    #~ prevrefs = refs
    metadict[filename] = meta
    refs = FindRefs(data)
    
    #~ png = Fit2png(data,i0=100,sharp=2.2)
    png = Fit2png(data)
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
    e0 = e.copy()
    e0.thumbnail(size, Image.BICUBIC)
    stamptext(e0, (10, 10), metadict[filename][0][:10]+"  "+
        metadict[filename][0][11:], color=190)
    e0.save("%sframe_%s.png" %(tmpfolder, filename[-7:-4]) )
    if filename[-7:-4]=="040": break    # <--- PRIMERAS 40

if type(pngsum) != type('str'): # si aun no existe Suma
    s = Image.fromarray(pngsum)
    #~ desde = 
    #~ hasta = metadict[filename][0]
    print"Saving sample: ", dt.datetime.now()-t0
    s0 = s.copy()
    s0.thumbnail(size, Image.BICUBIC)
    stamptext(s0, (10, 10), metadict[filename1][0][:10]+"  "+
        metadict[filename1][0][11:], color=190)
    stamptext(s0, (10, 30), metadict[filename][0][:10]+"  "+
        metadict[filename][0][11:], color=190)
    s0.save("%sSuma.png" %(tmpfolder) )

shiftlog.close()        

# Buscamos neos --------------------------------
comp = recognize(pngsum,11)
print
print len(comp), "Componentes:"
#~ print pngsum
#~ print comp
#~ Pause()
#   Lo marcamos:
green = png1.copy()
n = 0
for (y0, y1, x0, x1) in comp:
    n += 1
    print n,(y0, y1, x0, x1)
    y00 = max(2*(y0-5),0)
    x00 = max(2*(x0-5),0)
    y01 = min(2*(y1+5),1020)
    x01 = min(2*(x1+5),1530)
    green[y00:y01, x00] = 200
    green[y00:y01, x01] = 200
    green[y00, x00:x01] = 200
    green[y01, x00:x01] = 200
    
r = b = Image.fromarray(png1)
g = Image.fromarray(green)
#~ for n in range(0, len(comp)):
    #~ stamptext(g, (2*x1, 2*y1), str(n+1), color=190)

im = Image.merge("RGB", (r,g,b))
#~ stamptext(im, (c[2]-20, c[0]-25), "Suleika")
#~ im.show()
im.save(tmpfolder+"tmp.png")
os.system("eog %stmp.png"%(tmpfolder)) 
            
#~ os.system("apngasm out.png %sframe_002.png"%(tmpfolder))

