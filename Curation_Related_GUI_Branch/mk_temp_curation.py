import os
import os.path
import shutil
import re

#dir should be the folder for the current sample
#moves neurons consensus and dendrites swc to a "Temp_Curation" folder within the sample folder
#aids in copying swc into a curation workspace
#lets the user know if certain neurons are missing dendrites, uniques, base, or consensus
global missing
missing = []
def copyto_Temp_Curation(dir):
    if r"Temp_Curation" in os.listdir(dir):
        for f in os.listdir(rf"{dir}/Temp_Curation"):
            os.remove(f"{dir}/Temp_Curation/{f}")
    else:
        os.mkdir(f"{dir}/Temp_Curation")
    
    #parsing sample folder for neuron folders
    for fol in os.listdir(dir):
        if os.path.isdir(f"{dir}/{fol}") and re.search(r"G-\d{3}",fol):
            print(f"Copying files for neuron {fol}...")

            #checking neuron folder for dendrites
            if len([fil for fil in os.listdir(f"{dir}/{fol}") if re.search(r"rit", fil)]) == 0:
                missing.append(f"{fol} is missing dendrites!")
                print(f"{fol} is missing dendrites!")

            #checking neuron folder for a consensus folder
            contents = [c.lower() for c in os.listdir(f"{dir}/{fol}")]
            if "consensus" not in contents:
                missing.append(f"{fol} is missing a consensus folder!")
                print(f"{fol} is missing a consensus folder!")

            #copying dendrites
            for fil in os.listdir(f"{dir}/{fol}"):
                name, ext = os.path.splitext(fil)
                if re.search(r"rit", name) and ext == ".swc":
                    print(f"Copying {fol} dendrites...")
                    original = f"{dir}/{fol}/{fil}"
                    target = f"{dir}/Temp_Curation/{fil}"
                    
                    #print(f"{original}\n copied to\n{target}\n")
                    shutil.copyfile(original, target)
                    print(f"{fol} dendrites moved sucessfully!")
                
                #going into the consensus folder in the neuron folder
                if os.path.isdir(f"{dir}/{fol}/{fil}"):

                    #checking for two uniques
                    if len([fil2 for fil2 in os.listdir(f"{dir}/{fol}/{fil}") if re.search(r"[Uu]ni",fil2) and os.path.splitext(fil2)[1] == ".swc"]) < 2:
                        missing.append(f"{fol} is missing uniques!")
                        print(f"{fol} is missing uniques!")

                    #checking for a base
                    if len([fil2 for fil2 in os.listdir(f"{dir}/{fol}/{fil}") if re.search(r"[Bb]ase",fil2) and os.path.splitext(fil2)[1] == ".swc"])== 0:
                        missing.append(f"{fol} is missing a base!")
                        print(f"{fol} is missing a base!")
                    
                    #checking for a consensus file
                    if len([fil2 for fil2 in os.listdir(f"{dir}/{fol}/{fil}") if re.search(r"sus",fil2) and os.path.splitext(fil2)[1] == ".swc"])== 0:
                        missing.append(f"{fol} is missing a consensus file!")
                        print(f"{fol} is missing a consensus file!")

                    #copying consensus file                          
                    for fil2 in os.listdir(f"{dir}/{fol}/{fil}"):
                        name2, ext2 = os.path.splitext(fil2)
                        if re.search(r"sensus", name2) and ext2 == ".swc":
                            print(f"Copying {fol} conesnsus...")
                            original = f"{dir}/{fol}/{name}/{fil2}"
                            target = f"{dir}/Temp_Curation/{fil2}"

                            #print(f"{original}\n copied to\n{target}\n")
                            shutil.copyfile(original, target)
                            print(f"{fol} consensus moved sucessfully!\n")

