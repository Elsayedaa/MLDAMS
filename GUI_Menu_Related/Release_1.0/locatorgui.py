import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
from tkinter import *
from tkinter import ttk
from io import StringIO
import startpage
from somalocator import locator, availInSamp
import pandas as pd

pd.set_option('display.width', 1000)
pd.options.display.max_rows = 999999

class Locator_GUI(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)

        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.sample_list = availInSamp().keys()

        label = Label(self.mainframe, text = "Find the soma brain area location of a neuron:")
        label.grid(row = 0)

        self.report = Text(self.mainframe, bg="white", height=30, width=125)
        self.report.grid(row=5)

        self.sample_selection = StringVar()
        self.sample_selection.set("Select a sample:")
        
        try:
            self.sampledropdown = ttk.Combobox(self.mainframe, textvariable = self.sample_selection, width = 40)
            self.sampledropdown['values'] = list(self.sample_list)
            self.sampledropdown.bind('<<ComboboxSelected>>', self.unlock_tagdropdown)
        except Exception as e:
            if "__init__() missing 1 required positional argument: 'value'" in e.args[0]:
                errormsg = "Tracing Complete folder is missing ALL of it's sample folders. Have the files recently migrated?"
                self.sampledropdown = ttk.Combobox(self.mainframe, textvariable = self.sample_selection)
                self.sampledropdown['values'] = ['']
                self.report.insert(END, errormsg)
                
        self.sampledropdown.grid(row=1)

        self.tag_selection = StringVar()
        self.tag_selection.set("Select a tag from the sample:")    
        self.tagdropdown = ttk.Combobox(self.mainframe, textvariable = self.tag_selection, width = 40)
        self.tagdropdown['values'] = ['Please select a sample first']

        self.tagdropdown.grid(row=2)

        self.givelocation = ttk.Button(self.mainframe, text = "Give soma location", command = self.returnloc)
        self.givelocation.grid(row=3)

        self.checkvar = IntVar()
        self.checksimple = Checkbutton(self.mainframe, text = "Simple list", variable = self.checkvar)
        self.checksimple.grid(row = 4)

        exitButton = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exitButton.grid(row=6)

    def unlock_tagdropdown(self, event):
        selectionlist = list(availInSamp(self.sampledropdown.get()))
        self.tagdropdown['values'] = selectionlist

    def returnloc(self):

        #no sample and no tag selected:
        if self.sample_selection.get() == "Select a sample:":
            print("A sample must be selected first. Please use the dropdown menu to select a sample.")

        #sample selected, no tag selected:
        if self.tag_selection.get() == "Select a tag from the sample:":
            print(f"Returning all soma locations in sample {self.sample_selection.get()}:\n")
            sample_locs = locator(self.sample_selection.get())

            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, sample_locs)

        #sample selected, no tag selected, simple list toggled:
        if self.tag_selection.get() == "Select a tag from the sample:" and self.checkvar.get()==1:
            old_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result

            print(f"Returning all soma locations in sample {self.sample_selection.get()}:\n")
            sample_locs = locator(self.sample_selection.get())

            sys.stdout = old_stdout
            result_string = result.getvalue()
            

            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, result_string)

        #sample selected and tag selected
        if self.sample_selection.get() != "Select a sample:" and self.tag_selection.get() != "Select a tag from the sample:":

            single_loc = locator(self.sample_selection.get(), self.tag_selection.get())
            report = f"Returning the soma location for neuron {self.sample_selection.get()}_{self.tag_selection.get()}:\n\n{single_loc}"
            
            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, report)

            self.tag_selection.set("Select a tag from the sample:")
        
        

        

        
        


