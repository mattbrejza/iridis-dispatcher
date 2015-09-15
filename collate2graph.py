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
   print("\tcollate2graph.py -c complexity {-f filter_file, -t title -tex} -r results_folder -o output_folder\n\n\n")
   
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

filter_list = [];
filter_list_rename = [];
filter_list_lt = [];
if ('f' in args.keys()):
   if (os.path.isfile(args['f'])):
      f = open(args['f'],'r')
      for line in f:
         if (len(line)>2) and (line[0] != '#'):
            spl = line.split(' ',2);
            if (len(spl) == 1):
               filter_list.append(spl[0].strip().replace('-','_'))
               filter_list_rename.append(spl[0].strip())
               filter_list_lt.append('')
            elif (len(spl) == 2):
               filter_list.append(spl[0].strip().replace('-','_'))
               filter_list_rename.append(spl[1].strip())
               filter_list_lt.append('')
            elif (len(spl) == 3):
               filter_list.append(spl[0].strip().replace('-','_'))
               filter_list_rename.append(spl[1].strip())
               filter_list_lt.append(spl[2].strip())
               
   else:
      print("filter file not found")
      exit()

print(filter_list);
           
if ('r' not in args.keys()):
   print_usage()
   print(":(")
   exit()
   
if ('o' not in args.keys()):
   print_usage()
   print(":(")
   exit()
   
#if ('c' not in args.keys()):
#   print_usage()
#   print(":(")
#   exit()

run_names = []

cd = os.listdir(args['r'])
for i in cd:
   if os.path.isdir(args['r']+ "/" + i):
      print("Found directory: " + i)
      run_names.append(i)



snr_lists = []
ser_lists = []
run_list = []
rename_list = []
lt_list = []
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
   
   if ('c' not in args.keys()):
      target_c = -1;
   else:
      target_c = float(args['c']);
   
   unlimited = 0;
   include = 0;
   run_rename = run_name
   lt = ''
   if (len(filter_list) == 0):
      include = 1;
   else:
      i = 0;
      for line in filter_list:
         print(line + "  " + run_name);
         if run_name.startswith(line):
            include = 1;
            run_rename = filter_list_rename[i];
            lt = filter_list_lt[i];
         i=i+1;
   
   if (include > 0):
      if run_rename.endswith("unlimited"):
         unlimited = 1;
      #go through and extract each snr
      for s_d in out_list:
         #look here
         this_snr = s_d['snr']
         if (target_c == -1):
            sy = s_d['total_symbols'];
            ers = s_d['total_symbol_errors'];
            if (float(sy) > 0):            
               ser_list.append(float(ers)/float(sy))
               snr_list.append(this_snr)
            
            if (snr_min > float(this_snr)):
               snr_min = this_snr
            if ((snr_max < float(this_snr)) and (ers > 0)):
               snr_max = this_snr
         else:
            cc = s_d['combined_complexity']
            sy = s_d['total_symbols'];
            step = s_d['combined_complexity_step']
            if (unlimited == 0):
               index = int(target_c/step)
            else:
               index = int(100000000/step)
            if (index >= len(cc)):
               index = len(cc)-1;
            if (float(sy) > 0):            
               ser_list.append(float(cc[index])/float(sy))
               snr_list.append(this_snr)
            
            if (snr_min > float(this_snr)):
               snr_min = this_snr
            if ((snr_max < float(this_snr)) and (cc[index] > 0)):
               snr_max = this_snr
         
      if (len(snr_list)>0):
         ser_list = [x for y, x in sorted(zip(snr_list, ser_list))]
         snr_list.sort()
         snr_lists.append(snr_list)
         ser_lists.append(ser_list)
         run_list.append(run_name)
         rename_list.append(run_rename)
         lt_list.append(lt)

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
         f.write(str((snr_lists[i])[snr_index]) + ", "+ str((ser_lists[i])[snr_index]) + ", ")
      else:
         f.write(", , ")
   f.write("\n")
   snr_index = snr_index + 1
      
f.close()


#write gnuplot file
f = open(args['o']+"/results_run.gp",'w') 

