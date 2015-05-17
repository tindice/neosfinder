#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image , ImageDraw, ImageChops
from astrotools import *
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from math import log1p, exp
import threading, tempfile

_,tmpfolder = tempfile.mkstemp()

# =======   Functions Section  ========================================

def ZoomDefault(gui, pxbf):
    w0 = float(pxbf.get_width())
    h0 = float(pxbf.get_height())
    w1 = gui.viewport.get_property("width_request")
    h1 = gui.viewport.get_property("height_request")
    k = min(w1/w0, h1/h0)
    print "ZD",k
    return pxbf.scale_simple(k*w0, k*h0,
                             GdkPixbuf.InterpType.BILINEAR)

def Zoom(gui, k):
    gui.ViewZoom *= k
    print "zoom:", gui.ViewZoom
    if gui.ViewZoom == 1.0:
        gui.imagen.set_property("pixbuf", gui.pxbf)
    else:
        size = (gui.pxbf.get_width(),gui.pxbf.get_height())
        size = tuple(x * gui.ViewZoom for x in size)
        pxb = gui.pxbf.scale_simple(size[0], size[1],
                             GdkPixbuf.InterpType.BILINEAR)
        gui.imagen.set_property("pixbuf", pxb)
    return

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
    im.save("./tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("./tmp.png")
    gui.histo.set_property("pixbuf", pixbuf)

def ShowImage(gui, im):
    im.save("./tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("./tmp.png")
    gui.imagen.set_property("pixbuf", ZoomDefault(gui,pixbuf))
    return True

def ShowEqualized(gui, file, s0=0 , s1=0, msg=None):
    ''' accepts "file" as string or as np.array
    '''
    print "ShwEq",msg
    gui.spinner.start()
    # toogle   GTK_SHADOW_ETCHED_OUT / GTK_SHADOW_ETCHED_IN
    gui.viewport.set_shadow_type(3+gui.viewport.get_shadow_type()%2)
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
        #~ k = gui.ViewZoom
        #~ if k > 1: # si voy a ampliar
            #~ (h,w) = gui.data.shape
            #~ x0,y0 = w*(1-1/k)/2, h*(1-1/k)/2
            #~ x1,y1 = w*(k+1)/2/k, h*(k+1)/2/k
            #~ gui.data = gui.data[y0:y1, x0:x1]  # crop array
    else:
        print "not string ???"
        
    png = Fit2png(gui.data,s0, s1)
    im = Image.fromarray(png)
    if file in gui.align.keys():
        (dy,dx) = gui.align[file]
        im = ImageChops.offset(im,dx,dy)


    im.save("./tmp.png")
    if file == gui.fitlist[0]: # si primera imagen,
        gui.im_0 = im           # guardar
    gui.im_actual = im
    pxbf = GdkPixbuf.Pixbuf.new_from_file("./tmp.png")
    gui.pxbf = ZoomDefault(gui,pxbf)
    #~ # rescale slider:
    gui.adjselfit.set_property("upper", len(gui.fitlist))
    gui.selfit.set_property("visible", True)
    
    # show imge: 
    gui.imagen.set_property("pixbuf", gui.pxbf)
    #~ print "ShIm", gui.imagen.get_property("visible"),gui.imagen.get_property("pixbuf")
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
            gui.metaviewer.setkeys(gui.metalist[gui.fitlist_n],
                                   gui.DifKlist,gui.ConKlist)
            gui.metaviewer.show_all()
        else:
            print "159"
            gui.metaviewer.updatekeys(gui.metalist[gui.fitlist_n],
                                      gui.DifKlist)
        #~ 
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
    ZoomDefault(self)
    #~ self.msgdialog.run()
    
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
    im.save("./tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file("./tmp.png")
    self.histo.set_property("pixbuf", pixbuf)
    #~ if self.msg == 0:
        #~ self.msg = 1
    if self.histo.get_property("pixbuf") == None:
        print "Nunca pasare por aca !"
        self.chkauto.set_active(True)
    
def on_dlgEqualize_response(self, widget, btnID=None):
    if btnID == 1:   # Apply button pressed.
        #~ ShowEqualized(self,self.data, s0 = self.adjmin.get_property("value")/500,
                            #~ s1 = self.adjmax.get_property("value")/500)
        png = Fit2png(self.data,
                      s0 = self.adjmin.get_property("value")/500,
                      s1 = self.adjmax.get_property("value")/500, black=False)
        im = Image.fromarray(png)
        if self.fitlist_n in self.align.keys():
            (dy,dx) = self.align[file]
            im = ImageChops.offset(im,dx,dy)
        self.im_actual = im
        im.save("./tmp.png")
        pxbf = GdkPixbuf.Pixbuf.new_from_file("./tmp.png")
        self.pxbf = ZoomDefault(self,pxbf)
        # show imge: 
        self.imagen.set_property("pixbuf", self.pxbf)
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
    #~ if self.msg == 0:  return
    if self.histo.get_property("pixbuf") == None:  return
    if self.adjmin.get_property("value") > self.adjmax.get_property("value"):
        self.adjmin.set_property("value", self.adjmax.get_property("value")-1)
    UpdateSigmoid(self)
    
def on_adjmax_value_changed(self, obj):
    #~ if self.msg == 0:  return
    if self.histo.get_property("pixbuf") == None:  return
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
    im = Image.merge("RGB", (self.im_0,self.im_actual,self.im_0))
    ShowImage(self,im)
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
    print "filedialogID:", btnID
    if btnID <= 0:
        self.fitchooser.hide()
        return
    else:
        self.initialize()
        # mouse pointer:
        watch_cursor = Gdk.Cursor(Gdk.CursorType.WATCH)
        self.window.get_window().set_cursor(watch_cursor)
        GObject.threads_init()
        Gdk.threads_init()
        
        self.fitlist = sorted(self.fitchooser.get_filenames())
        self.fitchooser.hide()
        if self.fitlist == []: return
        def otrohilo():
            #~ print self.fitlist
            
            self.metaviewer.cleanme() # reiniciarlo
            # lista de diccionarios metadata:
            self.metalist = list(GetMeta(f) for f in self.fitlist)
            #~ # lista de registros variables:
            #~ diflist = list(set(self.metalist[0].items()) ^ set(self.metalist[1].items()))
            self.ConKlist = list(k for k in self.metalist[0].keys())

            if len(self.fitlist) > 1:
                for f in self.fitlist[1:]:
                    meta = GetMeta(f)
                    diflist = list(set(self.metalist[0].items()) ^ set(meta.items()))
                    difKlist=list(set(list(x[0] for x in diflist)))
                    self.DifKlist.extend(difKlist)
                self.DifKlist=list(set(self.DifKlist))  # lista de claves variable unique
                for key in self.DifKlist:
                    if key in self.ConKlist: self.ConKlist.remove(key)
    
            def done():
                self.window.get_window().set_cursor(None)
                return False
#~ 
#~ 
            GObject.idle_add(done)
            
        thread = threading.Thread(target=otrohilo)
        thread.start()
        otrohilo()
        ShowEqualized(self, self.fitlist[0],msg="de fitchooser")
    return
    #~ print "volvi con", self.fitlist_n, self.fitlist
        
    #~ if len(self.fitlist) > 1:
        #~ for btn in (self.first, self.next, self.prev, self.last):
            #~ btn.set_property("visible",True)
            #~ 
        #~ self.first.set_sensitive(False)
        #~ self.prev.set_sensitive(False)
        #~ self.next.set_sensitive(True)
        #~ self.last.set_sensitive(True)

    

#~ def on_btnFirst_clicked(self,button):
    #~ self.fitlist_n = 0
    #~ ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    #~ s0 = self.adjmin.get_property("value")/500,
                    #~ s1 = self.adjmax.get_property("value")/500)
    #~ for btn in (self.first,self.prev):
        #~ btn.set_sensitive(False) 
    #~ for btn in (self.next,self.last):
        #~ btn.set_sensitive(True) 
    #~ 
    #~ 
#~ def on_btnLast_clicked(self,button):
    #~ self.fitlist_n = len(self.fitlist)-1
    #~ ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    #~ s0 = self.adjmin.get_property("value")/500,
                    #~ s1 = self.adjmax.get_property("value")/500)
    #~ for btn in (self.first,self.prev):
        #~ btn.set_sensitive(True) 
    #~ for btn in (self.next,self.last):
        #~ btn.set_sensitive(False) 
#~ 
#~ def on_btnPrev_clicked(self,button):
    #~ if self.fitlist_n == 1:
        #~ on_btnFirst_clicked(self,button)
    #~ else:
        #~ self.fitlist_n -= 1
        #~ ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    #~ s0 = self.adjmin.get_property("value")/500,
                    #~ s1 = self.adjmax.get_property("value")/500)
        #~ for btn in (self.next,self.last):
            #~ btn.set_sensitive(True) 
#~ 
#~ def on_btnNext_clicked(self, button):
    #~ if self.fitlist_n == len(self.fitlist)-2:
        #~ on_btnLast_clicked(self,button)
    #~ else:
        #~ self.fitlist_n += 1
        #~ ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    #~ s0 = self.adjmin.get_property("value")/500,
                    #~ s1 = self.adjmax.get_property("value")/500)
        #~ for btn in (self.first,self.prev):
            #~ btn.set_sensitive(True) 

def on_combobox1_changed(self,widget):
    #~ print "Combo changed", widget.get_active()
    id = widget.get_active()
    filter = [self.fitfilter,self.rfitfilter,self.vfitfilter,None]
    self.fitchooser.set_property("filter", filter[id])
    
def on_lstFilter_row_changed(self,widget):
    print "row changed", widget
    
def on_adjfitlist_value_changed(self,widget,data=None):
    self.fitlist_n = int(widget.get_property("value")) - 1
    print "adj"
    ShowEqualized(self, self.fitlist[self.fitlist_n], 
                    s0 = self.adjmin.get_property("value")/500,
                    s1 = self.adjmax.get_property("value")/500,
                    msg = "FitNr")

def on_winMain_configure_event(self,widget,data=None):
    #~ w = self.viewport.get_property("width_request")
    #~ dx = self.window.get_size()[0]-self.winsize0[0]
    #~ self.viewport.set_property("width_request", w+dx)
    #~ return True
    pass
    
def on_adjDx_value_changed(self,widget,data=None):
    pass
    
def on_adjDy_value_changed(self,widget,data=None):
    pass
    
def on_adjZoom_value_changed(self,widget,data=None):
    pass
    
def  on_chkAlignAuto_toggled(self,widget,data=None):
    pass
    
