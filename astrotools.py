#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  pyfits as pyf, numpy as np
from PIL import Image, ImageOps
import os, math

#~ def Choosebest(f,bins,histox=[0,0,0,0,0,0,0,0,0,0],histoy=[0,0,0,0,0,0,0,0,0,0]):
	#~ import numpy as np
	#~ d = []
	#~ h = histox+histoy
	#~ leng = len(h)
	#~ for n in range(0,leng):
		#~ if h[n] != 0:
			#~ d.append(int(0.5+bins[n]))
	#~ print "d =", d
	#~ for dx in range(0,len(d)):
		#~ Shift(data,dx=dx) y pruebo.
	#~ return

def Putcross(array,refs,t=10):
	''' Put crosses on the image array.
		Uses the list refs=[(x0,y0),...,(xn,yn)] to center each cross.
		Returns the modified array '''
	a = array.astype(np.uint8)
	# Cross array definition
	lum = np.max(array)
	#~ lum = 255
	#~ t = 20	# cross size= 2*t+1
	cros = np.zeros((2*t+1,2*t+1),dtype=np.uint8)
	cros[:t-3,t] = cros[t+4:,t] = lum
	cros[t,:t-3] = cros[t,t+4:] = lum
	#~ print cros
	for pt in range(0,len(refs)):
		ptx = refs[pt][0]
		pty = refs[pt][1]
		#~ if array[pty-9:pty+10,ptx-9:ptx+10].shape == (19,19):
		if (ptx>=t and ptx<a.shape[1]-t) and (pty>=t and pty<a.shape[0]-t):
			if a[pty,ptx] > 150:
				#~ a[pty-t:pty+t+1,ptx-t:ptx+t+1] ^= cros
				a[pty-t:pty+t+1,ptx-t:ptx+t+1] = np.maximum(a[pty-t:pty+t+1,ptx-t:ptx+t+1],cros)
	return a
	
def update_progress(progress, total):
    print '\r[{0}] {1}%'.format('#'*(progress/5)+" "*(40-progress/5), progress*100/total),

def Pause(msg="Enter to cont, Ctrl-C to exit: "):
	raw_input(msg)

def Checkfits(filelist):
	print "\r Checking ..."
	cant = 0
	exclude = []
	for f in filelist:
		cant += 1
		update_progress(cant,len(filelist))
		data = Getdata(f)
		mean = int(np.mean(data))
		std = int(np.std(data))
		var = int(np.var(data))
		if cant == 1:
			mean1 = mean
			std1 = std
			var1 = var
		if mean<mean1/2 or mean>mean1 *10:
			exclude.append(f)
			print "\nWarning: image %s" %(f)
	print "\n"
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
	#~ print filefullname+":"
	#~ print data
	return data
    
def Fit2png(data,i0=10000, i1=16000, sharp=1.8):
	""" Returns the contrast enhaced array 
	"""
	import numpy as np
	Height, Width = data.shape
	#~ print data
	# Convert .FIT to PNG (int16 to uint8) with enhaced contrast.
	newarray = np.array(Image.new("L", (Width,Height), color=0)) 
	t = -sharp *(data-(i0+i1)/2)/(i1-i0)
	#~ print t
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
	#~ print sfi,x0,y0,x1,y1
	col, row = np.unravel_index(sfi, (y1-y0, x1-x0))
	#~ print "sfi =", sfi, " -->", row,col
	return x0+row,y0+col

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
	
def FindRefs(filename, boxes=8):
	""""
	Search references, the lightest	point on each box (there are boxes^2 boxes)
	Returns the list [(x0,y0),...,(xn,yn)] with the coords
	of the found references.
	Also accepts an np.array instead of "filename".
	"""
	a = Getdata(filename)
	Height, Width = a.shape

	plumx = []
	plumy = []
	lum = []
	boxes = 8	# boxes^2 boxes
	w = int(Width/boxes)
	h = int(Height/boxes)
	dd = 4	# pixels de separación entre boxes
	#~ dmax = 20 # diam max de estrellas ref.
	
	for n in range(0,boxes):	# recorrer boxes
		x0 = n*w+dd
		x1 = (n+1)*w-dd
		for m in range(0,boxes):
			y0 = m*h+dd
			y1 = (m+1)*h-dd
			subflatind = a[y0:y1,x0:x1].argmax() # flatten indice del box!
			X,Y = XYind(subflatind,x0,y0,x1,y1)	# indices de a
			
			#~ if a[Y,X] > 8000:
			lum.append(a[Y,X])
			plumx.append(X)
			plumy.append(Y)
			#~ print "en (%i , %i)"%(X,Y), a[Y,X]

	#~ print len(plumx), "detectadas."
	
	refs = []
	for pt in range(0,len(plumx)):
		ptx = plumx[pt]
		pty = plumy[pt]
		refs.append((ptx,pty,lum[pt]))
	return refs
	###############################################################
