import os
import os.path
import shutil
import re

#dir should be the folder for the current registration
#copies .t5 transform files into a new folder named "Result"
#renames transform files to correspond with the pass #
def copyto_results(dir):
    if "Result" in os.listdir(dir):
        for f in os.listdir(r"{}/Result".format(dir)):
            os.remove(r"{}/Result/{}".format(dir,f))
    else:
        os.mkdir(r"{}/Result".format(dir))
    for fol in os.listdir(dir):
        if os.path.isdir(r"{}/{}".format(dir,fol)) and re.search(r'^Result',fol) == None:
            tname = fol if "Pass" in fol else "Affine"
            for fil in os.listdir(r"{}/{}".format(dir,fol)):
                file_path, ext = os.path.splitext(fil)
                if ext == ".h5":
                    if "_" in file_path and "affine" not in file_path:
                        print("Found a more up to date transform...")
                    print(f"Renaming and moving {tname}...")
                    original = r"{}/{}/{}".format(dir,fol,fil)
                    target = r"{}/Result/{}.h5".format(dir,tname)
                    
                    #print(f"{original}\nrenamed and copied to\n{target}\n")
                    shutil.copyfile(original, target)
                    print(r"{} moved sucessfully!".format(tname))
                    print()
    print(r"Directory created successfully at: {}/Result".format(dir))
