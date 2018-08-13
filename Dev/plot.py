import matplotlib.pyplot as plt
from collections import OrderedDict

def plot_depth4(data):
    ELEM_LIST=["pos", "neg", "tot", "total"]
    data_matrix=OrderedDict()

    for year in data:
        for limit in data[year]:
            for period in data[year][limit]:
                if period not in data_matrix:
                    data_matrix[period]=OrderedDict()

                for elem in data[year][limit][period]:
                    if elem in ELEM_LIST:
                        if elem not in data_matrix[period]:
                            data_matrix[period][elem]=OrderedDict()
                            for lim in data[year]:
                                data_matrix[period][elem][limit]={"xaxis":[], "yaxis":[]}

                        data_matrix[period][elem][limit]["xaxis"].append(year)
                        data_matrix[period][elem][limit]["yaxis"].append(data[year][limit][period][elem])

    print(data_matrix)
    column=0
    rows=0
    plt.figure(1)
    for period in data_matrix:
        column+=1
        for elem in data_matrix[period]:
            rows+=1
            sub_data=data_matrix[period][elem]
            for limit in sub_data:
                plt.plot(sub_data[limit]["xaxis"], sub_data[limit]["yaxis"])
    plt.show()
