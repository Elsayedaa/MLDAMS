#no async
#Known issues:
#Fixed: AttributeError when Enter all neurons is clicked without a sample selected

import sys
import os
from pathlib import PurePath
import asyncio
import threading
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
sys.path.append(r"{}\Database_Related_GUI_Branch".format(appParentDir))
from tkinter import *
from tkinter import ttk
from io import StringIO
from ANWparser import anw
from MLDB_sample_enter import MLDB_sample_enter
from MLDB_neuron_enter import Neuronposter, SWCUploader
import startpage

def stdout_capture_start():
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    return [result, old_stdout]

def stdout_capture_stop(out):
    result = out[0]
    old = out[1]
    sys.stdout = old
    result_string = result.getvalue()
    return result_string


class DBSelect_GUI(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)

        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        label = Label(self.mainframe, text = "Select a database.")
        label.grid(row = 0, columnspan = 2)

        sandboxClk = ttk.Button(self.mainframe, text = "Sandbox database", command = lambda: controller.show_frame(Entry_GUI,"sandbox"))
        sandboxClk.grid(row = 1, column = 0, sticky = E)
    
        productionClk = ttk.Button(self.mainframe, text = "Production database", command = lambda: controller.show_frame(Entry_GUI,"production"))
        productionClk.grid(row = 1, column = 1, sticky = W)

        exitButton = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exitButton.grid(row = 2, columnspan = 2)

