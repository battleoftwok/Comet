from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import Table, TableStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


FONT = "Times"
FONTSIZE = 12
PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]

pdfmetrics.registerFont(TTFont(FONT, f'{FONT}.ttf', 'UTF-8'))

# "русификатор":

styles = getSampleStyleSheet()

styles['Normal'].fontName = FONT
styles['Heading1'].fontName = FONT
styles['Heading1'].spaceBefore = 70
styles['Heading2'].fontName = FONT
styles['Heading2'].spaceAfter = 20

mai = Image("mai.png")
mai.drawHeight = .85 * inch
mai.drawWidth = 1 * inch

title_head_1 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=12,
                              leading=18, spaceBefore=1, spaceAfter=1, alignment=TA_CENTER)

title_head_2 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=16,
                              leading=18, spaceBefore=120, spaceAfter=5, alignment=TA_CENTER)

title_head_3 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=16,
                              leading=18, spaceBefore=40, spaceAfter=1, alignment=TA_CENTER)

title_head_4 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=16,
                              leading=18, spaceBefore=5, spaceAfter=1, alignment=TA_CENTER)

title_head_5 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=14,
                              leading=18, spaceBefore=10, spaceAfter=1, alignment=TA_CENTER)

title_head_6 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=12,
                              leading=18, spaceBefore=110, spaceAfter=1, alignment=TA_LEFT)

title_head_7 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=12,
                              leading=18, spaceBefore=5, spaceAfter=1, alignment=TA_LEFT)

title_head_8 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontName=FONT, fontSize=12,
                              leading=18, spaceBefore=70, spaceAfter=1, alignment=TA_CENTER)


