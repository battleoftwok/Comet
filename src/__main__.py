from abc import abstractmethod, ABC
from dataclasses import dataclass
import yaml


FACTOR = 10 ** 6


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
            return yaml.load(file, Loader=yaml.Loader)

    def get_strength_factors(self):
        pass


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

    def create(self, structural_elems, grade_material):
        if structural_elems not in StructuralElementFactory.structural_elems:
            raise Exception(f"{structural_elems} не поддерживается")

        for grade in self.material_data:
            if grade_material in grade.values():
                return StructuralElementFactory.structural_elems[structural_elems](grade)

        raise KeyError(f"Не найдено информации о марке {grade_material}")


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

    def __init__(self, metal_element: Panel | Shelf,
                       composite_element: Panel | Shelf,
                       strength_factors: dict):

        self.strength_fact = strength_factors
        self.metal_elem = metal_element
        self.composite_elem = composite_element

    def safety_factor(self) -> tuple[float, float]:

        # для повышения читабельности формул:
        sigma_b = self.metal_elem.material_params["sigma_в"]
        sigma_1b = self.composite_elem.material_params["sigma_в"]
        sigma1 = self.voltage()[0]
        sigma2 = self.voltage()[1]

        return sigma_b / sigma1, sigma_1b / sigma2

    def voltage(self):

        """
        Returns: Напряжения в элементах
        """

        # для повышения читабельности формул:
        h1 = self.metal_elem.thickness
        h2 = self.composite_elem.width
        N1 = self.linear_effort()[0]
        N2 = self.linear_effort()[1]

        return N1 / h1, N2 / h2

    def linear_effort(self) -> tuple[float, float]:

        """
        Returns: погонные усилия
        """

        # для повышения читабельности формул:
        N = self.strength_fact["N"]
        E1 = self.metal_elem.material_params["E"]
        E2 = self.composite_elem.material_params["E"]
        h1 = self.metal_elem.thickness
        h2 = self.composite_elem.width

        return N * (E1 * h1 / (E1 * h1 + E2 * h2)), N * (E2 * h2 / (E1 * h1 + E2 * h2))

    def original_belt_thickness(self) -> float:
        """
        Исходная ширина пояса h_исх
        """
        return FACTOR * self.strength_fact["N"] / self.metal_elem.material_params["sigma_в"]


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


def run():
    metals = GetMaterialsData("material_data.yml", "Металл")
    composite = GetMaterialsData("material_data.yml", "Композит")

    panel = StructuralElementFactory(metals).create("панель", "B95")
    shelf = StructuralElementFactory(composite).create("полка лонжерона", "КМУ-7л")

    print(EffortDistributionMethod(panel, shelf, {"N": 80}).safety_factor())


if __name__ == '__main__':
    run()
