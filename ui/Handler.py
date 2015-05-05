#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image , ImageDraw, ImageChops
from astrotools import *
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from math import log1p, exp
import threading

# =======   Functions Section  ========================================

#~ def ViewDefault(gui):
    #~ ''' Restores View parameters and inicialize Metadata Viewer.
    #~ '''
    #~ gui.ViewZoom = 1
    #~ gui.ViewRotate = 0
    #~ gui.ViewFlipH = False
    #~ gui.ViewFlipV = False
    #~ 
    #~ gui.metaviewer.hide()

def Zoom(gui, k):
    #~ k = 1.25
    gui.ViewZoom *= k
    #~ print "VZ", gui.ViewZoom
    if k == 1:
        pxb = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    elif k > 1:
        pb = gui.imagen.get_property("pixbuf")
        src_x = (1-1/k)/2 * pb.get_height()
        src_y = (1-1/k)/2 * pb.get_width()
        # crops from pixbuf
        spb = pb.new_subpixbuf(int(src_x), int(src_y),
                  int(pb.get_width()/k) , int(pb.get_height()/k))
          # amplify
        pxb = spb.scale_simple(pb.get_width(), pb.get_height(),
                             GdkPixbuf.InterpType.BILINEAR)
    else:
        pb = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
        src_x = (1-1/gui.ViewZoom)/2 * pb.get_height()
        src_y = (1-1/gui.ViewZoom)/2 * pb.get_width()
        sub_w = pb.get_width()/gui.ViewZoom
        sub_h = pb.get_height()/gui.ViewZoom
        # crops from pixbuf
        spb = pb.new_subpixbuf(int(src_x), int(src_y),
                  int(sub_w) , int(sub_h))
          # amplify
        pxb = spb.scale_simple(pb.get_width(), pb.get_height(),
                             GdkPixbuf.InterpType.BILINEAR)
      # and apply
    gui.imagen.set_property("pixbuf", pxb)

def Sigmoid(h,s0,s1):
    '''  Toma la imagen h (np.array) y le superpone la
         sigmoide segun s0,s1.
    '''
    g = h.copy()
    a = (s0+s1)*637.5
    b = (s1-s0)*1275.0
    if b != 0:
        Sprev = 0
        for x in range(256):
            S = 100 / (1+ exp((a-x) / b))
            if abs(S-Sprev) > 1:
                g[min(99-S,99-Sprev):max(99-S,99-Sprev),x] = 90
            else:    
                g[99-S,x] = 90
            Sprev = S
    return g

def UpdateSigmoid(gui):
    h = Sigmoid(gui.arrHistogram,s0 = gui.adjmin.get_property("value")/500,
                                 s1 = gui.adjmax.get_property("value")/500)
    im = Image.fromarray(h)
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    gui.histo.set_property("pixbuf", pixbuf)

def ShowImage(gui, im):
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    gui.imagen.set_property("pixbuf", pixbuf)
    return True

def ShowEqualized(gui, file, s0=0 , s1=0):
    ''' accepts "file" as string or as np.array
    '''
    print "3"
    gui.spinner.start()
    # toogle   GTK_SHADOW_ETCHED_OUT / GTK_SHADOW_ETCHED_IN
    gui.frame.set_shadow_type(3+gui.frame.get_shadow_type()%2)
    #~ screenHeight = gui.window.get_property("default_height")
    if s0 == 0:
        s0=gui.automin/500
        s1=gui.automax/500

    if type(file) == type("str"):    # gets image data from file:
        #~ print "file",file
        meta, gui.data = Getdata(file)
        #~ print meta
        if gui.ViewFlipH:
            gui.data = np.fliplr(gui.data)
        if gui.ViewFlipV:
            gui.data = np.flipud(gui.data)
        if gui.ViewRotate != 0:
            gui.data = np.rot90(gui.data, gui.ViewRotate)
        k = gui.ViewZoom
        if k > 1: # si voy a ampliar
            (h,w) = gui.data.shape
            x0,y0 = w*(1-1/k)/2, h*(1-1/k)/2
            x1,y1 = w*(k+1)/2/k, h*(k+1)/2/k
            gui.data = gui.data[y0:y1, x0:x1]  # crop array

    png = Fit2png(gui.data,s0, s1)
    k = 0.75 * gui.window.get_property("default_height") / png.shape[0]
    size = tuple(x*k for x in png.shape)
    im = Image.fromarray(png)
    im.thumbnail((size[1],size[0]), Image.BICUBIC)
    arr = np.array(im.getdata()).flatten()
    if file in gui.align.keys():
        (dy,dx) = gui.align[file]
        #~ png = Shift(png,dx,dy)
        im = ImageChops.offset(im,dx,dy)

