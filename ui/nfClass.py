#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk
import DataViewerClass as dv
# ===== Variables Globales ====================    
window = Gtk.Window()
screen = window.get_screen()
screenWidth, screenHeight = screen.width(), screen.height()

# ===============================================

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
    self.adjselfit = self.builder.get_object("adjfitlist")
    self.chkauto = self.builder.get_object("chkAuto")
    self.prev = self.builder.get_object("btnPrev")
    self.first = self.builder.get_object("btnFirst")
    self.next = self.builder.get_object("btnNext")
    self.last = self.builder.get_object("btnLast")
    self.cmbFile = self.builder.get_object("cmbFile")
    self.fitfilter = self.builder.get_object("fitfilter")
    self.rfitfilter = self.builder.get_object("rfitfilter")
    self.vfitfilter = self.builder.get_object("vfitfilter")
    self.msgdialog = self.builder.get_object("msgdialog")
    self.dlgmeta = self.builder.get_object("dlgMeta1")
    self.chkmeta0 = self.builder.get_object("chkMeta0")
    self.textbuffer = self.builder.get_object("textbuffer1")
    self.spinner = self.builder.get_object("spinner3")
    self.frame = self.builder.get_object("frame1")
    self.selfit = self.builder.get_object("sclSelFit")
    self.dlgalinear = self.builder.get_object("dlgAlinear")
    self.adjdx = self.builder.get_object("adjDx")
    self.adjdy = self.builder.get_object("adjDy")
    self.metaviewer = dv.DataViewer()
    #~ self.window.add(self.metaviewer)
    
    # Accelerators
    #~ self.my_accelerators = Gtk.AccelGroup()
    #~ self.window.add_accel_group(self.my_accelerators)
    #~ self.entry = self.builder.get_object("entry1")
    #~ self.add_accelerator(self.entry, "<Control>+", signal="on_mnuZoom")
    self.initialize()
    
  def initialize(self, obj=None):  
    # inicializa variables:
    #~ self.fitminmax = {}
    self.DifKlist = []
    self.ConKlist = []
    self.chkmeta0.set_border_width(4)
    self.fitlist = []
    self.metalist = []
    self.fitlist_n = 0
    self.msg = 0
    self.automin = 500*0.01
    self.automax = 500*0.016
    self.ViewFlipH = False
    self.ViewFlipV = False
    self.ViewRotate = 0
    self.ViewZoom = 1
    self.folder = None
    self.align = {}             # Diccionario {filename : (dy,dx)}
    self.im_0 = None             # PIL.Image(self.fitlist[0])
    self.im_actual = None             # PIL.Image(self.fitlist_n)
    
    # asigna valores:
    self.adjselfit.set_property("lower", 1)
    self.adjmin.set_property("value", self.automin)
    self.cmbFile.set_active(0)
    self.adjmax.set_property("value", self.automax)
    self.window.set_property("default_width", screenWidth)
    self.window.set_property("default_height", screenHeight)
    self.metaviewer.set_property("default_width", int(screenWidth/3))
    self.metaviewer.set_property("default_height", int(screenHeight/10))
    self.window.show()
    
    #~ f = open("./settings", "r")
    #~ self.folder = eval(f.readline())
    #~ f.close()
    #~ self.fitchooser.set_current_folder(self.folder)

    

if __name__ == "__main__":
  main = Gui()
  Gtk.main()
