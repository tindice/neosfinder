#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image, ImageDraw
from astropy.io import fits
def Array2rgb(array,circles=[],texts=[]):
    ''' where circles=[(y0, y1, x0, x1),...] 
            texts=[(xy,string,color),...]
        Returns a resized RGB image from a 2D np.array 
    '''
    r = Image.fromarray(array)
    g = r.copy()
    b = r.copy()
    im = Image.merge("RGB", (r,g,b))
    size = (array.shape[1]/2, array.shape[0]/2)
    im.thumbnail(size, Image.BICUBIC)

    for (y0, y1, x0, x1) in circles:
        xy = (x0/2-5,y0/2-5,x1/2+5,y1/2+5)
        ImageDraw.Draw(im).ellipse(xy, fill=None, outline=(0,200,0))
        
    for (xy,string,color) in texts:
        xy = tuple(x/2 for x in xy)
        ImageDraw.Draw(im).text(xy, string, fill=color)
    return im

def Pause(msg="Enter to cont, Ctrl-C to exit: "):
    raw_input(msg)

def Checkfits(path, filelist, mean_criteria=(0.5,10), uprogress=True, log=False):
    ''' Purges form filelist all files not *.fit or *.fits and
            returns the exclude list following critera.
    '''
    print "\r Checking Fitfiles  ...",
    fitlist = [f for f in filelist if (f[-4:]==".fit") or (f[-5:]==".fits") ]
    means = {f:int(np.mean(Getdata(path+f)[1])) for f in fitlist}
    mean = means[fitlist[0]]
    exclude = [f for f in fitlist if means[f]<mean*mean_criteria[0] or means[f]>mean*mean_criteria[1]]
    
        # Guardo Exclude para el futuro
    log = open(path+"exclude.log", "w")
    log.write(str(exclude)+"\n")
    log.close()
    
    return fitlist, exclude

def Shift(array,dx=0,dy=0):
    dx = int(round(dx))
    dy = int(round(dy))
    a = array.copy()
    if dx > 0:
        a[:,-dx:] *= 0
    elif dx < 0:
        a[:,:-dx] *= 0
    a = np.roll(a,dx,axis=1)
    if dy > 0:
        a[-dy:,:] *= 0
    elif dy < 0:
        a[:-dy,:] *= 0
    a = np.roll(a,dy,axis=0)
    return a
    
def GetMeta(filefullname):
    """ Returns the Fit metadata dictionary
    """
    hduList = fits.open(filefullname)
    hduList.verify("fix")
    prihdr = hduList[0].header
    hduList.close()
    return prihdr

def Getdata(filefullname):
    """ Returns the Fit data array and the tuple (obsTime,Telescop, AsRect,Decl)
        accepts "filefullname" as string or as np.array
    """
    if type(filefullname) == type('str'):
        hduList = fits.open(filefullname)
        prihdr = hduList[0].header
        data = hduList[0].data.astype(np.uint16, copy=False)
        hduList.close()
        #~ if np.amin(data) < 0:
            #~ data = data + 32768
        #~ print "at11>", np.amin(data)
        return (prihdr[5],prihdr[31],
                 prihdr[17],prihdr[18]), data

    else:
        data = filefullname
        #~ if np.amin(data) < 0:
            #~ data = data + 32768
        #~ print "at12>", np.amin(data)
        return ("","","",""),data
    
def Fit2png(data,s0, s1, black=True):
    """ Returns the contrast enhaced array 
    """
    import numpy as np
    Height, Width = data.shape
    # Convert .FIT to PNG (int16 to uint8) with enhaced contrast.
    newarray = np.array(Image.new("L", (Width,Height), color=0)) 
    # auto equalization: s0=0.01  s1=0.0323
    # draft equalization: s0=0.0  s1=0.174
    amin, amax = np.amin(data), np.amax(data)
    delta = amax - amin
    i0 = amin + s0 * delta
    i1 = amin + s1 * delta
        
    t = -1.0 *(data-(i0+i1)/2)/(i1-i0)
    newarray = 255/(1+np.exp(t))
    if black:
        return (newarray - np.amin(newarray)).astype(np.uint8)
    else: return newarray.astype(np.uint8)
    

