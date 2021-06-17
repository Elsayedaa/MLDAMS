#last update 6/08/2021, 5:16 pm *
#known issues:
    #Fixed: attempting to 'clear all' on a newly loaded sample that is not saved will produce a key error since not all of its entryframes have been generated
    #Fixed: updating a single entry for a saved item, unqueuing it and requeuing it, will cause all entries except the updated one to be cleared
    #Fixed: clear data for items in the review tree which have been previously saved is not preserved throughout user session after unqueue/requeue 
    #Fixed: if a neuron in the review tree is selected and then the active sample is changed, the entry frame of the last selected neuron remains raised
    #Fixed: welcome frame is likely to be unintentionally saved due to the above problem
    #Fixed: If all neurons are removed from the queued column, the last raised frame remains raised, should address this to prevent entry errors
    #Fixed: cannot run previously scripted neurons and non scripted neurons through the ML script at the same time because unscripted ones will enter the scripted condition too
    #Fixed: Save condition 2 triggers a pandas caveat
    #Fixed: Final decision entrybox popup menu doesn't always disappear when clicking away
    #Fixed: neuron location data for the somalocator module doesn't update after ML script is run unless the program is restarted
    #Fixed: Inserting all neurons should raised the data entry frame for the first neuron in the queued column, currently it does so with the first neuron in the sample list 
    #       regardless of insertion order
    #Curated compartment line is not removed from the soma.txt file if 'Final Decision' is cleared
import time 
import sys
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
from tkinter import * 
import tkinter as tk
from tkinter import filedialog, ttk
import tkinter.font as tkFont
import threading
import requests 
from io import StringIO
import pandas as pd
import numpy as np
import re
from ANWparser import anw
from somalocator import locator, dataloader
from mk_temp_curation import copyto_Temp_Curation, missing
import startpage

pd.set_option('display.max_rows', 5000)

class Curation_GUI(Frame): 
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        
        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        label = Label(self.mainframe, text = "Make a temporary curation folder for the sample you're working on:")
        label.grid(row = 0)

        openfile = ttk.Button(self.mainframe, text = "Select sample directory", command = self.FileDialog)
        openfile.grid(row=1)

        makeCurFolder = ttk.Button(self.mainframe, text = "Make temporary curation folder", command = self.make)
        makeCurFolder.grid(row=3)

        self.report = Text(self.mainframe, bg="white", height=30, width=125)
        self.report.grid(row=4)

        showmissing = ttk.Button(self.mainframe, text = "Show missing files", command=self.ShowMissing)
        showmissing.grid(row=5)

        self.missingreport = Text(self.mainframe, bg="white", height=10, width=125)
        self.missingreport.grid(row=6)

        exitButton = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exitButton.grid(row=7)

    def FileDialog(self):
        self.filename = filedialog.askdirectory(initialdir = r'\\dm11\mousebrainmicro\shared_tracing\Finished_Neurons', title = "Select a sample folder")

        label2 = Label(self.mainframe, text = f"You are currently in directory: {self.filename}")
        label2.grid(row = 2)

    def make(self):
        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        try:
            copyto_Temp_Curation(self.filename)
        except AttributeError:
            print("Please select a directory before trying to make a temporary curation directory.")
        except FileNotFoundError:
            print("Please select another directory.")

        sys.stdout = old_stdout
        result_string = result.getvalue()

        if self.report.get(1.0,END) != "":
            self.report.delete(1.0,END)
        self.report.insert(END, result_string)
        self.filename = ""

    def ShowMissing(self):
        if self.missingreport.get(1.0,END) != "":
            self.missingreport.delete(1.0, END)
        for message in missing:
            self.missingreport.insert(END, message+"\n")

