from abc import ABC, abstractmethod

FACTOR = 10 ** 6


class Solution(ABC):

    @abstractmethod
    def safety_factor(self):
        raise NotImplementedError


class Method(Solution, ABC):
    def __init__(self, first_material_params: dict, second_material_params: dict,
                 strength_factors: dict, geom_params: dict):

        self.first_material = first_material_params
        self.second_material = second_material_params
        self.strength_factors = strength_factors
        self.geom_params = geom_params

    def original_belt_thickness(self) -> float:
        """
        Исходная ширина пояса h_исх
        """
        return self.linear_load() / self.first_material["sigma_в"]

    def linear_load(self) -> float:
        """
        Погонная нагрузка
        """
        return self.strength() / self.geom_params["Ширина пояса лонжерона"]

    def strength(self) -> float:
        """
        Сила P
        """
        return FACTOR * self.strength_factors["Мизг"] / (.95 * self.strength_factors["H"])


class EffortRedistribution(Method, ABC):
    """
    Метод распределения усилий между элементами по жесткости на растяжение
    """

    __name__ = "Метод распределения усилий"

    def __init__(self, first_material_params, second_material_params, strength_factors: dict, geom_params: dict):
        super().__init__(first_material_params, second_material_params, strength_factors, geom_params)

    def safety_factor(self) -> tuple:
        """
        Коэффициент запаса прочности
        """
        return self.first_material["sigma_в"] / self.calc_voltages()[0], \
               self.second_material["sigma_в"] / self.calc_voltages()[1]

    def calc_efforts(self) -> tuple:
        """
        Вычислить усилия N1 и N2
        """
        return self.linear_load() * \
               (self.first_material["E"] * self.original_belt_thickness() /
                (self.first_material["E"] * self.original_belt_thickness() +
                 self.second_material["E"] * self.geom_params["Толщина панели"])), \
               self.linear_load() * \
               (self.second_material["E"] * self.geom_params["Толщина панели"] /
                (self.first_material["E"] * self.original_belt_thickness() +
                 self.second_material["E"] * self.geom_params["Толщина панели"]))

    def calc_voltages(self) -> tuple:
        """
        Вычислить напряжения в элементах
        """
        return self.calc_efforts()[0] / self.original_belt_thickness(), \
               self.calc_efforts()[1] / self.geom_params["Толщина панели"]


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


if __name__ == '__main__':
    pass
