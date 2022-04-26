from abc import ABC, abstractmethod

import yaml

ENCODING = "utf-8"
SIGN = 2
DELIMITER = ";"

INPUT_DATA = {
    "Изгибающий момент": 180 * 10 ** 6,  #
    "Перерезывающая сила": 120 * 10 ** 6,  #
    "Высота лонжерона": 220,  # мм
    "Ширина пояса лонжерона": 100,  # мм
    "Толщина панели": 2  # мм
}


class ParamInfo:
    """
    Тут хранятся данные об используемых в расчёте величинах
    """

    PARAMETER_ALIASES = {
        "ro": "плотность",
        "gamma": "удельный вес",
        "delta": "толщина монослоя",
        "sigma_в": "предел прочности",
        "E": "модуль упругости",
        "L": "удельная прочность",
        "epsilon": "относительное удлинение металла при растяжении"
    }

    PARAMETER_UNITS = {
        "ro": "[кг/м3]",
        "gamma": "[Н/м3]",
        "delta": "[мм]",
        "sigma_в": "[МПа]",
        "E": "[МПа]",
        "L": "[км]",
        "epsilon": "[%]"
    }

    def __call__(self, alias: str, *args, **kwargs):
        if alias in (self.PARAMETER_ALIASES and self.PARAMETER_UNITS):
            print(f"{alias}: {self.PARAMETER_ALIASES[alias]}, {self.PARAMETER_UNITS[alias]}")
        else:
            raise KeyError("Нет информации о параметре!")


class Solution(ABC):

    @abstractmethod
    def safety_factor(self):
        raise NotImplementedError


class Method(Solution, ABC):
    def __init__(self, shelf_material: dict, panel_material: dict):
        self.shelf_material = shelf_material
        self.panel_material = panel_material

        self.strength()

    def original_belt_thickness(self) -> float:
        return self.linear_load() / self.shelf_material["sigma_в"]

    def linear_load(self) -> float:
        """
        Погонная нагрузка
        """
        return self.strength() / INPUT_DATA["Ширина пояса лонжерона"]

    @staticmethod
    def strength() -> float:
        """
        Сила P
        """
        return INPUT_DATA["Изгибающий момент"] / (.95 * INPUT_DATA["Высота лонжерона"])


class EffortRedistribution(Method, ABC):
    """
    Метод распределения усилий между элементами по жесткости на растяжение
    """

    def __init__(self, shelf_material, panel_material):
        super().__init__(shelf_material, panel_material)

    def safety_factor(self) -> tuple:
        """
        Коэффициент запаса прочности
        """
        return self.shelf_material["sigma_в"] / self.calc_voltages()[0], \
               self.panel_material["sigma_в"] / self.calc_voltages()[1]

    def calc_efforts(self) -> tuple:
        """
        Вычислить усилия N1 и N2
        """
        return self.linear_load() * \
               (self.shelf_material["E"] * self.original_belt_thickness() /
                (self.shelf_material["E"] * self.original_belt_thickness() +
                 self.panel_material["E"] * INPUT_DATA["Толщина панели"])), \
               self.linear_load() * \
               (self.panel_material["E"] * INPUT_DATA["Толщина панели"] /
                (self.shelf_material["E"] * self.original_belt_thickness() +
                 self.panel_material["E"] * INPUT_DATA["Толщина панели"]))

    def calc_voltages(self) -> tuple:
        """
        Вычислить напряжения в элементах
        """
        return self.calc_efforts()[0] / self.original_belt_thickness(), \
               self.calc_efforts()[1] / INPUT_DATA["Толщина панели"]


class StrainCompatibility(Method, ABC):
    """
    Метод совместности деформаций
    """
    pass


class ReductionFactor(Method, ABC):
    """
    Метод редукционных коэффициентов
    """
    pass


class Main:
    main_row = ["Элемент", "Марка", "h", "Ni", "sigma", "eta"]

    def __init__(self):
        with open('material_data.yml', encoding=ENCODING) as file:
            self.materials = yaml.load(file, Loader=yaml.FullLoader)

        self.metal = self.materials["Металл"]["Марка"]
        self.composite = self.materials["Композит"]["Марка"]

        with open("results.csv", "w") as results:
            for i in self.metal.keys():
                for j in self.composite.keys():

                    self.solution = EffortRedistribution(self.metal[i], self.composite[j])

                    self.info = [f"{i} + {j}"]
                    self.shelf = ["Полка", i,
                                  round(self.solution.original_belt_thickness(), SIGN),
                                  round(self.solution.calc_efforts()[0], SIGN),
                                  round(self.solution.calc_voltages()[0], SIGN),
                                  round(self.solution.safety_factor()[0], SIGN)
                                  ]
                    self.panel = ["Панель", j, INPUT_DATA["Толщина панели"],
                                  round(self.solution.calc_efforts()[1], SIGN),
                                  round(self.solution.calc_voltages()[1], SIGN),
                                  round(self.solution.safety_factor()[1], SIGN)]

                    results.write("\n" + DELIMITER.join(map(str, self.info)) + "\n")
                    results.write(DELIMITER.join(map(str, self.main_row)) + "\n")
                    results.write(DELIMITER.join(map(str, self.shelf)) + "\n")
                    results.write(DELIMITER.join(map(str, self.panel)) + "\n")


if __name__ == '__main__':
    Main()

