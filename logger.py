import ulogger
from machine import RTC

# Initialize Logger
class Clock(ulogger.BaseClock):
    def __init__(self):
        self.rtc = RTC()        
    def __call__(self) -> str:
        y,m,d,_,h,mi,s,_ = self.rtc.datetime ()
        return '%d-%d-%d %d:%d:%d' % (y,m,d,h,mi,s)

clock = Clock()

file_handler = ulogger.Handler(
    level=ulogger.INFO,
    fmt='&(time)% - &(level)% - &(msg)%',
    clock=clock,
    direction=ulogger.TO_FILE,
    file_name='log.txt',
    max_file_size=4096)

def get_logger(name=__name__):
    return ulogger.Logger(name, handlers=[file_handler])