# TODO: 
    im.save("../tmp/tmp.png")
    if file == gui.fitlist[0]: # si primera imagen,
        gui.im_0 = im           # guardar
    gui.im_actual = im
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    #~ im = im.convert("RGB")
    #~ pixbuf = GdkPixbuf.Pixbuf.new_from_data(arr,
     #~ GdkPixbuf.Colorspace.RGB, False, 8, size[1], size[0], 3*size[1])
     
    #~ # resize slider:
    gui.adjselfit.set_property("upper", len(gui.fitlist))
    gui.selfit.set_property("visible", True)
    # show imge: 
    gui.imagen.set_property("pixbuf", pixbuf)
    if type(file) == type("str"):
        idx = file.rfind("/")
        gui.window.set_property("title",
            "Neosfinder   -   ( %s )\t   %i de %i."%(file[idx+1:],
             1+gui.fitlist_n, len(gui.fitlist)))
    
        # calc arrHistogram:
        v,_ = np.histogram(gui.data,range=(0,65500),bins=256)
        h = np.zeros((100,256), dtype=np.uint8)
        for x in range(256):
            if v[x] != 0:
                b =min(100,7*log1p(v[x]))
                h[-b:,x] = 255
        # draw frame borders:
        h[0,:]=h[99,:]=h[:,0]=h[:,255] = 90 # ligth grey
        gui.arrHistogram = h
        
    # update Metadata viewer:
        if gui.metaviewer.rows == 1:
            #~ print "cero"
            gui.metaviewer.setkeys(gui.metalist[gui.fitlist_n],gui.DifKlist,gui.ConKlist)
            gui.metaviewer.show_all()
        else:
            gui.metaviewer.updatekeys(gui.metalist[gui.fitlist_n],gui.DifKlist)
        
    gui.spinner.stop()

    return  True

def ShowAlign(gui, dx=0, dy=0):
    print "ShowAlign", dx,dy
    im1 = ImageChops.offset(gui.im_actual,dx,dy)
    im = Image.merge("RGB", (gui.im_0,im1,gui.im_0))
    ShowImage(gui,im)
    return True
    


# ====================================================================

# ====  Handlers Section    ===================================

def on_notyet(self,menuitem):
    self.msgdialog.run()
    
def on_msgdialog_response(self,widget, data=None):
    widget.destroy()
    
def on_dlgMeta_response(self,widget, data=None):
    if data == 0:
        widget.hide()
    
def gtk_main_quit(self, menuitem, data=None):
    
    Gtk.main_quit()

def on_mnuEqualize(self, menuitem, data=None):
    on_dlgEqualize_realize(self, menuitem)
    self.equadialog.show()
        
def on_dlgEqualize_realize(self, obj):
    print "Realizo",self.histo.get_property("pixbuf")
    # show histogram with sigmoid:
    h = Sigmoid(self.arrHistogram,self.adjmin.get_property("value")/500,self.adjmax.get_property("value")/500)
    im = Image.fromarray(h)
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    self.histo.set_property("pixbuf", pixbuf)
    #~ if self.msg == 0:
        #~ self.msg = 1
    if self.histo.get_property("pixbuf") == None:
        print "Nunca pasare por aca !"
        self.chkauto.set_active(True)
    
def on_dlgEqualize_response(self, widget, btnID=None):
    if btnID == 1:   # Apply button pressed.
        ShowEqualized(self,self.data, s0 = self.adjmin.get_property("value")/500,
                            s1 = self.adjmax.get_property("value")/500)
    else:
        widget.hide()
        
def on_dlgAlinear_response(self, widget=None, btnID=None):
    if btnID == 1:   # Apply button pressed.
        ShowAlign(self, dx=int(self.adjdx.get_property("value")),
                        dy=int(self.adjdy.get_property("value")))
    else:
        self.dlgalinear.hide()
        
def on_chkAuto_toggled(self, menuitem, data=None):
    if self.chkauto.get_active():
        self.adjmin.set_property("value", self.automin)
        self.adjmax.set_property("value", self.automax)
          
def on_adjmin_value_changed(self, obj):
    if self.msg == 0:  return
    if self.adjmin.get_property("value") > self.adjmax.get_property("value"):
        self.adjmin.set_property("value", self.adjmax.get_property("value")-1)
    UpdateSigmoid(self)
    