class Entry_GUI(Frame):
    def __init__(self, parent, controller, instance): 
        Frame.__init__(self,parent)

        self.instance = instance
        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        button_dropdown_padx = 2
                
        bframe1 = Frame(self.mainframe)
        bframe1.grid(row = 0, columnspan = 2)

        ##########################################

        self.sample_selection = StringVar()
        self.sample_selection.set("Select an active sample:")
        self.sampledropdown = ttk.Combobox(bframe1, textvariable = self.sample_selection, width = 40)
        self.sampledropdown['values'] = controller.parser.sheets
        self.sampledropdown.bind('<<ComboboxSelected>>', self.unlock_neurondropdown)
        self.sampledropdown.grid(row=0, column = 0, sticky = "e", padx = button_dropdown_padx)
        
    
        entersamp = ttk.Button(bframe1, text = "Enter sample data", command = self.enterSamp, width = 25)
        entersamp.grid(row=0, column  = 1, padx = button_dropdown_padx) 

        self.completeneuron_selection = StringVar()
        self.completeneuron_selection.set("Select a completed neuron from the sample:")    
        self.neurondropdown = ttk.Combobox(bframe1, textvariable = self.completeneuron_selection, width = 40)
        self.neurondropdown['values'] = ['Please select an active sample first.']
        self.neurondropdown.grid(row=1, column = 0, padx = button_dropdown_padx)

        enter1neuron = ttk.Button(bframe1, text = "Enter selected neuron", command = self.enterNeuron, width = 25)
        enter1neuron.grid(row=1, column = 1, padx = button_dropdown_padx)

        enterallneurons = ttk.Button(bframe1, text = "Enter all neurons in selected sample", command = self.enterAllNeurons, width = 70)
        enterallneurons.grid(row=2, columnspan = 2)

        uploadSelected = ttk.Button(bframe1, text = 'Upload selected neuron SWCs', command = self.upload_controller, width = 70)
        uploadSelected.grid(row = 3, columnspan = 2)

        uploadAll = ttk.Button(bframe1, text = "Upload all sample neuron SWCs", width = 70, command = lambda: self.upload_controller(uploadAll=True))
        uploadAll.grid(row = 4, columnspan =2)

        ##########################################

        self.report = Text(self.mainframe, bg="white", height=30, width=120)
        self.report.grid(row=1)

        bframe2 = Frame(self.mainframe)
        bframe2.grid(row = 2)

        returnButton = ttk.Button(bframe2, text = "Return to database selection", command = lambda: controller.show_frame(DBSelect_GUI), width = 25)
        returnButton.grid(row = 0, column = 0)

        exitButton = ttk.Button(bframe2, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage), width = 25)
        exitButton.grid(row = 0, column = 1)

    def popreport(self, text):
        if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
        self.report.insert(END, text)

    def unlock_neurondropdown(self, event):
        print('activated')
        self.controller.parser = anw()
        self.controller.parser.set_activesheet(self.sampledropdown.get())
        neuronlist = self.controller.parser.consensuscompleteList
        neuronlist = [n[n.index("_")+1:] for n in neuronlist]

        self.neurondropdown['values'] = neuronlist

        self.controller.parser.anw.close()

    def enterSamp(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        sPoster = MLDB_sample_enter(self.instance)

        try:
            sPoster.post_sample(self.sample_selection.get())
            sys.stdout = old_stdout
            result_string = result.getvalue()

            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, result_string)
        except IndexError:
            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, "Please select a sample first.")

    def enterNeuron(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result
        try:
            nPoster = Neuronposter(self.sample_selection.get(), self.instance)
            nPoster.post_neuron(self.completeneuron_selection.get())

            sys.stdout = old_stdout
            result_string = result.getvalue()

            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, result_string)
            nPoster.parser.anw.close()
        except Exception as e:
            if "'int' object has no attribute 'values'" in e.args:
                if self.report.get(1.0,END) != "":
                    self.report.delete(1.0,END)
                self.report.insert(END, "Please select a sample first.")

            if "'NoneType' object has no attribute 'replace'" in e.args:
                if self.report.get(1.0,END) != "":
                    self.report.delete(1.0,END)
                self.report.insert(END, "Please select a neuron tag first.")
            
    def enterAllNeurons(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        try:
            nPoster = Neuronposter(self.sample_selection.get(), self.instance)
            nPoster.post_ALL_neurons()

            sys.stdout = old_stdout
            result_string = result.getvalue()

            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, result_string)
            nPoster.parser.anw.close()
        except AttributeError:
            if self.report.get(1.0,END) != "":
                self.report.delete(1.0,END)
            self.report.insert(END, "Please select a sample first.")

    def upload_caller(self, uploadAll):
        out = stdout_capture_start()
            
        try:
            uploader = SWCUploader(self.sample_selection.get(), self.instance)

            if uploadAll == False:
                uploader.uploadNeuron(self.completeneuron_selection.get())

            if uploadAll == True:
                uploader.uploadALLNeurons()

            result_string = stdout_capture_stop(out)
            self.popreport(result_string)
            uploader.parser.anw.close()
            self.imRunning.destroy()
            self.controller.unbind('<FocusIn>')
            self.controller.unbind('<Button-1>')

        except KeyError: #Exception should now be reduntant as it exists in the SWCUploader class
            self.imRunning.destroy()
            self.controller.unbind('<FocusIn>')
            self.controller.unbind('<Button-1>')
            self.popreport("Sample or tag not found. Make sure sample and tag are posted to the database.")
            uploader.parser.anw.close()
    
    def upload_controller(self, uploadAll = False):

        if "Select an active sample:" in self.sample_selection.get():
            self.popreport( "Please select a sample first.")
            return
        if "Select a completed neuron from the sample:" in self.completeneuron_selection.get():
            if uploadAll == False:
                self.popreport("Please select a neuron tag first.")
                return

        self.imRunning = Toplevel()

        self.controller.bind('<FocusIn>', self.runRaiser)
        self.controller.bind('<Button-1>', self.runRaiser)

        self.imRunning.wm_overrideredirect(True) 
                
        screen_width = self.controller.winfo_screenwidth()
        screen_height = self.controller.winfo_screenheight()

        window_height = 150
        window_width = 350

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))

        self.imRunning.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        runninglabel = Label(self.imRunning, text = "Upload in progress...")
        runninglabel.pack(pady = 20)

        self.pbar = ttk.Progressbar(self.imRunning, orient = HORIZONTAL, length = 300, mode = 'determinate')
        self.pbar.pack()

        t1 = threading.Thread(target = self.pbar.start)
        t1.start()
        t2 = threading.Thread(target=self.upload_caller, args = (uploadAll,))
        t2.start()

    def runRaiser(self, event):
        self.imRunning.deiconify()