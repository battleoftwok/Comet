import matplotlib.pyplot as plt


def create_plot(data):

    data.pop(0)

    shelf = []
    panel = []

    for elem in data:
        if len(elem) != 0:
            if elem[0] == "полка":
                shelf.append(elem)
            elif elem[0] == "панель":
                panel.append(elem)

    coord_x = []
    coord_y = []

    for i in shelf:
        coord_y.append(i[-2])

    for i in panel:
        coord_x.append(i[-1])


    # plt.plot(coord_x, coord_y)
    # plt.show()

# if __name__ == '__main__':
#     create_plot()
