import tkinter as tk
import datetime
import sys

#######################################################################################
#                                    Classes                                          #
#######################################################################################
class GlobalVariables():
    def __init__(self):
        self.datas=None
        self.read_log=None
        self.temp_col=False
        self.rain_col=False
        column_format_name=["STA", "JAHR", "MO", "TG", "HH", "MM"]
        column_format=["Station", "Year", "Month", "Day", "Hour", "Minutes"]
        self.column=Column.build(column_format_name, column_format)



#Column object
class Column():
    def __init__(self, pos, name, val):
        self.pos=pos
        self.name=name
        self.val=val

    def build(col_names, col_vals):
        if len(col_names)!=len(col_vals):
            print("Error: Column names not same length as column values\n")
        else:
            l=[]
            for i in range(0, len(col_names)):
                l.append(Column(i, col_names[i], col_vals[i]))
            return l

#Data object
class Data():
    def __init__(self, line):
        try:
            self.state=True
            self.date=Data.get_date(line)
            self.rain=eval(Data.get_elem("Rain", line))
            self.temp=eval(Data.get_elem("Temp", line))
            if abs(self.rain)>RAIN_LIMIT or abs(self.temp)>TEMP_LIMIT:
                self.state=False
        except:
            print("Error: Data could not be retrieved\n")
            print(sys.exc_info()[0])
            sys.exit()

    def get_elem(elem, line):
        for i in range(0,len(GV.column)):
            if GV.column[i].val==elem:
                return line[i]
        return None

    def get_date(line):
        date_val=Data.get_elem("Year", line)+"-"+Data.get_elem("Month", line)
        date_val+="-"+Data.get_elem("Day", line)
        date_val+="-"+Data.get_elem("Hour", line)+"-"+Data.get_elem("Minutes",line)
        return datetime.datetime.strptime(date_val, DATE_FORMAT)

############################# Type of analyse #########################################
#Difference of temp with 24h or 48h before
class Difference_Time():
    def __init__(self, first_data, after_data):
        self.first_data=first_data
        self.after_data=after_data
        self.dtemp=after_data.temp-first_data.temp
        self.drain=after_data.rain-first_data.rain

    def build(datas, delta_t):
        l=[]
        for i in range(0,len(datas)):
            j=i
            flag=True
            while datas[j].date-datas[i].date<delta_t:
                j+=1
                if j>=len(datas):
                    return l
            l.append(Difference_Time(datas[i], datas[j]))

    #temp over a certain point makes an event
    def analyse(datas, delta_temp, time_max_event):
        during_event=False
        event_list=[]
        for data in datas:
            if not during_event and abs(data.dtemp)>delta_temp:
                during_event=True
                event_type="+"
                if data.dtemp<0:
                    event_type="-"
                new_event={"start": data.first_data.date, "type": event_type}
                new_event["max"]=data.dtemp

            elif during_event:
                if new_event["type"]=="+":
                    new_event["max"]=max(data.dtemp, new_event["max"])
                elif new_event["type"]=="-":
                    new_event["max"]=min(data.dtemp, new_event["max"])

                if data.first_data.date-new_event["start"]>time_max_event:
                    during_event=False
                    new_event["year"]=new_event["start"].year
                    event_list.append(new_event)

        #for a certain periode (for now years)
        peri_list=[]
        for event in event_list:
            flag=True
            for peri in peri_list:
                if event["year"]==peri["periode"]:
                    flag=False
            if flag:
                peri={"periode": event["year"], "pos":0, "neg":0, "total":0}
                peri_list.append(peri)

            if event["type"]=="+":
                peri["pos"]+=1
            elif event["type"]=="-":
                peri["neg"]+=1
            peri["total"]+=1

        return peri_list



#######################################################################################
#                             File Reading and Writting                               #
#######################################################################################
def read_file(file_name, temp_col, rain_col, file_encoding="UTF-8"):
    def get_start(line):
        #Prevent exception
        if line==[]:
            return False
        for i in range(0, min(len(GV.column),len(line))):
            if GV.column[i].name!=line[i]:
                return False
        return True

    datas=[]
    bad_data=0

    file=open(file_name, 'r', encoding=file_encoding)
    file_lines=file.readlines()
    file.close()

    flag_1=False
    for comp_line in file_lines:
        line=comp_line.split()
        #Main data input
        if flag_1 and line!=[]:
            new_data=Data(line)
            if new_data.state:
                if len(datas)==0:
                    datas.append(new_data)
                elif new_data.date>datas[-1].date:
                        datas.append(new_data)
                else:
#!!! To do: Auto sort by date
                    print("Error: Data not in order (will be fixed)")
                    print("Date: ", line.date)
            else:
                bad_data+=1

        #Get startitng point
        elif get_start(line):
            for i in line:
                if i==rain_col:
                    GV.column.append(Column(i, rain_col, "Rain"))
                    flag_1=True
                elif i==temp_col:
                    GV.column.append(Column(i, temp_col, "Temp"))
                    flag_1=True
            if not flag_1:
                print("Error: No temperature or rain data detected, exitting")
                sys.exit()
        #Automatic rain and temp column detection
        elif len(line)>1 and AUTO_MODE:
            if line[1]==RAIN_KEYWORD:
                rain_col=line[0]
            elif line[1]==TEMP_KEYWORD:
                temp_col=line[0]

    if not flag_1:
        print("No data found (programmer might be an idiot), exitting")
        sys.exit()

    log="\t{} values with {} bad values ({}%) (taken out)".format(len(datas), bad_data, bad_data/len(datas)*100)
    return datas, log


