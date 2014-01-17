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

   print("\nUsage (single run): \n")
   print("\tcollate.py run_name -r results_folder -o output_folder\n\n")
   print("All folders in results path:\n")
   print("\tcollate.py -a -r results_folder -o output_folder\n\n\n")
   
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

run_names = []
if ('a' in args.keys()): 
   cd = os.listdir(args['r'])
   for i in cd:
      if os.path.isdir(args['r']+ "/" + i):
         print("Found directory: " + i)
         run_names.append(i)
else:
   run_names.append(sys.argv[1])


for run_name in run_names:

   res_path = args['r']+ "/" + run_name
   out_path = args['o']+ "/" + run_name

   out_suffix = "totals"

   print("Results folder: " + res_path)
   print("Run name to collate: " + run_name)


   file_list = glob.glob(res_path + "/*.json")

   print("Found files:")
   print(file_list)


   out_list = list();


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
                              
                              
               
               #for k in out_list[found].keys():
               #   if k == "total_bits":
               #      (out_list[found])[k] = (out_list[found])[k] + item[k]
               #   elif k == "total_bit_errors":
               #      (out_list[found])[k] = (out_list[found])[k] + item[k]
               #   elif k == "total_frames":
               #      (out_list[found])[k] = (out_list[found])[k] + item[k]
               #   elif k == "total_frame_errors":
               #      (out_list[found])[k] = (out_list[found])[k] + item[k]
               #   elif k == "total_symbols":
               #      (out_list[found])[k] = (out_list[found])[k] + item[k]
               #   elif k == "total_symbol_errors":
               #      (out_list[found])[k] = (out_list[found])[k] + item[k]
               #   elif k == "combined_complexity":
               #      if (out_list[found])["combined_complexity_step"] == item["combined_complexity_step"]:
               #         l1 = (out_list[found])[k]
               #         l2 = item[k]
               #         for a in range(0, min(len(l1), len(l2))):
               #            l1[a] = l1[a] + l2[a]
               #            
               #         if len(l2) > len(l1):
               #            l1.extend(l2[len(l1):])
               #      else:
               #         print("not yet implemented")
                     
                  
         if len(data) < 1:
            break
         item = data.pop()

   print("\n\n\n\n\n")


   mkdir_p(out_path)
   f = open(out_path+"/results.json",'w')
   f.write(json.dumps(out_list))
   f.close()






