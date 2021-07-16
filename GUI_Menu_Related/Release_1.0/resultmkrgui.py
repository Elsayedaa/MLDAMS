import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Registration_Related_GUI_Branch".format(appParentDir))
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import threading
from io import StringIO
from mk_result_dir import copyto_results
from mk_db_dir import copyto_db
import startpage

class RegResultDir_GUI(Frame): 
    def __init__(self, parent, controller, *args): 
        Frame.__init__(self,parent)
        self.args = args
        
        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        if args[0] == "r":
            label = Label(self.mainframe, text = "Make a result directory for the registration you are currently working on:")
            label.grid(row = 0)
        if args[0] == "d":
            label = Label(self.mainframe, text = "Make a database directory for the registration you are currently working on:")
            label.grid(row = 0)

        openfile = ttk.Button(self.mainframe, text = "Select a directory", command = self.FileDialog)
        openfile.grid(row=1)

        if args[0] == "r":
            makeresults = ttk.Button(self.mainframe, text = "Make Result Directory", command = self.make)
            makeresults.grid(row=3)
        if args[0] == "d":
            makeresults = ttk.Button(self.mainframe, text = "Make Database Directory", command = self.copy_controller)
            makeresults.grid(row=3)

        self.report = Text(self.mainframe, bg="white", height=30, width=125)
        self.report.grid(row=4)

        exitButton = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exitButton.grid(row=5)

    def FileDialog(self):
        self.filename = filedialog.askdirectory(initialdir = r'\\dm11\mousebrainmicro\registration', title = "Select a directory for your registration")
        print(self.filename)

        label2 = Label(self.mainframe, text = f"You are currently in directory: {self.filename}")
        label2.grid(row = 2)

    def make(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        try:
            if self.args[0] == "r":
                copyto_results(self.filename)
            if self.args[0] == "d":
                print(self.filename)
                copyto_db(self.filename, guicall = True)
        except AttributeError:
            print("Please select a directory first.")
        except FileNotFoundError:
            print("Please select another directory.")

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)
        self.filename = ""

        try:
            self.imRunning.destroy()
        except AttributeError:
            pass

        self.controller.unbind('<FocusIn>')
        self.controller.unbind('<Button-1>')

    def copy_controller(self):

        self.imRunning = Toplevel()

        self.controller.bind('<FocusIn>', self.runRaiser)
        self.controller.bind('<Button-1>', self.runRaiser)

        self.imRunning.wm_overrideredirect(True) 
                
        screen_width = self.controller.winfo_screenwidth()
        screen_height = self.controller.winfo_screenheight()

        window_height = 150
        window_width = 450

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))

        self.imRunning.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        runninglabel = Label(self.imRunning, text = "Copying in progress...this will take several minutes as the files are very large.")
        runninglabel.pack(pady = 20)

        self.pbar = ttk.Progressbar(self.imRunning, orient = HORIZONTAL, length = 300, mode = 'indeterminate')
        self.pbar.pack()

        t1 = threading.Thread(target = self.pbar.start)
        t1.start()
        t2 = threading.Thread(target=self.make)
        t2.start()

    def runRaiser(self, event):
        self.imRunning.deiconify()
