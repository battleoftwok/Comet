from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import A4
from abc import abstractmethod, ABC
from dataclasses import dataclass
from reportlab.lib import colors
import yaml

FACTOR = 10 ** 6
SIGN = 2


class InputData(ABC):

    @abstractmethod
    def read_file_data(self):
        raise NotImplementedError


class GetMaterialsData(InputData):

    def __init__(self, file_name: str, material: str):
        self.file_name = file_name
        self.material = material

    def read_file_data(self) -> dict:
        with open(self.file_name, "r", encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.Loader)[self.material]


class GetVariantData(InputData):

    def __init__(self, file_name: str, task_number: int, group_number: int):
        self.file_name = file_name
        self.task_num = task_number
        self.group_num = group_number

    def read_file_data(self) -> dict:
        with open(self.file_name, "r", encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.Loader)["Задание"]

    @staticmethod
    def get_KAP_variants(file_name: str):
        with open(file_name, "r", encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.Loader)

    def get_strength_factors(self) -> dict:
        for variant in self.read_file_data():
            if self.task_num == variant["№ задания"]:
                return self.get_KAP_variants("KAP_variants.yml")[variant["по задачнику КАП"]]

    def get_list_metals(self) -> list:
        return list(map(int, self.__search_materials_info()["эл. 1"].split(sep=",")))

    def get_list_composites(self):
        a = list(map(int, self.__search_materials_info()["эл. 2"].split(sep="-")))[0]
        b = list(map(int, self.__search_materials_info()["эл. 2"].split(sep="-")))[1]

        if a >= b:
            return list(range(a, b - 1, -1))

        else:
            return list(range(a, b + 1, 1))

    def __search_materials_info(self) -> dict:

        for variant in self.read_file_data():
            if self.task_num == variant["№ задания"]:
                return variant[f"М1О-{self.group_num}"]


class StructuralElements(ABC):
    """
    Элементы конструкции
    """

    pass


@dataclass
class Shelf(StructuralElements):
    """
    Полка лонжерона
    """

    material_params: dict
    width: int = 100
    thickness: int = 2


@dataclass
class Panel(StructuralElements):
    """
    Панель
    """

    material_params: dict
    thickness: int = 2


class StructuralElementFactory:
    """
    Фабрика конструкционных элементов
    """

    structural_elems = {
        "панель": Panel,
        "полка лонжерона": Shelf
    }

    def __init__(self, material_data: GetMaterialsData):
        self.material_data = material_data.read_file_data()

    def create(self, structural_elems, material_number: int):
        if structural_elems not in StructuralElementFactory.structural_elems:
            raise Exception(f"{structural_elems} не поддерживается")

        for grade in self.material_data:
            if material_number in grade.values():
                return StructuralElementFactory.structural_elems[structural_elems](grade)

        raise KeyError(f"Не найдено информации о марке {material_number}")


class Methods(ABC):
    """
    Методы расчёта напряжённо-деформированного состояния конструкции
    """

    @abstractmethod
    def safety_factor(self):
        """
        Коэффициент запаса прочности
        """
        return NotImplementedError


