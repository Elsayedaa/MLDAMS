import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
from ANWparser import anw
from tkinter import *
from PIL import ImageTk, Image
import multiprocessing
from startpage import StartPage
#from anwgui import ANWparser_GUI
#from mungui import MUN_GUI
#from locatorgui import Locator_GUI
#from resultmkrgui import RegResultDir_GUI
#from curationgui import Curation_GUI
#from databaseentrygui import DBSelect_GUI, Entry_GUI

class MLDAMS(Tk): 
    def __init__(self, *args, **kwargs): 
        Tk.__init__(self, *args, **kwargs)

        self.frame = Variable()
        self.mainframe = Frame(self) 
        self.mainframe.pack(side="top", fill="both", expand = True)
        self.mainframe.grid_rowconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.option_add('*tearOff', FALSE)

        self.parser = anw() 
        self.show_frame(StartPage)
        self.parser.anw.close() 

    def show_frame(self, cont, *args, **kwargs):
        if type(self.frame) == 'tkinter.Frame':
            self.frame.destroy()
        self.frame = cont(self.mainframe, self, *args, *kwargs)
        self.frame.grid(row=0, column=0, sticky="nsew")
    
    def startproc(self, proc):
        if __name__ == '__main__':
            proc.start()

    def joinproc(self, proc):
        if __name__ == '__main__':
            proc.join()

app = MLDAMS()

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

window_height = screen_height - 300
window_width = screen_width - 200

x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))

app.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
app.title("Mouselight Data Automation Management System")

app.iconbitmap(r'\\dm11\mousebrainmicro\Mouselight Data Management\GUI_Branch\mlicon.ico')

if __name__ == "__main__":
    app.mainloop()

try: 
    app.parser.anw.close()
except:
    print("""The active neuron worksheet parser failed to exit out of the excel sheet. 
    Check the source code for bugs or restart your computer to force close the excel sheet. 
    If the excel sheet is not closed, a OneDrive sync error will occur next time the active neuron worksheet is edited."""
    )

