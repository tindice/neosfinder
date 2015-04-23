#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class DataViewer:
  def __init__(self):
    # Create a new window
    self.window = Gtk.Window()
    
    # Set the window title
    self.window.set_title("Metadatos")
    
    # Set a handler for delete_event that immediately
    # exits GTK.
    #~ self.window.connect("delete_event", self.delete_event)
    
    # Sets the border width of the window.
    #~ self.window.set_border_width(20)
    
    # Create a 3x2 table
    table = Gtk.Table(3, 2, True)
    
    # Put the table in the main window
    self.window.add(table)

    table.show()
    self.window.show()



if __name__ == "__main__":
  main = DataViewer()
  Gtk.main()
