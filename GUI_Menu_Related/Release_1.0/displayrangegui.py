import sys
import os
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\GUI_Menu_Related\Release_1.0','')
sys.path.append(r"{}\GUI_Menu_Related\Release_1.0".format(appParentDir))
import startpage
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

        self.reviewTree = ttk.Treeview(self.mainframe, height = 35)
        self.reviewTree['columns'] = ("Display Range Minimum", "Display Range Maximum")
        
        self.reviewTree.column("#0", width = 300, minwidth = 25)
        self.reviewTree.column("#1", width = 300, minwidth = 25)
        self.reviewTree.column("#2", width = 300, minwidth = 25)

        self.reviewTree.heading("#0", text = 'Sample')
        self.reviewTree.heading("Display Range Minimum", text = "Display Range Minimum")
        self.reviewTree.heading("Display Range Maximum", text = "Display Range Maximum")

        self.reviewTree.grid(row=0, sticky = "nsew", columnspan = 3)
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

        sample_variable = StringVar()
        self.sample_entry = ttk.Entry(self.mainframe, textvariable = sample_variable)
        self.sample_entry.grid(row = 2, column = 0, sticky = "ew", pady = 5)
        min_variable = StringVar()
        self.min_entry = ttk.Entry(self.mainframe, textvariable = min_variable)
        self.min_entry.grid(row = 2, column = 1, sticky = "ew", pady = 5)
        max_variable = StringVar()
        self.max_entry = ttk.Entry(self.mainframe, textvariable = max_variable)
        self.max_entry.grid(row = 2, column = 2, sticky = "ew", pady = 5)

        add_new = ttk.Button(self.mainframe, text = "Add new row", command = self.add_row)
        add_new.grid(row = 3, column = 0, sticky = "ew")
        update_current = ttk.Button(self.mainframe, text = "Update selected row", command = self.update_row)
        update_current.grid(row = 3, column = 1, sticky = "ew")
        delete_current = ttk.Button(self.mainframe, text = "Delete selected row", command = self.delete_row)
        delete_current.grid(row = 3, column = 2, sticky = "ew")

        exit_button = ttk.Button(self.mainframe, text = "Return to Main Menu", command = lambda: controller.show_frame(startpage.StartPage))
        exit_button.grid(row = 4, column = 1, sticky = "ew")
    
    def add_row(self):
        #add new row
        id = list(self.treeindex.keys())[-1]+1
        self.treeindex[id] = self.sample_entry.get()
        self.reviewTree.insert(parent='', index='end', iid = id, text = self.sample_entry.get(), values = (
            self.min_entry.get(), 
            self.max_entry.get()
        ))

        #add entry to display settings json
        self.diplay_settings["Samples"].append(
            {
                "SampleStr": self.sample_entry.get(),
                "DisplayRange": [self.min_entry.get(), self.max_entry.get()]
            }
        )

        #save display settings json
        write = write = json.dumps(self.diplay_settings, indent = 4)
        with open(r"\\dm11\mousebrainmicro\registration\Database\displaySettings.json", "w") as f:
            f.write(write)

    def update_row(self):

        #update selected row
        if self.sample_entry.get() == "":
            sample_update = self.reviewTree.item(self.clickedindex)['text']
        else:
            sample_update = self.sample_entry.get()
        
        if self.min_entry.get() == "":
            min_update = self.reviewTree.set(self.clickedindex, "#1")
        else:
            min_update = self.min_entry.get()

        if self.max_entry.get() == "":
            max_update = self.reviewTree.set(self.clickedindex, "#2")
        else:
            max_update = self.max_entry.get()
        
        self.reviewTree.delete(self.clickedindex)

        self.reviewTree.insert(parent='', index=self.clickedindex, iid = self.clickedindex, text = sample_update, values = (
            min_update, 
            max_update
        ))

        #update selection in display settings json
        for dic in self.diplay_settings["Samples"]:
            if dic["SampleStr"] == self.reviewTree.item(self.clickedindex)['text']:
                dic["SampleStr"] = sample_update
                dic["DisplayRange"] = [min_update, max_update]
        
        #save display settings json
        write = write = json.dumps(self.diplay_settings, indent = 4)
        with open(r"\\dm11\mousebrainmicro\registration\Database\displaySettings.json", "w") as f:
            f.write(write)   

    def delete_row(self):
        selected_sample = self.reviewTree.item(self.clickedindex)['text']
        self.reviewTree.delete(self.clickedindex)
        for i in self.reviewTree.get_children():
            if int(i) > int(self.clickedindex)-1:
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

            screen_width = self.controller.winfo_screenwidth()
            screen_height = self.controller.winfo_screenheight()

            window_height = 20
            window_width = 75

            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))
            
            pos_x, pos_y = pyautogui.position()

            self.copied_msg.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
            
            msg = Label(self.copied_msg, text = "Copied")
            msg.pack()
            msg.after(1000, self.copied_msg.destroy)



