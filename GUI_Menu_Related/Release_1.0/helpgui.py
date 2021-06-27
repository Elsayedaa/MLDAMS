import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(appParentDir)
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
from tkinter import *
from tkinter import ttk

class Documentation(Frame): 
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        self.mainframe = Frame(self)
        self.mainframe.pack(side = 'top')
        self.controller = controller

        docs = open(r'{}\readme.txt'.format(appParentDir), 'r')
        fulldoc = docs.read()
        docs.close()
        self.report = Text(self.mainframe, width = 105, height = 120)
        self.report.insert(END, fulldoc)
        self.report['state'] = 'disabled'
        self.report.pack(side = LEFT)
    
        scroll = ttk.Scrollbar(self.mainframe, orient = VERTICAL, command = self.report.yview)
        scroll.pack(side = RIGHT, fill = Y)
        self.report['yscrollcommand'] = scroll.set

class Uins(Frame): 
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        self.mainframe = Frame(self)
        self.mainframe.pack(side = 'top')
        self.controller = controller

        docs = open(r'{}\GUI User Instructions.docx'.format(appParentDir), 'r')
        fulldoc = docs.read()
        docs.close()
        self.report = Text(self.mainframe, width = 105, height = 120)
        self.report.insert(END, fulldoc)
        self.report['state'] = 'disabled'
        self.report.pack(side = LEFT)
    
        scroll = ttk.Scrollbar(self.mainframe, orient = VERTICAL, command = self.report.yview)
        scroll.pack(side = RIGHT, fill = Y)
        self.report['yscrollcommand'] = scroll.set
