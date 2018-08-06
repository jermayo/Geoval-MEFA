#fixed1.py
#11 july 2018
#Jeremy Mayoraz
#Note: first debuged program: reads (formated) files, prepares data 

import datetime
import sys

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
        #try:
            self.date=Data.get_date(line)
            self.rain=Data.get_elem("Rain", line)
            self.temp=Data.get_elem("Temp", line)
        #except:
        #    print("Error: Data could not be retrieved\n")
        #    sys.exit()

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

def read_file(file_name, temp_col, rain_col, file_encoding="UTF-8", ):
    def get_start(line):
        #Prevent exception
        if line==[]:
            return False
        for i in range(0, min(len(column),len(line))):
            if column[i].name!=line[i]:
                return False
        return True

    datas=[]

    file=open(file_name, 'r', encoding=file_encoding)
    file_lines=file.readlines()
    file.close()

    flag_1=False
    for comp_line in file_lines:
        line=comp_line.split()
        #Main data input
        if flag_1 and line!=[]:
            datas.append(Data(line))
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
                print("No temperature or rain data detected, exitting")
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

    return datas



#File format
column_format_name=["STA", "JAHR", "MO", "TG", "HH", "MM"]
column_format=["Station", "Year", "Month", "Day", "Hour", "Minutes"]
column=Column.build(column_format_name, column_format)

DATE_FORMAT='%Y-%m-%d-%H-%M'

AUTO_MODE=True
#Rain column name
RAIN_COL_NAME="Niederschlag"
#Temperature column name
TEMP_COL_NAME="Lufttemperatur"

temp_col, rain_col= False, False


file_name="../Donnee/month1.txt"
file_encoding="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)



datas=read_file(file_name, temp_col, rain_col, file_encoding=file_encoding)

for i in datas:
    print(i.date, i.temp, i.rain)
