#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  neofind.py
#  
#  Copyright 2015 Rodolfo Leibner <rleibner@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
'''     TODO: Breve descripción.
                Modo de uso.
'''
def rgbcircle(array,box):
    ''' where box=(y0, y1, x0, x1) is in np-style.
        Returns a resized RGB image from array 
        with an ellipse on box coords.
    '''
    r = Image.fromarray(array)
    g = r.copy()
    b = r.copy()
    im = Image.merge("RGB", (r,g,b))
    size = (array.shape[1]/2, array.shape[0]/2)
    im.thumbnail(size, Image.BICUBIC)

    (y0, y1, x0, x1) = box
    xy = (x0/2-5,y0/2-5,x1/2+5,y1/2+5)
    return ImageDraw.Draw(im).ellipse(xy, fill=None, outline=(0,200,0))


def main():
    fitfolder = os.path.expanduser('~/Descargas/suleika_2/')
    print "Procesing %s*.fit files..." %(fitfolder)
    tmpfolder = "./tmp/"
    t0 = dt.datetime.now()
    
    # 1) Verificar integridad de imagenes FIT :
    filelist = sorted(os.listdir(fitfolder[:-1]))
    #~ exclude = Checkfits(fitfolder, filelist, log=False)
    print
    print"Checkfits: ", dt.datetime.now()-t0

    # 2) Calcular alineación de imagenes FIT :
    print "Aligning images..." 
    t0 = dt.datetime.now()
    cant = 0
    for filename in filelist:
        update_progress(cant,len(filelist))
        print str(dt.datetime.now()-t0)[:-7],
        #~ if filename[-4:] != ".fit" or filename in exclude:
            #~ continue        # -- exclude file
    
        cant += 1
        f = fitfolder+filename
        meta, data = Getdata(f)
        png = Fit2png(data) # auto equalization
    # Uso primera imagen como base para alinear -----------
        if cant == 1:
            Align = []
            refs1 = FindRefs(data)
            draft1 = Fit2png(data,i0=1,i1=1,sharp=1) # draft equalization
            draftsum = draft1.copy()
            meta1 = meta
            #~ pngsum = png
            png1 = png.copy()
            continue
            
        refs = FindRefs(data)
        draft = Fit2png(data,i0=1,i1=1,sharp=1) # draft equalization
        tn = ChooseBestAlign(draft1,draft,refs1-refs)
        Align.append(tn)
        #  Superponer imágenes :
        #~ pngsum = np.maximum(Shift(png,dy=tn[0],dx=tn[1]), pngsum)
        draftsum = np.maximum(Shift(draft,dy=tn[0],dx=tn[1]), draftsum)
    
    print
    t0 = dt.datetime.now()
    print "Recognizing ... ",

    # 3) Reconocer componentes sospechosos :
    im = Image.fromarray(draftsum)
    im.save(tmpfolder+"draft.png")
    dim = 25
    comp = []
    while dim>8 and len(comp) < 1:
        comp = recognize(tmpfolder+"draft.png", dim)
        #~ print dim, len(comp)
        dim -= 1
    #~ comp = recognize(draftsum,17)
    #~ print len(comp), "Componentes:"
    if len(comp) == 0:
        print
        print "Nothing found."
        exit
    #~ print comp
    #~ size = (draftsum.shape[1]/2, draftsum.shape[0]/2)
    #~ s = Image.fromarray(pngsum)
    #~ s.thumbnail(size, Image.BICUBIC)
    #~ s.show()
    
    # 4) Reducir tamaño, poner colores y mostrar :
    #~ size = (png1.shape[1]/2, png1.shape[0]/2)
    s = Image.fromarray(png1)
    #~ s.thumbnail(size, Image.BICUBIC)
    
    r = s.copy()
    g = s.copy()
    
    for (y0, y1, x0, x1) in comp:
        #~ print "comp w, h=", x1-x0, y1-y0
        xy = (x0-10,y0-10,x1+10,y1+10)
        ImageDraw.Draw(g).ellipse(xy, fill=None, outline=200)
        trace = im.crop((x0,y0, x1,y1)) # tomo traza del draft
        g.paste(trace, (x0,y0, x1,y1))  # pego en verde
        
    ImageDraw.Draw(r).text((10, 10), "desde "+ meta1[0][:10]+"  "+
        meta1[0][11:], fill=190)
    ImageDraw.Draw(r).text((10, 25), "hasta "+ meta[0][:10]+"  "+
        meta[0][11:], fill=190)
        
    #~ stamptext(s0, (10, 10), "desde "+ metadict[filename1][0][:10]+"  "+
        #~ metadict[filename1][0][11:], color=190)
    #~ stamptext(s0, (10, 25), "hasta "+ metadict[filename][0][:10]+"  "+
        #~ metadict[filename][0][11:], color=190)
    b = r.copy()
    im = Image.merge("RGB", (r,g,b))
    im.save(tmpfolder+"tmp.png")
    print 40*" ", dt.datetime.now()-t0
    print 
    # Show image
    os.system("eog %stmp.png"%(tmpfolder)) 

    frames = raw_input("Save frames ? [y/n] ")
    if frames == "y" or frames == "Y":
        cada = raw_input("from %i fit images, save 1 in n.  n = " %(cant))
        s.save(tmpfolder+"frame_001.png")
        t0 = dt.datetime.now()
        print "Saving png frames ... "

        for f in range(1,len(filelist), cada):
            update_progress(f,len(filelist)/cada)
            print str(dt.datetime.now()-t0)[:-7],

            meta, data = Getdata(fitfolder+filelist[f])
            png = Fit2png(data) # auto equalization
            im = Image.fromarray(png)
    
        #~ TODO:
    return 0

if __name__ == '__main__':
    import numpy as np
    #~ from numpy.lib.stride_tricks import as_strided
    from PIL import Image , ImageDraw
    import os, datetime as dt
    from astrotools import *
    import cclabel as ccl
    from recognize import recognize, stamptext

    main()

