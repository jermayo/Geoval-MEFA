#!/usr/bin/python
# -*- coding: UTF-8 -*-
# MEFA: Meterological Event Frequency Analysis Software
# Ver. 1.9.6
# Jérémy Mayoraz pour GéoVal
# Sion, Août 2018

TAKE_OUT_FIRST=2 #Number of years to take out
TAKE_OUT_LAST=1

DEFAULT_FILE_NAME=""

RAIN_LIMIT=100
TEMP_LIMIT=100

ANALYSE_TYPE = ("Data_Cleaning", "Difference_Time", "Temp_Average", "Day_To_Span_Average", "Rain_Cumul", "Rain_Event", "Rain_Max")
ANALYSE_TYPE_GUI=("Data_Cleaning", "Difference_Time", "Temp_Average", "Day_To_Span_Average", "Rain_Cumul")

FILE_ENCODING="ISO 8859-1"        #Encoding not same on linux and windows (fgs wondows)

CLEANING_INFO=""" Description:
Data Cleaning:
Does what it says. 'Daily Average': Daily average of the temperature and Rain Cumul"""
DIFF_TIME_INFO="""  Description:
Difference over time:
Event starts if the difference beetween a value and the value recorded "Time Diff" before is greater than "Delta Temp".
It ends after "Max event time" so every value greater than "Delta Temp" in that period is not taken into account. The period
allows one to look at the number of event per period of each year. """
TEMP_AVERAGE_INFO="""   Description:
Temperature average:
Event happens if the difference beetween the daily average and the typical average is greater than "Delta Temp".
The typical average is calulated for each day of the year as the average of the daily average of one of the day of the year.
(For exemple: take the daily average of each July 20th every year and make the average of them all, that is the typical daily average)
"Per event" implies that if two consecutive days are events, they only count as one,
whereas "day to day" counts every day that is an event."""
DAY_TO_SPAN_INFO="""    Description:
Day_To_Span_Average:
Event happens if the difference bettween the daily average and the average of 'span' days before and after is greater than 'Delta Temp'.
With 'Day to day': Every day that is over counts, with 'Per Event': Event stops if the daily average gets under 'Delta Temp' for more
than 'Min time beet. events' days."""
RAIN_CUMUL_INFO=""" Description:
Rain cumul:
Events starts when the rain cumul in the last "step" hours is greater than "Min Rain".
The value of "Min Rain" is in mm/"step"
Events stops when the time beetween the next time the cumul is greater than "Min Rain"
and the last time it did is greater than "Min time beet. events"."""
AUTO_RANGE_INFO="""\n\nAuto Range: automaticaly makes the analyses for all values beetween set boundaries"""
WITH_MAX_INFO="""
With 'With max' (only possible for Auto Range), an event is counted ONLY in the temperature corresponding to it's maximal value."""
