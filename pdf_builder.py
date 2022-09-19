"""
Для построения pdf-документа отчёта.
"""
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import LongTable, TableStyle


class PdfReport:
    def __init__(self, path, **options):
        self._path = path
        self._page = options.get('page', A4)
        self._canvas = canvas.Canvas(self._path, pagesize=self._page)
        self._current_x, self._current_y = 0, 0

    @property
    def canvas(self):
        return self._canvas

    def add_title(self, **options):
        return self

    def add_text(self, **options):
        """
        Добавление текста.
        """
        return self

    def add_table(self, **options):
        """
        Добавление таблицы.
        """
        header = options.get('header', None)
        table_data = options['data']
        x, y = options['x'], options['y']
        t = LongTable(table_data)
        t.setStyle(TableStyle(
            [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
            ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
            ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
            ('ALIGN', (1,1), (-1,-1), 'RIGHT')]
        ))
        t.wrapOn(self.canvas, *self._page)
        t.drawOn(self.canvas, x, y)
        self.canvas.showPage()
        return self

    def add_image(self, **options):
        """
        Добавление изображения.
        Аргумент image_as_bytes необходимо передавать в виде набора байтов.
        """
        raw_img = options.pop('image_as_bytes')
        x, y = options.pop('x'), options.pop('y')
        image = ImageReader(io.BytesIO(raw_img))
        self.canvas.drawImage(image, x, y, **options)
        return self

    def test(self):
        import plotly.express as px
        fig = px.line([1,22,45,33], [13,44,91, 7])
        raw = fig.to_image()
        self.add_image(image_as_bytes=raw, x=20, y=20, width=400, height=100)
        self.add_table(data=[[1,2,3],[4,5,6],[7,8,9]], x=50, y=50)
        self.canvas.showPage()
    
    def save(self):
        self.canvas.save()
