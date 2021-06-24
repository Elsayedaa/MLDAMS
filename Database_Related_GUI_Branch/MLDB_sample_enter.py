#MLDB Classy version, created 5/5/2021, allows switching between sandbox and production database
#VSCode falsely detects an indentation error wherever I use fr strings. Code still works regardless.
#*
import sys
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\Database_Related_GUI_Branch','')
import requests
import re
import os
import os.path
from Isb import isb

class MLDB_sample_enter:
    def __init__(self, GQLInstance):
        with open(r'{}\Database_Related_GUI_Branch\auth.txt'.format(appParentDir), 'r') as auth:
            auth_up = str(auth.read()).split('\n')
            u = auth_up[0]
            p = auth_up[1]
        try:
            self.isbdf = isb(u, p) #pandas dataframe containing the table data from the imaged samples board
        except Exception as e:
            if "local variable 'driver' referenced before assignment" in str(e):
                pass #this error is handled in Isb.py line 16
        self.folderpath = r"{}\Database_Related_GUI_Branch".format(appParentDir)  
        self.GQLInstance = GQLInstance

        #Initializing different variables for each database instance
        #-graphql server url:
        if self.GQLInstance == 'sandbox':
            self.sampleapi = "http://mouselight.int.janelia.org:10671/graphql"
            print("You are now accessing the SANDBOX database instance.")

        if self.GQLInstance == 'production':
            self.sampleapi = "http://mouselight.int.janelia.org:9671/graphql"
            print("You are now accessing the PRODUCTION database instance.")

        self.make_strain_id_source = 'source'
        self.make_virus_id_source = 'source'
        self.make_fluor_id_source = 'source'
        self.createSample_source = 'source'
        self.GQLDir = r'prodv_queries&mutations'
        #else:
            #print("URL entered does not match Sandbox or Production database.")

    #                            Standalone functions:

    #retrieves animal ID from imaged samples board for any sample entered as an argument
    def get_animalID(self, sample):
        if self.isbdf.loc[sample,"Animal ID"] == "":
            return "Id not found"
        else:
            return self.isbdf.loc[sample,"Animal ID"]

    #retrieves tag from imaged samples board for any sample entered as an argument
    #is called by get_injection_viruses() because it requires similar operations
    def get_tag(self, sample):
        r = r'(\w*-i?[Cc]re.?\+? ?)'
        tag = self.isbdf.loc[sample,"Genotype"]
        if re.findall(r,tag):
            for match in re.findall(r,tag):
                tag = tag.replace(match,"")
        if len(tag) == 0:
            tag = "Tag not found"
        return  tag.replace("RO:","Retro-orbital")if "RO: " in tag else tag       

    #                                             Mouse strain related functions:
    #   get_strain() finds the mouse strain (string), which is used as an argument for make_strain_id() to lookup or create an id
    #  for the strain (alphanumeric). Additionlly, make_strain_id() calls strain_ids() which is a function that compiles all strain 
    #    IDs that are already in the database into a dictionary via a query to the database, enabling make_strain_id() to lookup 
    #    existing strain ids. If the strain doesn't exist in the database, a mutation is sent to the database to create a new id.

    #retrieves mouse strain name from imaged samples board for any sample entered as an argument
    def get_strain(self, sample):
        r = r'(\w*-i?[Cc]re)'
        s = self.isbdf.loc[sample,"Genotype"]
        if re.findall(r, s):
            return re.findall(r, s)
        else:
            return ["No strain found"]
        
    #retreives the mouse strain IDs corresponding to the mouse strain Name for any database graphql instance link entered as an argument
    def strain_ids(self):
        with open(r"{}\{}\mousestrainIDs.json".format(self.folderpath, self.GQLDir)) as ms:
            q = requests.post(self.sampleapi, json={'query': ms.read()})
            strains = q.json()
            return {dic['name']: dic['id'] for dic in strains['data']['mouseStrains']}
        
    #makes strain ids for mouse strains that don't exist in the database and returns the ids for those that exist (currently using the sandbox ids)
    def make_strain_id(self, mousestrainname):
        with open(r"{}\{}\makemousestrain.json".format(self.folderpath, self.GQLDir)) as make:
            sandbox_strain_ids = self.strain_ids()
            if mousestrainname in sandbox_strain_ids:
                return sandbox_strain_ids[mousestrainname]
            else:
                q = requests.post(self.sampleapi, json={'query': make.read(), 'variables': {"name":mousestrainname}})
                response = q.json()
                return response['data']['createMouseStrain'][self.make_strain_id_source]['id']
            
        
    #                                             Injection info related functions:

    #                                                    Injection viruses:
    #   get_injection_viruses() finds the injection viruses (strings), which is used as an argument for make_virus_id() to lookup 
    #    or create an id for the virus (alphanumeric). Additionlly, make_virus_id() calls virus_ids() which is a function that 
    #       compiles all virus IDs that are already in the database into a dictionary via a query to the database, enabling 
    #  make_virus_id() to lookup existing virus ids. If the virus doesn't exist in the database, a mutation is sent to the database 
    #                                                    to create a new id.    

    #retrieves injection viruses from imaged samples board for any sample entered as an argument
    def get_injection_viruses(self, sample):
        if "Tag not found" in self.get_tag(sample):
            return []
        else:
            v = self.get_tag(sample).replace("Retro-orbital","") if "Retro-orbital" in self.get_tag(sample) else self.get_tag(sample)
            vs = v.split(";") if ";" in v else v.split()
            return [v.strip() for v in vs]
        
    #retreives the virus IDs corresponding to the mouse strain Name for any database graphql instance link entered as an argument
    def virus_ids(self):
        with open(r"{}\{}\virusIDs.json".format(self.folderpath, self.GQLDir)) as v:
            q = requests.post(self.sampleapi, json={'query': v.read()})
            viruses = q.json()
            return {dic['name']: dic['id'] for dic in viruses['data']['injectionViruses']}
        
    #makes id for injection viruses used in the sample
    def make_virus_id(self, sample):
        with open(r"{}\{}\makevirus.json".format(self.folderpath, self.GQLDir)) as make:
            virus_ids = self.virus_ids()
            viruses = ";".join(self.get_injection_viruses(sample))
            if self.get_injection_viruses(sample) == []:
                viruses = "Virus not found"
                print(f"WARNING: No injection viruses were found for {sample}. Virus field has been posted as 'Virus not found'.")
            if viruses in virus_ids:
                return virus_ids[viruses]
            else:
                q = requests.post(self.sampleapi, json={'query': make.read(), 'variables': {"name":viruses}})
                response = q.json()
                return response['data']['createInjectionVirus'][self.make_virus_id_source]['id']
            
    #                                                  Injection fluorophores:
    # get_fluors() finds the injection fluorophores (strings), which is used as an argument for make_fluor_id() to lookup or create 
    #   an id for the fluorophore (alphanumeric). Additionlly, make_fluor_id() calls fluor_ids() which is a function that compiles 
    #  all fluorophore IDs that are already in the database into a dictionary via a query to the database, enabling make_fluor_id() 
    #    to lookup existing fluorophore ids. If the fluorophore doesn't exist in the database, a mutation is sent to the database 
    #                                                   to create a new id.    

    #retrieves fluorophores from imaged samples board for any sample entered as an argument
    def get_fluors(self, sample):
        fluors = self.isbdf.loc[sample, "Fluorophore field for database upload"]
        if fluors == "":
            print(f"WARNING: No injection fluorophores were found for {sample}. Fluorophore field has been posted as 'Fluorophore not found'.")
            return "Fluorophore not found"
        return fluors.split(";")

    #retreives the fluorophore IDs corresponding to the mouse strain Name for any database graphql instance link entered as an argument
    def fluor_ids(self):
        with open(r"{}\{}\fluorIDs.json".format(self.folderpath, self.GQLDir)) as f:
            q = requests.post(self.sampleapi, json={'query': f.read()})
            fluorophores = q.json()
            return {dic['name']: dic['id'] for dic in fluorophores['data']['fluorophores']}
        
    #makes id for the fluorophores used in the sample 
    def make_fluor_id(self, sample):
        with open(r"{}\{}\makefluor.json".format(self.folderpath, self.GQLDir)) as make:
            sandbox_fluor_ids = self.fluor_ids()
            fluors = ";".join(self.get_fluors(sample))
            if fluors in sandbox_fluor_ids:
                return sandbox_fluor_ids[fluors]
            else:
                q = requests.post(self.sampleapi, json={'query': make.read(), 'variables': {"name":fluors}})
                response = q.json()
                return response['data']['createFluorophore'][self.make_fluor_id_source]['id']

    #                                                    Injection areas:
    #     get_injection_area() finds the injection areas (strings), which is used as an argument for make_injectionarea_id() to 
    #      lookup an id for the injection area (alphanumeric). This function ONLY looks up IDs and does not generate new ones, 
    #   make_injectionarea_id() calls brainarea_ids() which is a function that compiles all brainarea IDs that are already in the 
    #   database into a dictionary via a query to the database, enabling make_injectionarea_id() to lookup the ID. Unlike viruses 
    #and fluorophores, new brain area IDs should not be created because the database has all of the Allen Atlas brain areas already.
    #  If you can't lookup the brain area ID via make_injectionarea_id(), it is likely that get_injection_area() retrieved a brain
    #              area string with a typo, so make sure the brain area is spelled correctly in the imaged samples board.

    #retrieves injection areas as a list from imaged samples board for any sample entered as an argument
    #returns "Whole Brain" as a string if injection areas are retrooribital or multi or perfusion
    def get_injection_area(self, sample):
        field = self.isbdf.loc[sample, "Injection Details (Path to PDF of request)"]
        if field == "" or field == "N/A":
            return "Whole Brain"
        elif "RO" in field or "multi" in field or "perfusion" in field:
            return ["Whole Brain"]
        else:
            r = []
            for area in field.split(','):
                a = area.lower()
                l = a[0].upper()
                a = l+a[1:]
                r.append(a)
            return r

    #retreives the brain area IDs corresponding to brain areas in the Allen Atlas
    def brainarea_ids(self):
        with open(r"{}\{}\brainareaIDs.json".format(self.folderpath, self.GQLDir)) as ba:
            q = requests.post(self.sampleapi, json={'query': ba.read()})
            brainareas = q.json()
            return {dic['name']: dic['id'] for dic in brainareas['data']['brainAreas']}
        
    #retrieves the brain area id for the injection area of the sample
    def make_injectionarea_ids(self, sample):
        brainarea_ids = self.brainarea_ids()
        brainareas = self.get_injection_area(sample)
        if type(brainareas) == str:
            print("WARNING: No injection area found, defaulting to 'Whole Brain'.")
            return [brainarea_ids[brainareas]] 
        if type(brainareas) == list:
            return [brainarea_ids[BA] for BA in brainareas if BA in brainarea_ids]

    #                                        Sample injection to database poster:
    #  The following function creates an injection for the sample by calling the above injection related functions to generate IDs
    #                                   for the mutation that is posted to the database

    #makes injection input for sample/sample id passed as arguments
    def make_injection(self, sample, id):
        if type(self.get_injection_area(sample)) == list and len(self.get_injection_area(sample)) > 1:
            print(f"{sample} has multiple injections and should be filled manually.")
        else:
            variables = {
                "samid": id,
                "brainareaID": self.make_injectionarea_ids(sample)[0],
                "injectionvirusID": self.make_virus_id(sample),
                "fluorID": self.make_fluor_id(sample)
            }   
            with open(r"{}\{}\makeinjection.json".format(self.folderpath, self.GQLDir)) as make:
                q = requests.post(self.sampleapi, json={'query': make.read(), 'variables': variables})
                response = q.json()
                return response
    #                                       Sample transform related functions:

    #retrieves transform name from the registration folder for any sample entered as an argument
    def get_transform_name(self, sample):
        try:
            p = f'X:/registration/Database/{sample}'
            for fil in os.listdir(p):
                name, ext = os.path.splitext(fil)
                if ext == ".h5":
                    return fil
        except FileNotFoundError:
            return None

    #retrieves transform path from the registration folder for any sample entered as an argument
    def get_transform_path(self, sample):
        try:
            p = f'X:/registration/Database/{sample}'
            for fil in os.listdir(p):
                name, ext = os.path.splitext(fil)
                if ext == ".h5":
                    return f"/groups/mousebrainmicro/mousebrainmicro{p[p.index(':')+1:]}/{fil}"
        except FileNotFoundError:
            return None

    #makes registration input for sample/sample id passed as arguments
    def make_registration(self, sample, id):
        with open(r"{}\{}\makeregistration.json".format(self.folderpath, self.GQLDir)) as make:
            if self.get_transform_name(sample) == None:
                print(f"Transform file missing for {sample}, input has been skipped")
            if self.get_transform_path(sample) == None:
                print(f"Transform path missing for {sample}, input has been skipped")
            else:
                variables = {
                    "samid": id,
                    "name": self.get_transform_name(sample),
                    "path": self.get_transform_path(sample),
                    "active": True
                }
                q = requests.post(self.sampleapi, json={'query': make.read(), 'variables': variables})
                response = q.json()
                return response
            
    #                                             Sample to database poster:

    #posts a new sample with the sample name, tag, animal id, and mouse strain to the database for any sample passed as an argument
    def post_sample(self, sample):
        try:
            s = sample.split('-')
            with open(r"{}\{}\createsample.json".format(self.folderpath, self.GQLDir)) as createsample:
                if int(s[1]) in [9,4,6,11]:
                    if int(s[2]) == 30:
                        fsamp = f"{s[0]}-{int(s[1])+1}-01"
                    else:
                        fsamp = f"{s[0]}-{s[1]}-{int(s[2])+1}"
                elif int(s[1]) in [1,3,5,7,8,10,12]:
                    if int(s[2]) == 31:
                        fsamp = f"{s[0]}-{int(s[1])+1}-01"
                    else:
                        fsamp = f"{s[0]}-{s[1]}-{int(s[2])+1}"
                elif int(s[1]) == 2:
                    if int(s[0])%4 == 0 and int(s[2]) == 29:
                        fsamp = f"{s[0]}-{int(s[1])+1}-01"
                    elif int(s[0])%4 != 0 and int(s[2]) == 28:
                        fsamp = f"{s[0]}-{int(s[1])+1}-01"
                    else:
                        fsamp = f"{s[0]}-{s[1]}-{int(s[2])+1}"
                if self.get_animalID(sample) == "Id not found":
                    print(f"WARNING: No animal ID was found for {sample}. Animal ID has been posted as 'Id not found'.")
                if self.get_tag(sample) == "Tag not found":
                    print(f"WARNING: No tag was found for {sample}. Sample tag has been posted as 'Tag not found'.")
                variables = {'sample': 
                    {
                'sampleDate': fsamp, 
                'tag': self.get_tag(sample),
                'animalId': self.get_animalID(sample), 
                'mouseStrainId': self.make_strain_id("; ".join(self.get_strain(sample)))
                    }
                }
                try:
                    r = requests.post(self.sampleapi, json={'query': createsample.read(), 'variables': variables})
                    samid = r.json()['data']['createSample'][self.createSample_source]['id']
                    print("Preliminary sample info posted successfully.")
                    mr = self.make_registration(sample, samid)
                    if type(mr) == dict: 
                        if mr['data']['createRegistrationTransform']['error'] == None:
                            print("Sample registration transform linked successfully.")
                        else:
                            print(f"Could not post sample registration transform, error message: {mr['data']['createRegistrationTransform']['error']}")
                    mi = self.make_injection(sample, samid)
                    if mi['data']['createInjection']['error'] == None:
                        print("Sample injection info posted successfully.")                                        
                    else:
                        print(f"Could not post sample injection info, error message: {mi['data']['createInjection']['error']}")
                except:
                    print(f"Preliminary sample info could not be posted: {r.json()}")
        except requests.exceptions.ConnectionError:
            print("The Neuron Broswer Database is offline. Contact Patrick Edson if this is unexpected.")
        print()

#Sandbox = MLDB_sample_enter('sandbox')
#Production = MLDB_sample_enter('production')
#Sandbox.post_sample("2020-09-15")