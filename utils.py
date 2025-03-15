from kivy.graphics import Fbo
from kivy.core.image import Image as CoreImage

def save_widget_as_image(widget, filename):
    # Erstelle ein Fbo in der Größe des Widgets
    fbo = Fbo(size=widget.size)
    # Render den Canvas des Widgets ins Fbo
    fbo.add(widget.canvas)
    fbo.draw()
    # Speichere das Ergebnis als PNG
    texture = fbo.texture
    CoreImage(texture).save(filename)

