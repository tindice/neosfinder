#!/usr/bin/env python

#~ import Gtk
from gi.repository import Gtk,  GdkPixbuf
from astrotools import *
import numpy as np
from PIL import Image , ImageDraw

class Gui:

  def gtk_main_quit(self, menuitem, data=None):
    print "quit from menu"
    Gtk.main_quit()

  def on_mnuAcercaDe_activate(self, menuitem, data=None):
    print "help about selected"
    self.response = self.aboutdialog.run()
    
  def on_about_closebutton_release(self, menuitem, data=None):
    print "close button"
    self.aboutdialog.close()

  def on_AbrirFit_activate(self, menuitem, data=None):
    self.fitchooser.run()

  def on_fitchooserdialog_response(self, menuitem, data=None):
    if data == 1:
        self.fitlist = self.fitchooser.get_filenames()
        _, data = Getdata(self.fitlist[0])
        png = Fit2png(data)
        size = (png.shape[1]/2, png.shape[0]/2)
        im = Image.fromarray(png)
        im.thumbnail(size, Image.BICUBIC)
        im.save("../tmp/tmp.png")

        #~ pixbuf = GdkPixbuf.Pixbuf.new_from_array(png)
        pixbuf = GdkPixbuf.Pixbuf.new_from_file('../tmp/tmp.png')
        self.imagen.set_property("pixbuf", pixbuf)
    else:
        print "Cancel"
    self.fitchooser.hide()

  def __init__(self):
    XMLfile = "nfgui.glade"
    #~ self.gladefile = "tut1.glade"
    self.builder = Gtk.Builder()    # Crea una instancia de Builder
    # Carga la definicion de gui del archivo xml de Glade:
    self.builder.add_from_file(XMLfile)
    self.builder.connect_signals(self)
    self.window = self.builder.get_object("winMain")
    self.fitchooser = self.builder.get_object("fitchooserdialog")
    self.aboutdialog = self.builder.get_object("dlgAcercaDe")
    self.fitlist = []
    self.imagen = self.builder.get_object("imagen")
    self.window.show()
    
#~ print fitlist

if __name__ == "__main__":
  main = Gui()
  Gtk.main()
