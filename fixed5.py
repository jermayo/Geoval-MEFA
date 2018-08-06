import tkinter as tk
from tkinter import messagebox
import datetime
import sys

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

    for i in range(0, len(column_format)):
        column.append({"pos":i, "name":column_format_name[i], "val":column_format[i]})

    try:
        file=open(file_name, 'r', encoding=file_encoding)
        file_lines=file.readlines()
        file.close()
    except FileNotFoundError:
        messagebox.showerror("Error", "File not found (404)")
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
#Temperature
#Difference of temp with 24h or 48h before
def diff_temp(datas, delta_t):
    new_datas=[]
    for i in range(0,len(datas)):
        j=i
        while datas[j]["date"]-datas[i]["date"]<delta_t:
            j+=1
        new_data={"f_data":datas[i], "s_data":datas[j]}
        new_data["dtemp"]=datas[j]["temp"]-datas[i]["temp"]
        if j>=len(datas)-1:
            break
        new_datas.append(new_data)
    return new_datas


def diff_time(raw_datas, delta_t, delta_temp, time_max_event, period_start, period_end):
    during_event=False
    event_list=[]
    datas=[]

    for data in raw_datas:
        if data["date"].month>=period_start.month and data["date"].month<period_end.month:
            if data["date"].day>=period_start.day and data["date"].month<period_end.day:
                datas.append(data)

    datas=diff_temp(datas, delta_t)

    for data in datas:
        if not during_event and abs(data["dtemp"])>delta_temp:
            during_event=True
            event_type="+"
            if data["dtemp"]<0:
                event_type="-"
            new_event={"start": data["f_data"]["date"], "type": event_type}
            new_event["max"]=data["dtemp"]

        elif during_event:
            if new_event["type"]=="+":
                new_event["max"]=max(data["dtemp"], new_event["max"])
            elif new_event["type"]=="-":
                new_event["max"]=min(data["dtemp"], new_event["max"])

            if data["f_data"]["date"]-new_event["start"]>time_max_event:
                during_event=False
                new_event["year"]=new_event["start"].year
                event_list.append(new_event)

    #for a certain periode (for now years)
    peri_list=[]
    for event in event_list:
        flag=True
        for peri in peri_list:
            if event["year"]==peri["year"]:
                flag=False
        if flag:
            peri={"year": event["year"], "pos":0, "neg":0, "total":0}
            peri_list.append(peri)

        if event["type"]=="+":
            peri["pos"]+=1
        elif event["type"]=="-":
            peri["neg"]+=1
        peri["total"]+=1

    return peri_list




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

        tk.Label(self.w, text="File Name:").grid(row=1,column=0)
        self.E_file = tk.Entry(self.w)
        self.E_file.insert(0,"../Donnee/month6.txt")
        self.E_file.grid(row=1,column=1)
        self.B_open = tk.Button(self.w, text="Open", command=self.open_file)
        self.B_open.grid(row=1,column=2)

        self.B_exit = tk.Button(self.w, text="Exit", command=self.w.destroy)
        self.B_exit.grid(row=5, column=3)

        self.L_file=tk.Label(self.w, text=self.file_name)

        self.result_frame=tk.LabelFrame(self.w, text="Results")
        self.res_text=tk.Label(self.result_frame, justify=tk.LEFT)
        self.res_text.grid()
        self.result_frame.grid(row=4,column=3)
        self.result_frame.grid_remove()

        self.L_anayse=tk.Label(self.w, text = "")
        self.L_anayse.grid(row=4,column=3)

    def init_analyse_option(self):
        output_frame = tk.LabelFrame(self.w, text="Output Log File")
        self.CB_output = tk.Checkbutton(output_frame, variable=self.output_toggle, text="Output file")
        self.CB_output.grid(row=1,column=3)
        tk.Label(output_frame, text="File Name:").grid(row=2,column=3)
        self.E_output = tk.Entry(output_frame)
        self.E_output.insert(0,"output.txt")
        self.E_output.grid(row=2,column=4)
        output_frame.grid(row=1,rowspan=2, column=3)

        tk.Label(self.w, text="Analyse type:").grid(row=3,column=0)
        self.O_analyse=tk.OptionMenu(self.w, self.analyse_type, *ANALYSE_TYPE, command=self.change_analyse)
        self.O_analyse.grid(row=3,column=1)

        self.B_open = tk.Button(self.w, text="Analyse", command=self.analyse)
        self.B_open.grid(row=3,column=2)

        self.tweak_frame = tk.LabelFrame(self.w, text="Tweaks")

        self.change_analyse("Difference Time")

    def open_file(self):
        old_text=self.file_name
        self.L_file.config(text = "Loading File...")
        self.L_file.grid(row=2,column=0,columnspan=2)
        self.L_file.update_idletasks()
        self.disable_all()

        self.file_name=self.E_file.get()
        datas, read_log=read_file(self.file_name, GV.temp_col, GV.rain_col, file_encoding=FILE_ENCODING)
        if read_log:
            GV.datas, GV.read_log = datas, read_log
            self.init_analyse_option()
            self.L_file.config(text = "File '{}' loaded".format(self.file_name))
            messagebox.showinfo("Done", "File loaded: \n"+GV.read_log)
        else:
            self.L_file.config(text = old_text)
        self.enable_all()

    def analyse(self):
        analyse=self.analyse_type.get()
        self.result_frame.grid_remove()
        self.L_anayse.config(text="Analysing data ...")
        self.L_anayse.update_idletasks()
        self.disable_all()

        extra_text=""
        if analyse=="Difference Time":
            delta_t=datetime.timedelta(hours=int(self.Sb_tweak2.get()))
            time_max_event=datetime.timedelta(hours=int(self.Sb_tweak3.get()))
            start=datetime.datetime.strptime("1-1", "%m-%d")
            end=datetime.datetime.strptime("12-31", "%m-%d")
            res=diff_time(GV.datas, delta_t, int(self.Sb_tweak1.get()), time_max_event, start, end)
            res_text="Year\tPos.\tNeg.\tTotal\n"
            for i in res:
                res_text+="{}\t{}\t{}\t{}\n".format(i["year"], i["pos"], i["neg"], i["total"])

        if analyse=="Rain Cumuls":
            step=datetime.timedelta(hours=int(self.Sb_tweak1.get()))
            min_time_beetween_event=datetime.timedelta(minutes=int(self.Sb_tweak3.get()))
            if self.auto_step.get():
                res_total=[]
                res_text="\t"
                min=int(self.Sb_tweak21.get())
                max=int(self.Sb_tweak22.get())+1
                for i in range(min, max):
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

        if self.output_toggle.get():
            file_write(self.E_output.get(),res_text, GV.read_log)
            extra_text=", results in '{}'".format(self.E_output.get())
        messagebox.showinfo("Done", "Data analysed"+extra_text)

        self.L_anayse.config(text="")

        self.res_text.config(text=res_text)
        self.res_text.grid()
        self.result_frame.grid()

        self.enable_all()

    def change_analyse(self, value):
        for child in self.tweak_frame.winfo_children():
            child.destroy()
        if value=="Difference Time":
            tk.Label(self.tweak_frame, text="Min Event delta Temp:").grid(row=1,column=1)
            self.Sb_tweak1=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_tweak1.delete(0,tk.END)
            self.Sb_tweak1.insert(0,10)
            self.Sb_tweak1.grid(row=1,column=2)
            tk.Label(self.tweak_frame, text="°C").grid(row=1,column=3)

            tk.Label(self.tweak_frame, text="Time Diff:").grid(row=2,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=24, to_=1000, justify=tk.RIGHT, width=3, increment=24)
            self.Sb_tweak2.grid(row=2,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=2,column=3)

            tk.Label(self.tweak_frame, text="Max Event Time:").grid(row=3,column=1)
            self.Sb_tweak3=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak3.delete(0,tk.END)
            self.Sb_tweak3.insert(0,24)
            self.Sb_tweak3.grid(row=3,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=3,column=3)

        elif value=="Rain Cumuls":
            self.auto_step=tk.IntVar()
            self.auto_step.set(0)
            row=1
            tk.Label(self.tweak_frame, text="Step:").grid(row=row,column=1)
            self.Sb_tweak1=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_tweak1.delete(0,tk.END)
            self.Sb_tweak1.insert(0,6)
            self.Sb_tweak1.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=row,column=3)
            row+=1
            Cb_range_step=tk.Checkbutton(self.tweak_frame, variable=self.auto_step, text="Ranged Auto Min", command=self.toggle_auto_min)
            Cb_range_step.grid(row=row, column=1)
            row+=1
            self.Sb_L1_tweak2=tk.Label(self.tweak_frame, text="Min rain:")
            self.Sb_L1_tweak2.grid(row=row,column=1)
            self.Sb_tweak2=tk.Spinbox(self.tweak_frame, from_=0, to_=1000000, justify=tk.RIGHT, width=3)
            self.Sb_tweak2.delete(0,tk.END)
            self.Sb_tweak2.insert(0,5)
            self.Sb_tweak2.grid(row=row,column=2)
            self.Sb_L2_tweak2=tk.Label(self.tweak_frame, text="mm/time")
            self.Sb_L2_tweak2.grid(row=row,column=3)
            row+=1
            tk.Label(self.tweak_frame, text="Min time beet. events:").grid(row=row,column=1)
            self.Sb_tweak3=tk.Spinbox(self.tweak_frame, from_=0, to_=10000, justify=tk.RIGHT, width=3)
            self.Sb_tweak3.delete(0,tk.END)
            self.Sb_tweak3.insert(0,10)
            self.Sb_tweak3.grid(row=row,column=2)
            tk.Label(self.tweak_frame, text="Min").grid(row=row,column=3)

        self.tweak_frame.grid(row=4,column=0, rowspan=2, columnspan=3)


    def disable_all(self):
        for child in self.w.winfo_children():
            if child.winfo_class()=="Labelframe":
                for grand_child in child.winfo_children():
                    if grand_child.winfo_class()!="Message":
                        grand_child.configure(state='disable')
            else:
                child.configure(state='disable')

    def enable_all(self):
        for child in self.w.winfo_children():
            if child.winfo_class()=="Labelframe":
                for grand_child in child.winfo_children():
                    if grand_child.winfo_class()!="Message":
                        grand_child.configure(state='normal')
            else:
                child.configure(state='normal')

    def toggle_auto_min(self):
        row=3
        if self.auto_step.get():
            self.Sb_L1_tweak2.destroy()
            self.Sb_L2_tweak2.destroy()
            self.Sb_tweak2.destroy()
            self.w.update()

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


ANALYSE_TYPE = ("Difference Time", "Rain Cumuls", "Option 3")

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
