from abc import abstractmethod, ABC
from dataclasses import dataclass
from pdfs import pdfs
import yaml

FACTOR = 10 ** 6
SIGN = 2
NEED = " "


def time_work_func(func):
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))
        return return_value

    return wrapper


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
    def get_kap_variants(file_name: str):
        with open(file_name, "r", encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.Loader)

    def get_student_full_name(self) -> str:
        global NEED
        for variant in self.read_file_data():
            if self.task_num == variant["№ задания"]:
                NEED = variant["по задачнику КАП"]
                return variant[f"М1О-{self.group_num}"]["full_name"]

    def get_strength_factors(self) -> dict:
        for variant in self.read_file_data():
            if self.task_num == variant["№ задания"]:
                return self.get_kap_variants("KAP_variants.yml")[variant["по задачнику КАП"]]

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
    width: int = 100


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

        self.metal_epsilon = self.metal_elem.material_params["epsilon"]
        self.composite_epsilon = self.composite_elem.material_params["epsilon"]

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

        return round(self.N * self.E1 * self.h1 / self.summa_e_h(), SIGN), \
            round(self.N * self.E2 * self.h2 / self.summa_e_h(), SIGN)

    def thickness(self) -> tuple:

        """
        Исходная ширина пояса h_исх
        """

        if isinstance(self.metal_elem, Shelf) and isinstance(self.composite_elem, Panel):
            return round(self.N / self.sigma_b, SIGN), self.metal_elem.thickness

        elif isinstance(self.composite_elem, Shelf) and isinstance(self.metal_elem, Panel):
            return self.composite_elem.thickness, round(self.N / self.sigma_1b, SIGN)

        else:
            raise Exception(f"Ты дебил? Пытаешься объединить {self.metal_elem.__class__.__name__}"
                            f" c {self.composite_elem.__class__.__name__}!"
                            " Если очень хочешь, то добавь изменения в код!")

    def summa_e_h(self) -> float:
        return round(self.E1 * self.h1 + self.E2 * self.h2, SIGN)


class JointDeformationMethod(Methods):
    """
    Метод совместных деформаций
    """

    def __init__(self, metal_element: Panel or Shelf,
                 composite_element: Panel or Shelf,
                 strength_factors: dict):

        self.metal_elem = metal_element
        self.strength_fact = strength_factors
        self.composite_elem = composite_element

        self.metal_grade = self.metal_elem.material_params["Марка"]
        self.composite_grade = self.composite_elem.material_params["Марка"]

        self.metal_epsilon = self.metal_elem.material_params["epsilon"]
        self.composite_epsilon = self.composite_elem.material_params["epsilon"]

        # для повышения читабельности кода:
        self.E1 = self.metal_elem.material_params["E"]
        self.E2 = self.composite_elem.material_params["E"]

        self.sigma_b = self.metal_elem.material_params["sigma_в"]
        self.sigma_1b = self.composite_elem.material_params["sigma_в"]

        self.N = self.linear_load()

        self.h1 = self.thickness()[0]
        self.h2 = self.thickness()[1]

        self.h_sum = round(self.h1 + self.h2, SIGN)

        self.sigma_x = round(self.N / self.h_sum, SIGN)

        self.h1_ = round(self.h1 / self.h_sum, SIGN)
        self.h2_ = round(self.h2 / self.h_sum, SIGN)

        self.E_x = round(self.E1 * self.h1_ + self.E2 * self.h2_, SIGN)

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

        return round(self.sigma_x * self.E1 / self.E_x, SIGN), \
            round(self.sigma_x * self.E2 / self.E_x, SIGN)

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

        return round(self.N * self.E1 * self.h1_ / self.E_x, SIGN), \
            round(self.N * self.E2 * self.h2_ / self.E_x, SIGN)

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

    def summa_e_h(self) -> float:
        return round(self.E1 * self.h1 + self.E2 * self.h2, SIGN)


