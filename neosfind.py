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
            Align = {}  # Diccionario "filename : (dy,dx)"
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
        Align[filename] = tn
        
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

    if len(comp) == 0:
        print
        print "Nothing found."
        exit
    
    # 4) Poner colores y mostrar :
    s = Image.fromarray(png1)
    r = s.copy()
    g = s.copy()
    
    for (y0, y1, x0, x1) in comp:
        xy = (x0-10,y0-10,x1+10,y1+10)
        ImageDraw.Draw(g).ellipse(xy, fill=None, outline=200)
        trace = im.crop((x0,y0, x1,y1)) # tomo traza del draft
        g.paste(trace, (x0,y0, x1,y1))  # pego en verde
        
    ImageDraw.Draw(r).text((10, 10), "desde "+ meta1[0][:10]+"  "+
        meta1[0][11:], fill=190)
    ImageDraw.Draw(r).text((10, 25), "hasta "+ meta[0][:10]+"  "+
        meta[0][11:], fill=190)

    b = r.copy()
    im = Image.merge("RGB", (r,g,b))
    im.save(tmpfolder+"tmp.png")
    print 30*" "+str(dt.datetime.now()-t0)[:-7]
    print 
    # Show image
    print "Found !"
    print "Showing draft: (close your viewer to continue)"
    print
    os.system("eog %stmp.png"%(tmpfolder)) 

    # 5) Generar frames :
    frames = raw_input("Save frames ? [y/n] ")
    if frames == "y" or frames == "Y":
        cada = int(raw_input("  From %i fit images, save 1 in n:  n = " %(cant)))
        txt0 = ((5,5),"obs.: "+ meta1[0][:10],"YELLOW")
        # posicion inicial:
        (y0, y1, x0, x1) = comp[0]
        i,j = np.unravel_index(png1[y0:y1,x0:x1].argmax(), png1[y0:y1,x0:x1].shape)
        # posicion final:
        png = Shift(draft,dy=tn[0],dx=tn[1])
        u,v = np.unravel_index(png[y0:y1,x0:x1].argmax(), png[y0:y1,x0:x1].shape)
        # posiciones para textos:
        if i>u:
            inic = (x0+j, y1+15)
            fin = (x0+v, y0-30)
        else:
            inic = (x0+j, y0-30)
            fin = (x0+v, y1+15)
            
        txt1 = (inic, " from "+ meta1[0][11:], "ORANGE")
        txt2 = (fin, " to "+ meta[0][11:], "ORANGE")
        rgb = Array2rgb(png1,comp,[txt0,txt1] )
        rgb.save(tmpfolder+"frame_001.png")
        os.system("optipng -o2 -q %sframe_001.png"%(tmpfolder)) 
        t0 = dt.datetime.now()
        print "Saving png frames ... "

        z = "000"
        n = 1
        for f in range(cada,cant, cada):
            update_progress(f,cant)
            print str(dt.datetime.now()-t0)[:-7],

            meta, data = Getdata(fitfolder+filelist[f])
            png = Fit2png(data) # auto equalization
            # get shift
            tn = Align[filelist[f]]
            png = Shift(png,dy=tn[0],dx=tn[1])
            # get number
            #~ nr = filelist[f][-7:-4]
            # choose text
            if f < cant/2 :
                rgb = Array2rgb(png,comp,[txt0,txt1] )
            else:
                rgb = Array2rgb(png,comp,[txt0,txt2] )
            
            n += 1
            rgb.save(tmpfolder+"frame_%s.png" %((z+str(n))[-3:]))
            os.system("optipng -o2 -q %sframe_%s.png"%(tmpfolder,(z+str(n))[-3:])) 
        print
    print "Done."

    # 6) Generar animacion :
    anim = raw_input("Make animation.apng ? [y/n] ")
    if anim == "y" or anim == "Y":
        print
        print "Making animation ...",
        t0 = dt.datetime.now()
        os.system("apngasm anima.png ./tmp/frame_001.png 1 4")
        print 26*" "+str(dt.datetime.now()-t0)[:-7]
        print "Done. You can view anima.png with Firefox browser."
        
    return 0

if __name__ == '__main__':
    import numpy as np
    from PIL import Image , ImageDraw
    import os, datetime as dt
    from astrotools import *
    from recognize import recognize

    main()

