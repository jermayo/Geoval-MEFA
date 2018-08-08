#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tkinter as tk
from tkinter import messagebox
import datetime
from calendar import monthrange
from collections import OrderedDict

import analyse_type as at

#######################################################################################
#                  Classes and general functions                                      #
#######################################################################################
#Global variables of the programme
class GlobalVariables():
    def __init__(self):
        self.datas=None
        self.read_log=None
        self.temp_col=False
        self.rain_col=False

#Creation of data from input, returns a list of the datas (dictionnary)
#and if the data is good (True) not (False)
def create_data(line, column):
    def get(elem):
        for i in range(0,len(column)):
            if column[i]["val"]==elem:
                return line[i]
        return None

    try:
        date_val=get("Year")+"-"+get("Month")+"-"+get("Day")
        date_val+="-"+get("Hour")+"-"+get("Minutes")
        data={"date":datetime.datetime.strptime(date_val, DATE_FORMAT)}

        data["rain"]=eval(get("Rain"))
        data["temp"]=eval(get("Temp"))

        if abs(data["rain"])>RAIN_LIMIT or abs(data["temp"])>TEMP_LIMIT:
            return data, False
        return data, True
    except:
        messagebox.showerror("Error", "Data could not be retrieved")


#File Reading and Writting
def read_file(file_name, temp_col, rain_col, file_encoding="UTF-8"):
    def get_start(line, column):
        #Prevent exception
        if line==[]:
            return False
        for i in range(0, min(len(column),len(line))):
            if column[i]["name"]!=line[i]:
                return False
        return True

    datas=[]
    bad_data=0
    column=[]

    if file_name=="Hello There!":
        messagebox.showinfo("","General Kenobi, you're a bold one.")


    for i in range(0, len(column_format)):
        column.append({"pos":i, "name":column_format_name[i], "val":column_format[i]})

    try:
        file=open(file_name, 'r', encoding=file_encoding)
        file_lines=file.readlines()
        file.close()
    except FileNotFoundError:
        return False, False

    flag_1=False
    for comp_line in file_lines:
        line=comp_line.split()
        #Main data input
        if flag_1 and line!=[]:
            new_data, flag = create_data(line, column)
            if flag:
                if len(datas)==0:
                    datas.append(new_data)
                elif new_data["date"]>datas[-1]["date"]:
                        datas.append(new_data)
                else:
#!!! To do: Auto sort by date
                    messagebox.showwaring("Warning", "Data not in order (Date: {})".format(line["date"]))
            else:
                bad_data+=1

        #Get startitng point
        elif get_start(line, column):
            for i in line:
                if i==rain_col:
                    column.append({"pos":i, "name":rain_col, "val":"Rain"})
                    flag_1=True
                elif i==temp_col:
                    column.append({"pos":i, "name":temp_col, "val":"Temp"})
                    flag_1=True
            if not flag_1:
                messagebox.showwaring("Error", "No temperature or rain data detected")
        #Automatic rain and temp column detection
        elif len(line)>1 and AUTO_MODE:
            if line[1]==RAIN_KEYWORD:
                rain_col=line[0]
            elif line[1]==TEMP_KEYWORD:
                temp_col=line[0]

    log="{} values with {} bad values ({:.1f}%) (taken out)".format(len(datas), bad_data, bad_data/len(datas)*100)
    return datas, log


def file_write(file_name, res, log):
    file=open(file_name, "w")
    file.write("\t\t\t\t\t{}\n".format(datetime.datetime.now().strftime('%Y-%m-%d')))
    file.write("Result of analyse of data: ")
    file.write(log+"\n")
    file.write(res)
    file.close()

