import datetime
import time

def time_until(Year=None,     Month=None,     Day=None,     Hour=None,     Minute=None,     Second=None,
               AddYear=False, AddMonth=False, AddDay=False, AddHour=False, AddMinute=False, AddSecond=False):
    now = datetime.datetime.now()

    FinalYear = Year if Year is not None and not AddYear else now.year
    FinalMonth = Month if Month is not None and not AddMonth else now.month
    FinalDay = Day if Day is not None and not AddDay else now.day
    FinalHour = Hour if Hour is not None and not AddHour else now.hour
    FinalMinute = Minute if Minute is not None and not AddMinute else now.minute
    FinalSecond = Second if Second is not None and not AddSecond else now.second
    
    if AddYear and Year is not None:
        FinalYear += Year
    if AddMonth and Month is not None:
        FinalMonth += Month
    if AddDay and Day is not None:
        FinalDay += Day
    if AddHour and Hour is not None:
        FinalHour += Hour
    if AddMinute and Minute is not None:
        FinalMinute += Minute
    if AddSecond and Second is not None:
        FinalSecond += Second
        
    then = datetime.datetime(FinalYear, FinalMonth, FinalDay, FinalHour, FinalMinute, FinalSecond)
    return then - now

print(time_until(Hour=16, Minute=0, Second=0).total_seconds())
print(time_until(Hour=1, Minute=0, Second=0, AddHour=True).total_seconds())