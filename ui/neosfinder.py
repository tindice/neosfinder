#!/usr/bin/python
# -*- coding: utf-8 -*-
from gi.repository import Gtk
from PrincipalHandler import Handler

ARCHIVO_UI = "interfaz.glade"
ID_VENTANA = "AppWinPrincipal"
SENIAL_CIERRA_VENTANA = "delete-event"

# Crea una instancia de Builder en builder
builder = Gtk.Builder()

# Carga la definicion de la interfaz de usuario del archivo xml de Glade
builder.add_from_file(ARCHIVO_UI)

# Conecta las 'señales' (eventos) para que vinculen a los métodos declarados en la clase Handler
builder.connect_signals(Handler())

# Crea una instancia window a partir del objeto con id en builder
window = builder.get_object(ID_VENTANA)

# Conecta la señal "delete_event" al metodo Gtk.main_quit que cierra el loop Gtk principal
window.connect(SENIAL_CIERRA_VENTANA, Gtk.main_quit)

# Hace visibles todos los objetos mostrables hijos de window incluido si mismo
window.show_all()

# Inicia y mantiene corriendo el loop principal de la UI. Sale en main_quit
Gtk.main()
