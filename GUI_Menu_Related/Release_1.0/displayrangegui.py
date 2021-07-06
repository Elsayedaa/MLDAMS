#*
import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
import startpage
import re
import pyautogui
import json
from tkinter import *
from tkinter import ttk

class displayRangeTree(Frame):
    def __init__(self, parent, controller): 
        Frame.__init__(self,parent)
        
        self.controller = controller
        self.mainframe = Frame(self)
        self.mainframe.place(relx=0.5, rely=0.5, anchor=CENTER)

        treeframe = Frame(self.mainframe)
        treeframe.grid(row=0, sticky = "nsew", columnspan = 3)

        treescrollbar = Scrollbar(treeframe)
        treescrollbar.pack(side = "right", fill = "y")

        self.reviewTree = ttk.Treeview(treeframe, height = 35, yscrollcommand = treescrollbar.set)
        treescrollbar.config(command = self.reviewTree.yview)
        
        self.reviewTree['columns'] = ("Display Range Minimum", "Display Range Maximum")
        
        self.reviewTree.column("#0", width = 300, minwidth = 25)
        self.reviewTree.column("#1", width = 300, minwidth = 25)
        self.reviewTree.column("#2", width = 300, minwidth = 25)

        self.reviewTree.heading("#0", text = 'Sample')
        self.reviewTree.heading("Display Range Minimum", text = "Display Range Minimum")
        self.reviewTree.heading("Display Range Maximum", text = "Display Range Maximum")

        self.reviewTree.pack()
        with open(r"\\dm11\mousebrainmicro\registration\Database\displaySettings.json") as f:
            self.diplay_settings = json.load(f)

            self.treeindex  = {}
            for i, sample in enumerate(self.diplay_settings['Samples']):
                sample_name = sample['SampleStr']
                displaymin = sample['DisplayRange'][0]
                displaymax = sample['DisplayRange'][1]
                self.treeindex[i] = sample_name
                self.reviewTree.insert(parent='', index='end', iid = i, text = sample_name, values = (displaymin, displaymax))
        self.reviewTree.bind("<Button-1>", self.get_clicked_index)
        
        sample_label = Label(self.mainframe, text = "Sample:")
        sample_label.grid(row = 1, column = 0)
        min_label = Label(self.mainframe, text = "Display minimum:")
        min_label.grid(row = 1, column = 1)
        max_label = Label(self.mainframe, text = "Display maximum:")
        max_label.grid(row = 1, column = 2)

        self.sample_variable = StringVar()
        self.sample_entry = ttk.Entry(self.mainframe, textvariable = self.sample_variable)
        self.sample_entry.grid(row = 2, column = 0, sticky = "ew", pady = 5)
        self.min_variable = StringVar()
        self.min_entry = ttk.Entry(self.mainframe, textvariable = self.min_variable)
        self.min_entry.grid(row = 2, column = 1, sticky = "ew", pady = 5)
        self.max_variable = StringVar()
        self.max_entry = ttk.Entry(self.mainframe, textvariable = self.max_variable)
        self.max_entry.grid(row = 2, column = 2, sticky = "ew", pady = 5)

        add_new = ttk.Button(self.mainframe, text = "Add new row", command = self.add_row)
        add_new.grid(row = 3, column = 0, sticky = "ew")
        update_current = ttk.Button(self.mainframe, text = "Update selected row", command = self.update_row)
        update_current.grid(row = 3, column = 1, sticky = "ew")
        delete_current = ttk.Button(self.mainframe, text = "Delete selected row", command = self.delete_row)
        delete_current.grid(row = 3, column = 2, sticky = "ew")

        exit_button = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exit_button.grid(row = 4, column = 1, sticky = "ew")
        
        self.reviewTree.see(list(self.treeindex.keys())[-1])
    def add_row(self):
        #define entry conditions
        if re.search(r"\d{4}-\d{2}-\d{2}", self.sample_entry.get()) == None:
            self.sample_variable.set("Invalid entry, please enter in YYYY-MM-DD format.")
        if re.search(r"^\d{5}$", self.min_entry.get()) == None:
            self.min_variable.set("Invalid entry, please enter 5 digit number")
        if re.search(r"^\d{5}$", self.max_entry.get()) == None:
            self.max_variable.set("Invalid entry, please enter 5 digit number")

        #if any of the entry conditions aren't met, a new row won't be made
        if (
            re.search(r"\d{4}-\d{2}-\d{2}", self.sample_entry.get()) == None or
            re.search(r"^\d{5}$", self.min_entry.get()) == None or
            re.search(r"^\d{5}$", self.max_entry.get()) == None
        ):
            return
        
        #add new row
        row_id = list(self.treeindex.keys())[-1]+1
        self.treeindex[row_id] = self.sample_entry.get()
        self.reviewTree.insert(parent='', index='end', iid = row_id, text = self.sample_entry.get(), values = (
            self.min_entry.get(), 
            self.max_entry.get()
        ))
        self.controller.after(1, self.reviewTree.yview_moveto(1))
        self.controller.after(1, self.reviewTree.yview_moveto(1))
        self.reviewTree.see(row_id)

        #add entry to display settings json
        self.diplay_settings["Samples"].append(
            {
                "SampleStr": self.sample_entry.get(),
                "DisplayRange": [int(self.min_entry.get()), int(self.max_entry.get())]
            }
        )

        #save display settings json
        write = write = json.dumps(self.diplay_settings, indent = 4)
        with open(r"\\dm11\mousebrainmicro\registration\Database\displaySettings.json", "w") as f:
            f.write(write)

    def update_row(self):

        #retrieve selected row
        try:
            row_id = self.reviewTree.selection()[0]
        except IndexError:
            none_selected_warning = Toplevel()

            screen_width = self.controller.winfo_screenwidth()
            screen_height = self.controller.winfo_screenheight()

            window_height = 70
            window_width = 175

            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))

            none_selected_warning.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

            warninglabel = Label(none_selected_warning, text = "Error:\nNo row was selected.")
            warninglabel.pack()
            okbutton = ttk.Button(none_selected_warning, text = "Ok", command = none_selected_warning.destroy)
            okbutton.pack()
            return

        #update variable values are changed for valid entries; maintain current record value if entry is invalid
        if re.search(r"\d{4}-\d{2}-\d{2}", self.sample_entry.get()) == None:
            self.sample_variable.set("Invalid entry, please enter in YYYY-MM-DD format.")
            sample_update = self.reviewTree.item(row_id)['text']
        else:
            sample_update = self.sample_entry.get()
        
        if re.search(r"^\d{5}$", self.min_entry.get()) == None:
            self.min_variable.set("Invalid entry, please enter 5 digit number")
            min_update = self.reviewTree.set(row_id, "#1")
        else:
            min_update = self.min_entry.get()

        if re.search(r"^\d{5}$", self.max_entry.get()) == None:
            self.max_variable.set("Invalid entry, please enter 5 digit number")
            max_update = self.reviewTree.set(row_id, "#2")
        else:
            max_update = self.max_entry.get()
        
        #row is deleted and replaced with one that has the updates
        self.reviewTree.delete(row_id)
        self.reviewTree.insert(parent='', index=row_id, iid = row_id, text = sample_update, values = (
            min_update, 
            max_update
        ))

        #update selection in display settings json        
        updatedic = self.diplay_settings["Samples"][int(row_id)]
        updatedic["SampleStr"] = sample_update
        updatedic["DisplayRange"] = [int(min_update), int(max_update)]

        #save display settings json
        write = write = json.dumps(self.diplay_settings, indent = 4)
        with open(r"\\dm11\mousebrainmicro\registration\Database\displaySettings.json", "w") as f:
            f.write(write)   

    def delete_row(self):
        #retrieve selected row
        try:
            row_id = self.reviewTree.selection()[0]
        except IndexError:
            none_selected_warning = Toplevel()

            screen_width = self.controller.winfo_screenwidth()
            screen_height = self.controller.winfo_screenheight()

            window_height = 70
            window_width = 175

            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))

            none_selected_warning.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

            warninglabel = Label(none_selected_warning, text = "Error:\nNo row was selected.")
            warninglabel.pack()
            okbutton = ttk.Button(none_selected_warning, text = "Ok", command = none_selected_warning.destroy)
            okbutton.pack()
            return

        #delete selected row and update index of proceeding rows
        selected_sample = self.reviewTree.item(row_id)['text']
        self.reviewTree.delete(row_id)
        for i in self.reviewTree.get_children():
            if int(i) > int(row_id)-1:
                sample = self.reviewTree.item(i)['text']
                disp_min = self.reviewTree.set(i, "#1")
                disp_max = self.reviewTree.set(i, "#2")
                new_i = str(int(i)-1)
                self.reviewTree.delete(i)
                self.reviewTree.insert(parent='', index=new_i, iid = new_i, text = sample, values = (disp_min, disp_max))

        #delete selection in display settings json        
        for dic in self.diplay_settings["Samples"]:
            if dic["SampleStr"] == selected_sample:
                self.diplay_settings["Samples"].remove(dic)   

        #save disply settings json
        write = write = json.dumps(self.diplay_settings, indent = 4)
        with open(r"\\dm11\mousebrainmicro\registration\Database\displaySettings.json", "w") as f:
            f.write(write)   

    def get_clicked_index(self, event):
        self.clickedindex = self.reviewTree.identify('item', event.x, event.y)
        self.copier(event)
    
    def copier(self, event):

        cur_item = self.reviewTree.item(self.clickedindex)
        col = self.reviewTree.identify_column(event.x)
        if col == "#1" or col == '#2':
            if col == '#1':
                self.controller.clipboard_clear()
                self.controller.clipboard_append(cur_item['values'][0])
            if col == '#2':
                self.controller.clipboard_clear()
                self.controller.clipboard_append(cur_item['values'][1])

            self.copied_msg = Toplevel()
            self.copied_msg.wm_overrideredirect(True) 

            window_height = 20
            window_width = 75
            pos_x, pos_y = pyautogui.position()

            self.copied_msg.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
            
            msg = Label(self.copied_msg, text = "Copied")
            msg.pack()
            msg.after(1000, self.copied_msg.destroy)