def Equalize(filefullname, dataonly=False, cutoff=50):
    """ If optional 'dataonly' is True, returns the Fit data array.
    Otherwise, returns the contrast enhaced array computed with
    the optional 'cutoff' value, in range(0,100).
    (bigger cutoff values results in sharper contrast )
    """
    hduList = fits.open(filefullname)
    data = hduList[0].data
    Height, Width = data.shape
    minVal = np.amin(data) 
    maxVal = np.amax(data)
    hduList.close()
    if dataonly: return data
    # Convert .FIT to PNG (int16 to uint8) with enhaced contrast.
    newarray = np.array(Image.new("L", (Width,Height), color=0)) 
    newarray = (data+cutoff*100)/255
    return newarray
    

    
def FindRefs(a, n=6):
    ''' where "a" is a np.array (the image) and "n" is an integer.
        Splits the image in n*n boxes and finds the relative maxs of each box.
        Returns a np.array (n*n, 2)
        Thus, (FindRefs(a)[j,0], FindRefs(a)[j,1]) is the argmax of box j.
''' 
    from numpy.lib.stride_tricks import as_strided as ast
    box = tuple(x/6 for x in a.shape)
    z=ast(a, \
          shape=(6,6)+box, \
          strides=(a.strides[0]*box[0],a.strides[1]*box[1])+a.strides)
    v3 = np.max(z,axis=-1)
    i3r = np.argmax(z,axis=-1)
    #~ v2 = np.max(v3,axis=-1)
    i2 = np.argmax(v3,axis=-1)
    i2x = np.indices(i2.shape)
    i3 = i3r[np.ix_(*[np.arange(x) for x in i2.shape])+(i2,)]
    i3x = np.indices(i3.shape)
    ix0 = i2x[0]*box[0]+i2
    ix1 = i3x[1]*box[1]+i3
    #~ return np.ravel(ix0), np.ravel(ix1) ,np.ravel(v2)
    return np.vstack((np.ravel(ix0), np.ravel(ix1))).T

def ChooseBestAlign(arr1,arr2,shifts):
    ''' where "arr1" and "arr2" are the images and "shifts" is an
        np.array (n,2) with the n shifts to try.
        Overlaps the shifted "arr2" over "arr1" -using Max- and 
        returns the best one. Asumes that the minimum Sum gives the best.
    '''
    # Descartar shifts grandes y Quitar shifts repetidos
    b = np.ascontiguousarray(shifts).view(np.dtype((np.void, shifts.dtype.itemsize * shifts.shape[1])))
    _, idx = np.unique(b, return_index=True)
    shifts = np.unique(b).view(shifts.dtype).reshape(-1, shifts.shape[1])
    
    shrows = len(shifts)    # agregar columna para poner suma
    shifts = np.c_[shifts,np.zeros((shrows, 1),dtype=np.uint8)]
    
    for n in range(0,shrows):
        arr2 = np.roll(arr2,shifts[n,1],axis=1)
        arr2 = np.roll(arr2,shifts[n,0],axis=0)
        ali = np.maximum(arr2, arr1)
        
        shifts[n,2] = ali.sum(dtype=np.uint32)  # poner suma en 3a. columna.
        
    # buscar min ali y retornar su [dy dx]
    return shifts[np.argmin(shifts,axis=0)[2], :2]
    
def hhmmss2s(s):
    ''' where s is "hh:mm:ss"
        Returns seconds as integer.
    '''
    ss = s.split(":")
    return 3600*int(ss[0]) + 60*int(ss[1]) + int(ss[2])
    
    ###############################################################
