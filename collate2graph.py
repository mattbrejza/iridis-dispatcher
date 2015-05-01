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
import errno

#looks in a results folder that will contain a whole load of run_name_seed.json files about the same simulation
#collates these results into a single run_name.json


def print_usage():

   print("Graph all folders in results path:\n")
   print("\tcollate2graph.py -c complexity -r results_folder -o output_folder\n\n\n")
   
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


if len(sys.argv) < 6:
   print_usage()
   exit()
   
args = getoptions(sys.argv[1:])


if ('r' not in args.keys()):
   print_usage()
   print(":(")
   exit()
   
if ('o' not in args.keys()):
   print_usage()
   print(":(")
   exit()
   
if ('c' not in args.keys()):
   print_usage()
   print(":(")
   exit()

run_names = []

cd = os.listdir(args['r'])
for i in cd:
   if os.path.isdir(args['r']+ "/" + i):
      print("Found directory: " + i)
      run_names.append(i)



snr_lists = []
ser_lists = []
run_list = []
snr_min = 1000
snr_max = -1000

      
for run_name in run_names:

   res_path = args['r']+ "/" + run_name   

   out_suffix = "totals"

   print("Results folder: " + res_path)
   print("Run name to collate: " + run_name)


   file_list = glob.glob(res_path + "/*.json")

   print("Found files:")
   print(file_list)


   out_list = list();
   snr_list = list();
   ser_list = list();

   while len(file_list) > 0:

      #loop through each file
      file = file_list.pop()
      if os.path.basename(file).find(out_suffix) >= 0:
         break
      
      #load the json
      data = json.load(open(file))

      print("found: " + repr(len(data)) + " items")
      
      #check and get the first entry
      if len(data) < 1:
         break
      if type(data) is dict:
         item = data
         data = ""
      else:
         item = data.pop()
         

      #get data from the entry and merge into what we already have
      while True:
         
         #if ('run_name' in item.keys()):
         #   
         if ('snr' in item.keys()):
            #mush everything together
            
            #search through the list looking for a close match
            found = -1
            i=0
            for s_d in out_list:
               #look here
               this_snr = s_d['snr']
               if abs(this_snr - item['snr']) < 0.0005:
                  found = i
                  break
               i=i+1
                        
               
            if found < 0:
               #add new dictionary
               out_list.append(item)
            else:
               #merge
               #go through existing list and add new data
               for k in item.keys():
                  if k not in (out_list[found]).keys():
                     (out_list[found])[k] = item[k]
                  else:
                     if k == "total_bits":
                        (out_list[found])[k] = (out_list[found])[k] + item[k]
                     elif k == "total_bit_errors":
                        (out_list[found])[k] = (out_list[found])[k] + item[k]
                     elif k == "total_frames":
                        (out_list[found])[k] = (out_list[found])[k] + item[k]
                     elif k == "total_frame_errors":
                        (out_list[found])[k] = (out_list[found])[k] + item[k]
                     elif k == "total_symbols":
                        (out_list[found])[k] = (out_list[found])[k] + item[k]
                     elif k == "total_symbol_errors":
                        (out_list[found])[k] = (out_list[found])[k] + item[k]
                     elif k == "combined_complexity":
                        if (out_list[found])["combined_complexity_step"] == item["combined_complexity_step"]:
                           l1 = (out_list[found])[k]
                           l2 = item[k]
                           for a in range(0, min(len(l1), len(l2))):
                              l1[a] = l1[a] + l2[a]
                              
                           if len(l2) > len(l1):
                              l1.extend(l2[len(l1):])                          
                        else:
                           print("not yet implemented")
                           
                        
                     
                     elif (k == "op1_stats") or (k == "op2_stats") or (k == "op3_stats") or (k == "op4_stats") or (k == "op5_stats"):
                        if (out_list[found])["combined_complexity_step"] == item["combined_complexity_step"]:
                           l1 = (out_list[found])[k]
                           l2 = item[k]
                           for a in range(0, min(len(l1), len(l2))):
                              l1[a] = l1[a] + l2[a]                              
                           if len(l2) > len(l1):
                              l1.extend(l2[len(l1):]) 
                              
                              
               
                     
                  
         if len(data) < 1:
            break
         item = data.pop()

   print("\n\n\n\n\n")
   
   target_c = float(args['c']);
   
   #go through and extract each snr
   for s_d in out_list:
      #look here
      this_snr = s_d['snr']
      snr_list.append(this_snr)
      cc = s_d['combined_complexity']
      sy = s_d['total_symbols'];
      step = s_d['combined_complexity_step']
      index = int(target_c/step)
      ser_list.append(cc[index]/sy)
      
      if (snr_min > float(this_snr)):
         snr_min = this_snr
      if ((snr_max < float(this_snr)) and (cc[index] > 0)):
         snr_max = this_snr
      
   if (len(snr_list)>0):   
      snr_lists.append(snr_list)
      ser_lists.append(ser_list)
      run_list.append(run_name)

mkdir_p(args['o'])
f = open(args['o']+"/results_data.dat",'w')


#write dat output file
f.write("#");
for run_name in run_list:
   f.write(run_name + "\t")
f.write("\n")


snr_index = 0
keepgoing = 1
while keepgoing:
   keepgoing = 0
   for i in range(0, len(run_list)):
      if (len(snr_lists[i]) > snr_index):
         keepgoing = 1
         f.write(str((snr_lists[i])[snr_index]) + "\t"+ str((ser_lists[i])[snr_index]) + "\t")
      else:
         f.write("\t \t")
   f.write("\n")
   snr_index = snr_index + 1
      
f.close()


#write gnuplot file
f = open(args['o']+"/results_run.gp",'w') 

f.write(textwrap.dedent("""\
   set terminal png
   set termoptions enhanced
   set xlabel 'SNR (dB)'
   set ylabel 'SER'
   set logscale y
   set format y '10^{%L}'
   set yrange[0.00001:1]
   set output 'out.png'
   set xrange[""" + str(snr_min) + ":" + str(snr_max) + """]

   set style line 1 lc rgb 'black' pt 1 pi 2 ps 2   #rice
   set style line 2 lc rgb 'blue' pt 2 pi 2 ps 2    #expg
   set style line 3 lc rgb 'red' pt 6 pi 2 ps 2     #rice-cc
   set style line 4 lc rgb 'green' pt 4 pi 2 ps 2   #expg-cc
   set style line 5 lc rgb 'orange' pt 3 pi 2 ps 2  #uec
   set style line 6 lc rgb 'yellow' pt 5 pi 2 ps 2  #vlec
   set style line 7 lc rgb 'purple' pt 7 pi 2 ps 2

   plot """))

i=1
print(run_list)
for run_name in run_list:
   style = 7
   if "vlec" in run_name:
      style = 6
   elif "uec" in run_name:
      style = 5
   elif "expg_cc" in run_name:
      style = 4
   elif "rice_cc" in run_name:
      style = 3
   elif "expg" in run_name:
      style = 2
   elif "rice" in run_name:
      style = 1
   name = run_name.replace('_','-')
   f.write("'results_data.dat' using ($" + str(i) + "-10*log10(1)):($"+str(i+1)+"==0) ? NaN : $"+str(i+1)+" with line ls "+str(style)+" title '" + name + "', \\\n")
   i=i+2