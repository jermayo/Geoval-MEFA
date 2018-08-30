#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.7
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

import tkinter as tk
from tkinter import messagebox
import datetime

import plot
from constant import *
import temp_analyse as ta
import rain_analyse as ra
import utilities

#main window class
class Window():
    def __init__(self, file_name, data_format=0):
        #Main window
        self.w=tk.Tk()
        self.w.title("Meteorological Event Frequency Analysis")

        self.temp_datas, self.rain_datas, self.read_log = None, None, None
        #default format
        self.format_list={"date":DATE_FORMATS[data_format],
                          "col_form":COL_FORMATS[data_format],
                          "col_name":COL_NAMES[data_format],
                          "auto_mode":AUTO_MODES[data_format],
                          "rain_key":RAIN_KEY,
                          "temp_key":TEMP_KEY}
        #StringVar and IntVar()
        self.analyse_type = tk.StringVar(self.w)
        self.analyse_type.set(ANALYSE_TYPE_GUI[0])
        self.output_toggle = tk.IntVar()
        self.output_toggle.set(1)
        self.plot_toggle = tk.IntVar()
        self.plot_toggle.set(1)
        self.save_plot_toggle=tk.IntVar()
        self.save_plot_toggle.set(0)
        self.file_name=file_name
        self.auto_step=tk.IntVar()
        self.auto_step.set(0)
        self.max_limit=tk.IntVar()
        self.max_limit.set(0)
        self.daily_av=tk.IntVar()
        self.daily_av.set(0)
        self.period=tk.IntVar()
        self.period.set(1)
        self.analy_type=tk.IntVar()
        self.analy_type.set(1)
        #Widget list (for tweaks)
        self.w_list=[]

        #Open file part
        tk.Label(self.w, text="File Name:").grid(row=1,column=0)
        self.E_file = tk.Entry(self.w)
        self.E_file.insert(0, self.file_name)
        self.E_file.grid(row=1,column=1)
        self.B_open = tk.Button(self.w, text="Open", command=self.open_file)
        self.B_open.grid(row=1,column=2)

        #Exit and change load param button
        tk.Button(self.w, text="Change Load Param", command=self.change_load).grid(row=5, column=3, sticky=tk.SW)
        tk.Button(self.w, text="Exit", command=self.exit).grid(row=5, column=4, sticky=tk.SW)

        #Label for file name
        self.L_file=tk.Label(self.w, text=self.file_name)

        #Results part
        self.result_frame=tk.LabelFrame(self.w, text="Results")
        self.res_text=tk.Label(self.result_frame, justify=tk.LEFT)
        self.res_text.grid()
        self.result_frame.grid(row=4,column=3, columnspan=3)
        self.result_frame.grid_remove()

        self.L_anayse=tk.Label(self.w, text = "")
        self.L_anayse.grid(row=4,column=3)

        #Tweak part
        self.tweak_frame = tk.LabelFrame(self.w, text="Tweaks")
        #Analyse info
        self.L_info=tk.Label(self.w, justify=tk.LEFT, relief=tk.RIDGE, padx=5, pady=5)

    #after file opened
    def init_analyse_option(self):
        #new tweak frame
        for child in self.tweak_frame.winfo_children():
            child.destroy()

        #Output and plot part
        output_frame = tk.LabelFrame(self.w, text="Output")
        self.CB_output = tk.Checkbutton(output_frame, variable=self.output_toggle, text="Output file")
        self.CB_output.grid(row=1,column=1)
        tk.Label(output_frame, text="File Name:").grid(row=2,column=1)
        self.E_output = tk.Entry(output_frame)
        self.E_output.insert(0,"output.txt")
        self.E_output.grid(row=2,column=2)
        self.CB_plot = tk.Checkbutton(output_frame, variable=self.plot_toggle, text="Plot graph")
        self.CB_plot.grid(row=3,column=1)
        self.CB_plot = tk.Checkbutton(output_frame, variable=self.save_plot_toggle, text="Save Plot")
        self.CB_plot.grid(row=3,column=2)
        output_frame.grid(row=1,rowspan=2, column=3, stick=tk.W)

        #Tweak part
        tk.Label(self.w, text="Analyse type:").grid(row=3,column=0)
        self.analyse_type.set(ANALYSE_TYPE_GUI[0])
        self.O_analyse=tk.OptionMenu(self.w, self.analyse_type, *ANALYSE_TYPE_GUI, command=self.change_analyse)
        self.O_analyse.grid(row=3,column=1)

        self.B_open = tk.Button(self.w, text="Analyse", command=self.analyse)
        self.B_open.grid(row=3,column=2)

        self.tweak_frame.grid(row=4,column=0, rowspan=2, columnspan=3, sticky=tk.N)
        self.L_info.grid(row=7,column=0, rowspan=2, columnspan=4, sticky=tk.NW)

        #set analse type to default ("data cleaning")
        self.change_analyse("Data_Cleaning")

    #open new file, destroy old data and tweaks
    def open_file(self):
        #init
        plot.destroy()
        old_text=self.file_name
        self.L_file.config(text = "Loading File...")
        self.L_file.grid(row=2,column=0,columnspan=2)
        self.L_file.update_idletasks()
        self.load_begin()
        #read file
        self.file_name=self.E_file.get()
        temp_datas, rain_datas, read_log, message=utilities.read_file(self.file_name, self.format_list, file_enc=FILE_ENCODING)
        self.load_end()
        #error check
        if read_log:
            self.temp_datas, self.rain_datas, self.read_log = temp_datas, rain_datas, read_log
            self.init_analyse_option()
            self.L_file.config(text = "File '{}' loaded".format(self.file_name))
            messagebox.showinfo("Done", "File loaded: \n"+self.read_log)
        else:
            messagebox.showerror("Error", message)
            self.L_file.config(text = old_text)

    #find the min and the max value for range auto min/max
    def find_min_max(self, w_single, w_min, w_max):
        if self.auto_step.get():
            min=int(self.w_list[w_min].get())
            max=int(self.w_list[w_max].get())
            max_limit=self.max_limit.get()
        else:
            min=int(self.w_list[w_single].get())
            max=min
            max_limit=False
        if min>max:
            messagebox.showerror("Error", "Minimal value greater than maximal.\n(You fool)")
            return False, False, False, False
        return True, min, max, max_limit

    #main analyses function
    def analyse(self):
        #init
        analyse=self.analyse_type.get()
        self.result_frame.grid_remove()
        self.L_anayse.config(text="Analysing data ...")
        self.L_anayse.update_idletasks()
        self.load_begin()

        plot_depth=False
        title=analyse+": "
        text="Error"
        if analyse=="Data_Cleaning":
            if self.daily_av.get():
                text=ta.clean_daily_average(self.temp_datas)
            else:
                text=""
                temp, rain=self.temp_datas, self.rain_datas
                t,r=0,0
                for l in range(max(len(temp), len(rain))):
                    if t>=len(temp) or temp[t]["date"]>rain[r]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t \t"+str(rain[r]["rain"])
                        r+=1
                    elif r>=len(rain) or temp[t]["date"]<rain[r]["date"]:
                        text+="\n"+str(temp[t]["date"])+"\t"+str(temp[t]["temp"])+"\t "
                        t+=1
                    elif temp[t]["date"]==rain[r]["date"]:
                        text+="\n"+str(rain[r]["date"])+"\t"+str(temp[t]["temp"])+"\t"+str(rain[r]["rain"])
                        r+=1
                        t+=1

        elif analyse=="Difference_Time":
            plot_depth=4
            delta_t=datetime.timedelta(hours=int(self.Sb_tweak2.get()))
            time_max_event=datetime.timedelta(hours=int(self.Sb_tweak3.get()))
            period=self.period.get()
            go, T_min, T_max, max_limit=self.find_min_max(1, 3, 5)
            title+="delta t: {}, event time max: {}, from: {}°C to: {}°C".format(delta_t, time_max_event, T_min, T_max)
            if max_limit:
                title+=" with max limit"
            if go:
                text, data=ta.diff_time(self.temp_datas, delta_t, time_max_event, period, T_min, T_max, max_limit)


        elif analyse=="Temp_Average":
            plot_depth=4
            period_type=self.analy_type.get()
            period=self.period.get()
            go, T_min, T_max, max_limit=self.find_min_max(0, 2, 4)
            title+="from: {}°C to: {}°C".format(T_min, T_max)
            if period_type:
                title+=", per event"
            else:
                title+=", day to day"
            if go:
                text, data=ta.temp_average(self.temp_datas, period_type, T_min, T_max, max_limit, period)

        elif analyse=="Day_To_Span_Average":
            plot_depth=4
            span=int(self.Sb_tweak1.get())
            days=int(self.Sb_tweak2.get())
            analy_type=self.analy_type.get()
            period=self.period.get()
            go, T_min, T_max, max_limit=self.find_min_max(1, 3, 5)
            title+="span: {} days, min time beet. events: {} days,  from: {}°C to: {}°C".format(span, days, T_min, T_max)
            if max_limit:
                title+=" with max limit"
            if analy_type:
                title+=", per event"
            else:
                title+=", day to day"
            if go:
                text, data=ta.day_to_span_av(self.temp_datas, span, T_min, T_max, max_limit, analy_type, days, period)

        elif analyse=="Rain_Cumul":
            plot_depth=3
            min_rain=int(self.w_list[4].get())
            min_time_beetween_event=int(self.w_list[5].get())
            period=self.period.get()
            per_event=self.analy_type.get()
            go, T_min, T_max, max_limit=self.find_min_max(None, 1, 3)
            if go:
                text, data=ra.rain_cumul(self.rain_datas, T_min, T_max, min_time_beetween_event, min_rain, period, per_event)

        # --------> ADD HERE CALL OF NEW ANALYSE FUNCTION: put plot_depth=0 to not have probleme with the plot
        # plot: variable "data" must be dictionnaries of type:
        #        plot depth=3: Year > Limit > {.., type: value, ...} (e.g. {pos:5, neg:3, tot:8})
        #        plot_depth=4: Year > Limit > Period > {}..., type: value, ...}
        # text: "text" will be printed out in the output file
        # Use find_min_max if you have an auto range in self.w_list

        #output file
        res_text=title+"\n"+text
        if self.output_toggle.get():
            if not utilities.write_file(self.E_output.get(),res_text, self.read_log):
                messagebox.showerror("Error", "File not found (404)")
                self.load_end()
                return
        #new text config
        self.L_anayse.config(text="")
        if len(res_text)>1000:
            res_text="Data too big, see file\n"
        self.res_text.config(text=res_text)
        self.res_text.grid()
        self.result_frame.grid()

        self.load_end()

        #plotting
        if self.plot_toggle.get() and plot_depth and text!="Error":
            warning=False
            for i in range(TAKE_OUT_FIRST):
                data.pop(min([i for i in data]))
                if len(data)==0:
                    warning=True
                    break
            for i in range(TAKE_OUT_LAST):
                if len(data)==0 or warning:
                    warning=True
                    break
                data.pop(max([i for i in data]))

            if not warning:
                if not plot.plot_data(data, plot_depth, title, self.save_plot_toggle.get()):
                    warning=True
            if warning:
                messagebox.showwarning("Warning", "Cannot plot with only one year.")

    #change of analyse type
    def change_analyse(self, value):
        for child in self.tweak_frame.winfo_children():
            child.destroy()
        self.auto_step.set(0)
        row=1

        if value=="Data_Cleaning":
            self.daily_av.set(0)
            tk.Checkbutton(self.tweak_frame, variable=self.daily_av, text="Daily Average").grid(row=row, column=2)
            self.L_info.config(text=CLEANING_INFO)

        elif value=="Difference_Time":
            self.period.set(1)

            tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min).grid(row=row, column=1)
            row+=1
            self.toggle_auto_min()
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

            self.L_info.config(text=DIFF_TIME_INFO+AUTO_RANGE_INFO+WITH_MAX_INFO)

        elif value=="Temp_Average":
            self.analy_type.set(0)
            self.period.set(1)
            tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min2).grid(row=row, column=1)
            row+=1
            tk.Label(self.tweak_frame, text="Delta Temp: ").grid(row=row, column=1)
            self.toggle_auto_min2()
            tk.Label(self.tweak_frame, text="°C").grid(row=row,column=6)
            row+=1
            tk.Label(self.tweak_frame, text="Type:").grid(row=row, column=1)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Day to day", value=0).grid(row=row, column=2, sticky=tk.W, columnspan=10)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Per event", value=1).grid(row=row+1, column=2, sticky=tk.W, columnspan=10)
            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=7)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=7, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=7, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=7, sticky=tk.W)

            self.L_info.config(text=TEMP_AVERAGE_INFO+AUTO_RANGE_INFO)

        elif value=="Day_To_Span_Average":
            self.analy_type.set(0)
            self.period.set(1)
            tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min3).grid(row=row, column=1,columnspan=2)
            tk.Label(self.tweak_frame, text="Type:").grid(row=row, column=9)
            row+=1
            tk.Label(self.tweak_frame, text="Span:").grid(row=row,column=1)
            self.Sb_tweak1=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak1.delete(0,tk.END)
            self.Sb_tweak1.insert(0,30)
            self.Sb_tweak1.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Days").grid(row=row, column=3)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Day to day", value=0).grid(row=row, column=9, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Per event", value=1).grid(row=row+1, column=9, sticky=tk.W)
            row+=1
            self.toggle_auto_min3()
            row+=1
            tk.Label(self.tweak_frame, text="Min time beet. events:").grid(row=row,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=0, to_=10000, justify=tk.RIGHT, width=3)
            self.Sb_tweak2.delete(0,tk.END)
            self.Sb_tweak2.insert(0,2)
            self.Sb_tweak2.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Days").grid(row=row,column=3)
            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=8)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=8, sticky=tk.W)

            self.L_info.config(text=DAY_TO_SPAN_INFO+AUTO_RANGE_INFO+WITH_MAX_INFO)

        elif value=="Rain_Cumul":
            self.period.set(1)
            self.analy_type.set(0)
            tk.Label(self.tweak_frame, text="Step:").grid(row=row,column=1)
            for w in self.w_list:
                w.destroy()
            self.w_list=[]

            self.auto_step.set(1)
            self.create_range(row, 2, 6, 24)
            row+=1
            tk.Label(self.tweak_frame, text="Min Rain: ").grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,6)
            self.w_list[-1].grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="mm/time").grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Min time beet. events:").grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=10000, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,15)
            self.w_list[-1].grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Min").grid(row=row,column=3)

            tk.Label(self.tweak_frame, text="Period:").grid(row=1, column=8)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="All Year", value=1).grid(row=2, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Season", value=2).grid(row=3, column=8, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Month", value=3).grid(row=4, column=8, sticky=tk.W)

            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Day to day", value=0).grid(row=2, column=9, sticky=tk.W)
            tk.Radiobutton(self.tweak_frame, var=self.analy_type, text="Per event", value=1).grid(row=3, column=9, sticky=tk.W)

            self.L_info.config(text=RAIN_CUMUL_INFO)

        # ------> ADD HERE NEW ANALYSE TYPE: add checkbutton, Radiobutton, ... here. Everything MUST be in self.tweak_frame <------#

    #loading widget init
    def load_begin(self):
        load_w_width=230
        load_w_height=60
        x=self.w.winfo_x()+int(self.w.winfo_width()/2-load_w_width/2)
        y=self.w.winfo_y()+int(self.w.winfo_height()/2-load_w_height/2)

        self.w.config(cursor="watch")
        self.load_w=tk.Toplevel()
        self.load_w.title("Loading...")
        self.load_w.geometry('%dx%d+%d+%d' % (load_w_width, load_w_height, x, y))
        tk.Label(self.load_w, text="Loading, please wait...\n(This can take a few minutes)").pack()

        self.w.update()
        self.load_w.update()
        self.load_w.tkraise(self.w)

    #end loading widget (destroy)
    def load_end(self):
        self.w.config(cursor="")
        self.load_w.destroy()

    #auto range min tool, Diff_Time
    def toggle_auto_min(self):
        row=1
        self.max_limit.set(0)
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        #with auto_min
        if self.auto_step.get():
            self.w_list.append(tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit))
            self.w_list[-1].grid(row=row, column=2, columnspan=4)
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.create_range(row, 2, 5, 20)
            self.w_list.append(tk.Label(self.tweak_frame, text="°C"))
            self.w_list[-1].grid(row=row,column=6)
        #without auto_min
        else:
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,10)
            self.w_list[-1].grid(row=row,column=2)
            self.w_list.append(tk.Label(self.tweak_frame, text="°C"))
            self.w_list[-1].grid(row=row,column=3)

    #auto range min tool, Temp_Average
    def toggle_auto_min2(self):
        row=1
        self.max_limit.set(0)
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        if self.auto_step.get():
            self.w_list.append(tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit))
            self.w_list[-1].grid(row=row, column=2, columnspan=4)
            row+=1
            self.create_range(row, 2, 5, 10)

        else:
            row+=1
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,8)
            self.w_list[-1].grid(row=row,column=2)

    #auto range min tool, Day To Span
    def toggle_auto_min3(self):
        row=2
        self.max_limit.set(0)
        for widget in self.w_list:
            widget.destroy()
        self.w_list=[]
        #auto max enabled
        if self.auto_step.get():
            self.w_list.append(tk.Checkbutton(self.tweak_frame, text="With Max", variable=self.max_limit))
            self.w_list[-1].grid(row=row-1, column=3, columnspan=4)
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.create_range(row, 2, 2, 15)
        else:
            row+=1
            self.w_list.append(tk.Label(self.tweak_frame, text="Delta Temp:"))
            self.w_list[-1].grid(row=row,column=1)
            self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
            self.w_list[-1].delete(0,tk.END)
            self.w_list[-1].insert(0,8)
            self.w_list[-1].grid(row=row,column=2)

    #------------> ADD HERE NEW TOGGLE AUTO MIN: put your widgets in self.w_list and use find_min_max() after to get the value
    #create two spinbox for range value
    def create_range(self, row, first_column, default_min, default_max):
        self.w_list.append(tk.Label(self.tweak_frame, text="From:"))
        self.w_list[-1].grid(row=row,column=first_column)
        self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
        self.w_list[-1].delete(0,tk.END)
        self.w_list[-1].insert(0,default_min)
        self.w_list[-1].grid(row=row,column=first_column+1)
        self.w_list.append(tk.Label(self.tweak_frame, text="To:"))
        self.w_list[-1].grid(row=row,column=first_column+2)
        self.w_list.append(tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3))
        self.w_list[-1].delete(0,tk.END)
        self.w_list[-1].insert(0,default_max)
        self.w_list[-1].grid(row=row,column=first_column+3)

    #change loading parameters
    def change_load(self):
        self.tk_auto_mode=tk.IntVar()
        self.tk_auto_mode.set(self.format_list["auto_mode"])
        self.tk_date_format=tk.StringVar()
        self.tk_date_format.set(self.format_list["date"])
        self.tk_col_name=tk.StringVar()
        self.tk_col_name.set(self.format_list["col_name"])
        self.tk_col_format=tk.StringVar()
        self.tk_col_format.set(self.format_list["col_form"])

        self.change_w=tk.Toplevel()
        self.change_w.title("Change Loading Parameters")

        tk.Label(self.change_w, text="Date format: ").grid(column=0, row=0)
        tk.OptionMenu(self.change_w, self.tk_date_format, *DATE_FORMATS).grid(column=1, row=0)
        tk.Label(self.change_w, text="Column Names: ").grid(column=0, row=1)
        tk.OptionMenu(self.change_w, self.tk_col_name, *COL_NAMES).grid(column=1, row=1)
        tk.Label(self.change_w, text="Column Format: ").grid(column=0, row=2)
        tk.OptionMenu(self.change_w, self.tk_col_format, *COL_FORMATS).grid(column=1, row=2)
        tk.Checkbutton(self.change_w, variable=self.tk_auto_mode, text="Auto detection mode", command=self.auto_mode_true).grid(column=1, row=3)
        tk.Button(self.change_w, text="Save", command=self.end_change_load).grid(column=1, row=6)

        self.auto_mode_true()
        self.w.update()
        self.change_w.update()
        self.change_w.tkraise(self.w)

    #part for auto mode (keywords, ...)
    def auto_mode_true(self):
        if self.tk_auto_mode.get():
            self.auto_mode_l=[]
            self.auto_mode_l.append(tk.Label(self.change_w, text="Rain Keyword: "))
            self.auto_mode_l[-1].grid(row=4, column=0)
            self.auto_mode_l.append(tk.Entry(self.change_w))
            self.auto_mode_l[-1].insert(0, self.format_list["rain_key"])
            self.auto_mode_l[-1].grid(row=4, column=1)
            self.auto_mode_l.append(tk.Label(self.change_w, text="Temp Keyword: "))
            self.auto_mode_l[-1].grid(row=5, column=0)
            self.auto_mode_l.append(tk.Entry(self.change_w))
            self.auto_mode_l[-1].insert(0, self.format_list["temp_key"])
            self.auto_mode_l[-1].grid(row=5, column=1)
        else:
            for widget in self.auto_mode_l:
                widget.destroy()

    #end the change of loading parameters
    def end_change_load(self):
        #make list out of the wierd stuff that tk gives me (WTF)
        def make_list(string):
            list=[]
            for i in string.split("'"):
                if "(" not in i and ")" not in i and "," not in i:
                    list.append(i)
            return list

        #saving the new parameters
        self.format_list["auto_mode"]=self.tk_auto_mode.get()
        self.format_list["date"]=self.tk_date_format.get()
        self.format_list["col_form"]=make_list(self.tk_col_format.get())
        self.format_list["col_name"]=make_list(self.tk_col_name.get())
        if self.tk_auto_mode.get():
            self.format_list["rain_key"]=self.auto_mode_l[1].get()
            self.format_list["temp_key"]=self.auto_mode_l[3].get()
        self.change_w.destroy()

    #destroy everything
    def exit(self):
        plot.destroy()
        self.w.destroy()

    #mainloop to get from the outside
    def mainloop(self):
        return self.w.mainloop()
