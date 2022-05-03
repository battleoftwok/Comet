import itertools
from random import randint
from statistics import mean

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args)


def export_to_pdf(data):
    c = canvas.Canvas("grid-students.pdf", pagesize=A4)
    w, h = A4
    max_rows_per_page = 45
    # Margin.
    x_offset = 50
    y_offset = 50
    # Space between rows.
    padding = 15

    x_list = [x + x_offset for x in [0, 200, 250, 300, 350, 400, 480]]
    y_list = [h - y_offset - inn * padding for inn in range(max_rows_per_page + 1)]

    for rows in grouper(data, max_rows_per_page):
        rows = tuple(filter(bool, rows))
        c.grid(x_list, y_list[:len(rows) + 1])
        for y, row in zip(y_list[:-1], rows):
            for x, cell in zip(x_list, row):
                c.drawString(x + 2, y - padding + 3, str(cell))
        c.showPage()

    c.save()


data_1 = [("NAME", "GR. 1", "GR. 2", "GR. 3", "AVG", "STATUS")]

for i in range(1, 101):
    exams = [randint(0, 10) for _ in range(3)]
    avg = round(mean(exams), 2)
    state = "Approved" if avg >= 4 else "Disapproved"
    data_1.append((f"Student {i}", *exams, avg, state))

export_to_pdf(data_1)
