from pprint import pprint
import yaml

ENCODING = "utf-8"


class InputDataControl:
    """
    Данный класс считывает и возвращает
    информацию из файлов с данными
    """

    def __init__(self, task_number: int, group_number: int):
        self.task_number = task_number
        self.group_name = group_number

        # print(self.get_material_num())
        # print(self.parse_metal_num())
        # print(self.parse_composite_num())

    def __call__(self, *args, **kwargs):
        return None

    def get_input_data(self, index_metal, index_composite) -> tuple:
        return self._search_dict(self.get_metal_info(), index_metal), \
               self._search_dict(self.get_composite_info(), index_composite)

    @staticmethod
    def _search_dict(dictionaries: list, value: int) -> dict:
        for dictionary in dictionaries:
            if value == dictionary["№"]:
                return dictionary

        # for metal, composite in zip(self.get_metal_info(), self.get_composite_info()):
        #     if metal.values()["№"] == index_metal and composite["№"] == index_composite:
        #         return self.get_metal_info()[index_metal], self.get_composite_info()[index_composite]

    def get_composite_indexes(self) -> list:
        composite_elem = self.get_material_num()[1].split("-")

        if int(composite_elem[0]) > int(composite_elem[1]):
            return list([_ for _ in range(int(composite_elem[1]), int(composite_elem[0]) + 1)])

        elif int(composite_elem[0]) < int(composite_elem[1]):
            return list([_ for _ in range(int(composite_elem[0]), int(composite_elem[1]) + 1)])

    def get_metal_indexes(self) -> list:
        return list(map(int, self.get_material_num()[0].split(",")))

    def get_material_num(self) -> tuple:
        """
        Получить номера материалов для полки и для панели
        """
        shelf_materials_index = self.get_group_info()["эл. 1"]
        panel_materials_index = self.get_group_info()["эл. 2"]

        return shelf_materials_index, panel_materials_index

    def get_group_info(self) -> dict:
        """
        Возвращает информацию о том, какие материалы необходимо
        использовать для конкретного варианта задания
        """
        return self.get_variant_info()[f"М1О-{self.group_name}"]

    def get_variant_info(self) -> dict:
        """
        Информация о конкретном варианте задания
        Returns: словарь с информацией по конкретному выбранному варианту
        """

        # TODO: Переделать!
        for line in self.task_variants_info():
            for value in line.values():
                if value == self.task_number:
                    return line

        raise KeyError(f"Задания №{self.task_number} не найдено!")

    def get_composite_info(self):
        return self._materials_info()["Композит"]

    def get_metal_info(self):
        return self._materials_info()["Металл"]

    def task_variants_info(self) -> dict:
        """
        Информация о всех вариантах задания

        Returns: словарь с информацией о вариантах задания
        """
        return self._read_yaml_file("task_variants.yml")["Задание"]

    def get_force_strength(self):
        return self._KAP_variants()[self.get_variant_info()["по задачнику КАП"]]

    def _KAP_variants(self):
        """
        Получить все варианты из методички по КАПу
        """
        return self._read_yaml_file("KAP_variants.yml")

    def _materials_info(self) -> dict:
        """
        Получить сведения о всех материалах (и металлы и КМ)
        """
        return self._read_yaml_file("material_data.yml")

    @staticmethod
    def _read_yaml_file(file_name: str) -> dict:
        """
        Метод считывает всю информацию с YAML файла

        Args:
            file_name: имя файла

        Returns: словарь с данными
        """
        with open(file_name, "r", encoding=ENCODING) as file:
            return yaml.load(file, Loader=yaml.FullLoader)


if __name__ == '__main__':
    data = InputDataControl(7, 402)

    pprint(data.get_metal_indexes())
    pprint(data.get_composite_indexes())

    print(data.get_input_data(data.get_metal_indexes()[0], data.get_composite_indexes()[0]))
