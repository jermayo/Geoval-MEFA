import tkinter as tk
from tkinter import messagebox
import datetime
from calendar import monthrange, month_abbr
from collections import OrderedDict

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

############################# Type of analyse #########################################

def date_beetween(date, month_start, month_end):
    if month_start>month_end:
        if not(date.month<month_start and date.month>=month_end):
            return True
    elif date.month>=month_start and date.month<month_end:
        return True
    return False
#Temperature
#Difference of temp with 24h or 48h before

def diff_time(datas, delta_t, delta_temp, time_max_event, periods):
    #month_start and month end of type int, month_end NOT included, 13 means decembre included
    during_event=False
    event_list=OrderedDict()
    year_list=[]

    for i in range(0,len(datas)):
        year=datas[i]["date"].year
        if year not in year_list:
            year_list.append(year)
            new_period=OrderedDict()
            for key in periods:
                new_period[key]={"pos":0, "neg":0, "total":0}
            event_list[year]=new_period

        j=i
        while datas[j]["date"]-datas[i]["date"]<delta_t:
            j+=1

        d_temp=datas[j]["temp"]-datas[i]["temp"]
        if not during_event and abs(d_temp)>delta_temp:
            during_event=True
            event_type="+"
            if d_temp<0:
                event_type="-"

            for key in periods:
                if date_beetween(datas[i]["date"], periods[key][0], periods[key][1]):
                    new_event={"start": datas[i]["date"], "type": event_type, "period":key}
                    break
            #print(new_event["start"])

        elif during_event:
            if datas[i]["date"]-new_event["start"]>time_max_event:
                during_event=False

                if new_event["type"]=="+":
                    event_list[new_event["start"].year][new_event["period"]]["pos"]+=1
                elif new_event["type"]=="-":
                    event_list[new_event["start"].year][new_event["period"]]["neg"]+=1
                event_list[new_event["start"].year][new_event["period"]]["total"]+=1

        if j>=len(datas)-1:
            break

    if during_event:
        if new_event["type"]=="+":
            event_list[new_event["start"].year][new_event["period"]]["pos"]+=1
        elif new_event["type"]=="-":
            event_list[new_event["start"].year][new_event["period"]]["neg"]+=1
        event_list[new_event["start"].year][new_event["period"]]["total"]+=1

    return event_list

#Rain
def rain_cumuls(datas, step, min_rain, min_time_beetween_event):
    last_event_date=datetime.datetime.min
    events=[]
    for i in range(0,len(datas)):
        j=i
        sum=0
        while datas[j]["date"]-datas[i]["date"]<step:
            j+=1
            sum+=datas[j]["rain"]
        if sum>min_rain:
            if datas[j]["date"]-last_event_date>min_time_beetween_event:
                flag=True
                for event in events:
                    if event["year"]==datas[i]["date"].year:
                        flag=False
                        event["total"]+=1
                        break
                if flag:
                    events.append({"year":datas[i]["date"].year, "total":1})
            last_event_date=datas[j]["date"]

        if j>=len(datas)-1:
            break
    return events

#temp median: 1 median done for each day, 2 median over each same day of year, 3 comparaison each day/median of typical day
#analy_type: =0 -> day to day, =1 -> per event
def temp_median(datas, delta_temp, analy_type):
    typical_median={}
    days_median={}
    events={}

    for day in range(0,367):
        typical_median[day]={"val":0, "numb_of_val":0}
    for data in datas:
        date=data["date"].date()
        if date not in days_median:
            days_median[date]={"val":0, "numb_of_val":0}
        days_median[date]["val"]+=data["temp"]
        days_median[date]["numb_of_val"]+=1

        day_numb=(data["date"]-datetime.datetime(data["date"].year, 1, 1)).days+1
        typical_median[day_numb]["val"]+=data["temp"]
        typical_median[day_numb]["numb_of_val"]+=1

        if data["date"].year not in events:
            events[data["date"].year]={"pos":0, "neg":0, "tot":0}

    for day in typical_median:
        if typical_median[day]["numb_of_val"]>0:
            typical_median[day]=typical_median[day]["val"]/typical_median[day]["numb_of_val"]
        else:
            typical_median[day]=0
    for day in days_median:
        if days_median[day]["numb_of_val"]>0:
            days_median[day]=days_median[day]["val"]/days_median[day]["numb_of_val"]
        else:
            days_median[day]=0

    during_event=False
    for day in days_median:
        day_numb=(day-(datetime.datetime(day.year, 1, 1)).date()).days+1
        diff=typical_median[day_numb]-days_median[day]
        if abs(diff)>delta_temp and not during_event:
            if diff>0:
                events[day.year]["pos"]+=1
            else:
                events[day.year]["neg"]+=1
            events[day.year]["tot"]+=1

            if analy_type:
                during_event=True

        elif during_event and abs(diff)<delta_temp:
            during_event=False

    return events





