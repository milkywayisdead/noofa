"""
Для построения pdf-документа отчёта.
"""
from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PdfReport:
    def __init__(self, path, **options):
        self._current_x, self._current_y = 0, 0
        self._doc = SimpleDocTemplate(filename=path, pagesize=landscape(A4))
        self._story = []

    def add_title(self, **options):
        return self

    def add_text(self, **options):
        """
        Добавление текста.
        """
        return self

    def add_pagebreak(self):
        """
        Добавление разрыва страницы.
        """
        self._story.append(PageBreak())

    def add_table(self, data):
        """
        Добавление таблицы.
        data - содержимое таблицы в виде списка списков -
        т.е. каждый список содержит значения ячеек соответствующей
        строки. Заголовок должен передаваться в этом списке первым элементом.
        """
        pdfmetrics.registerFont(TTFont('DejaVuSerif','DejaVuSerif.ttf', 'UTF-8'))
        table_style = TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), 'DejaVuSerif'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table = Table(data)
        table.setStyle(table_style)
        self._story.append(table)
        return self

    def add_image(self, img):
        """
        Добавление изображения.
        img - изображение в виде потока байтов.
        """
        image = Image(BytesIO(img), width=self._doc.width - 100, height=self._doc.height - 100)
        self._story.append(image)
        return self
    
    def save(self):
        self._doc.build(self._story)
