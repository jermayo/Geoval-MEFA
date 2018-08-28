#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.6
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import matplotlib.pyplot as plt
from collections import OrderedDict

def lin_reg(x, y):
    def prod_sum(x, y, n):
        return sum([x[i]*y[i] for i in range(n)])
    n=len(x)
    if n!=len(y):
        print("Error: data not same length")
        return False, False
    a=(n*prod_sum(x,y,n)-sum(x)*sum(y))/(n*prod_sum(x,x,n)-sum(x)**2)
    b=(sum(y)-a*(sum(x)))/n
    return a,b

def get_points(x, y):
    a,b=lin_reg(x,y)
    return a,[x[0], x[-1]], [a*x[0]+b, a*x[-1]+b]

def get_data(sub_data_matrix, sub_data, lim_list, limit, year):

    for elem in sub_data:
        if elem not in sub_data_matrix:
            sub_data_matrix[elem]=OrderedDict()
            for lim in lim_list:
                sub_data_matrix[elem][lim]={"xaxis":[], "yaxis":[]}
        sub_data_matrix[elem][limit]["xaxis"].append(year)
        sub_data_matrix[elem][limit]["yaxis"].append(sub_data[elem])

    return sub_data_matrix


def build_plot(data_matrix, title, save_plot, extra_text="", fig_numb=1):
    for elem in data_matrix:
        plt.figure(extra_text+str(elem)+str(title)[:-2]+str(fig_numb), figsize=(15,5))

        plt.title(extra_text+str(elem))
        color=0
        for lim in data_matrix[elem]:
            plt.plot(data_matrix[elem][lim]["xaxis"], data_matrix[elem][lim]["yaxis"], alpha=0.3, color="C"+str(color%10))
            a,x,y=get_points(data_matrix[elem][lim]["xaxis"], data_matrix[elem][lim]["yaxis"])
            plt.plot(x,y, label="{} a:{:.4f}".format(lim,a), color="C"+str(color%10))
            color+=1

        x1,x2,y1,y2 = plt.axis()
        plt.axis((x1,x2,0,y2))
        plt.legend(loc='best', borderaxespad=0.)#(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        fig_numb+=1
        if save_plot:
            plt.savefig(extra_text+str(elem)+str(title)[:-2]+".pdf")
    return fig_numb

def plot_data(data, data_depth, title, save_plot, show_plot=True):
    if len(data)==1:
        return False
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
    if data_depth==4:
        fig_numb=1
        for period in data_matrix:
            fig_numb=build_plot(data_matrix[period], title, save_plot, extra_text=str(period)+" ", fig_numb=fig_numb)
            fig_numb+=1
    elif data_depth==3:
        build_plot(data_matrix, title, save_plot)

    plt.tight_layout()
    # plt.suptitle(title)
    if show_plot:
        plt.show()
    return True

def destroy():
    plt.close("all")
