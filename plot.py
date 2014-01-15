from tkinter import *
import matplotlib.pyplot as plt
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

class Example(Frame):
  
   def __init__(self, parent):
      Frame.__init__(self, parent, background="white")   

      self.parent = parent

      self.initUI()
    
   def initUI(self):
      
      self.parent.title("Plot")
      self.pack(fill=BOTH, expand=1)

      self.data = {}
      self.data_folder = ""
      self.fig_ber = plt.figure()
      self.fig_ser = plt.figure()
      self.fig_cc = plt.figure()
      
      #build the gui
      
      #top folder text box
      self.folder=""
      lbf = Label(self, text="Results folder:")        
      lbf.place(x=20, y=20)
      self.tb_folder = Entry(self, width = 30, textvariable=self.folder)
      self.tb_folder.place(x=104,y=20)      
      
      #avaliable data lb
      self.lb_av = Listbox(self)
      self.lb_av.place(x=10,y=50)
      
      #using data lb
      self.lb_us = Listbox(self)
      self.lb_us.place(x=247,y=50)
      
      #add to using button
      btn_add = Button(self, text="Add ->", width=10, command=self.add_item)
      btn_add.place(x=150,y=110)
      
      #update button
      btn_add = Button(self, text="Update", width=10, command=self.folder_update)
      btn_add.place(x=290,y=20)
      
      #remove from using button
      btn_rm = Button(self, text="<- Remove", width=10, command=self.remove_item)
      btn_rm.place(x=150,y=140)
      
      #complexity slider.
      self.cc_bar = Scale(self, from_=0, to=300, resolution=0.1, length=400, orient=HORIZONTAL, command=self.update_cc_plot)
      self.cc_bar.place(x=10,y=230)
        
     
   def onScale(self, val):     
      v = int(float(val))
      self.var.set(v)
      
   def onSelect(self, val):
      sender = val.widget
      idx = sender.curselection()
      value = sender.get(idx)   

      self.var1.set(value)
      
   def folder_update(self):
      run_names = []
      cd = os.listdir(self.tb_folder.get())
      self.data_folder = self.tb_folder.get();
      for i in cd:
         if os.path.isdir(self.tb_folder.get()+ "/" + i):            
            file_list = glob.glob(self.tb_folder.get()+ "/" + i + "/*.json")
            if (len(file_list) > 0):
               run_names.append(i)
      self.lb_av
      self.lb_av.delete(0,END)
      for item in run_names:   
         self.lb_av.insert(END,item)
         
   def add_item(self):
      selected=self.lb_av.curselection()
      
      for item in selected:
         run_name = self.lb_av.get(item)
         if (run_name not in self.data.keys()):
            #load json
            file = self.data_folder + "/" +run_name + "/*.json"
            file_list = glob.glob(file)
            if (len(file_list)>0):
               data_j = json.load(open(file_list[0]))
               self.data[run_name] = data_j
               self.lb_us.insert(END, run_name)
      
      self.update_plot()
      
   def remove_item(self):
      selected=self.lb_us.curselection()
      
      for item in selected:
         run_name = self.lb_us.get(item)
         if (run_name in self.data.keys()):
            self.data.pop(run_name,None)
            self.lb_us.delete(self.lb_us.curselection())
      self.update_plot()
      
   def btn_test(self):
      print("moo")
      plt.plot([1,2,3,4,6,8])
      plt.ylabel('some numbers')
      plt.show()
      
   def btn_test1(self):
      print("moo")
      plt.plot([1,7,3,4,6,8])
      plt.show()
      
   def update_plot(self):
      self.fig_ber.clf()
      self.fig_ser.clf()
      plotted_s = 0
      plotted_b = 0
      axb = self.fig_ber.add_subplot(111)
      axs = self.fig_ser.add_subplot(111)
      #line, = ax.plot(ad, color='blue', lw=2)
      #for l in ax.lines:
      #   ax.lines.pop(0).remove()
      
      for run_name in self.data:
         run = self.data[run_name]
         

         #ser plot
         if ('snr' in run[0].keys()) and ('total_symbols' in run[0].keys()) and ('total_symbol_errors' in run[0].keys()):
            snrs = {}
            xdata = []
            ydata = []
            for i in range(0,len(run)):
               snrs[run[i]['snr']]=i
            for i in sorted(snrs):
               xdata.append( run[snrs[i]]['snr'] )
               ydata.append( run[snrs[i]]['total_symbol_errors'] / run[snrs[i]]['total_symbols'] )
                           
            maxsnr = sorted(snrs)[len(snrs)-1];
            minsnr = sorted(snrs)[0];
            
            line = axs.plot(xdata, ydata, lw=1, label=run_name)
            axs.legend(bbox_to_anchor=(1.05, 1), loc="best", borderaxespad=0.)
            plotted_s = 1;
            
         #ber plot
         if ('snr' in run[0].keys()) and ('total_bits' in run[0].keys()) and ('total_bit_errors' in run[0].keys()):
            snrs = {}
            xdata = []
            ydata = []
            for i in range(0,len(run)):
               snrs[run[i]['snr']]=i
            for i in sorted(snrs):
               xdata.append( run[snrs[i]]['snr'] )
               ydata.append( run[snrs[i]]['total_bit_errors'] / run[snrs[i]]['total_bits'] )
                           
            maxsnr = sorted(snrs)[len(snrs)-1];
            minsnr = sorted(snrs)[0];
            
            line = axb.plot(xdata, ydata, label=run_name, lw=1)
            axb.legend(bbox_to_anchor=(1.05, 1), loc="best", borderaxespad=0.)
            plotted_b = 1;
      
      
      if plotted_b:
         axb.set_yscale('log')      
         axb.set_xlabel('SNR')
         axb.set_ylabel('BER')
         self.fig_ber.show()
      
      if plotted_s:
         axs.set_yscale('log')
         axs.set_ylabel('SER')
         axs.set_xlabel('SNR')
         self.fig_ser.show()
      
      
   def update_cc_plot(self, val):
      self.fig_cc.clf()
      axs = self.fig_cc.add_subplot(111)
      #line, = ax.plot(ad, color='blue', lw=2)
      #for l in ax.lines:
      #   ax.lines.pop(0).remove()

      plotted = 0;
      max_cplx = 0
      
      for run_name in self.data:
         run = self.data[run_name]
         #cc ser plot
         if ('snr' in run[0].keys()) and ('combined_complexity' in run[0].keys()) and ('combined_complexity_step' in run[0].keys()) and ('total_symbols' in run[0].keys()):
            for i in range(0,len(run)):
               max_cplx = max(run[i]['combined_complexity_step'] * len(run[i]['combined_complexity']),max_cplx)
            
      rqrd_c = float(val)/float(300)*max_cplx
      print(rqrd_c)
      for run_name in self.data:
         run = self.data[run_name]
         #cc ser plot
         if ('snr' in run[0].keys()) and ('combined_complexity' in run[0].keys()) and ('combined_complexity_step' in run[0].keys()) and ('total_symbols' in run[0].keys()):
            snrs = {}
            xdata = []
            ydata = []
            max_cplx = 0    

            for i in range(0,len(run)):
               snrs[run[i]['snr']]=i
                          
            for i in sorted(snrs):
               xdata.append( run[snrs[i]]['snr'] )
               bin = rqrd_c/float(run[snrs[i]]['combined_complexity_step']) -1
               bin = min(bin,len(run[snrs[i]]['combined_complexity'])-1)

               bin = math.floor(bin)
               bin = max(0,bin)               

               ydata.append( run[snrs[i]]['combined_complexity'][bin] / run[snrs[i]]['total_symbols'] )
                           
            maxsnr = sorted(snrs)[len(snrs)-1];
            minsnr = sorted(snrs)[0];
            
            line = axs.plot(xdata, ydata, lw=1, label=run_name)
            axs.legend(bbox_to_anchor=(1.05, 1), loc="best", borderaxespad=0.)
            plotted = 1;


      if plotted:      
         axs.set_yscale('log')
         axs.set_xlabel('SNR')
         axs.set_ylabel('SER')
         self.fig_cc.show()
      
def main():
  
   root = Tk()
   root.geometry("450x550+300+300")
   app = Example(root)



   root.mainloop()  


if __name__ == '__main__':
   main()