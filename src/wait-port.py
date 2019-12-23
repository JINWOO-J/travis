#!/usr/bin/env python3

from optparse import OptionParser
import socket
import time
import sys
class OptionException(Exception):
    def __init__(self, value):
        self.value = value

class wait_for_app:
    def log(self, loginfo):
        if self.options.quiet is not False:
            print(loginfo)

    def build_log(self, type, app, time=0):
        # 1=enable_timeout,2=disable_timeout,3=success_msg,4=unavailable,5=timeout_msg
        loginfo = {
             1:"%s: waiting %d seconds for %s" %(sys.argv[0],time,app),
             2:"%s: waiting for %s without a timeout" %(sys.argv[0],app),
             3:"%s: %s is available after %d seconds" %(sys.argv[0],app,time),
             4:"%s: %s is unavailable ------ " %(sys.argv[0],app),
             5:"%s: timeout occurred after waiting %d seconds for %s" %(sys.argv[0],time,app),
        }.get(type)
        return loginfo

    def wait_for(self, host, port, timeout):
        self.app = ("%s:%d") %(host,port)
        sk = socket.socket()
        logmsg = self.build_log(2, self.app, timeout)
        if timeout != 0:
            logmsg = self.build_log(1, self.app, timeout)
            sk.settimeout(timeout)
        self.log(logmsg)
        start_ts = int(time.time())
        sk.connect((host,port))
        end_ts = int(time.time())
        diff_ts= end_ts - start_ts
        logmsg = self.build_log(3,self.app,diff_ts)
        self.log(logmsg)
        
    def get_parser(self):
        parser = OptionParser()
        parser.add_option('-a','--address',dest='address',help='Host or IP under test')
        parser.add_option('-p','--port',dest='port',help='TCP port under test')
        parser.add_option('-t','--timeout',dest='timeout',type=int, default='15',help='Timeout in seconds, zero for no timeout')
        parser.add_option('-q','--quiet',dest='quiet',action='store_false',help='Don\'t output any status messages')
        return parser
    
    def verify_options(self):
        if self.options.address is None:
            raise OptionException("The address must be set!")
        elif self.options.port is None:
            raise OptionException("The port must be set!")
        elif str(self.options.port).isnumeric() is False:
            raise OptionException("The value of port must be number!")
    
    def start_up(self):
        status = "Fail"        
        parser = self.get_parser()
        self.options,self.args=parser.parse_args()
        self.verify_options()
        
        try:
            self.wait_for(self.options.address, int(self.options.port), int(self.options.timeout))
            status = "OK"            
        except OptionException as err:
            print(err)
            parser.print_help()            
        except socket.timeout as err:
            logmsg = self.build_log(5, self.app, int(self.options.timeout))
            self.log(logmsg)
        except ConnectionRefusedError as err:
            logmsg = self.build_log(4, self.app)
            self.log(logmsg)

        return status

if __name__=='__main__':    
    w = wait_for_app()
    parser = w.get_parser()
    args, option  = parser.parse_args()            
    timeout = args.timeout
    start_ts = int(time.time())

    while True:        
        res = w.start_up()        
        if res == "OK":
            break
        else:
            now_ts = int(time.time())
            if (now_ts - start_ts) > timeout:
                print(f"Timeout {timeout} sec")
                break

            time.sleep(1)