class ReductionCoefficientMethod(Methods):
    """
    Метод редукционных коэффициентов
    """

    def __init__(self, metal_element: Panel or Shelf,
                 composite_element: Panel or Shelf,
                 strength_factors: dict):

        self.metal_elem = metal_element
        self.strength_fact = strength_factors
        self.composite_elem = composite_element

        self.metal_grade = self.metal_elem.material_params["Марка"]
        self.composite_grade = self.composite_elem.material_params["Марка"]

        self.metal_epsilon = self.metal_elem.material_params["epsilon"]
        self.composite_epsilon = self.composite_elem.material_params["epsilon"]

        # для повышения читабельности кода:
        self.E1 = self.metal_elem.material_params["E"]
        self.E2 = self.composite_elem.material_params["E"]

        self.sigma_b = self.metal_elem.material_params["sigma_в"]
        self.sigma_1b = self.composite_elem.material_params["sigma_в"]

        self.N = self.linear_load()

        self.h1 = self.thickness()[0]
        self.h2 = self.thickness()[1]

        self.fi1 = round(self.E1 / self.E2, SIGN)
        self.fi2 = round(self.E2 / self.E2, SIGN)

        self.h_red = round(self.h1 * self.fi1 + self.h2 * self.fi2, SIGN)

        self.sigma_red = round(self.N / self.h_red, SIGN)

        self.sigma_1 = round(self.sigma_red * self.fi1, SIGN)
        self.sigma_2 = round(self.sigma_red * self.fi2, SIGN)

    def safety_factor(self) -> tuple[float, float]:

        """
        Коэффициенты запаса прочности
        """

        return round(self.sigma_b / self.sigma_1, SIGN), round(self.sigma_1b / self.sigma_2, SIGN)

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


def data_table_one_method(input_data: GetVariantData, output_data: list):
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")

    for metal_num in input_data.get_list_metals():
        for comp_num in input_data.get_list_composites():
            shelf = StructuralElementFactory(metals).create("полка лонжерона", metal_num)
            panel = StructuralElementFactory(composite).create("панель", comp_num)

            solution = EffortDistributionMethod(shelf, panel, input_data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.summa_e_h(), solution.N1, solution.sigma_1, solution.safety_factor()[0],
                                solution.metal_epsilon])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                '', solution.N2, solution.sigma_2, solution.safety_factor()[1],
                                solution.composite_epsilon])

            output_data.append([])

    return output_data


def data_table_four_method(input_data: GetVariantData, output_data: list):
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")

    a = input_data.get_list_metals()
    a.sort()

    for metal_num in range(a[0], a[-1]):
        for comp_num in input_data.get_list_composites():
            shelf = StructuralElementFactory(composite).create("полка лонжерона", comp_num)
            panel = StructuralElementFactory(metals).create("панель", metal_num)

            solution = EffortDistributionMethod(shelf, panel, input_data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.summa_e_h(), solution.N1, solution.sigma_1, solution.safety_factor()[0],
                                solution.metal_epsilon])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                '', solution.N2, solution.sigma_2, solution.safety_factor()[1],
                                solution.composite_epsilon])

            output_data.append([])

    return output_data


def data_table_two_method(input_data: GetVariantData, output_data: list):
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")

    for metal_num in input_data.get_list_metals():
        for comp_num in input_data.get_list_composites():
            shelf = StructuralElementFactory(metals).create("полка лонжерона", metal_num)
            panel = StructuralElementFactory(composite).create("панель", comp_num)

            solution = JointDeformationMethod(shelf, panel, input_data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.h_sum, solution.h1_, solution.E_x, solution.sigma_x, solution.sigma_1,
                                solution.safety_factor()[0], solution.metal_epsilon])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                '', solution.h2_, " ", " ", solution.sigma_2, solution.safety_factor()[1],
                                solution.composite_epsilon])

            output_data.append([])

    return output_data


def data_table_five_method(input_data: GetVariantData, output_data: list):
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")
    a = input_data.get_list_metals()
    a.sort()

    for metal_num in range(a[0], a[-1]):
        for comp_num in input_data.get_list_composites():
            shelf = StructuralElementFactory(composite).create("полка лонжерона", comp_num)
            panel = StructuralElementFactory(metals).create("панель", metal_num)

            solution = JointDeformationMethod(shelf, panel, input_data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.h_sum, solution.h1_, solution.E_x, solution.sigma_x, solution.sigma_1,
                                solution.safety_factor()[0], solution.metal_epsilon])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                '', solution.h2_, " ", " ", solution.sigma_2, solution.safety_factor()[1],
                                solution.composite_epsilon])

            output_data.append([])

    return output_data


