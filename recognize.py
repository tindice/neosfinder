#!/usr/bin/env python
# -*- coding: utf-8 -*-

def stamptext(img, pos, txt, color=(0,100,0)):
    ''' 
    '''
    import numpy as np, Image, ImageDraw
    import cclabel as ccl
    import astrotools as at
    
    draw = ImageDraw.Draw(img)
    draw.text(pos,txt, fill=color)
    return
    
def recognize(image, mindim=15):
    ''' where "image" is an imagefile or a np.array.
        Finds the Conected Components on the image and
        returns a list with the box coords of the filiform ones.
    '''
    import numpy as np, Image
    import cclabel as ccl
    import astrotools as at
    
    if 'numpy.ndarray' in str(type(image)):
        e = Image.fromarray(image)
    else:
        e = Image.open(image)
    if mindim < 8: return []
    img = ccl.bw(e)
    (labels, output_img) = ccl.run(img)
    png = np.array(img.getdata(),
             np.uint8).reshape(img.size[1], img.size[0])
    
    vals = labels.values()
    histo = np.array(list([(x, vals.count(x)) for x in set(vals)]))
    suspicious = []
    for n in range(0, len(histo)): 
        lbl = histo[n,0]
        Comp = ccl.findcomponent(labels,lbl)  # lista de pixels del componente lbl
        maxs = map(max, zip(*Comp))   
        mins = map(min, zip(*Comp))
        x0, x1, y0, y1 = mins[0], maxs[0], mins[1], maxs[1]
        
        # Descarto componentes pequeños:
        if (x1-x0+y1-y0) < mindim: continue
        # y descarto componentes no filiformes:
        #~ print "ul ",png[y0:y0+2,x0:x0+2]
        #~ print "ur ",png[y0:y0+2,x1-2:x1]
        #~ print "ll ",png[y1-2:y1,x0:x0+2]
        #~ print "lr ",png[y1-2:y1,x1-2:x1]
        #~ print
        
        if (png[y0:y0+2,x0:x0+2].sum(dtype=np.uint16)
          + png[y0:y0+2,x1-2:x1].sum(dtype=np.uint16) 
          + png[y1-2:y1,x0:x0+2].sum(dtype=np.uint16) 
          + png[y1-2:y1,x1-2:x1].sum(dtype=np.uint16)<255*4): continue 
        #~ print png[y0:y1+1,x0:x1+1]
        #~ Pause(str(lbl))
        suspicious.append((y0, y1, x0, x1))
    
    return suspicious