if ('tex' in args.keys()):
   f.write(textwrap.dedent("""\
      set terminal pslatex 8
      set xlabel 'SNR (dB)'
      set ylabel 'SER' offset 1,0
      set logscale y
      set format y '$10^{%L}$'
      set yrange[0.00001:1]
      set output 'results_run.tex'
      eta = 1
      capacity = -10
      ebstart = """ + str(snr_min) + """
      ebend = """ + str(snr_max) + """
      exist = system("[ -f eta.cfg ] && echo '1' || echo '0'") + 0
      if (exist)  load 'eta.cfg' 
      if (exist)  set xlabel '$E_\mathrm{b}/N_0$ (dB)'
      set xrange[ebstart : ebend ]
      set arrow from capacity,0.002 to capacity,0.9 nohead
      set label 2 "Capacity bound"   at capacity-0.08,0.002 rotate left
      
      set style line 1 lt 1 ps 1 pi 2 pt 1 lc rgb 'black'
      set style line 2 lt 1 ps 1 pi 2 pt 1 lc rgb 'blue'
      set style line 3 lt 1 ps 1 pi 2 pt 1 lc rgb 'red'
      set style line 4 lt 1 ps 1 pi 2 pt 1 lc rgb 'green'
      set style line 5 lt 1 ps 1 pi 2 pt 1 lc rgb 'orange'
      set style line 6 lt 1 ps 1 pi 2 pt 1 lc rgb 'yellow'
      set style line 7 lt 1 ps 1 pi 2 pt 1 lc rgb 'purple'
      
      set style line 11 lt 1 ps 1 pi 2 pt 6 lc rgb 'black'    #ExpGEC
      set style line 12 lt 1 ps 1 pi 2 pt 7 lc rgb 'black'    #ExpGEC
      
      set style line 21 lt 1 ps 1 pi 2 pt 4 lc rgb 'black'    #RiceEC
      set style line 22 lt 1 ps 1 pi 2 pt 5 lc rgb 'black'    #RiceEC
      
      set style line 31 lt 2 ps 1 pi 2 pt 1 lc rgb 'black'    #Expg
      set style line 41 lt 2 ps 1 pi 2 pt 2 lc rgb 'black'    #Rice
      set style line 51 lt 2 ps 1 pi 2 pt 3 lc rgb 'black'    #VLEC
      
      """))
else:
   f.write(textwrap.dedent("""\
      set terminal png
      set termoptions enhanced
      set xlabel 'SNR (dB)'
      set ylabel 'SER' offset 1,0
      set logscale y
      set format y '10^{%L}'
      set yrange[0.00001:1]
      set output 'out.png'
      eta = 1
      capacity = -10
      ebstart = """ + str(snr_min) + """
      ebend = """ + str(snr_max) + """
      exist = system("[ -f eta.cfg ] && echo '1' || echo '0'") + 0
      if (exist)  load 'eta.cfg' 
      if (exist)  set xlabel '$E_\mathrm{b}/N_0$ (dB)'
      set xrange[ebstart : ebend ]
      set arrow from capacity,0.002 to capacity,0.9 nohead
      set label 2 "Capacity bound"   at capacity-0.08,0.002 rotate left
      
      set style line 1 lt 1 ps 1 pi 2 pt 1 lc rgb 'black'
      set style line 2 lt 1 ps 1 pi 2 pt 1 lc rgb 'blue'
      set style line 3 lt 1 ps 1 pi 2 pt 1 lc rgb 'red'
      set style line 4 lt 1 ps 1 pi 2 pt 1 lc rgb 'green'
      set style line 5 lt 1 ps 1 pi 2 pt 1 lc rgb 'orange'
      set style line 6 lt 1 ps 1 pi 2 pt 1 lc rgb 'yellow'
      set style line 7 lt 1 ps 1 pi 2 pt 1 lc rgb 'purple'
      
      set style line 11 lt 1 ps 1 pi 2 pt 6 lc rgb 'black'    #ExpGEC
      set style line 12 lt 1 ps 1 pi 2 pt 7 lc rgb 'black'    #ExpGEC
      
      set style line 21 lt 1 ps 1 pi 2 pt 4 lc rgb 'black'    #RiceEC
      set style line 22 lt 1 ps 1 pi 2 pt 5 lc rgb 'black'    #RiceEC
      
      set style line 31 lt 2 ps 1 pi 2 pt 1 lc rgb 'black'    #Expg
      set style line 41 lt 2 ps 1 pi 2 pt 2 lc rgb 'black'    #Rice
      set style line 51 lt 2 ps 1 pi 2 pt 3 lc rgb 'black'    #VLEC
      """))
   
if ('t' in args.keys()):
   f.write("set title '" + args['t'] + "'\n\n")
else:
   f.write("set title 'Complexity: " + str(args['c']) + "'\n\n")
   
f.write("plot ");
   
i=1
pt=1
ptr = 0
colour = "blank"
print(run_list)
for run_name in run_list:
   style = '7'
   colour = "purple"
   if (lt_list[ptr] == ''):
      if "vlec" in run_name:
         style = '6'
         colour = "yellow"
      elif "uec" in run_name:
         style = '5'
         colour = "orange"
      elif "expg_cc" in run_name:
         style = '4'
         colour = "green"
      elif "rice_cc" in run_name:
         style = '3'
         colour = "red"
      elif "expg" in run_name:
         style = '2'
         colour = "blue"
      elif "rice" in run_name:
         style = '1'
         colour = "black"
   else:
      style = lt_list[ptr]
   name = rename_list[ptr].replace('_','-')
   if ( i > 1 ):
      f.write("', \\\n")
   f.write("'results_data.dat' using ($" + str(i) + "-10*log10(eta)):($"+str(i+1)+"==0) ? NaN : $"+str(i+1)+" with linespoints ls " + style + " title '" + name)
   #lc rgb'"+colour+"' ps 1 lt 1 pt "+str(pt)+" title '" + name)
   i=i+2
   pt=pt+1
   ptr = ptr + 1