class EffortDistributionMethod(Methods):
    """
    Метод распределения усилий между элементами по жёсткости на растяжение
    """

    def __init__(self, metal_element: Panel or Shelf,
                 composite_element: Panel or Shelf,
                 strength_factors: dict):

        self.metal_elem = metal_element
        self.strength_fact = strength_factors
        self.composite_elem = composite_element

        self.metal_grade = self.metal_elem.material_params["Марка"]
        self.composite_grade = self.composite_elem.material_params["Марка"]

        # для повышения читабельности кода:
        self.E1 = self.metal_elem.material_params["E"]
        self.E2 = self.composite_elem.material_params["E"]

        self.sigma_b = self.metal_elem.material_params["sigma_в"]
        self.sigma_1b = self.composite_elem.material_params["sigma_в"]

        self.N = self.linear_load()

        self.h1 = self.thickness()[0]
        self.h2 = self.thickness()[1]

        self.N1 = self.linear_effort()[0]
        self.N2 = self.linear_effort()[1]

        self.sigma_1 = self.voltage()[0]
        self.sigma_2 = self.voltage()[1]

    def safety_factor(self) -> tuple[float, float]:

        """
        Коэффициенты запаса прочности
        """

        return round(self.sigma_b / self.sigma_1, SIGN), round(self.sigma_1b / self.sigma_2, SIGN)

    def voltage(self):

        """
        Returns: Напряжения в элементах
        """

        return round(self.N1 / self.h1, SIGN), round(self.N2 / self.h2, SIGN)

    def linear_load(self) -> float:

        """
        Погонная нагрузка N
        """

        P = self.strength()
        B = self.metal_elem.width

        return P / B

    def strength(self) -> float:
        """
        Сила P
        """
        return FACTOR * self.strength_fact["Мизг"] / (.95 * self.strength_fact["H"])

    def linear_effort(self) -> tuple[float, float]:

        """
        Returns: погонные усилия N1 и N2
        """

        return round(self.N * self.E1 * self.h1 / self.summa_E_h(), SIGN),\
               round(self.N * self.E2 * self.h2 / self.summa_E_h(), SIGN)

    def thickness(self) -> tuple:

        """
        Исходная ширина пояса h_исх
        """

        if isinstance(self.metal_elem, Shelf) and isinstance(self.composite_elem, Panel):
            return round(self.N / self.sigma_b, SIGN), self.metal_elem.thickness

        elif isinstance(self.composite_elem, Shelf) and isinstance(self.metal_elem, Panel):
            return round(self.N / self.sigma_1b, SIGN), self.composite_elem.thickness

        else:
            raise Exception(f"Ты дебил? Пытаешься объединить {self.metal_elem.__class__.__name__}"
                            f" c {self.composite_elem.__class__.__name__}!"
                            " Если очень хочешь, то добавь изменения в код!")

    def summa_E_h(self) -> float:
        return round(self.E1 * self.h1 + self.E2 * self.h2, SIGN)


class JointDeformationMethod(Methods):
    """
    Метод совместных деформаций
    """

    def safety_factor(self):
        pass


class ReductionCoefficientMethod(Methods):
    """
    Метод редукционных коэффициентов
    """

    def safety_factor(self):
        pass


class CreateTable:
    def __init__(self, data: list, fontname: str, fontsize: int):
        self.data = data
        self.font_name = fontname
        self.font_size = fontsize

        self.create_table()

    def create_table(self):
        pdf_file = canvas.Canvas("table.pdf", pagesize=A4)

        elements = []

        table = Table(self.data, colWidths=[self.font_size + 55 for _ in range(len(self.data[0]))],
                      rowHeights=[self.font_size + 10 for _ in range(len(self.data))])

        table_style = TableStyle([("BOX", (0, 0), (-1, -1), 2, colors.black),
                                  ("GRID", (0, 0), (-1, -1), 1, colors.black),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                  ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                  ("FONTNAME", (0, 0), (-1, -1), self.font_name),
                                  ("TEXTCOLOR", (0, 0), (len(self.data[0]), 0), colors.green),
                                  ("FONTNAME", (0, 0), (len(self.data[0]), 0), "DejaVuSerif"),
                                  ("FONTSIZE", (0, 0), (-1, -1), self.font_size)])

        table.setStyle(table_style)
        elements.append(table)

        table.wrapOn(pdf_file, 550, 840)

        table.drawOn(pdf_file, 5, 200)
        pdf_file.save()


def run(task_num: int = 7, group_num: int = 402):

    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'DejaVuSerif'
    styles['Heading1'].fontName = 'DejaVuSerif'

    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8'))

    output_data = [["Элемент","Марка", "E, MPa", "σ_b, MPa", "h, mm", "Σ E*h, N/mm", "Ni, N/mm", "σ_i, MPa", "ηi"]]

    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")

    data = GetVariantData("task_variants.yml", task_num, group_num)

    for metal_num in data.get_list_metals():
        for comp_num in data.get_list_composites():
            shelf = StructuralElementFactory(metals).create("полка лонжерона", metal_num)
            panel = StructuralElementFactory(composite).create("панель", comp_num)
            solution = EffortDistributionMethod(shelf, panel, data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.summa_E_h(), solution.N1, solution.sigma_1, solution.safety_factor()[0]])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                '', solution.N2, solution.sigma_2, solution.safety_factor()[1]])

            output_data.append([])

        CreateTable(output_data, "DejaVuSerif", 10)


if __name__ == '__main__':
    run(1, 402)
