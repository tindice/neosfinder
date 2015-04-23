#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np, os, Image
from astrotools import *
import datetime as dt
from recognize import recognize, stamptext


t0 = dt.datetime.now()
fitfolder = '../Descargas/su/'
pngfolder = "./tmp"

from gi.repository import Gtk
window = Gtk.Window()
screen = window.get_screen()
print screen.width(), screen.height()

def GetMeta(filefullname):
    """ Returns the Fit metadata dictionary
    """
    hduList = pyf.open(filefullname)
    prihdr = hduList[0].header
    hduList.close()
    return prihdr
 
#~ filelist = sorted(os.listdir(fitfolder[:-1]))
filelist =["../Descargas/suleika/suleika_2_b1x_-001.fit",
            "../Descargas/suleika/suleika_2_b1x_-002.fit",
            "../Descargas/suleika/suleika_2_b1x_-003.fit",
            "../Descargas/suleika/suleika_2_b1x_-004.fit",
            ]
# lista de diccionarios metadata:
metalist = list(GetMeta(f) for f in filelist)
# lista de registros variables:
diflist = list(set(metalist[0].items()) ^ set(metalist[1].items()))
# lista de claves variables:
DifKlist=list(set(list(x[0] for x in diflist)))
# iterando:
for f in filelist[2:]:
    meta = GetMeta(f)
    diflist = list(set(metalist[0].items()) ^ set(meta.items()))
    difKlist=list(set(list(x[0] for x in diflist)))
    DifKlist.extend(difKlist)
    
# unique:
DifKlist=list(set(DifKlist))

print DifKlist

