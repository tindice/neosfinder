#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  pyfits as pyf, numpy as np
from PIL import Image, ImageOps
import os, math


def Putcross(array,refs,t=10):
	''' Put crosses on the image array. ( Cross size= 2*t+1 )
		Uses the list refs=[(x0,y0),...,(xn,yn)] to center each cross.
		Returns the modified array '''
	a = array.astype(np.uint8)
	# Cross array definition
	lum = np.max(array)
	cros = np.zeros((2*t+1,2*t+1),dtype=np.uint8)
	cros[:t-3,t] = cros[t+4:,t] = lum
	cros[t,:t-3] = cros[t,t+4:] = lum
	for pt in range(0,len(refs)):
		ptx = refs[pt][0]
		pty = refs[pt][1]
		if (ptx>=t and ptx<a.shape[1]-t) and (pty>=t and pty<a.shape[0]-t):
			if a[pty,ptx] > 150:	# luminosidad digna
				a[pty-t:pty+t+1,ptx-t:ptx+t+1] = np.maximum(a[pty-t:pty+t+1,ptx-t:ptx+t+1],cros)
	return a
	
def update_progress(progress, total):
    print '\r[{0}] {1}%'.format('#'*(progress/5)+" "*(40-progress/5), progress*100/total),

def Pause(msg="Enter to cont, Ctrl-C to exit: "):
	raw_input(msg)

def Checkfits(path, filelist, mean_criteria=(0.5,10), uprogress=True, log=True):
	print "\r Checking Fitfiles integrity ..."
	
	means = {f:int(np.mean(Getdata(path+f))) for f in filelist}
	mean = means[filelist[0]]
	exclude = [f for f in filelist if means[f]<mean*mean_criteria[0] or means[f]>mean*mean_criteria[1]]
	
	if log:
		checklog = open("./check.log", "w")
		checklog.write("File%s\tmean\tstd\tvar\n" %(spc))
		spc = " " * (len(filelist[0]) - 4)
		cant = 0
		for f in filelist:
			cant += 1
			if uprogress: update_progress(cant,len(filelist))
			checklog.write("%s\t%i\t%i\t%i\n" %(f,int(np.mean(Getdata(path+f))),int(np.std(Getdata(path+f))),int(np.var(Getdata(path+f)))))
		checklog.close()
		if uprogress: print "\n"
	
	return exclude

def Shift(array,dx=0,dy=0):
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
	
def Getdata(filefullname):
	""" Returns the Fit data array.
	"""
	if type(filefullname) == type('str'):
		hduList = pyf.open(filefullname)
		data = hduList[0].data
		hduList.close()
	else:
		data = filefullname.copy()
	return data
    
def Fit2png(data,i0=10000, i1=16000, sharp=1.8):
	""" Returns the contrast enhaced array 
	"""
	import numpy as np
	Height, Width = data.shape
	# Convert .FIT to PNG (int16 to uint8) with enhaced contrast.
	newarray = np.array(Image.new("L", (Width,Height), color=0)) 
	t = -sharp *(data-(i0+i1)/2)/(i1-i0)
	newarray = 255/(1+np.exp(t))
	return newarray - np.amin(newarray)
    
def Savepng(name,data,i0=10000, i1=16000, sharp=1.8):
	''' 
	"name" without extension
	'''
	png = Fit2png(data,i0,i1,sharp).astype(np.uint8)
	e = Image.fromarray(png)
	pngfolder = "./equalized/"
	e.save(pngfolder+name+".png")

def Equalize(filefullname, dataonly=False, cutoff=50):
	""" If optional 'dataonly' is True, returns the Fit data array.
	Otherwise, returns the contrast enhaced array computed with
	the optional 'cutoff' value, in range(0,100).
	(bigger cutoff values results in sharper contrast )
	"""
	hduList = pyf.open(filefullname)
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
    

def XYind(sfi,x0,y0,x1,y1):
	""" Returns both indexes X,Y of an array,
	#  from the SubarrayFlatenIndex of the box(x0,y0,x1,y1)
	"""
	y, x = np.unravel_index(sfi, (y1-y0, x1-x0))
	return x0+x,y0+y

def Distances(refs):
	""""
	The "refs" parameter is a list [(x0,y0),...,(xn-1,yn-1)] with n tuples.
	Returns the list [d0,...,dm-1] with m elements, where m=(n-1)n/2
	Each element d is the square of the distance between 2 tuples. 
	"""
	#~ print "refs =",refs
	n = len(refs)
	L = []
	for i in range(0,n):
		for j in range(i+1,n-1):
			print refs[i][0],refs[j][0],"   ",refs[i][1],refs[j][1]
			d = (refs[i][0]-refs[j][0])^2 + (refs[i][1]-refs[j][1])^2
			L.append(d)
	return L
	
def FindRefs2(filename, boxes=8):
	""""
	Search references, the lightest	point on each box (there are boxes^2 boxes)
	Returns the list [(x0,y0,l0),...,(xn,yn,ln)] with the coords and lum
	of the found references.
	Also accepts an np.array instead of "filename".
	"""
	a = Getdata(filename)
	Height, Width = a.shape

	plumx = []
	plumy = []
	lum = []
	w = int(Width/boxes)
	h = int(Height/boxes)
	
	box = [(n*w,m*h) for n in range(0,boxes) for m in range(0,boxes)]
	flatinds = [a[b[1]:h+b[1],b[0]:w+b[0]].argmax() for b in box]
	unravels = np.unravel_index(flatinds, (h, w))
	ur = [(unravels[1][n],unravels[0][n]) for n in range(0,len(box))]
	#~ print "box",box
	#~ print "ur",ur
	absinds = [map(sum,zip(box[n],ur[n])) for n in range(0,len(box))]
	refs = [(absinds[n][0],absinds[n][1],a[absinds[n][1],absinds[n][0]]) for n in range(0,len(box))] 
	#~ print "refs",refs
	#~ Pause()
	return refs
	
def FindRefs(a):
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
    #~ print np.ravel(ix0)
    #~ res = zip(np.ravel(ix0),np.ravel(ix1),np.ravel(v2))
    #~ res = zip(np.ravel(ix0),np.ravel(ix1))
    #~ print res
    #~ Pause()
    return np.ravel(ix0), np.ravel(ix1)

	###############################################################
