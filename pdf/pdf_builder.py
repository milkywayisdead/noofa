"""
Для построения pdf-документа отчёта.
"""
from io import BytesIO

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    Image,
    Table,
    PageBreak, 
    TableStyle,
    Paragraph,
    Spacer,
    SimpleDocTemplate,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch


#  фикс для корректного отображения кириллицы
pdfmetrics.registerFont(TTFont('DejaVuSerif','DejaVuSerif.ttf', 'UTF-8'))


class PdfReport:
    """
    Класс конструктора отчёта в виде pdf.
    """
    def __init__(self, filename, **options):
        orientation = options.get('orientation', 'portrait')
        self._orientation = orientation
        if orientation == 'landscape':
            pagesize = landscape(A4)
        else:
            pagesize = A4
        self._doc = SimpleDocTemplate(filename=filename, pagesize=pagesize)

        #  "история" - список операций (классы из reportlab.platypus),
        #  которые выполняются при построении документа
        self._story = []

    def add_pagebreak(self):
        """
        Добавление разрыва страницы.
        """
        self._story.append(PageBreak())

    def add_table(self, data, **options):
        """
        Добавление таблицы.
        data - содержимое таблицы в виде списка списков -
        т.е. каждый список содержит значения ячеек соответствующей
        строки. Заголовок должен передаваться в этом списке первым элементом.
        """
        default_font = 'DejaVuSerif'
        default_font_size = 8

        title = options.get('title', '')
        title_font = options.get('title_font', 'DejaVuSerif')
        title_font_size = options.get('title_font_size', 14)
        font = options.get('font', default_font)
        font_size = options.get('font_size', default_font_size)
        table_style = TableStyle([
            ('LINEABOVE', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.black),
            ('FONT', (0, 0), (-1, -1), font),
            ('FONTSIZE', (0, 0), (-1, -1), font_size),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table = Table(data)
        table.setStyle(table_style)

        if title:
            style = ParagraphStyle(
                name='table_title',
                fontName=title_font,
                alignment=1,
                fontSize=title_font_size)
            self._story.append(Paragraph(text=title, style=style))
            self._story.append(Spacer(0, 10))

        self._story.append(table)
        self.add_pagebreak()
        return self

    def add_image(self, img):
        """
        Добавление изображения.
        img - изображение в виде последовательности байт.
        """
        image = Image(BytesIO(img))
        w, h = self._doc.width, self._doc.height
        if self._orientation == 'landscape':
            w, h = h, w
        image._restrictSize(w, h)
        self._story.append(image)
        self.add_pagebreak()
        return self

    def save(self):
        """
        Сохранение pdf-документа.
        """
        self._doc.build(self._story)

    def from_list(self, components_list):
        """
        Формирование документа из списка компонентов.
        Список должен содержать экземпляры классов компонентов
        отчёта. У экземпляров должен быть атрибут type, указывающий
        на тип компонента - таблица/график ('table', 'figure').
        У компонентов-таблиц должно быть свойство data, возвращающее
        список списков значений для таблицы. У компонентов-графиков
        должен быть метод to_bytes, возвращающий изображение графика
        в виде байт.
        """
        for component in components_list:
            type_ = component.type
            if type_ == 'table':
                _ = self.add_table(data=component.data, title=component.title_text)
            elif type_ == 'figure':
                _ = self.add_image(component.to_bytes())
        return self
