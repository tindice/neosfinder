from gi.repository import Gtk

# Declaramos constantes y preferencias de configuracion
ANCHO_VENTANA = 640
ALTO_VENTANA = 480
TITULO = "NeosFinder v0.1"

class PrincipalWindow(Gtk.Window):
  
    def __init__(self):
        Gtk.Window.__init__(self, title=TITULO, default_width=ANCHO_VENTANA, default_height=ALTO_VENTANA)
        
        self.button = Gtk.Button(label="Cliqueame :-)")
        self.button.connect("clicked", self.on_button_clicked)
        self.add(self.button)

    def on_button_clicked(self, widget):
        print("Hola mundo UI!!")
