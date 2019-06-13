#!/usr/bin/python
import sys, getopt, subprocess, re

def main(argv):

   c_param = 10
   q_param = 20
   fixrate = False
   limit_latency = 0
   limit_raise = 95
   limit_keep = 85
   iterations = 50
   rate_change_inp = 10
   got_url = False
   verbose_mode = False
   test_len = 2 # in secs
#   rate_change_abs = 10

   try:
      opts, args = getopt.getopt(argv,"vhc:q:fl:r:k:i:p:u:t:")
   except getopt.GetoptError:
      helpmsg()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         helpmsg()
         sys.exit()
      elif opt in ("-u"):
         url = arg
         got_url = True
      elif opt in ("-c"):
         c_param = int(arg)
      elif opt in ("-q"):
         q_param = int(arg)
      elif opt in ("-l"):
         limit_latency = float(arg)
      elif opt in ("-r"):
         limit_raise = int(arg)
      elif opt in ("-k"):
         limit_keep = int(arg)
      elif opt in ("-i"):
         iterations = int(arg)
      elif opt in ("-t"):
         test_len = int(arg)
      elif opt in ("-p"):
         rate_change_inp = int(arg)
      elif opt in ("-f"):
         fixrate = True
      elif opt in ("-v"):
         verbose_mode = True

   if (not got_url):
       print 'Specifying the URL is mandatory.'
       helpmsg()
       sys.exit(0) 

   if (verbose_mode):
     print "Parameters: "
     print 'Iterations:                          ', iterations
     print 'Concurrent users:                    ', c_param 
     print 'Request rate per user:               ', q_param 
     print 'Latency limit:                       ', 'not set' if limit_latency == 0 else limit_latency 
     print 'Above this limit(%) increse load:    ', limit_raise
     print 'Above this limit(%) keep load level: ', limit_keep
     print 'Single test duration (sec):          ', test_len

   print "INPUT_QPS;OUTPUT_RPS;SUCC;AVG;P50;P95;P99;OPERATION" 

   op = '-'
   rps = avg = p50 = p95 = p99 = 0

   for i in range(iterations):
       qps = c_param * q_param
       cmd_str = 'hey -z ' + str(test_len) + 's -c ' + str(c_param) + ' -q ' + str(q_param) + ' ' + url
       p = subprocess.Popen(cmd_str, stdout=subprocess.PIPE, shell=True)
       for line in p.stdout:
         if "Req" in line: 
           rps = float(line.split(':')[1].strip())
         if "Ave" in line: 
           avg = float(line.split(':')[1].split(' ')[0].strip())
         if "50%" in line: 
           p50 = float(line.split(' ')[4].strip())
         if "95%" in line: 
           p95 = float(line.split(' ')[4].strip())
         if "99%" in line: 
           p99 = float(line.split(' ')[4].strip())

       succ_rate = 100 * rps / qps
       

       if (not fixrate): #adjust parameters
        if (limit_latency > 0 ):
          if (limit_latency < p95 ):
            op = 'v'
            c_param =  int(c_param * (100 - rate_change_inp) / 100)
        if (not op == 'v'):
          if (succ_rate >= limit_raise):  #increase load level
            c_new =  int(c_param * (100 + rate_change_inp) / 100)
            c_param = max(c_new, c_param+1)
            op = '^'
          elif (succ_rate >= limit_keep): #keep load level
            op = '-'
          else:  # back off load level to the achieved rps
            c_param =  int(rps / q_param )
            op = '_'

       if (c_param < 1):
         c_param = 1

       print ("%i;%.2f;%.2f;%.4f;%.4f;%.4f;%.4f;%s" % (qps, rps, succ_rate, avg, p50, p95 ,p99, op))
       sys.stdout.flush()
       op = 'x'

   

def helpmsg():
#    print sys.argv[0]
    print "Usage: "
    print "Mandatory parameter:"
    print '   -u <URL> : HTTP server URL, must start with http:// !!!'
    print "Optional parameters:"
    print '   -i <iterations, default: 50>'
    print '   -t <single test length in secs, default 2s>'
    print '   -c <concurrent users, default: 10>'
    print '   -q <ratelimit /user, default: 20>'
    print '   -f : do not adjust the request rate'
    print '   -l <latency limit for p95 in sec for control> '
    print '   -r <level in percentage, default: 95%> : load is increased if the reported request rate reaches at least this percentage'
    print '   -k <level in percentage, default: 85%> : load is unchanged if the reported request rate reaches at least this percentage and is below r'
    print '   -p <load increase in percentage, default: 10>             : load is increased with this percentage'
        
 
if __name__ == "__main__":
   main(sys.argv[1:])