def on_adjmax_value_changed(self, obj):
    if self.msg == 0:  return
    if self.adjmax.get_property("value") < self.adjmin.get_property("value"):
        self.adjmax.set_property("value", self.adjmin.get_property("value")+1)
    UpdateSigmoid(self)
    
    
def on_scale_release(self, obj, data):
    if self.chkauto.get_active():
        self.chkauto.set_active(False)

def on_mnuDetectar(self, menuitem, data=None):
    pass
                
def on_mnuRotar(self, menuitem, data=None):
    #~ self.data = np.rot90(self.data)
    #~ UpdateEqualized(self)
    pb = self.imagen.get_property("pixbuf").rotate_simple(90)
    self.imagen.set_property("pixbuf", pb)
    if self.ViewRotate == 3:
        self.ViewRotate = 0
    else:
        self.ViewRotate += 1
    
def on_mnuVoltearH(self, menuitem, data=None):
    pb = self.imagen.get_property("pixbuf").flip(True)
    self.imagen.set_property("pixbuf", pb)
    self.ViewFlipH = not self.ViewFlipH
    
def on_mnuVoltearV(self, menuitem, data=None):
    pb = self.imagen.get_property("pixbuf").flip(False)
    self.imagen.set_property("pixbuf", pb)
    self.ViewFlipV = not self.ViewFlipV
    
def on_mnuZoomU(self, menuitem, data=None):
    Zoom(self, 1.25)
              
def on_mnuMeta(self, menuitem, data=None):
    if self.fitlist != []:
        self.metaviewer.set_visible(not self.metaviewer.get_visible())
    
def on_mnuZoomD(self, menuitem, data=None):
    if self.ViewZoom < 1.25 : return
    Zoom(self, 1/1.25)
              
def on_mnuAcercaDe(self, menuitem, data=None):
    self.response = self.aboutdialog.run()
    
def on_about_closebutton_release(self, menuitem, data=None):
    self.aboutdialog.close()

def on_mnuAbrirFits(self, menuitem, data=None):
    self.fitchooser.set_default_response(1)
    self.fitchooser.run()

def on_mnuAlinear(self, menuitem, data=None):
    if self.fitlist_n == 0:
        Gtk.MessageDialog(text = "La primera imagen ya está alineada.").run()
        return True
    dx, dy = 0, 0
    if self.fitlist[self.fitlist_n] in self.align.keys():
        dy, dx = self.align[self.fitlist[self.fitlist_n]]
        self.adjdx.set_property("value", dx)
        self.adjdy.set_property("value", dy)
    #~ on_dlgAlinear_response(self,btnID=1)
    self.dlgalinear.run()
        
def on_mnuAlinearTodas(self, menuitem, data=None):
    for f in self.fitlist:
        _, data = Getdata(f)
        png = Fit2png(data, s0 = self.adjmin.get_property("value")/500,
                            s1 = self.adjmax.get_property("value")/500)
        if f == self.fitlist[0]:
            # Uso primera imagen como base para alinear:
            refs1 = FindRefs(data)
            #~ draft1 = Fit2png(data,i0=1,i1=1,sharp=1) # draft equalization
            pngsum = png.copy()
            #~ meta1 = meta
            #~ obs = meta1[1]+"_"+meta1[0][:10]
            png1 = png.copy()
            e = float(self.im_0.size[0])/png1.shape[1] # escala
            continue
            
        if f in self.align.keys():
            tn = self.align[f]
        else:
            refs = FindRefs(data)
            tn = ChooseBestAlign(png1,png,refs1-refs) * e
            self.align[f] = tuple(int(round(x)) for x in tn)
        #  Superponer imágenes :
        pngsum = np.maximum(Shift(png,dy=tn[0]/e,dx=tn[1]/e), pngsum)

    print self.align
    # mostrar superposicion:
    k = 0.75 * self.window.get_property("default_height") / pngsum.shape[0]
    size = tuple(x*k for x in pngsum.shape)
    im = Image.fromarray(pngsum)
    im.thumbnail((size[1],size[0]), Image.BICUBIC)
    
    #----------- poner colores
    redblue = im.copy()
    green = Image.fromarray(png1)
    green.thumbnail((size[1],size[0]), Image.BICUBIC)
    im = Image.merge("RGB", (redblue,green,redblue))
    #-----------

    ShowImage(self,im)
    self.window.set_property("title","Neosfinder - ( Todas alineadas )")

    