#######################################################################################
#                             GUI                                                     #
#######################################################################################
class Window():
    def __init__(self):
        #Main window
        self.w=tk.Tk()
        self.w.title("Meteorological Event Frequency Analysis")
        #StringVar
        self.analyse_type = tk.StringVar(self.w)
        self.analyse_type.set(ANALYSE_TYPE[0])
        self.output_toggle = tk.IntVar()
        self.output_toggle.set(1)
        self.file_name="..."
        self.auto_step=tk.IntVar()
        self.auto_step.set(0)
        self.max_limit=tk.IntVar()
        self.max_limit.set(0)

        tk.Label(self.w, text="File Name:").grid(row=1,column=0)
        self.E_file = tk.Entry(self.w)
        self.E_file.insert(0, DEFAULT_FILE_NAME)
        self.E_file.grid(row=1,column=1)
        self.B_open = tk.Button(self.w, text="Open", command=self.open_file)
        self.B_open.grid(row=1,column=2)

        self.B_exit = tk.Button(self.w, text="Exit", command=self.w.destroy)
        self.B_exit.grid(row=5, column=3, sticky=tk.SW)

        self.L_file=tk.Label(self.w, text=self.file_name)

        self.result_frame=tk.LabelFrame(self.w, text="Results")
        self.res_text=tk.Label(self.result_frame, justify=tk.LEFT)
        self.res_text.grid()
        self.result_frame.grid(row=4,column=3)
        self.result_frame.grid_remove()

        self.L_anayse=tk.Label(self.w, text = "")
        self.L_anayse.grid(row=4,column=3)

        self.tweak_frame = tk.LabelFrame(self.w, text="Tweaks")
        self.L_info=tk.Label(self.w, justify=tk.LEFT, relief=tk.RIDGE, padx=5, pady=5)

    def init_analyse_option(self):
        for child in self.tweak_frame.winfo_children():
            child.destroy()

        output_frame = tk.LabelFrame(self.w, text="Output Log File")
        self.CB_output = tk.Checkbutton(output_frame, variable=self.output_toggle, text="Output file")
        self.CB_output.grid(row=1,column=3)
        tk.Label(output_frame, text="File Name:").grid(row=2,column=3)
        self.E_output = tk.Entry(output_frame)
        self.E_output.insert(0,"output.txt")
        self.E_output.grid(row=2,column=4)
        output_frame.grid(row=1,rowspan=2, column=3, stick=tk.W)

        tk.Label(self.w, text="Analyse type:").grid(row=3,column=0)
        self.analyse_type.set(ANALYSE_TYPE[0])
        self.O_analyse=tk.OptionMenu(self.w, self.analyse_type, *ANALYSE_TYPE, command=self.change_analyse)
        self.O_analyse.grid(row=3,column=1)


        self.B_open = tk.Button(self.w, text="Analyse", command=self.analyse)
        self.B_open.grid(row=3,column=2)

        self.tweak_frame.grid(row=4,column=0, rowspan=2, columnspan=3, sticky=tk.N)
        self.L_info.grid(row=7,column=0, rowspan=2, columnspan=4, sticky=tk.NW)

        self.change_analyse("Difference Time")

    def open_file(self):
        old_text=self.file_name
        self.L_file.config(text = "Loading File...")
        self.L_file.grid(row=2,column=0,columnspan=2)
        self.L_file.update_idletasks()
        self.load_begin()

        self.file_name=self.E_file.get()
        datas, read_log=read_file(self.file_name, GV.temp_col, GV.rain_col, file_encoding=FILE_ENCODING)
        self.load_end()
        if read_log:
            GV.datas, GV.read_log = datas, read_log
            self.init_analyse_option()
            self.L_file.config(text = "File '{}' loaded".format(self.file_name))
            messagebox.showinfo("Done", "File loaded: \n"+GV.read_log)
        else:
            messagebox.showerror("Error", "File not found (404)")
            self.L_file.config(text = old_text)


    def analyse(self):
        analyse=self.analyse_type.get()
        self.result_frame.grid_remove()
        self.L_anayse.config(text="Analysing data ...")
        self.L_anayse.update_idletasks()
        self.load_begin()

        res_text=""
        extra_text=""
        if analyse=="Difference Time":
            delta_t=datetime.timedelta(hours=int(self.Sb_tweak2.get()))
            time_max_event=datetime.timedelta(hours=int(self.Sb_tweak3.get()))
            period=self.period.get()
            max_limit=False
            if self.auto_step.get():
                min=int(self.Sb_tweak11.get())
                max=int(self.Sb_tweak12.get())
                max_limit=self.max_limit.get()
            else:
                min=int(self.Sb_tweak1.get())
                max=min
            res_text=at.diff_time(GV.datas, delta_t, time_max_event, period, min, max, max_limit)

        if analyse=="Rain Cumul":
            step=datetime.timedelta(hours=int(self.Sb_tweak1.get()))
            min_time_beetween_event=datetime.timedelta(minutes=int(self.Sb_tweak3.get()))
            if self.auto_step.get():
                min=int(self.Sb_tweak21.get())
                max=int(self.Sb_tweak22.get())
            else:
                min=int(self.Sb_tweak2.get())
                max=min

            res_text=at.rain_cumul(GV.datas, step, min_time_beetween_event, min, max)

        if analyse=="Temp Average":
            period_type=self.period.get()
            if self.auto_step.get():
                min=int(self.Sb_tweak31.get())
                max=int(self.Sb_tweak32.get())
            else:
                min=int(self.Sb_tweak31.get())
                max=min
            res_text=at.temp_average(GV.datas, period_type, min, max)


        if self.output_toggle.get():
            file_write(self.E_output.get(),res_text, GV.read_log)
            extra_text=", results in '{}'".format(self.E_output.get())
        #messagebox.showinfo("Done", "Data analysed"+extra_text)

        self.L_anayse.config(text="")
        if len(res_text)>1000:
            res_text="Data too big, see file\n"
        self.res_text.config(text=res_text)
        self.res_text.grid()
        self.result_frame.grid()

        self.load_end()

    def change_analyse(self, value):
        for child in self.tweak_frame.winfo_children():
            child.destroy()
        self.auto_step.set(0)
        row=1
        if value=="Difference Time":
            self.period=tk.IntVar()
            self.period.set(1)

            Cb_range_step=tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.cb_toggle_auto_min)
            Cb_range_step.grid(row=row, column=1)
            row+=1
            self.toggle_auto_min(True)
            row+=1
            tk.Label(self.tweak_frame, text="Time Diff:").grid(row=row,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=24, to_=1000, justify=tk.RIGHT, width=3, increment=24)
            self.Sb_tweak2.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Max Event Time:").grid(row=row,column=1)
            self.Sb_tweak3=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak3.delete(0,tk.END)
            self.Sb_tweak3.insert(0,24)
            self.Sb_tweak3.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=7)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=7, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=7, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=7, sticky=tk.W)

            tk.Label(self.tweak_frame, text="(Season: Winter (Dec, Jan, Feb), and so on...)").grid(row=5, column=1, columnspan=3)

            self.L_info.config(text=DIFF_TIME_INFO+END_INFO)


        elif value=="Rain Cumul":
            tk.Label(self.tweak_frame, text="Step:").grid(row=row,column=1)
            self.Sb_tweak1=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak1.delete(0,tk.END)
            self.Sb_tweak1.insert(0,6)
            self.Sb_tweak1.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=row,column=3)
            row+=1
            Cb_range_step=tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.cb_toggle_auto_min2)
            Cb_range_step.grid(row=row, column=1)
            row+=1
            self.toggle_auto_min2(True)
            row+=1
            tk.Label(self.tweak_frame, text="Min time beet. events:").grid(row=row,column=1)
            self.Sb_tweak3=tk.Spinbox(self.tweak_frame, from_=0, to_=10000, justify=tk.RIGHT, width=3)
            self.Sb_tweak3.delete(0,tk.END)
            self.Sb_tweak3.insert(0,10)
            self.Sb_tweak3.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Min").grid(row=row,column=3)

            self.L_info.config(text=RAIN_CUMUL_INFO+END_INFO)

        elif value=="Temp Average":
            self.period.set(0)
            Cb_range_step=tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.cb_toggle_auto_min3)
            Cb_range_step.grid(row=row, column=1)
            row+=1
            tk.Label(self.tweak_frame, text="Delta Temp: ").grid(row=row, column=1)
            self.toggle_auto_min3(True)
            tk.Label(self.tweak_frame, text="°C").grid(row=row,column=6)
            row+=1
            tk.Label(self.tweak_frame, text="Type:").grid(row=row, column=1)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Day to day", value=0).grid(row=row, column=2, sticky=tk.W, columnspan=10)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Per event", value=1).grid(row=row+1, column=2, sticky=tk.W, columnspan=10)

            self.L_info.config(text=TEMP_AVERAGE_INFO+END_INFO)


    def load_begin(self):
        load_w_width=230
        load_w_height=60
        x=self.w.winfo_x()+int(self.w.winfo_width()/2-load_w_width/2)
        y=self.w.winfo_y()+int(self.w.winfo_height()/2-load_w_height/2)

        self.w.config(cursor="watch")

        self.load_w=tk.Tk()
        self.load_w.title("Loading")
        self.load_w.geometry('%dx%d+%d+%d' % (load_w_width, load_w_height, x, y))
        tk.Label(self.load_w, text="Loading, please wait...\n(This can take a few minutes)").pack()

        self.w.update()
        self.load_w.update()
        self.load_w.grab_set()

    def load_end(self):
        self.w.config(cursor="")
        self.load_w.destroy()

    def cb_toggle_auto_min(self):
        self.toggle_auto_min(False)

    def toggle_auto_min(self, first):
        row=1
        if self.auto_step.get():
            self.Sb_L1_tweak1.destroy()
            self.Sb_tweak1.destroy()
            self.Sb_L2_tweak1.destroy()

            self.Sb_tweak0=tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit)
            self.Sb_tweak0.grid(row=row, column=2, columnspan=4)
            row+=1
            self.Sb_L1_tweak1=tk.Label(self.tweak_frame, text="Delta Temp:")
            self.Sb_L1_tweak1.grid(row=row,column=1)
            self.Sb_L2_tweak1=tk.Label(self.tweak_frame, text="From:")
            self.Sb_L2_tweak1.grid(row=row,column=2)
            self.Sb_tweak11=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_tweak11.delete(0,tk.END)
            self.Sb_tweak11.insert(0,5)
            self.Sb_tweak11.grid(row=row,column=3)
            self.Sb_L3_tweak1=tk.Label(self.tweak_frame, text="To:")
            self.Sb_L3_tweak1.grid(row=row,column=4)
            self.Sb_tweak12=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_tweak12.delete(0,tk.END)
            self.Sb_tweak12.insert(0,20)
            self.Sb_tweak12.grid(row=row,column=5)
            self.Sb_L4_tweak1=tk.Label(self.tweak_frame, text="°C")
            self.Sb_L4_tweak1.grid(row=row,column=6)
        else:
            if not first:
                self.Sb_tweak0.destroy()
                self.Sb_L1_tweak1.destroy()
                self.Sb_tweak11.destroy()
                self.Sb_L3_tweak1.destroy()
                self.Sb_tweak12.destroy()
                self.Sb_L4_tweak1.destroy()
            row+=1
            self.Sb_L1_tweak1=tk.Label(self.tweak_frame, text="Delta Temp:")
            self.Sb_L1_tweak1.grid(row=row,column=1)
            self.Sb_tweak1=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_tweak1.delete(0,tk.END)
            self.Sb_tweak1.insert(0,10)
            self.Sb_tweak1.grid(row=row,column=2)
            self.Sb_L2_tweak1=tk.Label(self.tweak_frame, text="°C")
            self.Sb_L2_tweak1.grid(row=row,column=3)


    def cb_toggle_auto_min2(self):
        self.toggle_auto_min2(False)

    def toggle_auto_min2(self, first):
        row=3
        if self.auto_step.get():
            self.Sb_L1_tweak2.destroy()
            self.Sb_L2_tweak2.destroy()
            self.Sb_tweak2.destroy()
            #self.w.update()

            self.Sb_L1_tweak2=tk.Label(self.tweak_frame, text="Min Rain:")
            self.Sb_L1_tweak2.grid(row=row,column=1)
            self.Sb_L2_tweak2=tk.Label(self.tweak_frame, text="From:")
            self.Sb_L2_tweak2.grid(row=row,column=2)
            self.Sb_tweak21=tk.Spinbox(self.tweak_frame, from_=0, to_=1000000, justify=tk.RIGHT, width=3)
            self.Sb_tweak21.delete(0,tk.END)
            self.Sb_tweak21.insert(0,1)
            self.Sb_tweak21.grid(row=row,column=3)
            self.Sb_L3_tweak2=tk.Label(self.tweak_frame, text="To:")
            self.Sb_L3_tweak2.grid(row=row,column=4)
            self.Sb_tweak22=tk.Spinbox(self.tweak_frame, from_=0, to_=1000000, justify=tk.RIGHT, width=3)
            self.Sb_tweak22.delete(0,tk.END)
            self.Sb_tweak22.insert(0,15)
            self.Sb_tweak22.grid(row=row,column=5)
            self.Sb_L4_tweak2=tk.Label(self.tweak_frame, text="mm/time")
            self.Sb_L4_tweak2.grid(row=row,column=6)
        else:
            if not first:
                self.Sb_L1_tweak2.destroy()
                self.Sb_L2_tweak2.destroy()
                self.Sb_L3_tweak2.destroy()
                self.Sb_L4_tweak2.destroy()
                self.Sb_tweak21.destroy()
                self.Sb_tweak22.destroy()

            self.Sb_L1_tweak2=tk.Label(self.tweak_frame, text="Min Rain:")
            self.Sb_L1_tweak2.grid(row=row,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=0, to_=1000000, justify=tk.RIGHT, width=3)
            self.Sb_tweak2.delete(0,tk.END)
            self.Sb_tweak2.insert(0,5)
            self.Sb_tweak2.grid(row=row,column=2)
            self.Sb_L2_tweak2=tk.Label(self.tweak_frame, text="mm/time")
            self.Sb_L2_tweak2.grid(row=row,column=3)

    def cb_toggle_auto_min3(self):
        self.toggle_auto_min3(False)

    def toggle_auto_min3(self, first):
        row=2
        if self.auto_step.get():
            self.Sb_tweak31.destroy()

            self.Sb_L1_tweak3=tk.Label(self.tweak_frame, text="From:")
            self.Sb_L1_tweak3.grid(row=row,column=2)
            self.Sb_tweak31=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_tweak31.delete(0,tk.END)
            self.Sb_tweak31.insert(0,5)
            self.Sb_tweak31.grid(row=row,column=3)
            self.Sb_L2_tweak1=tk.Label(self.tweak_frame, text="To:")
            self.Sb_L2_tweak1.grid(row=row,column=4)
            self.Sb_tweak32=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_tweak32.delete(0,tk.END)
            self.Sb_tweak32.insert(0,10)
            self.Sb_tweak32.grid(row=row,column=5)

        else:
            if not first:
                self.Sb_L1_tweak3.destroy()
                self.Sb_tweak31.destroy()
                self.Sb_L2_tweak1.destroy()
                self.Sb_tweak32.destroy()

            self.Sb_tweak31=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak31.delete(0,tk.END)
            self.Sb_tweak31.insert(0,8)
            self.Sb_tweak31.grid(row=row,column=2)



