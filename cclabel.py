#!/usr/bin/python

#
# Implements 8-connectivity connected component labeling
# 
# Algorithm obtained from "Optimizing Two-Pass Connected-Component Labeling 
# by Kesheng Wu, Ekow Otoo, and Kenji Suzuki
#

import Image, ImageDraw

import sys, numpy as np
import math, random
from itertools import product
from ufarray import *

def findcomponent(lbldict,lblval):
    return [cords for cords,val in lbldict.iteritems() if val == lblval]

def run(img):
    data = img.load()
    width, height = img.size
 
    # Union find data structure
    uf = UFarray()
 
    #
    # First pass
    #
 
    # Dictionary of point:label pairs
    labels = {}
 
    for y, x in product(range(height), range(width)):
 
        #
        # Pixel names were chosen as shown:
        #
        #   -------------
        #   | a | b | c |
        #   -------------
        #   | d | e |   |
        #   -------------
        #   |   |   |   |
        #   -------------
        #
        # The current pixel is e
        # a, b, c, and d are its neighbors of interest
        #
        # 255 is white, 0 is black
        # Black pixels part of the background, so they are ignored
        # If a pixel lies outside the bounds of the image, it default to black
        #
 
        # If the current pixel is black, it's obviously not a component...
        if data[x, y] == 0:
            pass
 
        # If pixel b is in the image and white:
        #    a, d, and c are its neighbors, so they are all part of the same component
        #    Therefore, there is no reason to check their labels
        #    so simply assign b's label to e
        elif y > 0 and data[x, y-1] == 255:
            labels[x, y] = labels[(x, y-1)]
 
        # If pixel c is in the image and white:
        #    b is its neighbor, but a and d are not
        #    Therefore, we must check a and d's labels
        elif x+1 < width and y > 0 and data[x+1, y-1] == 255:
 
            c = labels[(x+1, y-1)]
            labels[x, y] = c
 
            # If pixel a is in the image and white:
            #    Then a and c are connected through e
            #    Therefore, we must union their sets
            if x > 0 and data[x-1, y-1] == 255:
                a = labels[(x-1, y-1)]
                uf.union(c, a)
 
            # If pixel d is in the image and white:
            #    Then d and c are connected through e
            #    Therefore we must union their sets
            elif x > 0 and data[x-1, y] == 255:
                d = labels[(x-1, y)]
                uf.union(c, d)
 
        # If pixel a is in the image and white:
        #    We already know b and c are black
        #    d is a's neighbor, so they already have the same label
        #    So simply assign a's label to e
        elif x > 0 and y > 0 and data[x-1, y-1] == 255:
            labels[x, y] = labels[(x-1, y-1)]
 
        # If pixel d is in the image and white
        #    We already know a, b, and c are white
        #    so simpy assign d's label to e
        elif x > 0 and data[x-1, y] == 255:
            labels[x, y] = labels[(x-1, y)]
 
        # All the neighboring pixels are black,
        # Therefore the current pixel is a new component
        else: 
            labels[x, y] = uf.makeLabel()
 
    #
    # Second pass
    #
 
    uf.flatten()
 
    colors = {}
    
    # Image to display the components in a nice, colorful way
    output_img = Image.new("RGB", (width, height))
    outdata = output_img.load()

    for (x, y) in labels:
 
        # Name of the component the current point belongs to
        component = uf.find(labels[(x, y)])

        # Update the labels with correct information
        labels[(x, y)] = component
 
        # Associate a random color with this component 
        if component not in colors: 
            colors[component] = (random.randint(0,255), random.randint(0,255),random.randint(0,255))
        #~ if component == 12:
            #~ colors[component] = (255, 100,100)  # RGB
        #~ else:
            #~ colors[component] = (255, 255,255)  # RGB

        # Colorize the image
        outdata[x, y] = colors[component]
    
    
    #~ C12 = findcomponent(labels,12)  # lista de pixels etiquetados 12
    #~ xx, yy = [], []
    #~ for (x,y) in C12:
        #~ xx.append(x)
        #~ yy.append(y)
    #~ x0 = min(xx)
    #~ x1 = max(xx)
    #~ y0 = min(yy)
    #~ y1 = max(yy)
    #~ print np.asarray(data)[y0:y1,x0:x1]
    #~ vals = labels.values()
    #~ histo = list([(x, vals.count(x)) for x in set(vals)])
    #~ print histo
    #~ raw_input("...")

    return (labels, output_img)

def bw(img):
    img = img.point(lambda p: p > 200 and 255)
    return img.convert('1')
	
def main():
    # Open the image
    #~ img = Image.open(sys.argv[1])
    img = Image.open("/home/rodolfo/neosfinder/1 a 041.png")

    # Threshold the image, this implementation is designed to process b+w
    # images only
    img = img.point(lambda p: p > 190 and 255)
    img = img.convert('1')
    #~ img.show()
    # labels is a dictionary of the connected component data in the form:
    #     (x_coordinate, y_coordinate) : component_id
    #
    # if you plan on processing the component data, this is probably what you
    # will want to use
    #
    # output_image is just a frivolous way to visualize the components.
    #~ (labels, output_img) = run(img)
    (labels, output_img) = run(img)
    output_img.save("a41.png")

    #~ output_img.show()

if __name__ == "__main__": main()