def on_fitchooserdialog_response(self, obj, btnID=-1):
    if btnID == 1:
        self.initialize()
        #~ watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        #~ self.window.get_window().set_cursor(watch_cursor)
        #~ GObject.threads_init()
        #~ Gdk.threads_init()
        def otrohilo():
            self.fitlist = sorted(self.fitchooser.get_filenames())
            print self.fitlist
            if self.fitlist == []: return
            
            self.metaviewer.cleanme() # reiniciarlo
            # lista de diccionarios metadata:
            self.metalist = list(GetMeta(f) for f in self.fitlist)
            #~ # lista de registros variables:
            #~ diflist = list(set(self.metalist[0].items()) ^ set(self.metalist[1].items()))
            #~ self.DifKlist = []  
            self.ConKlist = list(k for k in self.metalist[0].keys())

            if len(self.fitlist) > 1:
                for f in self.fitlist[1:]:
                    meta = GetMeta(f)
                    diflist = list(set(self.metalist[0].items()) ^ set(meta.items()))
                    difKlist=list(set(list(x[0] for x in diflist)))
                    self.DifKlist.extend(difKlist)
                self.DifKlist=list(set(self.DifKlist))  # lista de claves variable unique
                for key in self.DifKlist:
                    self.ConKlist.remove(key)
    
            #~ print "DifKlist", self.DifKlist
            #~ print "ConKlist", self.ConKlist
            
            #~ self.metaviewer.close()
            #~ self.metaviewer = dv.DataViewer()
                
            #~ print self.fitlist
            ShowEqualized(self, self.fitlist[0])
    
            #~ def done():
                #~ self.window.get_window().set_cursor(None)
                #~ return False
#~ 
#~ 
            #~ GObject.idle_add(done)
            #~ 
        #~ thread = threading.Thread(target=otrohilo)
        #~ thread.start()
        otrohilo()
    #~ print "volvi con", self.fitlist_n, self.fitlist
        
    if len(self.fitlist) > 1:
        for btn in (self.first, self.next, self.prev, self.last):
            btn.set_property("visible",True)
            
        self.first.set_sensitive(False)
        self.prev.set_sensitive(False)
        self.next.set_sensitive(True)
        self.last.set_sensitive(True)

    self.fitchooser.hide()
    

def on_btnFirst_clicked(self,button):
    self.fitlist_n = 0
    ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    s0 = self.adjmin.get_property("value")/500,
                    s1 = self.adjmax.get_property("value")/500)
    for btn in (self.first,self.prev):
        btn.set_sensitive(False) 
    for btn in (self.next,self.last):
        btn.set_sensitive(True) 
    
    
def on_btnLast_clicked(self,button):
    self.fitlist_n = len(self.fitlist)-1
    #~ UpdateEqualized(self)
    ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    s0 = self.adjmin.get_property("value")/500,
                    s1 = self.adjmax.get_property("value")/500)
    for btn in (self.first,self.prev):
        btn.set_sensitive(True) 
    for btn in (self.next,self.last):
        btn.set_sensitive(False) 

def on_btnPrev_clicked(self,button):
    if self.fitlist_n == 1:
        on_btnFirst_clicked(self,button)
    else:
        self.fitlist_n -= 1
        #~ UpdateEqualized(self)
        ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    s0 = self.adjmin.get_property("value")/500,
                    s1 = self.adjmax.get_property("value")/500)
        for btn in (self.next,self.last):
            btn.set_sensitive(True) 

def on_btnNext_clicked(self, button):
    if self.fitlist_n == len(self.fitlist)-2:
        on_btnLast_clicked(self,button)
    else:
        self.fitlist_n += 1
        #~ UpdateEqualized(self)
        ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    s0 = self.adjmin.get_property("value")/500,
                    s1 = self.adjmax.get_property("value")/500)
        for btn in (self.first,self.prev):
            btn.set_sensitive(True) 

def on_combobox1_changed(self,widget):
    #~ print "Combo changed", widget.get_active()
    id = widget.get_active()
    filter = [self.fitfilter,self.rfitfilter,self.vfitfilter,None]
    self.fitchooser.set_property("filter", filter[id])
    
def on_lstFilter_row_changed(self,widget):
    print "row changed", widget
    
def on_adjfitlist_value_changed(self,widget,data=None):
    self.fitlist_n = int(widget.get_property("value")) - 1
    ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    s0 = self.adjmin.get_property("value")/500,
                    s1 = self.adjmax.get_property("value")/500)

def on_adjDx_value_changed(self,widget,data=None):
    pass
    
def on_adjDy_value_changed(self,widget,data=None):
    pass
    
def on_adjZoom_value_changed(self,widget,data=None):
    pass
    
def  on_chkAlignAuto_toggled(self,widget,data=None):
    pass
    