#######################################################################################
#                             GUI                                                     #
#######################################################################################
class Window():
    def __init__(self):
        #Main window
        self.w=tk.Tk()
        self.w.title("Environemental Analyse Tool")
        #StringVar
        self.analyse_type = tk.StringVar(self.w)
        self.analyse_type.set(ANALYSE_TYPE[0])
        self.output_toggle = tk.IntVar()
        self.output_toggle.set(1)
        self.file_name="..."
        self.auto_step=tk.IntVar()
        self.auto_step.set(0)

        tk.Label(self.w, text="File Name:").grid(row=1,column=0)
        self.E_file = tk.Entry(self.w)
        self.E_file.insert(0,"../test_file/month6.txt")
        self.E_file.grid(row=1,column=1)
        self.B_open = tk.Button(self.w, text="Open", command=self.open_file)
        self.B_open.grid(row=1,column=2)

        self.B_exit = tk.Button(self.w, text="Exit", command=self.w.destroy)
        self.B_exit.grid(row=5, column=3, sticky=tk.S)

        self.L_file=tk.Label(self.w, text=self.file_name)

        self.result_frame=tk.LabelFrame(self.w, text="Results")
        self.res_text=tk.Label(self.result_frame, justify=tk.LEFT, wraplength=1000)
        self.res_text.grid()
        self.result_frame.grid(row=4,column=3)
        self.result_frame.grid_remove()

        self.L_anayse=tk.Label(self.w, text = "")
        self.L_anayse.grid(row=4,column=3)

        self.tweak_frame = tk.LabelFrame(self.w, text="Tweaks")

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
            def make_text(data):
                text="Year\t"
                for key in data[list(data.keys())[0]]:
                    text+=key+"\t"*3
                text+="\n"
                text+="\tPos.\tNeg.\tTotal"*len(data[list(data.keys())[0]])
                text+="\n"
                for year in data:
                    text+=str(year)
                    for p in data[year]:
                        value=data[year][p]
                        text+="\t{}\t{}\t{}".format(value["pos"], value["neg"], value["total"])
                    text+="\n"
                return text

            delta_t=datetime.timedelta(hours=int(self.Sb_tweak2.get()))
            time_max_event=datetime.timedelta(hours=int(self.Sb_tweak3.get()))
            period=self.period.get()
            res_total=[]
            if period==1:
                period_list={"All Year":[1,13]} #period list from month# to month# NOT INCLUDED, 13 => december included
            elif period==2:
                period_list={"Winter":[12,3],"Spring":[3,6],"Summer":[6,9],"Autumn":[9,12]}
            elif period==3:
                period_list={}
                for i in range(1,13):
                    period_list[month_abbr[i]]=[i, i+1]

            if self.auto_step.get():
                min=int(self.Sb_tweak11.get())
                max=int(self.Sb_tweak12.get())
                res_text=""
                for i in range(min, max+1):
                    res=diff_time(GV.datas, delta_t, i, time_max_event, period_list)
                    res_text+="Delta T: "+str(i)+"\n"+make_text(res)+"\n\n"
            else:
                res=diff_time(GV.datas, delta_t, int(self.Sb_tweak1.get()), time_max_event, period_list)
                res_text=make_text(res)


        if analyse=="Rain Cumuls":
            step=datetime.timedelta(hours=int(self.Sb_tweak1.get()))
            min_time_beetween_event=datetime.timedelta(minutes=int(self.Sb_tweak3.get()))
            if self.auto_step.get():
                res_total=[]
                res_text="\t"
                min=int(self.Sb_tweak21.get())
                max=int(self.Sb_tweak22.get())
                for i in range(min, max+1):
                    res=rain_cumuls(GV.datas, step, i, min_time_beetween_event)
                    res_total.append({"min":i, "res":res})
                for i in res_total[0]["res"]:
                    res_text+=str(i["year"])+"\t"
                for res in res_total:
                    res_text+="\n"+str(res["min"])
                    for i in res["res"]:
                        res_text+="\t"+str(i["total"])
            else:
                res=rain_cumuls(GV.datas, step, float(self.Sb_tweak2.get()), min_time_beetween_event)
                res_text="Year\tTotal\n"
                for i in res:
                    res_text+="{}\t{}\n".format(i["year"], i["total"])

        if analyse=="Temp Median":
            if self.auto_step.get():
                min=int(self.Sb_tweak31.get())
                max=int(self.Sb_tweak32.get())
                res_text+="Delta_T\t"
                res={}
                for i in range(min, max+1):
                    res_text+=str(i)+"\t"*3
                res_text+="\n"
                for i in range(min, max+1):
                    res[i]=temp_median(GV.datas, i, self.period.get())
                    for elem in res[i][list(res[i].keys())[0]]:
                        res_text+="\t"+elem
                res_text+="\n"
                for year in res[list(res.keys())[0]]:
                    res_text+=str(year)
                    for i in res:
                        for j in res[i]:
                            if j==year:
                                for k in res[i][j]:
                                    res_text+="\t"+str(res[i][j][k])
                    res_text+="\n"

            else:
                res=temp_median(GV.datas, int(self.Sb_tweak31.get()), self.period.get())
                for elem in res[list(res.keys())[0]]:
                    res_text+="\t"+elem
                res_text+="\n"
                for year in res:
                    res_text+=str(year)
                    for data in res[year]:
                        res_text+="\t"+str(res[year][data])
                    res_text+="\n"


        if self.output_toggle.get():
            file_write(self.E_output.get(),res_text, GV.read_log)
            extra_text=", results in '{}'".format(self.E_output.get())
        #messagebox.showinfo("Done", "Data analysed"+extra_text)

        self.L_anayse.config(text="")
        if len(res_text)>2000:
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


        elif value=="Rain Cumuls":
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

        elif value=="Temp Median":
            self.period.set(0)
            Cb_range_step=tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.cb_toggle_auto_min3)
            Cb_range_step.grid(row=row, column=1)
            row+=1
            tk.Label(self.tweak_frame, text="Delta temp: ").grid(row=row, column=1)
            self.toggle_auto_min3(True)
            tk.Label(self.tweak_frame, text="°C").grid(row=row,column=6)
            row+=1
            tk.Label(self.tweak_frame, text="Type:").grid(row=row, column=1)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Day to day", value=0).grid(row=row, column=2, sticky=tk.W, columnspan=10)
            tk.Radiobutton(self.tweak_frame, var=self.period, text="Per event", value=1).grid(row=row+1, column=2, sticky=tk.W, columnspan=10)


    def load_begin(self):
        load_w_width=200
        load_w_height=70
        x=self.w.winfo_x()+int(self.w.winfo_width()/2-load_w_width/2)
        y=self.w.winfo_y()+int(self.w.winfo_height()/2-load_w_height/2)

        self.w.config(cursor="watch")

        self.load_w=tk.Tk()
        self.load_w.title("Loading")
        self.load_w.geometry('%dx%d+%d+%d' % (load_w_width, load_w_height, x, y))
        tk.Label(self.load_w, text="Loading, please wait...\n(This can take a few minutes)").pack()#.grid(row=1,column=1)
        tk.Button(self.load_w, text="Cancel", state="disable").pack()#.grid(row=2, column=1)

        self.w.update()
        self.load_w.update()
        self.load_w.grab_set()

    def load_end(self):
        self.w.config(cursor="")
        self.load_w.destroy()

    def cb_toggle_auto_min(self):
        self.toggle_auto_min(False)

    def toggle_auto_min(self, first):
        row=2
        if self.auto_step.get():
            self.Sb_L1_tweak1.destroy()
            self.Sb_tweak1.destroy()
            self.Sb_L2_tweak1.destroy()

            self.Sb_L1_tweak1=tk.Label(self.tweak_frame, text="Min Event delta Temp:")
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
                self.Sb_L1_tweak1.destroy()
                self.Sb_tweak11.destroy()
                self.Sb_L3_tweak1.destroy()
                self.Sb_tweak12.destroy()
                self.Sb_L4_tweak1.destroy()

            self.Sb_L1_tweak1=tk.Label(self.tweak_frame, text="Min Event delta Temp:")
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

            self.Sb_L1_tweak2=tk.Label(self.tweak_frame, text="Min rain:")
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

            self.Sb_L1_tweak2=tk.Label(self.tweak_frame, text="Min rain:")
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


ANALYSE_TYPE = ("Difference Time", "Rain Cumuls", "Temp Median")

#file_name="../Donnee/month6.txt"
FILE_ENCODING="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)



column_format_name=["STA", "JAHR", "MO", "TG", "HH", "MM"]
column_format=["Station", "Year", "Month", "Day", "Hour", "Minutes"]

#######################################################################################
#                            Main programme                                           #
#######################################################################################
GV=GlobalVariables()

main=Window()
main.w.mainloop()


#TO DO: Finish ranged min temperature (GUI ok, calcule not)
