import os
import src.input_data_control as data
import src.solution as solution

ENCODING = "utf-8"
DELIMITER = ";"
SIGN = 2

INPUT_DATA = {
    "Ширина пояса лонжерона": 100,  # мм
    "Толщина панели": 2  # мм
}


class Solve:
    main_row = ["Элемент", "Марка", "h", "Ni", "sigma", "eta"]

    def __init__(self, task_number: int = 7, group_number: int = 402):
        self.data = data.InputDataControl(task_number, group_number)

        self.unite = self.data.get_input_data(self.data.get_metal_indexes()[0],
                                              self.data.get_composite_indexes()[0])

        if "results" not in os.listdir():
            os.mkdir("results")

        with open("results/Ме+КМ.csv", "w", encoding="windows-1251") as results:

            for i in self.data.get_metal_indexes():
                for j in self.data.get_composite_indexes():

                    metal = self.data.get_input_data(i, j)[0]
                    composite = self.data.get_input_data(i, j)[1]

                    self.solve = solution.EffortRedistribution(metal, composite,
                                                               self.data.get_force_strength(),
                                                               INPUT_DATA)

                    self.info = [f"{self.solve.__name__}: {metal['Марка']} + {composite['Марка']}"]
                    self.shelf = ["Полка", metal["Марка"],
                                  round(self.solve.original_belt_thickness(), SIGN),
                                  round(self.solve.calc_efforts()[0], SIGN),
                                  round(self.solve.calc_voltages()[0], SIGN),
                                  round(self.solve.safety_factor()[0], SIGN)
                                  ]
                    self.panel = ["Панель", composite["Марка"],
                                  INPUT_DATA["Толщина панели"],
                                  round(self.solve.calc_efforts()[1], SIGN),
                                  round(self.solve.calc_voltages()[1], SIGN),
                                  round(self.solve.safety_factor()[1], SIGN)]

                    results.write("\n" + DELIMITER.join(map(str, self.info)) + "\n")
                    results.write(DELIMITER.join(map(str, self.main_row)) + "\n")
                    results.write(DELIMITER.join(map(str, self.shelf)) + "\n")
                    results.write(DELIMITER.join(map(str, self.panel)) + "\n")


if __name__ == '__main__':

    INPUT_DATA["Толщина панели"] = int(input("Выберете толщину панели в [мм]: "))
    INPUT_DATA["Ширина пояса лонжерона"] = int(input("Выберете ширину пояса лонжерона в [мм]: "))
    Solve(int(input("Введите номер задания: ")), int(input("Введите номер группы: ")))
    input("\nДанные сохранены в папке results, нажмите\nлюбую клавишу для завершения работы программы...")
