#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image , ImageDraw
from astrotools import *
from gi.repository import Gtk, Gdk, GdkPixbuf
from math import log1p, exp

# =======   Functions Section  ========================================

def Sigmoid(h,s0,s1):
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

def ShowEqualized(gui, file, s0=0.0185, s1=0.0323):
    ''' accepts "file" as string or as np.array
    '''
    screenHeight = gui.window.get_property("default_height")

    if type(file) == type("str"):    # gets image data from file:
        _, gui.data = Getdata(file)
        if gui.ViewFlipH:
            gui.data = np.fliplr(gui.data)
        if gui.ViewFlipV:
            gui.data = np.flipud(gui.data)
        if gui.ViewRotated != 0:
            gui.data = np.rot90(gui.data, gui.ViewRotated)
        k = gui.ZoomK
        if k > 1: # si voy a ampliar
            (h,w) = gui.data.shape
            x0,y0 = w*(1-1/k)/2, h*(1-1/k)/2
            x1,y1 = w*(k+1)/2/k, h*(k+1)/2/k
            gui.data = gui.data[y0:y1, x0:x1]  # crop array

    png = Fit2png(gui.data,s0, s1)
    k = 0.65 * screenHeight / png.shape[0]
    size = tuple(x*k for x in png.shape)
    im = Image.fromarray(png)
    im.thumbnail((size[1],size[0]), Image.BICUBIC)
    arr = np.array(im.getdata()).flatten()
# TODO: 
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    #~ im = im.convert("RGB")
    #~ pixbuf = GdkPixbuf.Pixbuf.new_from_data(arr,
     #~ GdkPixbuf.Colorspace.RGB, False, 8, size[1], size[0], 3*size[1])
     
    # show imge: 
    gui.imagen.set_property("pixbuf", pixbuf)
    if type(file) == type("str"):
        idx = file.rfind("/")
        gui.info.set_property("label",file[idx+1:])
    
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
    return  

def UpdateEqualized(gui):
    ShowEqualized(gui, gui.data, 
                    s0 = gui.adjmin.get_property("value")/500,
                    s1 = gui.adjmax.get_property("value")/500)


# ====================================================================

# ====  Handlers Section    ===================================

def gtk_main_quit(self, menuitem, data=None):
    
    Gtk.main_quit()

def on_mnuEqualize(self, menuitem, data=None):
    on_dlgEqualize_realize(self, menuitem)
    if self.msg == 0:   # only first time,
        self.equadialog.run()
    else:
        self.equadialog.show()
        
def on_dlgEqualize_realize(self, obj):
    # show histogram with sigmoid:
    print ">",self.adjmin.get_property("value")/500,self.adjmax.get_property("value")/500
    h = Sigmoid(self.arrHistogram,self.adjmin.get_property("value")/500,self.adjmax.get_property("value")/500)
    im = Image.fromarray(h)
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    self.histo.set_property("pixbuf", pixbuf)
    if self.msg == 0:
        self.msg = 1
        self.chkauto.set_active(True)
    
def on_dlgEqualize_response(self, obj, btnID=None):
    if btnID == 1:   # Apply button pressed.
        ShowEqualized(self,self.data, s0 = self.adjmin.get_property("value")/500,
                            s1 = self.adjmax.get_property("value")/500)
    else:
        self.equadialog.hide()
        
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
    if self.ViewRotated == 3:
        self.ViewRotated = 0
    else:
        self.ViewRotated += 1
    
def on_mnuVoltearH(self, menuitem, data=None):
    #~ self.data = np.fliplr(self.data)
    #~ UpdateEqualized(self)
    
    pb = self.imagen.get_property("pixbuf").flip(True)
    self.imagen.set_property("pixbuf", pb)

    self.ViewFlipH = not self.ViewFlipH
    
def on_mnuVoltearV(self, menuitem, data=None):
    #~ self.data = np.flipud(self.data)
    #~ UpdateEqualized(self)
    pb = self.imagen.get_property("pixbuf").flip(False)
    self.imagen.set_property("pixbuf", pb)
    self.ViewFlipV = not self.ViewFlipV
    
def on_mnuZoom(self, menuitem, data=None):
    k = 1.25
    pb = self.imagen.get_property("pixbuf")
    src_x = (1-1/k)/2 * pb.get_height()
    src_y = (1-1/k)/2 * pb.get_width()
    spb = pb.new_subpixbuf(int(src_x), int(src_y),
              int(pb.get_width()/k) , int(pb.get_height()/k))
    pxb = spb.scale_simple(pb.get_width(), pb.get_height(),
                         GdkPixbuf.InterpType.BILINEAR)
    self.imagen.set_property("pixbuf", pxb)
    self.ZoomK *= k
              
def on_mnuAcercaDe(self, menuitem, data=None):
    self.response = self.aboutdialog.run()
    
def on_about_closebutton_release(self, menuitem, data=None):
    self.aboutdialog.close()

def on_mnuAbrirFits(self, menuitem, data=None):
    self.fitchooser.set_default_response(1)
    self.fitchooser.run()

def on_fitchooserdialog_response(self, obj, btnID=1):
    watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
    self.window.get_window().set_cursor(watch_cursor)
    if btnID == 1:
        self.fitlist = sorted(self.fitchooser.get_filenames())
        #~ self.fitminmax = {n: n**2 for n in range(len(self.fitlist))}
        if len(self.fitlist) > 1:
            for btn in (self.first, self.next, self.prev, self.last):
                btn.set_property("visible",True)
        ShowEqualized(self, self.fitlist[0])
        for btn in (self.first,self.prev):
            btn.set_sensitive(False) 
        for btn in (self.next,self.last):
            btn.set_sensitive(True) 
    self.window.get_window().set_cursor(None)
    self.fitchooser.hide()
    

def on_btnFirst_clicked(self,button):
    self.fitlist_n = 0
    #~ UpdateEqualized(self)
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

    
