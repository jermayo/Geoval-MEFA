#proto2.py
#11 july 2018
#Jeremy Mayoraz
#Note: work in progress

import datetime
import sys

#######################################################################################
#                                    Classes                                          #
#######################################################################################

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
        for i in range(0,len(column)):
            if column[i].val==elem:
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

    def build(datas):
        l=[]
        for i in range(0,len(datas)):
            j=i
            flag=True
            while datas[j].date-datas[i].date<DELTA_T:
                j+=1
                if j>=len(datas):
                    return l
            l.append(Difference_Time(datas[i], datas[j]))

    #temp over a certain point makes an event
    def analyse(datas):
        during_event=False
        event_list=[]
        for data in datas:
            if not during_event and abs(data.dtemp)>DELTA_TEMP_MIN_EVENT:
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

                if data.first_data.date-new_event["start"]>TIME_MAX_EVENT:
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
        for i in range(0, min(len(column),len(line))):
            if column[i].name!=line[i]:
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
                    column.append(Column(i, rain_col, "Rain"))
                    flag_1=True
                elif i==temp_col:
                    column.append(Column(i, temp_col, "Temp"))
                    flag_1=True
            if not flag_1:
                print("Error: No temperature or rain data detected, exitting")
                sys.exit()
        #Automatic rain and temp column detection
        elif len(line)>1 and AUTO_MODE:
            if line[1]==RAIN_COL_NAME:
                rain_col=line[0]
            elif line[1]==TEMP_COL_NAME:
                temp_col=line[0]

    if not flag_1:
        print("No data found (programmer might be an idiot), exitting")
        sys.exit()

    print("Data reading successful")
    log="\t{} values with {} bad values ({}%) (taken out)".format(len(datas), bad_data, bad_data/len(datas)*100)
    return datas, log


def file_write(res, log):
    file=open("result.txt", "w")
    file.write("\t\t\t\t\t{}\n".format(datetime.datetime.now().strftime('%Y-%m-%d')))
    file.write("Result of analyse of data:")
    file.write(log+"\n")
    file.write("Periode Pos. Neg. Total\n")
    for i in res:
        file.write("{}\t{}\t{}\t{}\n".format(i["periode"], i["pos"], i["neg"], i["total"]))
    file.close()


#######################################################################################
#                      Global Constant and Variables                                  #
#######################################################################################
#File format
column_format_name=["STA", "JAHR", "MO", "TG", "HH", "MM"]
column_format=["Station", "Year", "Month", "Day", "Hour", "Minutes"]
column=Column.build(column_format_name, column_format)

DATE_FORMAT='%Y-%m-%d-%H-%M'

DELTA_T=datetime.timedelta(hours=24)
TIME_MAX_EVENT=datetime.timedelta(hours=24)

AUTO_MODE=True
#Rain column name
RAIN_COL_NAME="Niederschlag"
#Temperature column name
TEMP_COL_NAME="Lufttemperatur"

RAIN_LIMIT=100
TEMP_LIMIT=100

temp_col, rain_col= False, False

DELTA_TEMP_MIN_EVENT=10


file_name="test_file/month6.txt"
#file_name="../Donnee/month6.txt"
file_encoding="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)

#######################################################################################
#                            Main programme                                           #
#######################################################################################


print("Reading Data")
datas, read_log=read_file(file_name, temp_col, rain_col, file_encoding=file_encoding)
print("Analysing")

diff_time=Difference_Time.build(datas)
res=Difference_Time.analyse(diff_time)
print("Done!")
file_write(res, read_log)
