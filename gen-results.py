import sys
import string
import textwrap
import math
import numpy
import time
import random
import glob
import os
import json
from os import system, remove
import errno


def print_usage():

   print("Usage: \n\n")
   print("\tgen-results.py run_name -o output_folder \n\n")
   
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
   
def getoptions(args):
   
   found = ""
   dict = {}
   for arg in args:
      if found != "":
         if arg[0] == "-":
            arg = arg.lstrip("-")
            if len(arg) > 0:
               dict[found] = ""
               found = arg
         else:
            dict[found] = arg
            found = ""
      else:
         if arg[0] == "-":
            arg = arg.lstrip("-")
            if len(arg) > 0:
               found = arg
   if found != "":
      dict[found] = ""
   
   print (dict,'\n')
   return dict
   
   

if len(sys.argv) < 4:
   print_usage()
   exit()
   
args = getoptions(sys.argv[1:])


if ('o' not in args.keys()):
   print_usage()
   print(":(")
   exit()
   
   
#read in the results file
run_name = sys.argv[1]
input = args['o']+ "/" + run_name + "/results.json"
try:
   f = open(input)
   res = json.load(f)
   f.close()
   
except FileNotFoundError:
   print("Results file not found in specified location")
   exit()



if len(res) < 1:
   print("results file empty")
   exit()
#generate the ber plot
#requires: snr, total_bits, total_bit_errors
if ('snr' in res[0].keys()) and ('total_bits' in res[0].keys()) and ('total_bit_errors' in res[0].keys()):
   print("generating ber graph")
   
   #write .dat with all the data
   dat_file = args['o']+ "/" + run_name + "/ber_gnuplot.dat" 
   f=open(dat_file,"w")
   f.write("#dat file for ber plot\n")
   maxsnr = -1000;
   minsnr = 1000;
   for i in range(0,len(res)):
      f.write(repr(res[i]['snr']) + "\t" + repr(res[i]['total_bit_errors']) + "\t" + repr(res[i]['total_bits'])+"\n")
      if float(res[i]['snr']) < minsnr:
         minsnr = float(res[i]['snr'])
      if float(res[i]['snr']) > maxsnr:
         maxsnr = float(res[i]['snr'])
   f.close()
   
   f=open(args['o']+ "/" + run_name + "/ber_gnuplot.gp" ,"w")
   #generate the gnuplot script
   f.write(textwrap.dedent("""\
   set terminal png
   set termoptions enhanced
   set xlabel 'SNR (dB)'
   set ylabel 'BER'
   set logscale y
   set format y '10^{%L}'
   set yrange[0.00001:1]
   """))
   f.write("set output '"+args['o']+ "/" + run_name+"/ber.png\n")
   f.write("set xrange["+repr(minsnr)+":"+repr(maxsnr)+"]\n\n")
   f.write("plot '"+args['o']+ "/" + run_name+"/ber_gnuplot.dat' using ($1-10*log10(1)):($2==0 ? NaN : $2/$3) with line ls 1 notitle")

   f.close()
   #run gnuplot
   system("gnuplot "+args['o']+ "/" + run_name + "/ber_gnuplot.gp")
