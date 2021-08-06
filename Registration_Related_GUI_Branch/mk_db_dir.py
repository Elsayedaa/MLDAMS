import os, sys, stat
import os.path
import shutil
import threading
import re

def copyto_db(dir, guicall = False):

    #parent directories
    registration_dir = r"\\dm11\mousebrainmicro\registration"
    database_dir = r"\\dm11\mousebrainmicro\registration\Database"
    
    #gettting registration sample directory + registration sample folder name
    if os.path.isdir(dir):
        sample_reg_dir = dir
        if guicall == False:
            fsindex = dir.rindex("\\")
        if guicall == True:
            fsindex = dir.rindex("/")
        sample_reg_fol = dir[fsindex+1:]
        r = re.search(r"(\d{4}-\d{2}-\d{2})", sample_reg_fol)
        sample_name = r.group(1)
    else:
        print("Sample registration folder does not exist.")
        return

    #making database sample directory
    sample_db_dir = r"{}\{}".format(database_dir,sample_reg_fol)

    #if the database sample directory already exists, clear it before recopying
    if os.path.isdir(sample_db_dir):
        print("Sample database folder exists, clearing before recopy...")
        for f in os.listdir(sample_db_dir):
            if f == "HortaObj":
                db_obj_dir = r"{}\{}".format(sample_db_dir, f)
                for dmesh in os.listdir(db_obj_dir):
                    os.remove(r"{}\{}".format(db_obj_dir, dmesh))
                pass
        print("Sample database folder cleared.")

    #otherwise, make the database sample directory
    else:
        print("Creating sample database folder...")       
        os.mkdir(sample_db_dir)
        db_obj_dir = r"{}\HortaObj".format(sample_db_dir)
        os.mkdir(db_obj_dir)
        print("Sample database folder created.")

    #getting the level 2 directory
    level2 = "Level.2.Channel.0.nrrd"
    level2_dir = r"{}\{}".format(sample_reg_dir, level2) #foi1

    #checking to see if level 2 nrrd file exists
    if level2 in os.listdir(sample_reg_dir):
        pass
    else:
        print("Level.2.Channel.0.nrrd not found.")
        return

    #getting the registration result directory 
    reg_result_dir = None
    for f in os.listdir(sample_reg_dir):
        if f.lower() == "result":
            reg_result_dir = r"{}\{}".format(sample_reg_dir,f)

    #checking if registration result directory exists
    if reg_result_dir == None:
        print("Registration 'Result' folder not found.\nIf you see the folder, make sure it is named correctly")
        return
    
    #getting the final transform and horta obj directories
    final_transform_dir = None
    HortaObj_dir = None
    for f in os.listdir(reg_result_dir):
        if re.search(r"[Tt]ransform.\d{4}-\d{2}-\d{2}.h5",f):
            final_transform = f
            final_transform_dir = r"{}\{}".format(reg_result_dir, f) #foi2
        if f.lower() == "hortaobj":
            HortaObj_dir = r"{}\{}".format(reg_result_dir,f) #foi3

    #checking if final transform file exists
    if final_transform_dir == None:
        print("Final transform file not found\nIf you see the file, make sure it is named correctly")
        return

    #checking to see if HortaObj folder exists
    if HortaObj_dir == None:
        print("HortaObj folder does not exist\nIf you see the folder, make sure it is named correctly")
        return

    #getting registration final directory
    final_dir = None
    for f in os.listdir(sample_reg_dir):
        if f.lower() == "final":
            final_dir = r"{}\{}".format(sample_reg_dir,f)

    #checking to see if the registration final directory exists
    if final_dir == None:
        print("Registration 'Final' folder not found.\nIf you see the folder, make sure it is named correctly")
        return

    #getting final image volume file
    final_volume_dir = None
    for f in os.listdir(final_dir):
        if re.search(r"\d{4}-\d{2}-\d{2}_[Ff]inal.nrrd", f):
            final_volume = f
            final_volume_dir = r"{}\{}".format(final_dir, f) #foi4

    #checking to see if the final image volume file exists
    if final_volume_dir == None:
        print("Final transformed volume file not found.\nIf you see the file, make sure it is named correctly.")
        return

    #copy files to database folder
    #print("Copying in progress...this will take several minutes as the files are very large.")
    #level2_dir, sample_db_dir, level2
    def copy_level2():
        shutil.copyfile(level2_dir, r"{}\{}".format(sample_db_dir, level2))
        print("Level 2 volume copied sucessfully.")
    t1 = threading.Thread(target = copy_level2)

    #final_transform_dir, sample_db_dir, final_transform
    def copy_finaltransform():
        shutil.copyfile(final_transform_dir, r"{}\{}".format(sample_db_dir, final_transform))
        print("Final transform file copied sucessfully.")

    #HortaObj_dir, db_obj_dir
    def copy_hortaobj():
        for rmesh in os.listdir(HortaObj_dir):
            target = r"{}\{}".format(HortaObj_dir, rmesh)
            destination = r"{}\{}".format(db_obj_dir, rmesh)
            shutil.copyfile(target, destination)
        print("Horta Obj folder copied sucessfully.")
    t2 = threading.Thread(target = copy_hortaobj)

    #final_volume_dir, sample_db_dir, sample_name
    def copy_finalvolume():
        shutil.copyfile(final_volume_dir, r"{}\Transformed_{}.nrrd".format(sample_db_dir, sample_name))
        print("Final transformed volume copied sucessfully.")
    t3 = threading.Thread(target = copy_finalvolume)

    t1.start()
    t2.start()
    t3.start()

    copy_finaltransform()

    return















