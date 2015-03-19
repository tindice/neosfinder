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


def main():
    fitfolder = os.path.expanduser('~/Descargas/suleika_2/')
    tmpfolder = "./tmp/"
    t0 = dt.datetime.now()
    
    # 1) Verificar integridad de imagenes FIT :
    filelist = sorted(os.listdir(fitfolder[:-1]))
    #~ exclude = Checkfits(fitfolder, filelist, log=False)
    print
    print"Checkfits: ", dt.datetime.now()-t0

    # 2) Calcular alineación de imagenes FIT :
    print "aligning %s*.fit files..." %(fitfolder)
    t0 = dt.datetime.now()
    cant = 0
    for filename in filelist:
        update_progress(cant,len(filelist))
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
            pngsum = png
            png1 = png.copy()
            continue
            
        refs = FindRefs(data)
        draft = Fit2png(data,i0=1,i1=1,sharp=1) # draft equalization
        tn = ChooseBestAlign(draft1,draft,refs1-refs)
        Align.append(tn)
        #  Superponer imágenes :
        pngsum = np.maximum(Shift(png,dy=tn[0],dx=tn[1]), pngsum)
        draftsum = np.maximum(Shift(draft,dy=tn[0],dx=tn[1]), draftsum)
    
    print
    print"Aligning: ", dt.datetime.now()-t0
    
    # 3) Reconocer componentes sospechosos :
    im = Image.fromarray(draftsum)
    im.save(tmpfolder+"draft.png")
    dim = 25
    comp = [1,2]
    while dim>8 and len(comp) < 3:
        comp = recognize(tmpfolder+"draft.png", dim)
        print dim, len(comp)
        dim -= 1
    #~ comp = recognize(draftsum,17)
    print
    print len(comp), "Componentes:"
    if len(comp) == 0:
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
        xy = (x0-5,y0-5,x1+5,y1+5)
        ImageDraw.Draw(g).ellipse(xy, fill=None, outline=200)
        
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
    print
    print"Showing: ", dt.datetime.now()-t0
    os.system("eog %stmp.png"%(tmpfolder)) 
    #~ s0.save("%sSuma.png" %(tmpfolder) )


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

