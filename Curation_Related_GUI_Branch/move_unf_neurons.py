#updated to utilized the new ANWparser

import os
import os.path
import shutil
import re
from ANWparser import anw

#moves neurons not marked as completed in the worksheet but exist in the "Finished Neurons" folder to the "Unfinished Neurons" folder
def copyto_unf(anw, *samplename):

    if samplename == ():
        anw.set_activesheet()
    else:
        anw.set_activesheet(samplename[0])

    unf_neuron_fol = r"\\dm11\mousebrainmicro\shared_tracing\Unfinished_Neurons"
    sample_path = r'\\dm11\mousebrainmicro\shared_tracing\Finished_Neurons\{}'.format(anw.sample)
    finished = [n[n.index("G"):] for n in anw.consensuscompleteList]
    if anw.sample in os.listdir(unf_neuron_fol):
        pass
    else:
        os.mkdir(f"{unf_neuron_fol}/{anw.sample}")
    for fol in os.listdir(sample_path):
        fol, ext = os.path.splitext(fol)
        if ((ext == "" and re.search(r"^\w-\d{3}$", fol)) or (ext == '.swc' or ext == '.json')) and fol not in finished:
            if ext == "":
                source = f"{sample_path}/{fol}"
            else:
                source = f"{sample_path}/{fol}{ext}"
            destination = f"{unf_neuron_fol}/{anw.sample}"
            shutil.move(source, destination)
            print(f"{source}\nmoved to:\n{destination}\n")

#copyto_unf(anw())