#######################################################################################
#                      Global Constant                                                #
#######################################################################################
#File format
DATE_FORMAT='%Y-%m-%d-%H-%M'

AUTO_MODE=True
#Rain column name
RAIN_KEYWORD="Niederschlag"
#Temperature column name
TEMP_KEYWORD="Lufttemperatur"

RAIN_LIMIT=100
TEMP_LIMIT=100


ANALYSE_TYPE = ("Difference Time", "Rain Cumul", "Temp Average")

DEFAULT_FILE_NAME="../test_file/month6.txt"
#DEFAULT_FILE_NAME=".txt"

FILE_ENCODING="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)



column_format_name=["STA", "JAHR", "MO", "TG", "HH", "MM"]
column_format=["Station", "Year", "Month", "Day", "Hour", "Minutes"]

DIFF_TIME_INFO="""  Description:
Difference over time:
Event starts if the difference beetween a value and the value recorded "Time Diff" before is greater than "Delta Temp".
It ends after "Max event time" so every value greater than "Delta Temp" in that period is not taken into account. The period
allows one to look at the number of event per period of each year. When 'With max' (only possible for Auto Range) is checked,
an event is counted ONLY in the temperature corresponding to it's maximal value."""
RAIN_CUMUL_INFO=""" Description:
Rain cumul:
Events starts when the rain cumul in the last "step" hours is greater than "Min Rain".
The value of "Min Rain" is in mm/"step" (so mm/6h per default)
Events stops when the time beetween the next time the cumul is greater than "Min Rain"
and the last time it did is greater than "Min time beet. events"."""
TEMP_AVERAGE_INFO="""   Description:
Temperature average:
Event happens if the difference beetween the daily average and the typical average is greater than "Delta Temp".
The typical average is calulated for each day of the year as the average of the daily average of one of the day of the year.
(For exemple: take the daily average of each July 20th every year and make the average of them all, that is the typical daily average)
"Per event" implies that if two consecutive days are events, they only count as one,
whereas "day to day" counts every day that is an event."""
END_INFO="""\n\nAuto Range: automaticaly makes the analyses for all values beetween set boundaries"""

#######################################################################################
#                            Main programme                                           #
#######################################################################################
GV=GlobalVariables()

main=Window()
main.w.mainloop()