class Somacuration_GUI(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        
        #initializing main page elements
        self.controller = controller
        self.mainframe = ttk.Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        #page description label
        label = ttk.Label(self.mainframe, text = "Review the root structure and soma brain area for each neuron:")
        label.grid(row = 0, columnspan = 3, sticky = "n")

        #the pandas dataframe where the entry data is saved
        self.savefile = r"\\dm11\mousebrainmicro\Mouselight Data Management\GUI_Branch\curationtestlog.pkl"
        self.curationlog = pd.read_pickle(self.savefile)

        self.NBmenu = Variable()

        #-----------------------------------------------------------------------------------------
        # Preparing the list of acceptable soma brain area strings for the Neuron Browser Database
        #-----------------------------------------------------------------------------------------
        produrl = 'http://mouselight.int.janelia.org:9671/graphql'
        q = requests.post(produrl, json={'query':"query {brainAreas {name}}"})
        keylist = q.json()['data']['brainAreas']
        self.NB_Somaloc = list(map(lambda x: x['name'],keylist))

        #-----------------------------------------------------------------------------------------
        #                          Sample selection dropdown menu
        #-----------------------------------------------------------------------------------------
        self.sample_selection = StringVar()
        self.sample_selection.set("Select a sample from the dropdown menu:")
        self.sampledropdown = ttk.Combobox(self.mainframe, textvariable = self.sample_selection)
        self.sampledropdown['values'] = controller.parser.sheets
        self.sampledropdown.bind('<<ComboboxSelected>>', self.insertcomplete)
        self.sampledropdown.grid(row=1, column = 0, columnspan = 2, sticky = "new")


        #-----------------------------------------------------------------------------------------
        #                       Labels for neuron selection columns
        #-----------------------------------------------------------------------------------------

        completelabel = ttk.Label(self.mainframe, text = "Completed Neurons:")
        completelabel.grid(row=2, column = 0, sticky = "n")
        selectedlabel = ttk.Label(self.mainframe, text = "Queued for review:")
        selectedlabel.grid(row=2, column = 1, sticky = "n")

        #-----------------------------------------------------------------------------------------
        #                       Queue all/Unqueue all neurons buttons
        #-----------------------------------------------------------------------------------------

        Qall = ttk.Button(self.mainframe, text = "Queue all >>", command = lambda: self.insertall(list(self.CompleteNeurons.get(0,END))))
        Qall.grid(row = 3, column = 0, sticky = "ew")
        UnQall = ttk.Button(self.mainframe, text = "<< Unqueue all", command = lambda: self.uninsertall(list(self.SelectedNeurons.get(0,END))))
        UnQall.grid(row = 3, column = 1, sticky = "ew")

        #-----------------------------------------------------------------------------------------
        #                        Neuron selection listbox columns
        #-----------------------------------------------------------------------------------------

        #a mouseclick event is sent to
        self.CompleteNeurons = Listbox(self.mainframe, height = 40)
        self.CompleteNeurons.grid(row=4, column = 0, sticky = "ew")
        #a right mouseclick event on the listbox is is sent to self.OnCSelect method
        self.CompleteNeurons.bind('<Button-1>', self.OnCSelect)

        self.SelectedNeurons = Listbox(self.mainframe, height = 40)
        self.SelectedNeurons.grid(row=4, column = 1, sticky  = "ew")
        #a right mouseclick event on the listbox is is sent to self.OnSSelect method
        self.SelectedNeurons.bind('<Button-1>', self.OnSSelect)

        #-----------------------------------------------------------------------------------------
        #            Making a frame to hold the treeview and data entry portion
        #----------------------------------------------------------------------------------------- 

        self.tvframe = ttk.Frame(self.mainframe)
        self.tvframe.grid(row = 1, column = 2, rowspan = 5, sticky = "ns")

        #-----------------------------------------------------------------------------------------
        #                   making the treeview and setting the columns
        #-----------------------------------------------------------------------------------------

        self.reviewTree = ttk.Treeview(self.tvframe, height = 25)
        self.reviewTree.bind('<1>', self.createEntryFrame)
        self.reviewTree['columns'] = ("Root Review", "Compartment from Script", "Compartment from Mesh", "Compartment from Manual Review", "Final Decision", "Comments")
        
        self.reviewTree.column("#0", width = 5)
        self.reviewTree.column("#1", width = 5)
        self.reviewTree.column("#2", width = 150, minwidth = 25)
        self.reviewTree.column("#3", width = 150, minwidth = 25)
        self.reviewTree.column("#4", width = 150, minwidth = 25)
        self.reviewTree.column("#5", width = 150, minwidth = 25)
        self.reviewTree.column("#6", width = 300, minwidth = 25)

        self.reviewTree.heading("#0", text = 'Tag')
        self.reviewTree.heading("Root Review", text = "Root Review")
        self.reviewTree.heading("Compartment from Script", text = "Compartment from Script")
        self.reviewTree.heading("Compartment from Mesh", text = "Compartment from Mesh")
        self.reviewTree.heading("Compartment from Manual Review", text = "Compartment from Manual Review")
        self.reviewTree.heading("Final Decision", text = "Final Decision")
        self.reviewTree.heading("Comments", text = "Comments")

        self.reviewTree.grid(row=0, sticky = "nsew")


        #-----------------------------------------------------------------------------------------
        #            Dictionary of frames for neuron data entry into the treeview
        #   a new frame is generated for each neruon that is moved into the queued column
        # this frame is entered into a new child dictionary with the neuron name as the key
        #        a neuron frame is raised by calling the sample_neuron combo string
        #               ie self.entryframes[sample_neuron]['frame'].raise()
        #  temporarily caches the data that is entered for a neuron during the user session
        #this data is stored in corresponding keys under the child dictionary, similar to 'frame'
        #-----------------------------------------------------------------------------------------

        self.entryframes = {}
        #calls future defined method to create and raise the welcome frame
        self.createEntryFrame("Welcome")

        #-----------------------------------------------------------------------------------------
        # making a class attribute to iterate ids for unsaved neurons added to the treeview
        #         and also making a dictionary linking each neuron to the unique id
        #the id number at the start of a session is the index length of the curation log + 1
        #                   first new neuron entered takes the initial id 
        #  the id is raised by 1 each time a new neuron is entered (defined in OnCSelect)
        #-----------------------------------------------------------------------------------------

        if len(self.curationlog.index) == 0:
            self.treeid = 0
        else:
            self.treeid = self.curationlog.index[-1]+1
        self.iddoc = {neuron:list(self.curationlog['tag'].values).index(neuron) for neuron in list(self.curationlog['tag'].values)}


        #-----------------------------------------------------------------------------------------
        #        Button for generating the final tracing files via Johan's MATLAB script
        #-----------------------------------------------------------------------------------------

        runML = ttk.Button(self.mainframe, text = "Create final tracing files", command = self.runML)
        runML.grid(row = 5, column = 0, columnspan = 2, sticky = "nsew")

        exitButton = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exitButton.grid(row=6, columnspan = 3)
 
    ######################################################################################
    # Method for inserting ANW complete neurons from a sample into the 'complete' listbox
    ######################################################################################
    def insertcomplete(self, event):

        #anw parser object created for the sample
        self.controller.parser = anw()
        self.controller.parser.set_activesheet(self.sampledropdown.get())

        #if any neurons were already in the 'complete' listbox or the 'to be queued' listbox, they are cleared
        if self.CompleteNeurons.get(0,END) !="":
            self.CompleteNeurons.delete(0,END)
        if self.SelectedNeurons.get(0, END) != "":
            self.SelectedNeurons.delete(0,END)
            for entry in self.reviewTree.get_children():
                self.reviewTree.delete(entry)

        #neurons are inserted into the listbox via a list comprehension 
        [self.CompleteNeurons.insert(END, neuron[neuron.index('_')+1:]) for neuron in self.controller.parser.consensuscompleteList]

        #a dictionary of neuron keys and index values is created for the inserted neurons
        #these will be used to remember the position of each neruon in the 'complete' column in case the user wants to transfer them from queued back to complete
        self.nlistindex = {neuron[neuron.index('_')+1:]: self.controller.parser.consensuscompleteList.index(neuron) for neuron in self.controller.parser.consensuscompleteList}

        #active neuron worksheet closed
        self.controller.parser.anw.close()
        self.createEntryFrame("Welcome")

    ######################################################################################
    #method to quickly get the index of a neuron in the treeview by its tag only
    ######################################################################################
    def get_reviewTree_index(self, text):
        for i in self.reviewTree.get_children():
            if self.reviewTree.item(i)['text'] == text:
                return i

    ######################################################################################
    #method for making and entering a tree row from a saved entry
    ######################################################################################
    def makeTree_fromSaved(self, nstring, selection):
        treeid = self.iddoc[nstring]

        #dataframe call id is defined like this here because the curationlog updates in session
        #and the iddoc syncs to match the curationlog index on start only
        callid = list(self.curationlog['tag'].values).index(nstring)
        self.reviewTree.insert(parent='', index='end', iid = treeid, text = selection, values = (
        self.curationlog['root_review'][callid],
        self.curationlog['comp_from_script'][callid],
        self.curationlog['comp_from_mesh'][callid],
        self.curationlog['comp_from_manual'][callid],
        self.curationlog['final'][callid],
        self.curationlog['comments'][callid]
                    ))

    ######################################################################################
    # Method for transferring neurons from 'complete' to 'queued for review'
    # Note: all neuron names are entered as: sample string_neuron tag
    ######################################################################################
    def OnCSelect(self, event):
        #defines the selection (neuron tag) if it is called by a click event
        if type(event) == Event:
            #grabs the index of whatever was clicked in the listbox
            clickedindex = event.widget.index(f"@{event.x},{event.y}")
            #grabs the associated item with the index
            selection = self.CompleteNeurons.get(clickedindex)
            if selection == "": #breaks out of the function if an empty value is clicked
                return

        #defines the selection if it comes from a regular function call
        else:
            selection = event[1]
            clickedindex = event[0]

        #combines the current sample with the selection tag to generate a unique string key for:
            #self.iddoc
            #self.entryframes
            #self.curationlog
        sample_neuron = f"{self.sample_selection.get()}_{selection}"

        #selection is deleted from the 'complete' listbox, a blank strig placeholder replaces it, and the tag is transferred to the 'queued' listbox
        self.CompleteNeurons.delete(clickedindex)
        self.CompleteNeurons.insert(clickedindex,'')
        self.SelectedNeurons.insert(END, selection)

        #this condition handles queuing saved neurons
        if sample_neuron in self.curationlog['tag'].values:

            treeid = self.iddoc[sample_neuron] #id of the neuron from iddoc
            scriptcomp = self.curationlog.loc[self.curationlog['tag']==sample_neuron]['comp_from_script'].values[0] #ML script output compartment

            #subcondition to handle queuing neurons that were modified in current session after save
            if (
                sample_neuron in self.entryframes and
                self.entryframes[sample_neuron]['modified_after_save'] == True
            ):
                self.makeTree_fromSaved(sample_neuron, selection) #retrieving entries from save file

                #if any post save modifications have been made, they replace the saved entry in current user session only
                #if modifications aren't saved, savefile entries are used in the next session
                if 'root_review' in self.entryframes[sample_neuron]:
                    self.reviewTree.set(treeid, '#1', self.entryframes[sample_neuron]['root_review'])

                self.reviewTree.set(treeid, '#2', scriptcomp)

                if 'entered_compFromMesh' in self.entryframes[sample_neuron]:
                    self.reviewTree.set(treeid, '#3', self.entryframes[sample_neuron]['entered_compFromMesh'])

                if 'entered_compFromManual' in self.entryframes[sample_neuron]:
                    self.reviewTree.set(treeid, '#4', self.entryframes[sample_neuron]['entered_compFromManual'])

                if 'entered_compFromFinal' in self.entryframes[sample_neuron]:
                    self.reviewTree.set(treeid, '#5', self.entryframes[sample_neuron]['entered_compFromFinal'])

                if 'entered_commentbox' in self.entryframes[sample_neuron]:
                    self.reviewTree.set(treeid, '#6', self.entryframes[sample_neuron]['entered_commentbox'])

            #subcondition to handle queuing neurons that were cleared in current user session
            elif (
                sample_neuron in self.entryframes and
                self.entryframes[sample_neuron]['modified_after_save'] == False
            ):
                self.reviewTree.insert(parent='', index='end', iid=treeid, text = selection)
                self.reviewTree.set(treeid, '#2', scriptcomp)
            
            #subcondition to handle queuing neurons that were neither moified nor cleared in user session
            #for these, the self.entryframes[sample_neuron]['modified_after_save'] key will not exist
            else:
                self.makeTree_fromSaved(sample_neuron, selection)

        #this condition handles queuing previously queued but unsaved neurons:
        elif sample_neuron in self.entryframes:

            treeid = self.iddoc[sample_neuron]

            #inserts an empty tree row with the neuron id retrieved from iddocs
            self.reviewTree.insert(parent='', index='end', iid=treeid, text = selection)

            #checks to see which data is available in the entryframes child dictionary and enters it into the empty row
            if 'root_review' in self.entryframes[sample_neuron]:
                self.reviewTree.set(treeid, '#1', self.entryframes[sample_neuron]['root_review'])

            if 'entered_compFromMesh' in self.entryframes[sample_neuron]:
                self.reviewTree.set(treeid, '#3', self.entryframes[sample_neuron]['entered_compFromMesh'])

            if 'entered_compFromManual' in self.entryframes[sample_neuron]:
                self.reviewTree.set(treeid, '#4', self.entryframes[sample_neuron]['entered_compFromManual'])
            
            if 'entered_compFromFinal' in self.entryframes[sample_neuron]:
                self.reviewTree.set(treeid, '#5', self.entryframes[sample_neuron]['entered_compFromFinal'])

            if 'entered_commentbox' in self.entryframes[sample_neuron]:
                self.reviewTree.set(treeid, '#6', self.entryframes[sample_neuron]['entered_commentbox'])

        #this condtion handles brand new queues   
        else:  
            #if a pairing doesn't exist, it is generated and the neuron is entered into the treeview
            self.iddoc[sample_neuron] = self.treeid
            self.reviewTree.insert(parent='', index='end', iid=self.treeid, text = selection)
            self.treeid = self.treeid+1

        #an entryframe is created for each queue
        self.createEntryFrame(selection)

    ######################################################################################
    # Method for transferring neurons from 'queued for review' back to 'complete'
    ######################################################################################
    def OnSSelect(self, event):

        #defines the selection (neuron tag) if it is called by a click event
        if type(event) == Event:
            #grabs the index of whatever was clicked in the listbox
            clickedindex = event.widget.index(f"@{event.x},{event.y}")
            #grabs the associated item with the index
            selection = self.SelectedNeurons.get(clickedindex)

        #defines the selection if it comes from a regular function call
        else:
            if event != "":
                selection = event[1]
                clickedindex = 0

        #test if it also works with iddoc
        treeid = self.get_reviewTree_index(selection)
        
        sample_neuron = f"{self.sample_selection.get()}_{selection}"
        #if a neuron tag item is clicked:
        if selection != "":
            #it is deleted from the queued column
            self.SelectedNeurons.delete(clickedindex)
            #the empy string placeholder is deleted from the complete column
            self.CompleteNeurons.delete(self.nlistindex[selection])
            #the neuron is placed where the placeholder was
            self.CompleteNeurons.insert(self.nlistindex[selection], selection)
            #the neuron is removed from the treeview
            self.reviewTree.delete(treeid)
        
        if clickedindex == 0 and len(list(self.SelectedNeurons.get(0,END))) <= 1:
            self.createEntryFrame("Welcome")


    ######################################################################################
    #     Method for inserting all tags into queue, called by the queue all button
    ######################################################################################
    #completelist is self.CompleteNeurons.get(0,END) argument
    def insertall(self, completelist):
        filled = list(np.where(np.array(completelist) != "")[0])

        array = pd.Series(list(enumerate(completelist))).values[filled]
        insert = np.vectorize(lambda x: self.OnCSelect(x), otypes = [tuple])
        np.where(insert(array))
  
        if len(filled) == 0:
            print("User attempted to insert all when there are no neurons to insert.")
        else:
            first = list(self.SelectedNeurons.get(0,END))[0]
            self.createEntryFrame(first)

    ######################################################################################
    #     Method for removing all tags into queue, called by the unqueue all button
    ######################################################################################
    #list is self.SelectedNeurons.get(0,END) argument
    def uninsertall(self, selectedlist):
        array = pd.Series(list(enumerate(selectedlist))).values
        uninsert = np.vectorize(lambda x: self.OnSSelect(x), otypes = [tuple])
        np.where(uninsert(array))

    ######################################################################################
    # Method for making a data entry frame when a neuron in the treeview is clicked
    ######################################################################################
    def createEntryFrame(self, event):
        
        #::::::::::::::::::::::::::::::::::::::::::::::::::::
        #creating a nested function which handles the widgets
        #::::::::::::::::::::::::::::::::::::::::::::::::::::

        def createEntryWidgets(frametext, framestate='normal'):

            #a child dictionary with the neuron name as a key is generated
            self.entryframes[frametext] = {}
            self.entryframes[frametext]['modified_after_save'] = None

                #a new frame is made and stored as a value under the key of 'frame' inside the child dictionary
                #the frame is initiated inside the self.tvframe frame
                #the call structure is as follows: 
                    #-self.entryframes is the parent dictionary
                    #-[frametext] is an f string combo of the sample name and neuron tag, used as a key to the child dictionary
                    #-['frame'] is the key fro the frame value

            if "Welcome" in frametext:
                self.entryframes[frametext]['frame'] = ttk.LabelFrame(self.tvframe, text = "Please queue and select a neuron for curation.")
            else:
                self.entryframes[frametext]['frame'] = ttk.LabelFrame(self.tvframe, text = f"Data entry for {frametext}")
            
            self.tvframe.rowconfigure(0, weight = 1)
            self.entryframes[frametext]['frame'].grid(row=1, sticky = "nsew")

            #subframes are added inside the neuron frame to hold different data entry componenets:

            #holds the root review portion
            rootreview = ttk.Frame(self.entryframes[frametext]['frame'])
            rootreview.pack(side="left", fill = BOTH, expand = True, padx = 10)

            #holds the MATLAB script soma location output review portion
            scriptreview = ttk.Frame(self.entryframes[frametext]['frame'])
            scriptreview.pack(side = "left", fill = BOTH, expand = True, pady = 6)

            #holds the portion for additional comments
            comments = ttk.Frame(self.entryframes[frametext]['frame'])
            comments.pack(side = "left", fill = Y, pady = 5)

            saving = ttk.Frame(self.entryframes[frametext]['frame'])
            saving.pack(side = "left", fill = BOTH, expand = True, pady = 5, padx = 10)

            #-----------------------------------------------------------------------------------------------------------------
            #                                           ::::Root Review Widgets::::
            #-----------------------------------------------------------------------------------------------------------------

            fontstyle1 = tkFont.Font(family="Lucida Grande", size=10)
            labelypad = 5
            labelxpad = 10
            checkxpad = 0

            #Label and checkbox 1: Root assigned to correct node
            rrLabel1 = Label(rootreview, text = "Root assigned to correct node:", font = fontstyle1)
            rrLabel1.grid(row = 0, column = 0, sticky = "w", pady = labelypad, padx = labelxpad)

            self.entryframes[frametext]['checkvar1'] = IntVar()
            checklabel1 = ttk.Checkbutton(rootreview, variable = self.entryframes[frametext]['checkvar1'], state = framestate)
            checklabel1.grid(row = 0, column = 1, sticky = "e", padx = checkxpad)

            #_________________________________________________________________________________________________________________

            #Label and checkbox 2: One root per consensus/dendrite
            rrLabel2 = ttk.Label(rootreview, text = "One root per consensus/dendrite:", font = fontstyle1)
            rrLabel2.grid(row = 1, column = 0, sticky = "w", pady = labelypad, padx = labelxpad)


            self.entryframes[frametext]['checkvar2'] = IntVar()
            checklabel2 = ttk.Checkbutton(rootreview, variable = self.entryframes[frametext]['checkvar2'], state = framestate)
            checklabel2.grid(row = 1, column = 1, sticky = "e", padx = checkxpad)

            #_________________________________________________________________________________________________________________

            #Label and checkbox 3: Roots centered in soma
            rrLabel3 = ttk.Label(rootreview, text = "Roots centered in soma:", font = fontstyle1)
            rrLabel3.grid(row = 2, column = 0, sticky = "w", pady = labelypad, padx = labelxpad)

            self.entryframes[frametext]['checkvar3'] = IntVar()
            checklabel3 = ttk.Checkbutton(rootreview, variable = self.entryframes[frametext]['checkvar3'], state = framestate)
            checklabel3.grid(row = 2, column = 1, sticky = "e", padx = checkxpad)

            #_________________________________________________________________________________________________________________

            #Label and checkbox 4: No obvious tracing errors around the soma:
            rrLabel4 = ttk.Label(rootreview, text = "No obvious tracing errors around the soma:", font = fontstyle1)
            rrLabel4.grid(row = 3, column = 0, sticky = "w", pady = labelypad, padx = labelxpad)

            self.entryframes[frametext]['checkvar4'] = IntVar()
            checklabel4 = ttk.Checkbutton(rootreview, variable = self.entryframes[frametext]['checkvar4'], state = framestate)
            checklabel4.grid(row = 3, column = 1, sticky = "e", padx = checkxpad)

            #_________________________________________________________________________________________________________________

            #Buttons to update the entries in the treeview

            updateRR = ttk.Button(rootreview, text = "Update selected", command = lambda: self.RRupdate(self.raised), state = framestate)
            updateRR.grid(row = 4, column = 0, columnspan = 2, sticky = "nsew")
            clearRR = ttk.Button(rootreview, text = "Clear selected", command = lambda: self.RRClear(self.raised), state = framestate)
            clearRR.grid(row = 5, column = 0, columnspan = 2, sticky = "nsew", pady = 11)
            SaveRR = ttk.Button(rootreview, text = "Save and export selected", command = self.save_to_df, state = framestate)
            SaveRR.grid(row = 6, column = 0, columnspan = 2, sticky = "nsew")

            
            #-----------------------------------------------------------------------------------------------------------------
            #                                           ::::script review widgets::::
            #-----------------------------------------------------------------------------------------------------------------

            #Manual check for which registration mesh the soma falls within
            cfmshLabel = ttk.Label(scriptreview, text = "Compartment from mesh:")
            cfmshLabel.pack()        
            self.entryframes[frametext]['compFromMesh'] = Entry(scriptreview, state = framestate, width = 50)
            self.entryframes[frametext]['compFromMesh'].pack(expand  = True, fill = BOTH)

            #_________________________________________________________________________________________________________________

            #manuaL check for soma location via the allen atlas
            cfmanLabel = ttk.Label(scriptreview, text = "Compartment from manual review:")
            cfmanLabel.pack()
            self.entryframes[frametext]['compFromManual'] = Entry(scriptreview, state = framestate)
            self.entryframes[frametext]['compFromManual'].pack(expand=True, fill = BOTH)

            #_________________________________________________________________________________________________________________

            #final decision for the soma location
            cffLabel = ttk.Label(scriptreview, text = "Final Decision:")
            cffLabel.pack()   
            self.entryframes[frametext]['compFromFinal'] = Entry(scriptreview, state = framestate)
            textFromFinal = StringVar()
            #self.entryframes[frametext]['compFromFinal'] = ttk.Combobox(scriptreview, textvariable = textFromFinal, state = framestate)
            self.entryframes[frametext]['compFromFinal'].bind("<KeyRelease>", self.raiseNBMenu)
            #self.entryframes[frametext]['compFromFinal']['values'] = self.NB_Somaloc
            self.entryframes[frametext]['compFromFinal'].pack(expand = True, fill = BOTH)
            #-----------------------------------------------------------------------------------------------------------------
            #                                    ::::comments section review widgets::::
            #-----------------------------------------------------------------------------------------------------------------

            commentlabel = ttk.Label(comments, text = "Additonal comments:")
            commentlabel.grid(row = 0, sticky = "w", padx = 10)
            self.entryframes[frametext]['commentbox'] = Text(comments, bg="white", height = 12, width = 70, state = framestate)
            self.entryframes[frametext]['commentbox'].grid(row=1, sticky = "ns", padx = 10)

            #-----------------------------------------------------------------------------------------------------------------
            #                                      ::::Save all/clear all buttons::::
            #-----------------------------------------------------------------------------------------------------------------

            savedata = ttk.Button(saving, text = "Save and export all", width = 50, command = self.save_all_qd, state = framestate)
            #clearselected = Button(saving, text = "Clear selected", width = 50)
            clearall = ttk.Button(saving, text = "Clear all data in review", width = 50, command = self.cleartree, state = framestate)
            savedata.pack(side = "top", fill = BOTH, expand = True)
            #clearselected.pack(side = "top", fill = BOTH, expand = True)
            clearall.pack(side = "top", fill = BOTH, expand = True)

            self.raised = frametext

        #::::::::::::::::::::::::::::::::::::::::::::::::::::
        #             END OF NESTED FUNCTION
        #::::::::::::::::::::::::::::::::::::::::::::::::::::

        #defines the selection (neuron tag) if it is called by a click event
        if type(event) == Event:
            #retrieves the id of whatever was clicked in the treeview
            self.clickedindex = self.reviewTree.identify('item', event.x, event.y)
            #grabs the text associated with the #0 heading of the id (programmed to be the neuron)
            clicked = self.reviewTree.item(self.clickedindex)['text']

        #defines the selection if it comes from a regular function call
        else:
            clicked = event
        
        #creating a combo string of the selected sample and neuron tag
        sample_neuron = f"{self.sample_selection.get()}_{clicked}"

        #Condition for the default welcome frame
        if "Welcome" in str(event):
            createEntryWidgets("Welcome", framestate = 'disabled')

        #if the neuron does not already have a child dictionary inside entryrames:
        if (
            sample_neuron not in self.entryframes and 
            re.search(r'^\w-\d{3}$', clicked)
        ):  
            createEntryWidgets(sample_neuron)

        #if the frame already exists for the neuron, it is raised to the foreground
        elif re.search(r'^\w-\d{3}$', clicked):
            self.entryframes[sample_neuron]['frame'].tkraise()
            self.raised = sample_neuron

    ###################################################################################################################
    #                            Method for updating entries into the review tree
    ###################################################################################################################    
    def RRupdate(self, instance):
        tagonly = instance[instance.index('_')+1:]
        instanceIndex = self.get_reviewTree_index(tagonly)
                
        if instance in self.curationlog['tag'].values:
            self.entryframes[instance]['modified_after_save'] = True

        if self.entryframes[instance]['compFromMesh'].get() != "":
            self.entryframes[instance]['entered_compFromMesh'] = self.entryframes[instance]['compFromMesh'].get()
            self.reviewTree.set(instanceIndex, '#3', self.entryframes[instance]['entered_compFromMesh'])

        if self.entryframes[instance]['compFromManual'].get() != "":
            self.entryframes[instance]['entered_compFromManual'] = self.entryframes[instance]['compFromManual'].get()
            self.reviewTree.set(instanceIndex, '#4', self.entryframes[instance]['entered_compFromManual'])

        if self.entryframes[instance]['compFromFinal'].get() != "":
            if self.entryframes[instance]['compFromFinal'].get() in self.NB_Somaloc:
                self.entryframes[instance]['entered_compFromFinal'] = self.entryframes[instance]['compFromFinal'].get()
                self.reviewTree.set(instanceIndex, '#5', self.entryframes[instance]['entered_compFromFinal'])
            else:
                self.invalidDataWarning()

        if self.entryframes[instance]['commentbox'].get(1.0,END) != "\n":
            self.entryframes[instance]['entered_commentbox'] = self.entryframes[instance]['commentbox'].get(1.0,END)
            self.reviewTree.set(instanceIndex, '#6', self.entryframes[instance]['entered_commentbox'])

        if (
            self.entryframes[instance]['checkvar1'].get() == 1 and
            self.entryframes[instance]['checkvar2'].get() == 1 and
            self.entryframes[instance]['checkvar3'].get() == 1 and
            self.entryframes[instance]['checkvar4'].get() == 1
        ):
            #the root review key value for the child dictionary is set to 'complete'
            self.entryframes[instance]['root_review'] = "Complete"
            #the treeview item is edited to include the root reivew value
            self.reviewTree.set(instanceIndex, '#1', self.entryframes[instance]['root_review'])
            return True


    ###################################################################################################################
    #                            Method for clearing entries from the review tree
    ###################################################################################################################  
    def RRClear(self, instance):

        tagonly = instance[instance.index('_')+1:]

        if instance in self.curationlog['tag'].values:
            if instance not in self.entryframes:
                self.createEntryFrame(tagonly)
            self.entryframes[instance]['modified_after_save'] = False

        instanceIndex = self.get_reviewTree_index(tagonly)
        #if all the root review checkboxes are checked:
        #the root review key value for the child dictionary is set to 'complete'
        try:
            if 'root_review' in self.entryframes[instance]:
                del self.entryframes[instance]['root_review']
            #the treeview item is edited to include the root reivew value
            self.reviewTree.set(instanceIndex, '#1', "")

            if 'entered_compFromMesh' in self.entryframes[instance]:
                del self.entryframes[instance]['entered_compFromMesh']
            self.reviewTree.set(instanceIndex, '#3', "")

            if 'entered_compFromManual' in self.entryframes[instance]:
                del self.entryframes[instance]['entered_compFromManual']
            self.reviewTree.set(instanceIndex, '#4', "")

            if 'entered_compFromFinal' in self.entryframes[instance]:
                del self.entryframes[instance]['entered_compFromFinal']
            self.reviewTree.set(instanceIndex, '#5', "")

            if 'entered_commentbox' in self.entryframes[instance]:
                del self.entryframes[instance]['entered_commentbox']
            self.reviewTree.set(instanceIndex, '#6', "")
        except KeyError:
            print(f"No data to clear for {instance}")
            pass

    ######################################################################################
    #   Method for clearing all data (except script compartment) from the review tree
    ######################################################################################
    def cleartree(self):
        firstindex = self.reviewTree.get_children()[0]
        firsttag = self.reviewTree.item(firstindex)['text']
        firstintree = f"{self.sample_selection.get()}_{firsttag}"

        for line in self.reviewTree.get_children(): 
            sample_neuron = f"{self.sample_selection.get()}_{self.reviewTree.item(line, option='text')}"

            self.RRClear(sample_neuron)
        try:
            self.raised = firstintree
            self.entryframes[firstintree]['frame'].tkraise()
        except KeyError:
            print("No frame has been created for the first entry yet.")

        
    ######################################################################################
    #                Method for saving a single entry into the dataframe
    ######################################################################################
    def save_to_df(self, *args):
        
        if args == ():
            savename = self.raised
            scriptcomp = ""
        else:
            savename = args[1]
            scriptcomp = args[0]

        tagonly = savename[savename.index('_')+1:]
        treeindex = self.get_reviewTree_index(tagonly)

        #Previously saved and unmodified in current session
        if (
            savename in self.curationlog['tag'].values and
            savename in self.entryframes and
            self.entryframes[savename]['modified_after_save'] == None
        ):  
            print(f"First save condition triggered: {savename} was previously saved and has NOT been modified in the current session.")
            print("No changes have been made to the dataframe.")
            pass
            
        #Previously saved and modified in current session
        elif (
            savename in self.curationlog['tag'].values and
            savename in self.entryframes and
            (
                self.entryframes[savename]['modified_after_save'] == True or
                self.entryframes[savename]['modified_after_save'] == False
            )
        ):  
            print(f"Second save condition triggered: {savename} was previously saved and has been modified in the current session.")
            print(f"All modified entries for {savename} have been updated in the dataframe, all unmodified entries are unchnaged.")

            self.curationlog.loc[(self.curationlog['tag']==savename),('root_review')] = self.reviewTree.set(treeindex,"#1")

            self.curationlog.loc[(self.curationlog['tag']==savename),('comp_from_mesh')] = self.reviewTree.set(treeindex,"#3")

            self.curationlog.loc[(self.curationlog['tag']==savename),('comp_from_manual')] = self.reviewTree.set(treeindex,"#4")

            self.curationlog.loc[(self.curationlog['tag']==savename),('final')] = self.reviewTree.set(treeindex,"#5")

            self.curationlog.loc[(self.curationlog['tag']==savename),('comments')] = self.reviewTree.set(treeindex,"#6")

        #newly added without a script compartment
        #this condition is fairly atypical since it is best practice to run the ML script before saving
        #when a script compartment is appended to a newly added neuron after running the ML script, the neuron is auto saved to the dataframe
            #this means that all newly added neurons post ML script will fall under conditon 1: (Previously saved and unmodified in current session)
            #when a newly added post ML script neuron is further edited, it will fall under condition 2: (Previously saved and modified in current session)
        elif (
            savename not in self.curationlog['tag'].values and
            savename in self.entryframes
        ):  
            print(f"Third save condition triggered: {savename} is newly added before or during running the ML script.")
            print(f"A series for {savename} has been appended to the dataframe along with the user entries.")

            if 'root_review' in self.entryframes[savename]:
                root_review = self.entryframes[savename]['root_review']
            else:
                root_review = ""

            if 'entered_compFromMesh' in self.entryframes[savename]:
                entered_compFromMesh = self.entryframes[savename]['entered_compFromMesh']
            else:
                entered_compFromMesh = ""
            
            if 'entered_compFromManual' in self.entryframes[savename]:
                entered_compFromManual = self.entryframes[savename]['entered_compFromManual']
            else:
                entered_compFromManual = ""
            
            if 'entered_compFromFinal' in self.entryframes[savename]:
                entered_compFromFinal = self.entryframes[savename]['entered_compFromFinal']
            else:
                entered_compFromFinal = ""
            
            if 'entered_commentbox' in self.entryframes[savename]:
                entered_commentbox = self.entryframes[savename]['entered_commentbox']
            else:
                entered_commentbox = ""

            updateline = pd.DataFrame(
                {                   
                'tag':[savename],
                'root_review':[root_review],
                'comp_from_script':[scriptcomp],
                'comp_from_mesh':[entered_compFromMesh],
                'comp_from_manual':[entered_compFromManual],
                'final':[entered_compFromFinal],
                'comments':[entered_commentbox]
                }
            )
            self.curationlog = self.curationlog.append(updateline, ignore_index = True)

        self.exportFinalDecision(treeindex, tagonly, savename)
        self.curationlog.to_pickle(self.savefile)
        
    ######################################################################################
    #  Method for exporting the final decision to the brain area text file of the neuron
    ######################################################################################
    def exportFinalDecision(self, treeindex, tagonly, savename):

        scriptcomp = self.reviewTree.set(treeindex,"#2")
        finaldecision = self.reviewTree.set(treeindex,"#5")
        parentdir = r"\\dm11\mousebrainmicro\tracing_complete"
        selectedsample = self.sample_selection.get()

        neuronlocdir = "{}\{}\{}\soma.txt".format(parentdir, selectedsample, tagonly)

        if (
            scriptcomp == "" or
            finaldecision == ""
        ):
            if scriptcomp != "" and finaldecision == "":
                self.curationlog.loc[(self.curationlog['tag']==savename),('matches_manual')] = 'Yes'
                with open(neuronlocdir, 'r+') as somatxt:
                    contents = somatxt.read()
                    somatxt.truncate(0)
                    somatxt.seek(0)
                    somatxt.write(scriptcomp.strip())
        else:
            if (
                scriptcomp.replace(',','') == finaldecision
            ):
                self.curationlog.loc[(self.curationlog['tag']==savename),('matches_manual')] = 'Yes'
                with open(neuronlocdir, 'r+') as somatxt:
                    contents = somatxt.read()
                    somatxt.truncate(0)
                    somatxt.seek(0)
                    somatxt.write(scriptcomp.strip())
                    
            elif scriptcomp.replace(',','') != finaldecision:
                self.curationlog.loc[(self.curationlog['tag']==savename),('matches_manual')] = 'No'
                with open(neuronlocdir, 'w') as somatxt:
                    writemessage = f"{scriptcomp}\nCurated compartment: {finaldecision}"
                    somatxt.write(writemessage)
                    
    ######################################################################################
    #        Method for saving all entries in the review tree to the dataframe
    ######################################################################################
    def save_all_qd(self):
        first = self.SelectedNeurons.get(0)
        for tagonly in list(self.SelectedNeurons.get(0,END)):
            sample_neuron = f"{self.sample_selection.get()}_{tagonly}"
            self.createEntryFrame(tagonly)
            self.save_to_df()
        self.createEntryFrame(first)

    ######################################################################################
    #Method that calls the MATLAB curation script and enters its output into the review tree
    ######################################################################################
    def ML_DL_Tfunc(self, sample, includelist):

        self.MATeng.MLCuration(sample, includelist, nargout = 0)
        self.sampleloc = locator(sample, reload=True)

        for neuron in includelist:

            sample_neuron = f"{sample}_{neuron}"

            #finding the script output
            scriptcompartment = self.sampleloc.loc[self.sampleloc['tag']==neuron]['script'].values[0]

            #entering script output into the reviewtree
            treeid = self.get_reviewTree_index(neuron)
            self.reviewTree.set(treeid, "#2", scriptcompartment)

            if sample_neuron in self.curationlog['tag'].values:

                self.curationlog.loc[(self.curationlog['tag']==sample_neuron),('comp_from_script')] = scriptcompartment

            self.save_to_df(scriptcompartment, sample_neuron)
            self.curationlog.to_pickle(self.savefile)
        try:
            self.existing_entry_warning.destroy()
        except AttributeError:
            pass
        self.imRunning.destroy()
        print("MLCuration script has finished running.")


    ######################################################################################
    #Method that generates loading screen while the MATLAB script runs and calls the above method
    ######################################################################################
    def runner(self, sample,includelist):
        self.imRunning = Toplevel()
                
        screen_width = self.controller.winfo_screenwidth()
        screen_height = self.controller.winfo_screenheight()

        window_height = 150
        window_width = 350

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))

        self.imRunning.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        runninglabel = Label(self.imRunning, text = "The ML Curation Script is running\n\nPlease wait, this will take a few minutes...")
        runninglabel.pack(pady = 20)

        self.pbar = ttk.Progressbar(self.imRunning, orient = HORIZONTAL, length = 300, mode = 'determinate')
        self.pbar.pack()

        t = threading.Thread(target = self.pbar.start())
        t.start()
        pt = threading.Thread(target = self.ML_DL_Tfunc, args=(sample, includelist))
        pt.start()

    ######################################################################################
    #Method that handles whether a warning about a user attempt to curate a previously curated neurons is raised
    #                                 Calls the above method
    ######################################################################################
    def runML(self):
        if 'matlab.engine.matlabengine' not in sys.modules:
            print("Please wait, initializing MATLAB engine for the session...")
            import matlab.engine
            self.MATeng = matlab.engine.start_matlab()
            self.MATeng.addpath(r"\\dm11\mousebrainmicro\tracing_complete\Matlab scripts\MLCuration")
            print("MATLAB engine initiated successfully!")

        sample = self.sample_selection.get()
        includelist = list(self.SelectedNeurons.get(0,END))
        self.warning = None
        for neuron in includelist:
            sample_neuron = f"{sample}_{neuron}"

            if sample_neuron in self.curationlog['tag'].values:

                    scriptcomp = self.curationlog.loc[
                        (self.curationlog['tag']==sample_neuron)
                    ]['comp_from_script'].values[0]

                    if scriptcomp != "":
                        self.warning = True
        if self.warning == True:
            self.existing_entry_warning = Toplevel()

            screen_width = self.controller.winfo_screenwidth()
            screen_height = self.controller.winfo_screenheight()

            window_height = 150
            window_width = 375

            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))

            self.existing_entry_warning.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

            warning_label = Label(self.existing_entry_warning, text="WARNING:\n\nSome of these selections already exist in the tracing complete folder.\nAre you sure you want to overwrite the output folders?\n")
            warning_label.pack()

            yesbutton = ttk.Button(self.existing_entry_warning, text = 'Yes, overwrite the folders.', command = lambda: self.runner(sample, includelist))
            yesbutton.pack()
            nobutton = ttk.Button(self.existing_entry_warning, text = 'No, go back.', command = self.existing_entry_warning.destroy)
            nobutton.pack()
        
        if self.warning == None:
            self.runner(sample, includelist)


    ######################################################################################
    #Method that raises a popup menu of valid brain area selections for Final Decision entry
    ######################################################################################
    def raiseNBMenu(self, event):

        x = self.entryframes[self.raised]['compFromFinal'].winfo_rootx()
        y = self.entryframes[self.raised]['compFromFinal'].winfo_rooty()-300

        if str(type(self.NBmenu)) == "<class 'tkinter.Toplevel'>":
            self.NBmenu.destroy()

        self.NBmenu = Toplevel()
        self.NBmenu.geometry(f"305x300+{x}+{y}")
        self.NBmenu.wm_overrideredirect(True) 
        self.controller.bind('<Button-1>', self.NBmenu_offclick)
        

        self.menuboxFinal = Listbox(self.NBmenu)
        self.menuboxFinal.pack(side = 'left', expand = True, fill = BOTH)
        self.menuboxFinal.bind("<<ListboxSelect>>", self.popFinal)

        scroll = ttk.Scrollbar(self.NBmenu, orient = VERTICAL, command = self.menuboxFinal.yview)
        scroll.pack(side = 'left', fill = Y)
        self.menuboxFinal['yscrollcommand'] = scroll.set

        typed = self.entryframes[self.raised]['compFromFinal'].get()
        if typed == '':
            data = self.NB_Somaloc
        else:
            data = []
            for item in self.NB_Somaloc:
                if typed.lower() in item.lower():
                    data.append(item)
                data.sort(key = lambda x: len(x))
        for x in data:
            self.menuboxFinal.insert(END,x)

    ######################################################################################
    #        Method that populates the Final Decision entrybox on NBMenu selection
    ######################################################################################
    def popFinal(self, event):
        i = self.menuboxFinal.curselection()

        try:
            ba = self.menuboxFinal.get(i)
            if self.entryframes[self.raised]['compFromFinal'].get() != "":
                self.entryframes[self.raised]['compFromFinal'].delete(0,END)
            self.entryframes[self.raised]['compFromFinal'].insert(END, ba)
            self.NBmenu.destroy()
            self.controller.unbind('<Button-1>')
        except Exception as e:
            if 'bad listbox index "":' in e.args[0]:
                pass

    ######################################################################################
    #                    Method that destroys the NBMenu on offclick
    ######################################################################################
    def NBmenu_offclick(self, event):
        self.NBmenu.destroy()
        self.controller.unbind('<Button-1>')
    
    ######################################################################################
    #Method that raises a popup warning if user attempts to update with an invalid Final Decision entry
    ######################################################################################
    def invalidDataWarning(self):
        warningwindow = Toplevel()

        screen_width = self.controller.winfo_screenwidth()
        screen_height = self.controller.winfo_screenheight()

        window_height = 150
        window_width = 375

        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))

        warningwindow.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

        warninglabel = Label(warningwindow, text = "Invalid Final Decision entry.\nThe brain area you tried to enter is not part of the Allen ontology.\nPlease make sure your selection is in the Final Decision popup menu.\n")
        warninglabel.pack(pady=10)
        exitbutton = ttk.Button(warningwindow, text = "Ok", command = warningwindow.destroy)
        exitbutton.pack()

