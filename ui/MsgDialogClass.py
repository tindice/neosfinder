#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gi.repository import Gtk

class Msg(Gtk.MessageDialog):
  def __init__(self):
    # Create a new dialog
    Gtk.Window.__init__(self, title="Ayuda")
    self.set_keep_above(True)
    #~ self.connect("delete_event", self.hideme)
 
