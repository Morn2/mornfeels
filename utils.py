from fpdf import FPDF
from kivy.graphics import Fbo, ClearBuffers, ClearColor, Scale, Translate
from kivy.core.image import Image as CoreImage

def save_widget_as_image(widget, filename, scale_factor=3):
    # 3 = 300% der Widget-Größe
    w = int(widget.width * scale_factor)
    h = int(widget.height * scale_factor)

    fbo = Fbo(size=(w, h), with_stencilbuffer=True)
    with fbo:
        ClearColor(1,1,1,1)
        ClearBuffers()
        # Flip + verschieben
        Scale(1, -1, 1)
        Translate(0, -h, 0)

    # Skaliere das Widget-Canvas
    # Trick: Man erstellt eine eigene Canvas, in die man das Widget rendert,
    #        aber das erfordert, das Widget "umzumodeln".
    # Oder man kopiert den Canvas-Inhalt – aber das ist in Kivy limitiert.
    # Besser: Den Graph selbst größer darstellen, bevor man ihn aufnimmt.

    fbo.add(widget.canvas)
    fbo.draw()
    texture = fbo.texture
    CoreImage(texture).save(filename)

#PDF Generieren----------------------------------

def generate_pdf_from_images(image_paths, output_pdf):
    # Hier z. B. im Hochformat (P) mit A4
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)

    for img_path in image_paths:
        pdf.add_page()
        # Bildbreite so setzen, dass es fast seitenfüllend ist
        # epw = effective page width = 210 mm - left_margin - right_margin
        epw = pdf.w - 2 * pdf.l_margin
        # x=pdf.l_margin, y=pdf.t_margin positionieren
        pdf.image(img_path, x=pdf.l_margin, y=pdf.t_margin, w=epw)
    pdf.output(output_pdf, "F")

