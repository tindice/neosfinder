#!/usr/bin/python
from gi.repository import Gtk
from PrincipalWindow import PrincipalWindow

win = PrincipalWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
