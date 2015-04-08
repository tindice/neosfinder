#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image , ImageDraw
from astrotools import *
from gi.repository import Gtk,  GdkPixbuf
from math import log1p

def ShowEqualized(data,s0=0.0185, s1=0.0323):
    ''' returns pixbuf
    '''
    png = Fit2png(data,s0, s1)
    size = tuple(x/2 for x in png.shape)
    im = Image.fromarray(png)
    im.thumbnail((size[1],size[0]), Image.BICUBIC)
    #~ im.show()
    arr = np.array(im.getdata()).flatten()
    #~ print size
# TODO: 
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    #~ im = im.convert("RGB")
    #~ pixbuf = GdkPixbuf.Pixbuf.new_from_data(arr,
     #~ GdkPixbuf.Colorspace.RGB, False, 8, size[1], size[0], 3*size[1])
     
    return pixbuf 


def gtk_main_quit(self, menuitem, data=None):
    Gtk.main_quit()

def on_mnuEqualize(self, menuitem, data=None):
    # show histogram:
    v,_ = np.histogram(self.data,bins=256)
    h = np.zeros((100,256), dtype=np.uint8)
    for x in range(256):
        #~ b =min(100,7*log1p(v[x]))
        b = 7*log1p(v[x])
        h[-b:,x] = 255
    # draw frame borders:
    h[0,:]=h[99,:]=h[:,0]=h[:,255] = 90 # ligth grey
    im = Image.fromarray(h)
    #~ im.show()
    im.save("../tmp/tmp.png")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
    self.histo.set_property("pixbuf", pixbuf)

    # valores por defecto:
    amin, amax = np.amin(self.data), np.amax(self.data)
    delta = amax-amin
    #~ i0, i1 = amin+ 0.0185*delta, amin+ 0.0323*delta
    self.info.set_property("label","min=%i   max=%i"%(amin,amax))
    #~ self.adjmin.set_property("upper", 1.25 * delta/256)
    #~ self.adjmax.set_property("upper", 1.25 * delta/256)
    #~ self.adjmin.set_property("upper", 100)
    #~ self.adjmax.set_property("upper", 100)
    self.adjmin.set_property("value", 500*0.0185)
    self.adjmax.set_property("value", 500*0.0323)
    self.automin = self.adjmin.get_property("value")
    self.automax = self.adjmax.get_property("value")
    self.chkauto.set_property("active", True)
    
    self.equadialog.run()
    
def on_dlgEqualize_response(self, menuitem, data=None):
    if data == 1:   # Apply button pressed.
        pbuf = ShowEqualized(self.data, self.adjmin.get_property("value")/500,
                                 self.adjmax.get_property("value")/500)
        self.imagen.set_property("pixbuf", pbuf)
        self.info.set_property("label",self.fitlist[0])

    else:
        self.equadialog.hide()
        
def on_chkAuto_toggled(self, menuitem, data=None):
    if self.chkauto.get_property("active"):
        self.adjmin.set_property("value", self.automin)
        self.adjmax.set_property("value", self.automax)
          
def on_adjmin_value_changed(self, menuitem, data=None):
    if self.chkauto.get_property("active"):
        self.chkauto.set_property("active", False)

def on_adjmax_value_changed(self, menuitem, data=None):
    if self.chkauto.get_property("active"):
        self.chkauto.set_property("active", False)

def on_mnuAcercaDe_activate(self, menuitem, data=None):
    print "help about selected"
    self.response = self.aboutdialog.run()
    
def on_about_closebutton_release(self, menuitem, data=None):
    #~ print "close button"
    self.aboutdialog.close()

def on_AbrirFit_activate(self, menuitem, data=None):
    self.fitchooser.run()

def on_fitchooserdialog_response(self, menuitem, data=None):
    if data == 1:
        self.fitlist = self.fitchooser.get_filenames()
        # display imagen 1:
        _, self.data = Getdata(self.fitlist[0])
        pbuf = ShowEqualized(self.data)     # autoequaliz
        self.imagen.set_property("pixbuf", pbuf)
        self.info.set_property("label",self.fitlist[0])

    else:
        print "Cancel"
    self.fitchooser.hide()
