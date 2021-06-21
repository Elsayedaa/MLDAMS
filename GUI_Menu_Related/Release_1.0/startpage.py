import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
from tkinter import *
from tkinter import ttk
import anwgui, mungui, locatorgui, resultmkrgui, curationgui, databaseentrygui


class StartPage(Frame): 
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        welcome_frame = Frame(self)
        welcome_frame.place(relx=0.5, rely=0.5,anchor=CENTER)
        self.controller = controller

        welcometext = """Welcome to the Mouselight Data Automation Management System\nA graphical user interface for annotator pipeline related automation scripts\n\nPlease select a service:\n"""

        welcome_label1 = Label(welcome_frame, text=welcometext, font = ('Arial', 14))
        welcome_label1.grid(column=0, row=0, columnspan=7)

        ###################################################################################################
        #                           Making the buttons for the various services
        ###################################################################################################

        anw_parsker_clk = ttk.Button(welcome_frame,text = "Neuron Worksheet Report Generator",command=lambda: controller.show_frame(anwgui.ANWparser_GUI))
        anw_parsker_clk.grid(column=0, row=1, columnspan = 1)
        
        somalocator_clk= ttk.Button(welcome_frame,text = "Soma Brain Area Locator", command= lambda: controller.show_frame(locatorgui.Locator_GUI))
        somalocator_clk.grid(column=1, row=1, columnspan = 1)
  
        mk_result_dir_clk = ttk.Button(welcome_frame,text = "Registration Result Folder Maker", command = lambda: controller.show_frame(resultmkrgui.RegResultDir_GUI))
        mk_result_dir_clk.grid(column=2, row=1, columnspan = 1)

        move_unf_neurons_clk= ttk.Button(welcome_frame,text = "Unfinished Neuron Mover", command=lambda: controller.show_frame(mungui.MUN_GUI))
        move_unf_neurons_clk.grid(column=3, row=1, columnspan = 1)

        mk_temp_curation_clk= ttk.Button(welcome_frame,text = "Temporary Curation Folder Maker", command = lambda: controller.show_frame(curationgui.Curation_GUI))
        mk_temp_curation_clk.grid(column=4, row=1, columnspan = 1)

        mk_temp_curation_clk= ttk.Button(welcome_frame,text = "Curation Helper", command = lambda: controller.show_frame(curationgui.Somacuration_GUI))
        mk_temp_curation_clk.grid(column=5, row=1, columnspan = 1)

        mldb_sample_enter_clk= ttk.Button(welcome_frame,text = "Database Sample & Neuron Entry", command = lambda: controller.show_frame(databaseentrygui.DBSelect_GUI))
        mldb_sample_enter_clk.grid(column=6, row=1, columnspan = 1)


        ###################################################################################################
        #                             Making the main top menu for the program
        ###################################################################################################
        self.topmenu  = Menu(controller)
        controller.config(menu = self.topmenu)

        ###################################################################################################
        #Adding the 'file' submenu to the topmenu
        ###################################################################################################
        filesub = Menu(self.topmenu)
        self.topmenu.add_cascade(label = 'File', menu = filesub)
        filesub.add_command(label='Main menu', command = lambda: controller.show_frame(StartPage))
        filesub.add_command(label='Exit', command = self.controller.quit)

        ###################################################################################################
        #Adding the 'services' submenu to the topmenu
        ###################################################################################################
        servicessub = Menu(self.topmenu)
        self.topmenu.add_cascade(label = 'Services', menu = servicessub)

        servicessub.add_command(label= "Neuron Worksheet Report Generator", command = lambda: controller.show_frame(anwgui.ANWparser_GUI))

        servicessub.add_command(label= "Soma Brain Area Locator", command = lambda: controller.show_frame(locatorgui.Locator_GUI))

        servicessub.add_command(label= "Registration Result Folder Maker", command = lambda: controller.show_frame(resultmkrgui.RegResultDir_GUI))

        servicessub.add_command(label= "Unfinished Neuron Mover", command = lambda: controller.show_frame(mungui.MUN_GUI))

        servicessub.add_command(label= "Temporary Curation Folder Maker", command = lambda: controller.show_frame(curationgui.Curation_GUI))

        servicessub.add_command(label= "Soma Compartment Curation Helper", command = lambda: controller.show_frame(curationgui.Somacuration_GUI))

        servicessub.add_command(label= "Database Sample & Neuron Entry", command = lambda: controller.show_frame(databaseentrygui.DBSelect_GUI))

        ###################################################################################################
        #Adding the 'help' submenu to the topmenu
        ###################################################################################################
        helpsub = Menu(self.topmenu)
        self.topmenu.add_cascade(label = 'Help', menu = helpsub)

        helpsub.add_command(label = 'Documentation')
        helpsub.add_command(label = 'User instructions')
        helpsub.add_command(label = 'Protocols') #needs 2 cascading menus, 'manual protocol' and 'automation assisted protocol'
