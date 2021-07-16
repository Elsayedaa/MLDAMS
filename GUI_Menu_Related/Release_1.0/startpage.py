import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
from tkinter import *
from tkinter import ttk
import anwgui, mungui, locatorgui, resultmkrgui, curationgui, databaseentrygui, helpgui, displayrangegui


class StartPage(Frame): 
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        welcome_frame = Frame(self)
        welcome_frame.place(relx=0.5, rely=0.5,anchor=CENTER)
        self.controller = controller

        welcometext = """Welcome to the Mouselight Data Automation Management System\nA graphical user interface for annotator pipeline related automation scripts\n\nPlease select a service:\n"""

        welcome_label1 = Label(welcome_frame, text=welcometext, font = ('Arial', 14))
        welcome_label1.grid(column=0, row=0, columnspan=3)

        ###################################################################################################
        #                           Making the buttons for the various services
        ###################################################################################################
        #--------------------------------------------------------------------------------------------------
        label1 = Label(welcome_frame, text = "Data Querying & Management:")
        label1.grid(column=0, row=1, columnspan = 1)

        anw_parsker_clk = ttk.Button(welcome_frame,text = "Neuron Worksheet Report Generator",command=lambda: controller.show_frame(anwgui.ANWparser_GUI), width = 35)
        anw_parsker_clk.grid(column=0, row=2, columnspan = 1)
        
        somalocator_clk= ttk.Button(welcome_frame,text = "Soma Brain Area Locator", command= lambda: controller.show_frame(locatorgui.Locator_GUI), width = 35)
        somalocator_clk.grid(column=0, row=3, columnspan = 1)

        move_unf_neurons_clk= ttk.Button(welcome_frame,text = "Unfinished Neuron Mover", command=lambda: controller.show_frame(mungui.MUN_GUI), width = 35)
        move_unf_neurons_clk.grid(column=0, row=4, columnspan = 1)

        #--------------------------------------------------------------------------------------------------
        label2 = Label(welcome_frame, text = "Sample Registration:")
        label2.grid(column=1, row=1, columnspan = 1)

        displayrange_clk = ttk.Button(welcome_frame,text = "Registration Display Settings Record", command = lambda: controller.show_frame(displayrangegui.displayRangeTree), width = 35)
        displayrange_clk.grid(column=1, row=2, columnspan = 1)
  
        mk_result_dir_clk = ttk.Button(welcome_frame, text = "Registration Result Folder Maker", command = lambda: controller.show_frame(resultmkrgui.RegResultDir_GUI, "r"), width = 35)
        mk_result_dir_clk.grid(column=1, row=3, columnspan = 1)

        mk_db_dir_clk = ttk.Button(welcome_frame, text = "Registration Database Folder Maker", command = lambda: controller.show_frame(resultmkrgui.RegResultDir_GUI, "d"), width = 35)
        mk_db_dir_clk.grid(column=1, row=4, columnspan = 1)

        #--------------------------------------------------------------------------------------------------
        label3 = Label(welcome_frame, text = "Data Curation & Entry:")
        label3.grid(column=2, row=1, columnspan = 1)

        mk_temp_curation_clk= ttk.Button(welcome_frame,text = "Temporary Curation Folder Maker", command = lambda: controller.show_frame(curationgui.Curation_GUI), width = 35)
        mk_temp_curation_clk.grid(column=2, row=2, columnspan = 1)

        mk_temp_curation_clk= ttk.Button(welcome_frame,text = "Curation Helper", command = lambda: controller.show_frame(curationgui.Somacuration_GUI), width = 35)
        mk_temp_curation_clk.grid(column=2, row=3, columnspan = 1)

        mldb_sample_enter_clk= ttk.Button(welcome_frame,text = "Database Sample & Neuron Entry", command = lambda: controller.show_frame(databaseentrygui.DBSelect_GUI), width = 35)
        mldb_sample_enter_clk.grid(column=2, row=4, columnspan = 1)

        


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

        servicessub.add_command(label = "Registration Display Settings Record", command = lambda: controller.show_frame(displayrangegui.displayRangeTree))

        servicessub.add_command(label= "Registration Result Folder Maker", command = lambda: controller.show_frame(resultmkrgui.RegResultDir_GUI))

        servicessub.add_command(label= "Temporary Curation Folder Maker", command = lambda: controller.show_frame(curationgui.Curation_GUI))

        servicessub.add_command(label= "Curation Helper", command = lambda: controller.show_frame(curationgui.Somacuration_GUI))

        servicessub.add_command(label= "Database Sample & Neuron Entry", command = lambda: controller.show_frame(databaseentrygui.DBSelect_GUI))
        
        servicessub.add_command(label= "Unfinished Neuron Mover", command = lambda: controller.show_frame(mungui.MUN_GUI))
        ###################################################################################################
        #Adding the 'help' submenu to the topmenu
        ###################################################################################################
        helpsub = Menu(self.topmenu)
        self.topmenu.add_cascade(label = 'Help', menu = helpsub)

        helpsub.add_command(label = 'Documentation', command = lambda: controller.show_frame(helpgui.Documentation))
        helpsub.add_command(label = 'User instructions', command = lambda: controller.show_frame(helpgui.Uins))
        helpsub.add_command(label = 'Protocols') #needs 2 cascading menus, 'manual protocol' and 'automation assisted protocol'