def data_table_three_method(input_data: GetVariantData, output_data: list):
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")

    for metal_num in input_data.get_list_metals():
        for comp_num in input_data.get_list_composites():
            shelf = StructuralElementFactory(metals).create("полка лонжерона", metal_num)
            panel = StructuralElementFactory(composite).create("панель", comp_num)

            solution = ReductionCoefficientMethod(shelf, panel, input_data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.fi1, solution.h_red, solution.sigma_red, solution.sigma_1,
                                solution.safety_factor()[0], solution.metal_epsilon])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                solution.fi2, " ", " ", solution.sigma_2, solution.safety_factor()[1],
                                solution.composite_epsilon])

            output_data.append([])

    return output_data


def data_table_six_method(input_data: GetVariantData, output_data: list):
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")
    a = input_data.get_list_metals()
    a.sort()

    for metal_num in range(a[0], a[-1]):
        for comp_num in input_data.get_list_composites():
            shelf = StructuralElementFactory(composite).create("полка лонжерона", comp_num)
            panel = StructuralElementFactory(metals).create("панель", metal_num)

            solution = ReductionCoefficientMethod(shelf, panel, input_data.get_strength_factors())

            output_data.append(["полка", solution.metal_grade, solution.E1, solution.sigma_b, solution.h1,
                                solution.fi1, solution.h_red, solution.sigma_red, solution.sigma_1,
                                solution.safety_factor()[0], solution.metal_epsilon])

            output_data.append(["панель", solution.composite_grade, solution.E2, solution.sigma_1b, solution.h2,
                                solution.fi2, " ", " ", solution.sigma_2, solution.safety_factor()[1],
                                solution.composite_epsilon])

            output_data.append([])

    return output_data


@time_work_func
def run(task_num: int = 7, group_num: int = 402):
    global NEED

    output_data_1 = [["Элемент", "Марка", "E,МПа", "σ_b,МПа", "h, мм", "ΣE*h,Н/мм", "Ni,Н/мм", "σ_i,МПа", "ηi", "ε,%"]]
    output_data_2 = [["Элемент", "Марка", "E,МПа", "σ_b,МПа", "h,мм", "Σh,мм",
                      "h_", "E_x,МПа", "σ_x,МПа", "σ_i, МПа", "ηi", "ε,%"]]

    output_data_3 = [
        ["Элемент", "Марка", "E,МПа", "σ_b,МПа", "h,мм", "φ_i", "h_ред,мм", "σ_ред,МПа", "σ_i,МПа", "ηi", "ε,%"]]
    output_data_4 = [["Элемент", "Марка", "E,МПа", "σ_b,МПа", "h, мм", "ΣE*h,Н/мм", "Ni,Н/мм", "σ_i,МПа", "ηi", "ε,%"]]
    output_data_5 = [["Элемент", "Марка", "E,МПа", "σ_b,МПа", "h,мм", "Σh,мм",
                      "h_", "E_x,МПа", "σ_x,МПа", "σ_i, МПа", "ηi", "ε,%"]]
    output_data_6 = [
        ["Элемент", "Марка", "E,МПа", "σ_b,МПа", "h,мм", "φ_i", "h_ред,мм", "σ_ред,МПа", "σ_i,МПа", "ηi", "ε,%"]]

    data_one = GetVariantData("task_variants.yml", task_num, group_num)

    pdf = pdfs.CreateReport(f"{data_one.get_student_full_name()} - Лр №1, вар. {task_num}, гр. М1О-{group_num}с.pdf",
                            NEED, group_num, data_one.get_student_full_name())

    pdf.add_table_one_method(data_table_one_method(data_one, output_data_1),
                             "Вариант Ме + КМ", " 1. Метод распределения усилий.")
    pdf.add_table_two_method(data_table_two_method(data_one, output_data_2),
                             " ", " 2. Метод совместных деформаций.")
    pdf.add_table_three_method(data_table_three_method(data_one, output_data_3),
                               " ", " 3. Метод редукционных коэффициентов.")

    pdf.add_table_one_method(data_table_four_method(data_one, output_data_4),
                             "Вариант КМ + Ме", " 1. Метод распределения усилий.")

    pdf.add_table_two_method(data_table_five_method(data_one, output_data_5),
                             " ", " 2. Метод совместных деформаций.")

    pdf.add_table_three_method(data_table_six_method(data_one, output_data_6),
                               " ", " 3. Метод редукционных коэффициентов.")

    pdf.run()


if __name__ == '__main__':

    run(7, 402)
