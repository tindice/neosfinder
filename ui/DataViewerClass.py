#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class DataViewer(Gtk.Window):
  def __init__(self):
    # Create a new window
    Gtk.Window.__init__(self, title="Metadatos")
    #~ self.set_border_width(20)
    
    # Create a grid
    self.grid = Gtk.Grid()
    self.grid.props.column_spacing = 10
    
    # Put the grid in the main window
    self.add(self.grid)
    self.rows = 0
    
  def newrow(self,list):
        lbl = Gtk.Label()
        lbl.set_markup("<b>%s</b>"%list[0])
        self.grid.attach(lbl, 0, self.rows, 1, 1)  
        lbl = Gtk.Label(list[1])
        self.grid.attach(lbl, 1, self.rows, 1, 1) 
        lbl = Gtk.Label()
        lbl.set_markup("<small>%s</small>"%list[2])
        self.grid.attach(lbl, 2, self.rows, 1, 1) 
        self.rows += 1

  def changetext(self,row,list):
        self.grid.get_child_at(1,row).set_label(list[0])
        self.grid.get_child_at(2,row).set_markup("<small>%s</small>"%list[1])
        
  def updatekeys(self,metadict,keylist):
        print "upd", metadict[0], keylist
        n = 0
        for k in keylist:
            changetext(n,[k,metadict[k][0],metadict[k][1]])
            n += 1
            
  def setkeys(self,metadict,keylist):
        print "upd", metadict[0], keylist
        for k in keylist:
            newrow([k,metadict[k][0],metadict[k][1]])

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
