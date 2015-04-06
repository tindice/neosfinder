#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image , ImageDraw
from astrotools import *
from gi.repository import Gtk,  GdkPixbuf

def gtk_main_quit(self, menuitem, data=None):
    Gtk.main_quit()

def on_mnuEqualize(self, menuitem, data=None):
    # valores por defecto:
    amin, amax = np.amin(self.data), np.amax(self.data)
    delta = amax-amin
    i0, i1 = amin+ 0.0185*delta, amin+ 0.0323*delta
    self.info.set_property("label","min=%i   max=%i"%(amin,amax))
    self.adjmin.set_property("upper", 1.25 * delta/256)
    self.adjmax.set_property("upper", 1.25 * delta/256)
    self.adjmin.set_property("value", i0/256)
    self.adjmax.set_property("value", i1/256)
    self.automin = self.adjmin.get_property("value")
    self.automax = self.adjmax.get_property("value")
    self.chkauto.set_property("active", True)
    self.equadialog.run()
    
def on_dlgEqualize_response(self, menuitem, data=None):
    if data == 1:
        pass
    else:
        self.equadialog.hide()
        
def on_chkAuto_toggled(self, menuitem, data=None):
    if self.chkauto.get_property("active"):
        self.info.set_property("label","activo")
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
        png = Fit2png(self.data)
        size = (png.shape[1]/2, png.shape[0]/2)
        im = Image.fromarray(png)
        im.thumbnail(size, Image.BICUBIC)
        im.save("../tmp/tmp.png")
# TODO: 
        #~ pixbuf = Gtk.Gdk.pixbuf_new_from_array(np.array(im),Gtk.gdk.COLORSPACE_RGB,8)
        #~ pixbuf = GdkPixbuf.pixbuf_new_from_array(np.array(im),Gtk.gdk.COLORSPACE_RGB,8)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
        self.imagen.set_property("pixbuf", pixbuf)
        self.info.set_property("label",self.fitlist[0])
    else:
        print "Cancel"
    self.fitchooser.hide()
