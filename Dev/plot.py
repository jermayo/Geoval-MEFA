import matplotlib.pyplot as plt
from collections import OrderedDict

def get_data(sub_data_matrix, sub_data, lim_list, limit, year):

    for elem in sub_data:
        if elem not in sub_data_matrix:
            sub_data_matrix[elem]=OrderedDict()
            for lim in lim_list:
                sub_data_matrix[elem][lim]={"xaxis":[], "yaxis":[]}
        sub_data_matrix[elem][limit]["xaxis"].append(year)
        sub_data_matrix[elem][limit]["yaxis"].append(sub_data[elem])

    return sub_data_matrix

# def build_plot(ax, data_matrix, total_row, total_column, column=0, extra_text=""):
#     row=0
#     for elem in data_matrix:
#         for lim in data_matrix[elem]:
#             if total_row==1 and total_column==1:
#                 n=ax
#             elif total_column==1 or total_row==1:
#                 n=ax[row]
#             else:
#                 n=ax[row][column]
#             n.set_title(extra_text+str(elem))
#             n.plot(data_matrix[elem][lim]["xaxis"], data_matrix[elem][lim]["yaxis"], label=str(lim))
#             n.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#         row+=1

def build_plot(data_matrix, title, extra_text="", fig_numb=1):
    for elem in data_matrix:
        plt.figure(title+str(fig_numb))
        plt.title(extra_text+str(elem))
        for lim in data_matrix[elem]:
            plt.plot(data_matrix[elem][lim]["xaxis"], data_matrix[elem][lim]["yaxis"], label=str(lim))
        plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
        fig_numb+=1
    return fig_numb

def plot_data(data, data_depth, title):

    data_matrix=OrderedDict()
    for year in data:
        lim_list=[i for i in data[year]]
        break
    for year in data:
        for limit in data[year]:
            if data_depth==4:
                for period in data[year][limit]:
                    if period not in data_matrix:
                        data_matrix[period]=OrderedDict()
                    data_matrix[period]=get_data(data_matrix[period], data[year][limit][period], lim_list, limit, year)
            elif data_depth==3 or data_depth==2:
                data_matrix=get_data(data_matrix, data[year][limit], lim_list, limit, year)

    columns=len(data_matrix)
    rows=1
    if data_depth==4:
        for i in data_matrix:
            rows=len(data_matrix[i])
            break

    # fig, ax = plt.subplots(nrows=rows, ncols=columns)
    # if data_depth==4:
    #     column=0
    #     for period in data_matrix:
    #         build_plot(ax, data_matrix[period], rows, columns, column=column, extra_text=str(period)+" ")
    #         column+=1
    # elif data_depth==3:
    #     build_plot(ax, data_matrix, rows, columns)


    if data_depth==4:
        fig_numb=1
        for period in data_matrix:
            fig_numb=build_plot(data_matrix[period], title, extra_text=str(period)+" ", fig_numb=fig_numb)
            fig_numb+=1
    elif data_depth==3:
        build_plot(data_matrix, title)

    # plt.tight_layout()
    # plt.suptitle(title)
    plt.show()