class CreateReport:
    PS = ParagraphStyle

    story = []

    strings = [
        ["МОСКОВСКИЙ АВИАЦИОННЫЙ ИНСТИТУТ", title_head_1],
        ["(национальный исследовательский университет)", title_head_1],
        ['Кафедра 101 "Проектирование и сертификация АТ"', title_head_1],
        ["Лабораторная работа №1", title_head_2],
        ["по дисциплине", title_head_1],
        ['"Основы проектирования конструкций самолёта', title_head_1],
        [' из композиционных материалов"', title_head_1],
        ['"Проектирование и расчёт составного', title_head_3],
        [' пояса лонжерона"', title_head_4],
        [None, title_head_5],
        [None, title_head_6],
        ["Проверил: профессор" + 75 * " " + "Попов Ю.И.", title_head_7],
        ["Москва 2022", title_head_8]]

    indents = [68, 88, 108, 300, 320, 340, 360, 420, 440, 470, 670, 690, 790]

    def __init__(self, file_name: str, var_task: str, group: int, name: str):
        self.file_name = file_name
        self.var_task = var_task
        self.group = group
        self.name = name

        self.report = SimpleDocTemplate(self.file_name, pagesize=A4)

        self._add_title()

    def _add_title(self):
        self.strings[9][0] = f"Задание {self.var_task}"
        self.strings[10][0] = f"Выполнил: студент группы М1О-{self.group}С-18" + 40 * " " + f"{self.name}"

        for i in self.strings:
            self.story.append(Paragraph(i[0], i[1]))

        self.story.insert(3, Paragraph(" ", title_head_5))
        self.story.insert(4, mai)

    def add_table_one_method(self, data, head_1: str, head_2: str):

        table = Table(data, colWidths=[len(str(i)) + 52 for i in data[0]],
                      rowHeights=[FONTSIZE + 15 for _ in range(len(data))])

        paragraph = Paragraph(head_1, styles['Heading1'])
        paragraph_2 = Paragraph(head_2, styles['Heading2'])

        self.story.append(paragraph)
        self.story.append(paragraph_2)

        list_style = [("BOX", (0, 0), (-1, -1), 2, colors.black),
                      ("GRID", (0, 0), (-1, -1), 1, colors.black),
                      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                      ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                      ("FONTNAME", (0, 0), (-1, -1), FONT),
                      ("TEXTCOLOR", (0, 0), (len(data[0]), 0), colors.green),
                      ("FONTNAME", (0, 0), (len(data[0]), 0), FONT),
                      ("FONTSIZE", (0, 0), (-1, -1), FONTSIZE)]

        add_list_style = \
            list([('SPAN', (5, il), (5, j)) for il, j in zip(range(1, len(data), 3),
                                                             range(2, len(data) + 1, 3))])

        add_two_style = [('SPAN', (0, il), (len(data[0]) - 1, il)) for il in range(3, len(data), 3)]

        add_three_style = list([('BACKGROUND',
                                 (len(data[0]) - 2, col),
                                 (len(data[0]) - 2, col),
                                 colors.lightyellow) for col in range(1, len(data), 3)
                                if data[col][len(data[0]) - 2] < 1])

        add_four_style = list([('TEXTCOLOR',
                                (len(data[0]) - 2, col),
                                (len(data[0]) - 2, col),
                                colors.darkred) for col in range(1, len(data), 3)
                               if data[col][len(data[0]) - 2] < 1])

        add_five_style = list([('BACKGROUND',
                                (len(data[0]) - 2, col),
                                (len(data[0]) - 2, col),
                                colors.lightyellow) for col in range(2, len(data), 3)
                               if data[col][len(data[0]) - 2] < 1])

        add_six_style = list([('TEXTCOLOR',
                               (len(data[0]) - 2, col),
                               (len(data[0]) - 2, col),
                               colors.darkred) for col in range(2, len(data), 3)
                              if data[col][len(data[0]) - 2] < 1])

        list_style += add_list_style
        list_style += add_two_style
        list_style += add_three_style
        list_style += add_four_style
        list_style += add_five_style
        list_style += add_six_style

        table_style = TableStyle(list_style)

        table.setStyle(table_style)

        self.story.append(table)

    def add_table_two_method(self, data, head_1: str, head_2: str):

        table = Table(data, colWidths=[len(str(i)) + 43 for i in data[0]],
                      rowHeights=[FONTSIZE + 15 for _ in range(len(data))])

        paragraph = Paragraph(head_1, styles['Heading1'])
        paragraph_2 = Paragraph(head_2, styles['Heading2'])

        self.story.append(paragraph)
        self.story.append(paragraph_2)

        list_style = [("BOX", (0, 0), (-1, -1), 2, colors.black),
                      ("GRID", (0, 0), (-1, -1), 1, colors.black),
                      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                      ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                      ("FONTNAME", (0, 0), (-1, -1), FONT),
                      ("TEXTCOLOR", (0, 0), (len(data[0]), 0), colors.green),
                      ("FONTNAME", (0, 0), (len(data[0]), 0), FONT),
                      ("FONTSIZE", (0, 0), (-1, -1), FONTSIZE)]

        add_list_style = \
            list([('SPAN', (5, il), (5, j)) for il, j in zip(range(1, len(data), 3),
                                                             range(2, len(data) + 1, 3))])

        add_list_style_two = \
            list([('SPAN', (7, il), (7, j)) for il, j in zip(range(1, len(data), 3),
                                                             range(2, len(data) + 1, 3))])

        add_list_style_three = \
            list([('SPAN', (8, il), (8, j)) for il, j in zip(range(1, len(data), 3),
                                                             range(2, len(data) + 1, 3))])

        add_two_style = list([('SPAN', (0, il), (len(data[0]) - 1, il)) for il in range(3, len(data), 3)])

        add_three_style = list([('BACKGROUND',
                                 (len(data[0]) - 2, col),
                                 (len(data[0]) - 2, col),
                                 colors.lightyellow) for col in range(1, len(data), 3)
                                if data[col][len(data[0]) - 2] < 1])

        add_four_style = list([('TEXTCOLOR',
                                (len(data[0]) - 2, col),
                                (len(data[0]) - 2, col),
                                colors.darkred) for col in range(1, len(data), 3)
                               if data[col][len(data[0]) - 2] < 1])

        add_five_style = list([('BACKGROUND',
                                (len(data[0]) - 2, col),
                                (len(data[0]) - 2, col),
                                colors.lightyellow) for col in range(2, len(data), 3)
                               if data[col][len(data[0]) - 2] < 1])

        add_six_style = list([('TEXTCOLOR',
                               (len(data[0]) - 2, col),
                               (len(data[0]) - 2, col),
                               colors.darkred) for col in range(2, len(data), 3)
                              if data[col][len(data[0]) - 2] < 1])

        list_style += add_list_style
        list_style += add_list_style_two
        list_style += add_list_style_three
        list_style += add_two_style
        list_style += add_three_style
        list_style += add_four_style
        list_style += add_five_style
        list_style += add_six_style

        table_style = TableStyle(list_style)

        table.setStyle(table_style)

        self.story.append(table)

    def add_table_three_method(self, data, head_1: str, head_2: str):

        table = Table(data, colWidths=[len(str(i)) + 47 for i in data[0]],
                      rowHeights=[FONTSIZE + 15 for _ in range(len(data))])

        paragraph = Paragraph(head_1, styles['Heading1'])
        paragraph_2 = Paragraph(head_2, styles['Heading2'])

        self.story.append(paragraph)
        self.story.append(paragraph_2)

        list_style = [("BOX", (0, 0), (-1, -1), 2, colors.black),
                      ("GRID", (0, 0), (-1, -1), 1, colors.black),
                      ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                      ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                      ("FONTNAME", (0, 0), (-1, -1), FONT),
                      ("TEXTCOLOR", (0, 0), (len(data[0]), 0), colors.green),
                      ("FONTNAME", (0, 0), (len(data[0]), 0), FONT),
                      ("FONTSIZE", (0, 0), (-1, -1), FONTSIZE)]

        add_list_style_two = \
            list([('SPAN', (7, il), (7, j)) for il, j in zip(range(1, len(data), 3),
                                                             range(2, len(data) + 1, 3))])

        add_list_style_three = \
            list([('SPAN', (6, il), (6, j)) for il, j in zip(range(1, len(data), 3),
                                                             range(2, len(data) + 1, 3))])

        add_two_style = list([('SPAN', (0, il), (len(data[0]) - 1, il)) for il in range(3, len(data), 3)])

        add_three_style = list([('BACKGROUND',
                                 (len(data[0]) - 2, col),
                                 (len(data[0]) - 2, col),
                                 colors.lightyellow) for col in range(1, len(data), 3)
                                if data[col][len(data[0]) - 2] < 1])

        add_four_style = list([('TEXTCOLOR',
                                (len(data[0]) - 2, col),
                                (len(data[0]) - 2, col),
                                colors.darkred) for col in range(1, len(data), 3)
                               if data[col][len(data[0]) - 2] < 1])

        add_five_style = list([('BACKGROUND',
                                (len(data[0]) - 2, col),
                                (len(data[0]) - 2, col),
                                colors.lightyellow) for col in range(2, len(data), 3)
                               if data[col][len(data[0]) - 2] < 1])

        add_six_style = list([('TEXTCOLOR',
                               (len(data[0]) - 2, col),
                               (len(data[0]) - 2, col),
                               colors.darkred) for col in range(2, len(data), 3)
                              if data[col][len(data[0]) - 2] < 1])

        list_style += add_list_style_two
        list_style += add_list_style_three
        list_style += add_two_style
        list_style += add_three_style
        list_style += add_four_style
        list_style += add_five_style
        list_style += add_six_style

        table_style = TableStyle(list_style)

        table.setStyle(table_style)

        self.story.append(table)

    def run(self):
        self.report.build(self.story)


if __name__ == '__main__':
    a = CreateReport("my_title.pdf", "Л-2-6", 402, "Коновалов Ф.")
    a.add_table_one_method([[1, 2, 3], [4, 5, 6]], "Вариант Ме + КМ", "1. Метод распределения усилий.")
    a.add_table_one_method([[5, 5, 3], [4, 5, 6]], " ", "1. Метод редукционных коэфф.")
    a.run()
