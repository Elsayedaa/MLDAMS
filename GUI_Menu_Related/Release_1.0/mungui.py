import sys
import os
from pathlib import Path
filepath = Path(__file__)
appParentDir = str(filepath.parent.absolute()).replace('x:', r'\\dm11\mousebrainmicro').replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
#sys.path.append(r"\\dm11\mousebrainmicro\Mouselight Data Management\GUI_Branch\Curation_Related_GUI_Branch")
from ANWparser import anw
from move_unf_neurons import copyto_unf
from tkinter import *
from tkinter import ttk
from io import StringIO
import startpage


class MUN_GUI(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)

        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        label = Label(self.mainframe, text = "Move incomplete neurons in a sample from the Finished Neurons folder to the Unfinished Neurons Folder")
        label.grid(row = 0)

        self.sample_selection = StringVar()
        self.sample_selection.set("Select a sample to move unfinished neurons:")
        self.sampledropdown = ttk.Combobox(self.mainframe, textvariable = self.sample_selection, width = 40)
        self.sampledropdown['values'] = controller.parser.sheets
        self.sampledropdown.grid(row=1)

        self.report = Text(self.mainframe, bg="white", height=30, width=125)
        self.report.grid(row=3)

        move_button = ttk.Button(self.mainframe, text = "Move neurons now", command=self.move_now)
        move_button.grid(row=2)

        return_button = ttk.Button(self.mainframe, text = "Return to Main Menu", command=self.MUNguiExit)
        return_button.grid(row=4)

    def move_now(self):

        self.parser = anw()

        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        copyto_unf(self.parser, self.sampledropdown.get())

        sys.stdout = old_stdout
        result_string = result.getvalue()
        result_str = str(result_string)
        result_str = result_str[result_str.index("\n")+1:]

        self.parser.anw.close()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_str)
    
    def MUNguiExit(self):
        try:
            self.parser.anw.close()
        except AttributeError:
            pass
        self.controller.show_frame(startpage.StartPage)

