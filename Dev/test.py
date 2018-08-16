import datetime
import tkinter as tk
import plot
import random

# l1=[i for i in range(0,5)]
# l2=[i for i in range(5,10)]
#
# print(l1)
# print(l2)
# print(l1+l2)

# date_start=datetime.datetime.strptime("5", "%m")
#
# print(date_start.month, type(date_start.month))

#hello="bonjour "*3

#print(hello)

# test={"un":1, "deux":2, "trois":3}
# test2={"un2":1, "deux2":2, "trois2":3}
# tot={"test":test, "test2":test2}
#
# print(list(tot[list(tot.keys())[0]].keys())[0])
#
# period_end=datetime.datetime.strptime("01-03-2011","%d-%m-%Y")
#
# yday = (period_end - datetime.datetime(period_end.year, 1, 1)).days+1
#
# print(datetime.datetime.date(period_end))
# print(period_end.date())
#
#
# print(text)

# for i in range(10):
#     print(i)
#     i=i+1
#     print(i)

# start=datetime.datetime.strptime("01-03-2010","%d-%m-%Y")
# end=datetime.datetime.strptime("01-03-2011","%d-%m-%Y")
#
# print(end-start)
# print((-1)*(start-end))


# data={}
#
# for year in range(2000, 2003):
#     data[year]={}
#     for limit in range(5,7):
#         data[year][limit]={}
#         for period in ["A","B","C"]:
#             data[year][limit][period]={}
#             for elem in ["pos","neg","tot"]:
#                 data[year][limit][period][elem]=random.random()
# plot.plot_depth4(data)

x=[2,6,43,6,8,8,5,43,3,4,6,8,34]
y=[56,34,34,53,6,54,43,34,34,5,6,45,67]
x=[60,61,62,63,65]
y=[3.1,3.6,3.8,4,4.1]

print(plot.get_points(x,y))
