#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image , ImageDraw
from astrotools import *
from gi.repository import Gtk, Gdk, GdkPixbuf
from math import log1p, exp

# =======   Functions Section  ========================================

def ViewDefault(gui):
    ''' Restores View parameters.
    '''
    gui.ViewZoom = 1
    gui.ViewRotate = 0
    gui.ViewFlipH = False
    gui.ViewFlipV = False

#~ def Zoom(gui, k):
    #~ gui.ViewZoom *= k
    #~ print "VZ", gui.ViewZoom
    #~ if k < 1:
        #~ pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
        #~ Zoom(gui,gui.ViewZoom)
        #~ return
    #~ elif k == 1:
        #~ pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
        #~ 
    #~ pb = gui.imagen.get_property("pixbuf")
    #~ src_x = (1-1/k)/2 * pb.get_height()
    #~ src_y = (1-1/k)/2 * pb.get_width()
    #~ # crops from pixbuf
    #~ spb = pb.new_subpixbuf(int(src_x), int(src_y),
              #~ int(pb.get_width()/k) , int(pb.get_height()/k))
      #~ # amplify
    #~ pxb = spb.scale_simple(pb.get_width(), pb.get_height(),
                         #~ GdkPixbuf.InterpType.BILINEAR)
      #~ # and apply
    #~ gui.imagen.set_property("pixbuf", pxb)
#~ 
def Zoom(gui, k):
    #~ k = 1.25
    gui.ViewZoom *= k
    print "VZ", gui.ViewZoom
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

def ShowEqualized(gui, file, s0=0 , s1=0):
    ''' accepts "file" as string or as np.array
    '''
    gui.spinner.start()
    screenHeight = gui.window.get_property("default_height")
    if s0 == 0:
        s0=gui.automin/500
        s1=gui.automax/500

    if type(file) == type("str"):    # gets image data from file:
        meta, gui.data = Getdata(file)
        print meta
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
        gui.info.set_property("label","%s\t UTC=%s"%(file[idx+1:],meta[0][-8:]))
    
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
    gui.spinner.stop()

    return  

def UpdateEqualized(gui):
    ShowEqualized(gui, gui.data, 
                    s0 = gui.adjmin.get_property("value")/500,
                    s1 = gui.adjmax.get_property("value")/500)


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
    if self.msg == 0:   # only first time,
        self.equadialog.run()
    else:
        self.equadialog.show()
        
def on_dlgEqualize_realize(self, obj):
    # show histogram with sigmoid:
    #~ print ">",self.adjmin.get_property("value")/500,self.adjmax.get_property("value")/500
    h = Sigmoid(self.arrHistogram,self.adjmin.get_property("value")/500,self.adjmax.get_property("value")/500)
    im = Image.fromarray(h)
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    self.histo.set_property("pixbuf", pixbuf)
    if self.msg == 0:
        self.msg = 1
        self.chkauto.set_active(True)
    
def on_dlgEqualize_response(self, widget, btnID=None):
    if btnID == 1:   # Apply button pressed.
        ShowEqualized(self,self.data, s0 = self.adjmin.get_property("value")/500,
                            s1 = self.adjmax.get_property("value")/500)
    else:
        widget.hide()
        
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
    
def on_mnuZoomU(self, menuitem, data=None):
    Zoom(self, 1.25)
              
def on_mnuMeta(self, menuitem, data=None):
    header = Getmeta(self.fitlist[self.fitlist_n])
    #~ print metalist
    self.textbuffer.set_text(repr(header))
    self.dlgmeta.run()
              
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

def on_fitchooserdialog_response(self, obj, btnID=1):
    if btnID == 1:
        #~ watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        #~ self.window.get_window().set_cursor(watch_cursor)
        ViewDefault(self)
        
        self.fitlist = sorted(self.fitchooser.get_filenames())
        if self.fitlist == []: return
        if len(self.fitlist) > 1:
            for btn in (self.first, self.next, self.prev, self.last):
                btn.set_property("visible",True)
        metaConst, metaVar = GetMeta(self.fitlist)
        ShowEqualized(self, self.fitlist[0])
        for btn in (self.first,self.prev):
            btn.set_sensitive(False) 
        for btn in (self.next,self.last):
            btn.set_sensitive(True) 

            
    #~ self.window.get_window().set_cursor(None)
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

def on_combobox1_changed(self,widget):
    #~ print "Combo changed", widget.get_active()
    id = widget.get_active()
    filter = [self.fitfilter,self.rfitfilter,self.vfitfilter,None]
    self.fitchooser.set_property("filter", filter[id])
    
def on_lstFilter_row_changed(self,widget):
    print "row changed", widget
    

    