def file_write(file_name, res, log):
    file=open(file_name, "w")
    file.write("\t\t\t\t\t{}\n".format(datetime.datetime.now().strftime('%Y-%m-%d')))
    file.write("Result of analyse of data:")
    file.write(log+"\n")
    file.write("Periode Pos. Neg. Total\n")
    for i in res:
        file.write("{}\t{}\t{}\t{}\n".format(i["periode"], i["pos"], i["neg"], i["total"]))
    file.close()

#######################################################################################
#                             GUI                                                    #
#######################################################################################
class Window():
    def __init__(self):
        #Main window
        self.w=tk.Tk()
        #StringVar
        self.analyse_type = tk.StringVar(self.w)
        self.analyse_type.set(ANALYSE_TYPE[0])
        self.output_toggle = tk.IntVar()
        self.output_toggle.set(1)

        tk.Label(self.w, text="File Name:").grid(row=1,column=0)
        self.E_file = tk.Entry(self.w)
        self.E_file.insert(0,"../Donnee/month6.txt")
        self.E_file.grid(row=1,column=1)
        self.B_open = tk.Button(self.w, text="Open", command=self.open_file)
        self.B_open.grid(row=1,column=2)

        output_frame = tk.LabelFrame(self.w, text="Output Log File")
        self.CB_output = tk.Checkbutton(output_frame, variable=self.output_toggle, text="Output file")
        self.CB_output.grid(row=1,column=3)
        tk.Label(output_frame, text="File Name:").grid(row=2,column=3)
        self.E_output = tk.Entry(output_frame)
        self.E_output.insert(0,"output.txt")
        self.E_output.grid(row=2,column=4)
        output_frame.grid(row=1,rowspan=2, column=3)

        tk.Label(self.w, text="Analyse type:").grid(row=2,column=0)
        self.O_analyse=tk.OptionMenu(self.w, self.analyse_type, *ANALYSE_TYPE, command=self.change_analyse)
        self.O_analyse.grid(row=2,column=1)

        self.B_open = tk.Button(self.w, text="Analyse", command=self.analyse)
        self.B_open.grid(row=2,column=2)

        self.B_exit = tk.Button(self.w, text="Exit", command=self.w.destroy)
        self.B_exit.grid(row=1000, column=3)

        self.tweak_frame = tk.LabelFrame(self.w, text="Tweaks")


    def open_file(self):
        file_name=self.E_file.get()
        GV.datas, GV.read_log=read_file(file_name, GV.temp_col, GV.rain_col, file_encoding=FILE_ENCODING)

    def analyse(self):
        analyse=self.analyse_type.get()
        if analyse=="Difference Time":
            delta_t=datetime.timedelta(hours=int(self.Sb_Dtime.get()))
            time_max_event=datetime.timedelta(hours=int(self.Sb_Dmax_time.get()))
            diff_time=Difference_Time.build(GV.datas, delta_t)
            res=Difference_Time.analyse(diff_time, int(self.Sb_Dtemp.get()), time_max_event)

        if self.output_toggle:
            file_write(self.E_output.get(),res, GV.read_log)

    def change_analyse(self, value):
        for child in self.tweak_frame.winfo_children():
            child.destroy()
        if value=="Difference Time":
            tk.Label(self.tweak_frame, text="Min Event delta Temp:").grid(row=1,column=1)
            self.Sb_Dtemp=tk.Spinbox(self.tweak_frame, from_=0, to_=TEMP_LIMIT, justify=tk.RIGHT, width=3)
            self.Sb_Dtemp.delete(0,tk.END)
            self.Sb_Dtemp.insert(0,10)
            self.Sb_Dtemp.grid(row=1,column=2)
            tk.Label(self.tweak_frame, text="°C").grid(row=1,column=3)

            tk.Label(self.tweak_frame, text="Time Diff:").grid(row=2,column=1)
            self.Sb_Dtime=tk.Spinbox(self.tweak_frame, from_=24, to_=1000, justify=tk.RIGHT, width=3, increment=24)
            self.Sb_Dtime.grid(row=2,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=2,column=3)

            tk.Label(self.tweak_frame, text="Max Event Time:").grid(row=3,column=1)
            self.Sb_Dmax_time=tk.Spinbox(self.tweak_frame, from_=0, to_=1000, justify=tk.RIGHT, width=3)
            self.Sb_Dmax_time.delete(0,tk.END)
            self.Sb_Dmax_time.insert(0,24)
            self.Sb_Dmax_time.grid(row=3,column=2)
            tk.Label(self.tweak_frame, text="Hours").grid(row=3,column=3)

            self.tweak_frame.grid(row=3,column=0, columnspan=3)



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


ANALYSE_TYPE = ("Difference Time", "Option 2", "Option 3")

#file_name="../Donnee/month6.txt"
FILE_ENCODING="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)





#######################################################################################
#                            Main programme                                           #
#######################################################################################
GV=GlobalVariables()

main=Window()
main.w.mainloop()
