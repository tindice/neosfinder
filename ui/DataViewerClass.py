#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class DataViewer(Gtk.Window):
  def __init__(self):
    # Create a new window
    Gtk.Window.__init__(self, title="Metadatos",deletable=False)
    #~ self.set_border_width(20)
    self.set_keep_above(True)
    self.connect("delete_event", self.hideme)
    
    # Create a scrollwindow
    self.scroll = Gtk.ScrolledWindow(shadow_type="in")
    # Put it in the main window
    self.add(self.scroll)
    
    # Create a grid
    self.grid = Gtk.Grid(row_homogeneous=False)
    self.grid.props.column_spacing = 6
    
    # Put the grid in the scroll
    self.scroll.add(self.grid)
    btn = Gtk.Button(label="campos variables")
    self.grid.attach(btn, 0, 0, 1, 1)  
    btn = Gtk.Button(label="valor")
    self.grid.attach(btn, 1, 0, 1, 1)  
    btn = Gtk.Button(label="comentario")
    self.grid.attach(btn, 2, 0, 1, 1)  
    self.rows = 1
    
  def hideme(self, *args):
      self.set_visible(False)
      return True
          
  def cleanme(self, *args):
      while self.rows > 1:
          self.grid.remove_row(1)
          self.rows -= 1
      return True
          
  def newrow(self,txtlist):
        lbl = Gtk.Label()
        lbl.set_markup("<b>%s</b>"%txtlist[0])
        self.grid.attach(lbl, 0, self.rows, 1, 1)  
        lbl = Gtk.Label(txtlist[1])
        self.grid.attach(lbl, 1, self.rows, 1, 1) 
        lbl = Gtk.Label()
        lbl.set_markup("<small>%s</small>"%txtlist[2])
        #~ lbl.set_line_wrap(True)
        self.grid.attach(lbl, 2, self.rows, 1, 1) 
        self.rows += 1
        return True

  def newline(self):
        lbl = Gtk.Label(20*"_")
        self.grid.attach(lbl, 0, self.rows, 3, 1)  
        self.rows += 1
        return True

  def changetext(self,row,txtlist):
        #~ print "row,txt",row,txtlist
        lbl = self.grid.get_child_at(1,row)
        lbl.set_label(txtlist[0])
        lbl = self.grid.get_child_at(2,row)
        lbl.set_markup("<small>%s</small>"%txtlist[1])
        
  def updatekeys(self,metadict,keylist):
        n = 1
        for k in keylist:
            self.changetext(n,[str(metadict[k]),metadict.comments[k]])
            n += 1
        return True
            
  def setkeys(self,metadict,keylist):
        print "setkeys", keylist
        for k in keylist:
            self.newrow([k,str(metadict[k]),metadict.comments[k]])
        self.newline()
        return True

def main():
    win = DataViewer()
    win.newrow(["uno","dos","va un muy largo texto aquí."])
    win.newrow(["cuatro","cinco","seis"])
    win.changetext(1,["5","otro largo"])
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    

if __name__ == "__main__":
  main()
