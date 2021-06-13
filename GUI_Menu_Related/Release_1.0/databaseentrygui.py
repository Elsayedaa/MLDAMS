import sys
import os
from pathlib import Path
filepath = Path(__file__)
appParentDir = str(filepath.parent.absolute()).replace('x:', r'\\dm11\mousebrainmicro').replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
sys.path.append(r"{}\Database_Related_GUI_Branch".format(appParentDir))
from tkinter import *
from io import StringIO
from ANWparser import anw
from MLDB_sample_enter import MLDB_sample_enter
from MLDB_neuron_enter import Neuronposter
import startpage

class DBSelect_GUI(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)

        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        label = Label(self.mainframe, text = "Select a database.")
        label.grid(row = 0, columnspan = 2)

        sandboxClk = ttk.Button(self.mainframe, text = "Sandbox database", command = lambda: controller.show_frame(Entry_GUI,"http://localhost:9671/graphql"))
        sandboxClk.grid(row = 1, column = 0, sticky = E)
    
        productionClk = ttk.Button(self.mainframe, text = "Production database", command = lambda: controller.show_frame(Entry_GUI,"http://mouselight.int.janelia.org:9671/graphql"))
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
        ##########################################

        self.report = Text(self.mainframe, bg="white", height=30, width=120)
        self.report.grid(row=1)

        bframe2 = Frame(self.mainframe)
        bframe2.grid(row = 2)

        returnButton = ttk.Button(bframe2, text = "Return to database selection", command = lambda: controller.show_frame(DBSelect_GUI), width = 25)
        returnButton.grid(row = 0, column = 0)

        exitButton = ttk.Button(bframe2, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage), width = 25)
        exitButton.grid(row = 0, column = 1)

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
        sPoster.post_sample(self.sample_selection.get())

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)

    def enterNeuron(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        nPoster = Neuronposter(self.sample_selection.get(), self.instance)
        nPoster.post_neuron(self.completeneuron_selection.get())

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)
        nPoster.parser.anw.close()

    def enterAllNeurons(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        nPoster = Neuronposter(self.sample_selection.get(), self.instance)
        nPoster.post_ALL_neurons()

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)
        nPoster.parser.anw.close()