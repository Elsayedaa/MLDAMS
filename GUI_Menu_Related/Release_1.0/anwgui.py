import sys
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(abspath[0:2], r'\\dm11\mousebrainmicro').replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
from tkinter import *
from tkinter import ttk
from ANWparser import anw
from PIL import ImageTk, Image
from io import StringIO
import startpage

class ANWparser_GUI(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)

        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        #creating the sample selection menu
        ###########################################

        self.label = "" 

        self.sample_selection = StringVar()
        self.sample_selection.set("Select a sample from the dropdown menu:")
        self.sampledropdown = ttk.Combobox(self.mainframe, textvariable = self.sample_selection, width = 50)
        self.sampledropdown['values'] = controller.parser.sheets
        self.sampledropdown.bind('<<ComboboxSelected>>', self.selectsample)
        self.sampledropdown.grid(row=0)

        #Making a report dropdown menu and textbox
        ##########################################

        self.report = Text(self.mainframe, bg="white", height=30, width=125)
        self.report.grid(row=3)

        self.parse_selection = StringVar()
        self.parse_selection.set("Select a report to generate from the dropdown menu:")
        reportlist = [
            "Second passes needed", 
            "Second passes done", 
            "Dendrites needed", 
            "Splits needed", 
            "Consensus needed", 
            "Consensus complete", 
            "Return coordinates", 
            "Percent complete",
            "Full Report (all)"]

        self.reportdropdown = ttk.Combobox(self.mainframe, textvariable = self.parse_selection, width = 50)
        self.reportdropdown['values'] = reportlist
        self.reportdropdown.bind('<<ComboboxSelected>>', self.generate)
        self.reportdropdown.grid(row=2)

        self.return_button = ttk.Button(self.mainframe, text = "Return to Main Menu", command=self.anwExit)
        self.return_button.grid(row=4)    

    #creating the function that runs on sample selection
    ###########################################
            
    def selectsample(self, event):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        sample = self.sampledropdown.get()
        self.parser = anw()
        self.parser.set_activesheet(sample)

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.label != "":
            self.label.destroy()
        self.label = Label(self.mainframe, text=result_string.strip())
        self.label.grid(row=1)

        self.parser.anw.close()

    #creating the function that runs on report selection
    ##########################################

    def generate(self, event):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        report = self.reportdropdown.get()

        if report ==  "Second passes needed":
            self.parser.secpassneeded()
        if report == "Second passes done":
            self.parser.secpassdone()
        if report == "Dendrites needed":
            self.parser.needsdendrites()
        if report == "Splits needed":
            self.parser.needssplit()
        if report == "Consensus needed":
            self.parser.needsconsensus()
        if report == "Consensus complete":
            self.parser.consensuscomplete()
        if report == "Return coordinates":
            self.parser.returncoords()
        if report == "Percent complete":
            self.parser.percentcomplete()
        if report == "Full Report (all)":
            self.parser.all()

        sys.stdout = old_stdout
        result_string = result.getvalue()
        
        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)

    def anwExit(self):
        try:
            self.parser.anw.close()
        except AttributeError:
            pass
        self.controller.show_frame(startpage.StartPage)