class MessagePrefix:
    ERROR = "[ERROR]\t"
    DEBUG = "[DEBUG]\t" 
    INFO  = "[INFO]\t"
   
def print_error(msg):
    print(MessagePrefix.ERROR+msg)
def print_debug(msg):
    print(MessagePrefix.DEBUG+msg)
def print_info(msg):
    print(MessagePrefix.INFO+msg)
