import sys
import os
from pathlib import Path
filepath = Path(__file__)
appParentDir = str(filepath.parent.absolute()).replace('x:', r'\\dm11\mousebrainmicro').replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Registration_Related_GUI_Branch".format(appParentDir))
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from io import StringIO
from mk_result_dir import copyto_results
import startpage

class RegResultDir_GUI(Frame): 
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        
        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        label = Label(self.mainframe, text = "Make a result directory for the registration you are currently working on:")
        label.grid(row = 0)

        openfile = ttk.Button(self.mainframe, text = "Select a directory", command = self.FileDialog)
        openfile.grid(row=1)

        makeresults = ttk.Button(self.mainframe, text = "Make Result Directory", command = self.make)
        makeresults.grid(row=3)

        self.report = Text(self.mainframe, bg="white", height=30, width=125)
        self.report.grid(row=4)

        exitButton = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exitButton.grid(row=5)

    def FileDialog(self):
        self.filename = filedialog.askdirectory(initialdir = r'\\dm11\mousebrainmicro\registration', title = "Select a directory for your registration")

        label2 = Label(self.mainframe, text = f"You are currently in directory: {self.filename}")
        label2.grid(row = 2)

    def make(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        try:
            copyto_results(self.filename)
        except AttributeError:
            print("Please select a directory before trying to make a result directory.")
        except FileNotFoundError:
            print("Please select another directory.")

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)
        self.filename = ""

