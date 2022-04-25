from dataclasses import dataclass

ENCODING = "utf-8"


class Parameter:
    def __init__(self, value, alias: str, symbol: str = None, dimension: str = None):
        """
        Инициализация параметров

        Args:
            value: значение
            alias: псевдоним
            symbol: символ
            dimension: размерность

        """
        self.value = value
        self.alias = alias
        self.symbol = symbol
        self.dimension = dimension


class Table:
    def __init__(self, data: list):
        self.data = data

    def get_cell(self, row: str, col: str):
        return self.data[list(self.main_col).index(row)][list(self.main_row).index(col)]

    @property
    def main_row(self):
        for row in self.data[0]:
            yield row

    @property
    def main_col(self):
        for col in self.data:
            yield col[0]


class CsvFileAnalysis:
    def __init__(self, csv_file_name: str):
        with open(csv_file_name, "r", encoding=ENCODING) as self.file:
            self.rows = self.file.readlines()

    def get_data(self):
        for row in self.rows:
            yield row.strip().split(",")


@dataclass
class MetalParam:
    pass


@dataclass
class KMParam:
    pass


@dataclass
class Variants:
    pass


if __name__ == '__main__':
    csv_data = CsvFileAnalysis(csv_file_name="material_parameters/metals.csv")

    table = Table(list(csv_data.get_data()))

    print(table.get_cell("1-1", "ro [кг/м3]"))

    metal = MetalParam()
