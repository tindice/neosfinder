#!/usr/bin/python
from gi.repository import Gtk
from PrincipalHandler import Handler

builder = Gtk.Builder()
builder.add_from_file("interfaz.glade")
builder.connect_signals(Handler())

window = builder.get_object("AppWinPrincipal")
window.connect("delete-event", Gtk.main_quit)
window.show_all()

Gtk.main()
