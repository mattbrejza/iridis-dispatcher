import sys
import string
import textwrap
import math
import numpy
import time
import random

def write_preamble(file,nodes,ppn,walltime):
   file.write(textwrap.dedent("""\
   #!/bin/bash
   #PBS -S /bin/bash
   # Script to run some jobs in parallel.

   # set default resource requirements for job (8 processors on 1 node for 1
   # minute). These can be overridden on the qsub command line.
   """))
   
   file.write("#PBS -l nodes="+repr(int(nodes))+":ppn="+repr(int(ppn))+"\n")
   file.write("#PBS -l walltime="+repr(int(walltime))+":00:00\n")

   file.write(textwrap.dedent("""\
   # Change to directory from which job was submitted.
   cd $PBS_O_WORKDIR
   
   module load matlab/2013a
   module load matlab/2011a
   
   ~/message.py "Job: $PBS_JOBNAME started" -1

   """))

def write_postamble(file):
   file.write("~/extract_runtime.py $PBS_JOBID 10 1")

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

def uecadap(file, args):

   print("Creating job file for uec adaptive job.\n\nFound arguments:")
   
   #look for options like -startsnr, -stopsnr etc
   opt_dict = getoptions(args)
   
   die=0
   
   if ('snrs' not in opt_dict.keys()):   
      if ('startsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -startsnr")     
      if ('stopsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -stopsnr")      
      if ('stepsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -stepsnr")
         
      if die==0:
         startsnr = float(opt_dict['startsnr'])
         stopsnr = float(opt_dict['stopsnr'])
         stepsnr = float(opt_dict['stepsnr'])
         snrs = numpy.arange(startsnr, stopsnr+0.0002, stepsnr)
         print("List of SNRs:")
         print (snrs)
      
   else:
      snrs_s = opt_dict['snrs']
      snrs_s=snrs_s.split(",")
      snrs = [float(s) for s in snrs_s]
      print("List of SNRs:")
      print (snrs)
 
   
   print ("\n\n")
   
   if ('copies' not in opt_dict.keys()):
      copies = 1;
      print("Defaulting -copies to 1")
   else:
      copies = int(opt_dict['copies'])
      
   if ('eq' not in opt_dict.keys()):
      eq = 0;
      print("Defaulting -eq (exit-quantisation) to 0")
   else:
      eq = int(opt_dict['eq'])
      
   if ('wall' not in opt_dict.keys()):
      wall = 36;
      print("Defaulting -wall to 36")
   else:
      wall = opt_dict['wall'] 
      
   if ('n' not in opt_dict.keys()):
      name = time.strftime("%y%m%d-%H%M%S");
      print("Defaulting -n (name) to "+name)
   else:
      name = opt_dict['n'] 

   if ('bits' not in opt_dict.keys()):
      bits = 1000;
      print("Defaulting -bits to 1000")
   else:
      bits = float(opt_dict['bits']) 
      
   if ('demod' not in opt_dict.keys()):
      demod = 1;
      print("Defaulting -demod to 1 (enabled)")
   else:
      demod = float(opt_dict['demod'])  

   if ('mm' not in opt_dict.keys()):
      mm = 'exact';
      print("Defaulting -mm (MI measuring) to 'exact'")
   else:
      mm = opt_dict['mm']
      
   if ('type' not in opt_dict.keys()):
      type = "m2ms";
      print("Defaulting -type to m2ms")
   else:
      type = opt_dict['type']    
      
   if ('uec_r' not in opt_dict.keys()):
      uec_r = "8";
      print("Defaulting -uec_r (non adaptive uec states to 8")
   else:
      uec_r = opt_dict['uec_r']   
      
   if ('ut' not in opt_dict.keys()):
      urc_type = "URC8";
      print("Defaulting -ut (urc_type) to URC8 (other options: URC1, URC4)")
   else:
      urc_type = opt_dict['ut']
      
   if ('lus' not in opt_dict.keys()):
      last_uec_states = "4";
      print("Defaulting -lus (last_uec_states) to 4 (other options: 2,4,6,8,10,adap)")
   else:
      last_uec_states = opt_dict['lus']

   if ('i' not in opt_dict.keys()):
      inter = "randn";
      print("Defaulting -i (interleaver) to randn. (other options: srandn)")
   else:
      inter = opt_dict['i']       

   if ('mc' not in opt_dict.keys()):
      mi_c = "na";
      print("Defaulting -mc (mi c value) to na.")
   else:
      mi_c = opt_dict['mc']    

   if ('mg' not in opt_dict.keys()):
      mi_m = "na";
      print("Defaulting -mg (mi gradient value) to na.")
   else:
      mi_m = opt_dict['mg']          
      
   if ('src' not in opt_dict.keys()):
      die=1
      print("Requires option -src")
      
   if ('res' not in opt_dict.keys()):
      die=1
      print("Requires option -res")
      
      
   if die>0:
      print("Quiting...")
      return
      

      
   #total nodes
   nodes = len(snrs)
   if nodes < 1 or copies < 1:
      print("Invalid combination of snr start/stop/step / copies")
      print("Quiting...")
      return
   
   nodes = nodes * copies
   
   mach = math.ceil(nodes/float(16))
   ppn = math.ceil(nodes/mach)
   
   #open file for writing
   f = open(file,'w')
   write_preamble(f,mach,ppn,wall)
   f.write("SRC=\""+opt_dict['src']+"\"\n")
   f.write("RES=$PBS_O_WORKDIR/\""+opt_dict['res']+"/"+name+"\"\n")
   f.write("mkdir -p $RES\n\n\n\n")
   
   uec_scaling = "-1"
   if type == "non":
      adap = "0"
   else:
      adap = "1"
      if type == "m1ms":
         uec_scaling = "-1"
      elif type == "m2ms":
         uec_scaling = "-2"
      elif type == "1ms":
         uec_scaling = "1"
      else:
         print("Invalid -type option. Choose either non,m1ms,m2ms")
   
   for c in range(0, copies):
      for snr in snrs:
         f.write("matlab -nodisplay -nojvm -r \"cd $SRC; adaptive_uec_urc_d_ber( 'results_filename', '$RES/files"+type+"', 'int_len', '"+repr(int(bits))+"', 'max_type', 'max_star', 'start_snr', '"+repr(snr)+"', 'stop_snr', '"+repr(snr)+"', 'step_snr', '1', 'number_type', 'do', 'seed', '"+repr(random.randint(0,100000))+"', 'uec_exit_scaling', '"+uec_scaling+"', 'adaptive', '"+adap+"', 'channel', 'r',")
         if (not(mi_c=="na")) and (not(mi_m=="na")):
            f.write(" 'mi_m', '"+mi_m+"', 'mi_c', '"+mi_c+"',")
         f.write(" 'minimum_tx_bits', '100000000', 'uec_r', '"+uec_r+"', 'last_uec_states', '"+last_uec_states+"', 'reuse_demod', '"+repr(demod)+"', 'urc_type', '"+ urc_type +"', 'int1', '"+inter+"', 'int2', '"+inter+"', 'int3', '"+inter+"', 'int3_1', '"+inter+"', 'mi_measure', '"+mm+"', 'exit_quant', '"+repr(eq)+"')\"&\n")
      f.write("\n")
      
   f.write("\nwait\n")
   
   write_postamble(f)
   
   f.close()  
   
def uecimpl(file, args):   
   
   print("creating job file for uec implementation job reference code")

   
   #look for options like -startsnr, -stopsnr etc
   opt_dict = getoptions(args)
   
   die=0
   
   if ('snrs' not in opt_dict.keys()):   
      if ('startsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -startsnr")     
      if ('stopsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -stopsnr")      
      if ('stepsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -stepsnr")
      
      if die==0:
         startsnr = float(opt_dict['startsnr'])
         stopsnr = float(opt_dict['stopsnr'])
         stepsnr = float(opt_dict['stepsnr'])
         snrs = numpy.arange(startsnr, stopsnr+0.0002, stepsnr)
         print("List of SNRs:")
         print (snrs)
      
   else:
      snrs_s = opt_dict['snrs']
      snrs_s=snrs_s.split(",")
      snrs = [float(s) for s in snrs_s]
      print("List of SNRs:")
      print (snrs)
         
   
   print ("\n\n")
   
   if ('copies' not in opt_dict.keys()):
      copies = 1;
      print("Defaulting -copies to 1")
   else:
      copies = int(opt_dict['copies'])
      
   if ('wall' not in opt_dict.keys()):
      wall = 36;
      print("Defaulting -wall to 36")
   else:
      wall = opt_dict['wall'] 
      
   if ('n' not in opt_dict.keys()):
      name = time.strftime("%y%m%d-%H%M%S");
      print("Defaulting -n (name) to "+name)
   else:
      name = opt_dict['n'] 

   if ('bits' not in opt_dict.keys()):
      bits = 1024;
      print("Defaulting -bits to 1024")
   else:
      bits = float(opt_dict['bits'])   

#   if ('type' not in opt_dict.keys()):
#      die=1
#      print("Requires option -type. Choose either ET,EUT,UT2")

#   if ('d' not in opt_dict.keys()):
#      demod = 1;
#      print("Defaulting -d (demod) to 1")
#   else:
#      demod = opt_dict['d'] 

      
   if ('src' not in opt_dict.keys()):
      die=1
      print("Requires option -src")
      
   if ('res' not in opt_dict.keys()):
      die=1
      print("Requires option -res")
      
      
   if die>0:
      print("Quiting...")
      return

   #total nodes
   nodes = len(snrs)
   if nodes < 1 or copies < 1:
      print("Invalid combination of snr start/stop/step / copies")
      print("Quiting...")
      return
   
   nodes = nodes * copies
   
   mach = math.ceil(nodes/float(16))
   ppn = math.ceil(nodes/mach)
   
   #open file for writing
   f = open(file,'w')
   write_preamble(f,mach,ppn,wall)
   f.write("SRC=\""+opt_dict['src']+"\"\n")
   f.write("RES=$PBS_O_WORKDIR/\""+opt_dict['res']+"/"+name+"/\"\n")
   f.write("mkdir -p $RES\n\n\n\n")
   f.write("cd $SRC\n")
   f.write("#mcc -vm run_exit_ber.m *.m\n")
   f.write("cd $PBS_O_WORKDIR\n")
   #f.write("COMMON=\"modulation qpsk start_snr 1.6 stop_snr 3 step_snr 0.2 pivi 0 int1 srandn int2 srandn stopping_mi 2 minimum_tx_bits 1000000000 enable_trellis_block 1 trellis_knows_first 1 use_trellis_iter 1\"\n\n\n")
   f.write("COMMON=\"'modulation', 'qpsk', 'start_snr', '1.6', 'stop_snr', '3', 'step_snr', '0.2', 'pivi', '0', 'int1', 'srandn', 'int2', 'srandn', 'stopping_mi', '2', 'minimum_tx_bits', '1000000000', 'enable_trellis_block', '1', 'trellis_knows_first', '1', 'use_trellis_iter', '1',\"\n\n\n")

   
   for c in range(0, copies):
      for snr in snrs:
      #   f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+"  "+repr(snr)+" "+repr(int(symbols))+" 1 '$RES'\"&\n")
         f.write("matlab -nodisplay -nojvm -r \"cd $SRC; run_exit_ber ( $COMMON 'seed', '41', 'results_filename', '$RES', 'start_snr', '"+repr(snr)+"', 'stop_snr', '"+repr(snr)+"', 'step_snr', '0.2', 'generate_unary_mode', '3', 'reuse_demod', '1', 'qpsk_mapping', 'n', 'decoding_loops', '10', 'int3_1', 'same', 'int3', 'randn',  'number_type', 'do') \" &\n")
      f.write("\n")
      
   f.write("\nwait\n")
   
   write_postamble(f)
   
   f.close()  
   
def uecadapref(file, args):

   print("creating job file for uec adaptive job reference code")

   
   #look for options like -startsnr, -stopsnr etc
   opt_dict = getoptions(args)
   
   die=0
   
   if ('snrs' not in opt_dict.keys()):   
      if ('startsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -startsnr")     
      if ('stopsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -stopsnr")      
      if ('stepsnr' not in opt_dict.keys()):
         die=1
         print("Requires option -stepsnr")
      
      if die==0:
         startsnr = float(opt_dict['startsnr'])
         stopsnr = float(opt_dict['stopsnr'])
         stepsnr = float(opt_dict['stepsnr'])
         snrs = numpy.arange(startsnr, stopsnr+0.0002, stepsnr)
         print("List of SNRs:")
         print (snrs)
      
   else:
      snrs_s = opt_dict['snrs']
      snrs_s=snrs_s.split(",")
      snrs = [float(s) for s in snrs_s]
      print("List of SNRs:")
      print (snrs)
         
   
   print ("\n\n")
   
   if ('copies' not in opt_dict.keys()):
      copies = 1;
      print("Defaulting -copies to 1")
   else:
      copies = int(opt_dict['copies'])
      
   if ('wall' not in opt_dict.keys()):
      wall = 36;
      print("Defaulting -wall to 36")
   else:
      wall = opt_dict['wall'] 
      
   if ('n' not in opt_dict.keys()):
      name = time.strftime("%y%m%d-%H%M%S");
      print("Defaulting -n (name) to "+name)
   else:
      name = opt_dict['n'] 

   if ('symbols' not in opt_dict.keys()):
      symbols = 666;
      print("Defaulting -symbols to 666")
   else:
      symbols = float(opt_dict['symbols'])   
      
   if ('demod' not in opt_dict.keys()):
      demod = 1;
      print("Defaulting -demod to 1 (enabled)")
   else:
      demod = float(opt_dict['demod'])
      
   if ('non_r' not in opt_dict.keys()):
      non_r = "8";
      print("Defaulting -non_r (non adaptive uec states) to 8")
   else:
      non_r = (opt_dict['non_r'])
      
   if ('ut' not in opt_dict.keys()):
      urc_type = "URC8";
      print("Defaulting -ut (urc_type) to URC8 (other options: URC1, URC4)")
   else:
      urc_type = opt_dict['ut']

   if ('type' not in opt_dict.keys()):
      die=1
      print("Requires option -type. Choose either ET,EUT,UT2,REFA,REFNON")      
      
   if ('src' not in opt_dict.keys()):
      die=1
      print("Requires option -src")
      
   if ('res' not in opt_dict.keys()):
      die=1
      print("Requires option -res")
      
      
   if die>0:
      print("Quiting...")
      return
      

      
   #total nodes
   nodes = len(snrs)
   if nodes < 1 or copies < 1:
      print("Invalid combination of snr start/stop/step / copies")
      print("Quiting...")
      return
   
   nodes = nodes * copies
   
   mach = math.ceil(nodes/float(16))
   ppn = math.ceil(nodes/mach)
   
   #open file for writing
   f = open(file,'w')
   write_preamble(f,mach,ppn,wall)
   f.write("SRC=\""+opt_dict['src']+"/ref-wenbo/main/Iridis_Jobs/ser/\"\n")
   f.write("RES=$PBS_O_WORKDIR/\""+opt_dict['res']+"/"+name+"/\"\n")
   f.write("mkdir -p $RES\n\n\n\n")
   
   type = opt_dict['type'] 
   if type.lower() == "et":
      cmmd = "main_ET_ser_Iridis"
   elif type.lower() == "eut":
      cmmd = "main_EUT_ser_Iridis"
   elif type.lower() == "ut2":
      cmmd = "main_UT2_ser_Iridis"
   elif type.lower() == "refa":
      cmmd = "main_UT1A_ser_Iridis"
   elif type.lower() == "refnon":
      cmmd = "main_UT1A_ser_Iridis"
   elif type.lower() == "refan":
      cmmd = "main_UT1A_ser_Iridis_new"
   elif type.lower() == "refnonn":
      cmmd = "main_UT1A_ser_Iridis_new"
   else:
      print("Invalid -type option. Choose either ET,EUT,UT2")
   
   for c in range(0, copies):
      for snr in snrs:
         if type.lower() == "et":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+"  "+repr(snr)+" "+repr(int(symbols))+" "+repr(demod)+" "+urc_type+" '$RES'\"&\n")
         elif type.lower() == "ut2":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+"  "+repr(snr)+" "+repr(int(symbols))+" "+repr(demod)+" "+urc_type+" '$RES'\"&\n")
         elif type.lower() == "eut":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+"  "+repr(snr)+" "+repr(int(symbols))+" "+repr(demod)+" "+urc_type+" '$RES'\"&\n")
         elif type.lower() == "refa":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; main_UT1A_ser_Iridis "+repr(snr)+" "+repr(int(symbols))+" 1 1 '$RES'\"&\n")
         elif type.lower() == "refnon":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; main_UT1A_ser_Iridis "+repr(snr)+" "+repr(int(symbols))+" 1 0 '$RES'\"&\n")
         elif type.lower() == "refan":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+" "+repr(snr)+" "+repr(int(symbols))+" 1 '$RES' 0\"&\n")
         elif type.lower() == "refnonn":
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+" "+repr(snr)+" "+repr(int(symbols))+" 0 '$RES' "+non_r+"\"&\n")
         else:
            f.write("matlab -nodisplay -nojvm -r \"cd $SRC; "+cmmd+"  "+repr(snr)+" "+repr(int(symbols))+" "+repr(demod)+" '$RES'\"&\n")
      f.write("\n")
      
   f.write("\nwait\n")
   
   write_postamble(f)
   
   f.close()  


#main entry point
 
#test sys.argv[1] to see what type of job

try:

   options = { "uec-adaptive" : uecadap,
               "uec-adaptive-ref" : uecadapref,
               "uec-impl" : uecimpl,
             }
             
   options[sys.argv[2]](sys.argv[1],sys.argv[3:])

except IndexError:
   print("Usage: \n\n")
   print("\tcreate-job.py job_out run_type <specific options>\n\n")
   print("\trun_type options: \n\t\tuec-adaptive\tuec-adaptive-ref\tuec-impl\n")
