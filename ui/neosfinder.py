#!/usr/bin/python
from gi.repository import Gtk

class PrincipalWindow(Gtk.Window):
    
    # Declaramos constantes y preferencias de configuracion
    ANCHO_VENTANA = 640
    ALTO_VENTANA = 480
    global TITULO = "NeosFinder v0.1"
    
    def __init__(self):
        ANCHO_VENTANA = 640
        ALTO_VENTANA = 480
        #~ TITULO = "NeosFinder v0.1"
        Gtk.Window.__init__(self, title=TITULO, default_width=ANCHO_VENTANA, default_height=ALTO_VENTANA)
        
        self.button = Gtk.Button(label="Cliqueame :-)")
        self.button.connect("clicked", self.on_button_clicked)
        self.add(self.button)
        #~ self.default_height = 200

    def on_button_clicked(self, widget):
        print("Hola mundo UI!!")

win = PrincipalWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
