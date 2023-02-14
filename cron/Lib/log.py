import logging
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

def getLogger(name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    #dir_path = "/var/log/cron/"
    log = logging.getLogger(name)
    hdlr = logging.FileHandler(dir_path+'/report.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s: %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr) 
    log.setLevel(logging.ERROR)
    log.setLevel(logging.INFO)
    #log.setLevel(logging.DEBUG)
    return log
  