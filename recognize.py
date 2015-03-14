#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np, Image
import cclabel as ccl
from astrotools import *
#~ import datetime as dt
#~ t0 = dt.datetime.now()
#~ fitfolder = '../Descargas/suleika/'
#~ pngfolder = "./equalized"
    
e = Image.open("/home/rodolfo/neosfinder/2_1 a 039.png")
img = ccl.bw(e)
#~ a_bw = np.array(e_bw)
(labels, output_img) = ccl.run(img)
pngsum = np.array(img.getdata(),
         np.uint8).reshape(img.size[1], img.size[0])
#~ output_img.show()

vals = labels.values()
histo = np.array(list([(x, vals.count(x)) for x in set(vals)]))
#~ print histo
histo = histo[histo[:,1].argsort()]
#~ print histo
#~ Pause("histo")

for n in range(len(histo)-1,-1,-1): # orden de tamaño descendente
    lbl = histo[n,0]
    Comp = ccl.findcomponent(labels,lbl)  # lista de pixels del componente lbl
    #~ print "Comp", lbl
    #~ print Comp
    #~ Pause()
    y0 = min(Comp,key=lambda item:item[1])[1]
    y1 = max(Comp,key=lambda item:item[1])[1]
    x0 = min(Comp,key=lambda item:item[0])[0]
    x1 = max(Comp,key=lambda item:item[0])[0]
    if (x1-x0+y1-y0) < 15: continue # Descarto componentes pequeños.
    if (pngsum[y0:y0+2,x0:x0+2].sum(dtype=np.uint16)
      + pngsum[y0:y0+2,x1-1:x1].sum(dtype=np.uint16) 
      + pngsum[y1-1:y1,x0:x0+2].sum(dtype=np.uint16) 
      + pngsum[y1-1:y1,x1-1:x1].sum(dtype=np.uint16)<255*3): continue # Descarto componentes redondos.
    print pngsum[y0:y1+1,x0:x1+1]
    print "x0, x1, y0, y1 :", x0,x1, y0,y1
    Pause(str(lbl))
