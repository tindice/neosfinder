#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
    

class Gui:
  from Handler import *


  def __init__(self):
    XMLfile = "nf.glade"
    self.builder = Gtk.Builder()    # Crea una instancia de Builder
    # Carga la definicion de gui del archivo xml de Glade:
    self.builder.add_from_file(XMLfile)
    self.builder.connect_signals(self)
    # levanta objetos:
    self.window = self.builder.get_object("winMain")
    self.fitchooser = self.builder.get_object("fitchooserdialog")
    self.aboutdialog = self.builder.get_object("dlgAcercaDe")
    self.equadialog = self.builder.get_object("dlgEqualize")
    self.imagen = self.builder.get_object("imagen")
    self.histo = self.builder.get_object("imgHistogram")
    self.histogram = self.builder.get_object("drawingarea")
    self.info = self.builder.get_object("infolbl")
    self.adjmin = self.builder.get_object("adjmin")
    self.adjmax = self.builder.get_object("adjmax")
    self.chkauto = self.builder.get_object("chkAuto")
    self.prev = self.builder.get_object("btnPrev")
    self.first = self.builder.get_object("btnFirst")
    self.next = self.builder.get_object("btnNext")
    self.last = self.builder.get_object("btnLast")
    # inicializa variables:
    #~ self.fitminmax = {}
    self.fitlist = []
    self.fitlist_n = 0
    self.msg = 0
    self.automin = 500*0.0185
    self.automax = 500*0.0323
    self.adjmin.set_property("value", self.automin)
    self.adjmax.set_property("value", self.automax)
    self.window.show()
    

if __name__ == "__main__":
  main = Gui()
  Gtk.main()
