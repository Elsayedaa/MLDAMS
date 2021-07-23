#No async
#Uploader class started and new api urls used 6/23/2021

#things that are different between the sandbox and production databases regarding the neuron poster:
#-graphql server url
#-path for queries and mutations
#-brainAreaID variable

import sys
from pathlib import PurePath
filepath = PurePath(__file__)
abspath = str(filepath.parent)
appParentDir = abspath.replace(r'\Database_Related_GUI_Branch','')
sys.path.append(r"{}\Curation_Related_GUI_Branch".format(appParentDir))
import requests
import asyncio
import logging
import numpy as np
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport
from io import BytesIO
from ANWparser import anw
from somalocator import locator
import re
import os, os.path
import datetime

logging.basicConfig(level=logging.INFO)

class Neuronposter:
    def __init__(self, sample, GraphQLInstance):
        self.GraphQLInstance = GraphQLInstance
        self.folderpath = r"{}\Database_Related_GUI_Branch".format(appParentDir) 

        #Initializing different variables for each database instance
        #graphql server url:
        if self.GraphQLInstance == "sandbox":
            self.sampleapi = "http://mouselight.int.janelia.org:10671/graphql"
            print("You are now accessing the SANDBOX database instance.")
            
        #Same structure as above for the production database    
        if self.GraphQLInstance == "production":
            self.sampleapi = "http://mouselight.int.janelia.org:9671/graphql"
            print("You are now accessing the PRODUCTION database instance.")

        self.GQLDir = r'prodv_queries&mutations'

        self.sample = sample #sample name entered as a class arg
        self.parser = anw() #parser object associated with the sample
        self.parser.set_activesheet(self.sample)

        #made these functions into attributes to reduce the number of times the functions are called as this data does not change after each neuron post
        self.brainarea_ids = self.brainarea_ids() #dictionary of Allen Atlas brain area IDs in the database keyed by brain area names
        self.sampledata = self.sampledata() #dictionary of sample ids and their corresponding injection ids keyed by sample names
        #self.sampledata dictionary structure {"sample name": {"Id": sample id,"injectionId": sample injection id}}

        self.in_sample()
    
    def in_sample(self, *sample):
        with open(r"{}\{}\insample.json".format(self.folderpath, self.GQLDir)) as f:
            q = requests.post(self.sampleapi, json={'query':f.read()})
            response = q.json()
        main_list = response["data"]["neurons"]["items"]
        main_list
        self.neurons_in_sample = {}
        for dic in main_list:
            timestamp = dic["injection"]["sample"]["sampleDate"]
            sampledate = datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%dT%H:%M:%SZ')
            samplename = sampledate[:sampledate.index("T")]

            neuron = dic["tag"]

            if samplename not in self.neurons_in_sample:
                self.neurons_in_sample[samplename] = []
                self.neurons_in_sample[samplename].append(neuron)
            else:
                self.neurons_in_sample[samplename].append(neuron)

        if sample == ():
            return self.neurons_in_sample
        else:
            return self.neurons_in_sample[sample[0]]

    #retrieves a dictionary of ids for Allen Atlas brain areas in the database by querying the database
    def brainarea_ids(self):
        with open(r"{}\{}\brainareaIDs.json".format(self.folderpath, self.GQLDir)) as ba:
            q = requests.post(self.sampleapi, json={'query': ba.read()})
            brainareas = q.json()
            return {dic['name']: dic['id'] for dic in brainareas['data']['brainAreas']}

    #retrieves a dictionary with keys x,y,z for the coordinates of a particular neuron by utilizing the 'parser' anw object
    def coordinateRetriever(self, tag):
        clist = [float(c.strip("'").strip('"').strip(" ")) for c in self.parser.ws["Neuron Location (µm)"][f"{self.sample}_{tag}"].strip("[]").split(",")]
        #clist = [float(c) for c in self.parser.ws["Neuron Location (µm)"][f"{self.sample}_{tag}"].strip(" ").strip("[]").split(", ")]
        return {"x":clist[0],"y":clist[1],"z":clist[2]}

    #creates a dictionary of ids needed to post a neuron to a sample in the database
    #is saved as the self.sampledata attribute defined above
    def sampledata(self, *samplestr):
        with open(r"{}\{}\sampledata.json".format(self.folderpath, self.GQLDir)) as data:
            q = requests.post(self.sampleapi, json={'query': data.read()})
            response = q.json()
            data = {}
            for sample in response["data"]["samples"]["items"]:

                #sample names used as keys
                #sample names retrieved by converting the sampleDate unix timestamp queried from the database
                sampledate = datetime.datetime.fromtimestamp(sample["sampleDate"]/1000).strftime('%Y-%m-%dT%H:%M:%SZ')
                samplename = sampledate[:sampledate.index("T")]
                data[samplename] = {"Id":sample['id'],"injectionId":sample['injections'][0]['id']}

        #if no sample is entered as an argument, the entire dictionary is returned
        if samplestr == ():
            return data
            
        #otherwise, the subdictionary for the sample is returned
        else: 
            return data[samplestr[0]]

    #calculates the ID tag for each neuron to be entered
    def idnum(self):
        with open(r"{}\{}\idRetriever.json".format(self.folderpath, self.GQLDir)) as ids:

            #sends a query to the database for the IDs of all the neurons and compiles them into a list
            q = requests.post(self.sampleapi, json={'query': ids.read()})
            resp = q.json()
            rlist = [i["idString"] for i in resp["data"]["neurons"]["items"]]

            #if no neurons are in the database, the IDs are initialized at 0001
            if len(rlist) == 0:
                idnum = "0001"
            
            #if the latest neuron doesn't follow the typical ID structure, it gives the user the option to input the next number
            elif re.search("(AA)(\d+)",rlist[-1]) == None:
                idnum = input("The latest ID in the database does not follow the typical naming convention. Unable generate a new one automatically. Please enter a 4 digit number for the ID manually:")
            
            #if the latest ID is <1000, zeroes are added before the number accordingly
            #ie: 1 = 0001, 10 = 0010, 100 = 0100
            else:
                s = re.search("(AA)(\d+)",rlist[-1])
                idint = int(s.group(2))
                idint = idint+1
                s = f"{idint/1000:e}"
                try:
                    zeroes = int(s[s.index("-")+1:])
                    idnum=f"{str(0)*zeroes}{idint}"
                
                #nothing is done to the number if it is >1000
                except ValueError:
                    idnum = str(idint)
            return idnum

    def post_neuron(self, tag):
        with open(r"{}\{}\addneuron.json".format(self.folderpath, self.GQLDir)) as addneuron:

            #only posts if the neuron exists in tracing_complete
            if os.path.isdir(r"\\dm11\mousebrainmicro\tracing_complete\{}\{}".format(self.sample, tag)):
                pass
            else:
                print(f"File folder for {self.sample}_{tag} does not exist in the Tracing Complete folder, skipping...\n")
                return

            #Checks if the brain area is a valid Allen ontology soma compartment    
            try:
                brainAreaID = self.brainarea_ids[locator(self.sample,tag).replace(",","")]
            except KeyError:
                print(f"Brain area for {tag} does not exist in the Allen Atlas; input has been skipped. Check for typos in the soma.txt file.\n")
                return

            #looking up the injection ID for the sample
            #the injection ID is needed to post the neuron to the correct sample
            try:
                injectionID = self.sampledata[self.sample]["injectionId"]
            except KeyError:
                print(f"Sample {self.sample} does not exist in the Neuron Broswer Database. Check that it has been entered correctly.")

            #looking up the coordinates for the neuron to be posted
            try:    
                coordinates = self.coordinateRetriever(tag)
            except KeyError:
                coordinates = {'x': None, 'y': None, 'z': None}
                print(f"Could not retrieve coordinates for {tag} because it was not found in the Active Neuron Worksheet,\nmake sure there are no typos in the Neuron Name.\n")

            #entering all the required variables
            variables = {
                "idString": f"AA{self.idnum()}",
                "tag": tag,
                "injectionId": injectionID,
                "baID":brainAreaID,
                "x":coordinates["x"],
                "y":coordinates["y"],
                "z":coordinates["z"]
            }

            #posting the neuron to the database

            #only posts the neuron if it does not already have a container posted in the database.
            if self.sample not in self.neurons_in_sample:
                q = requests.post(self.sampleapi, json={'query': addneuron.read(), 'variables': variables})
                if q.json()['data']['createNeuron']['error'] == None:
                    print(f"Neuron {tag} posted successfully.\n")
                else:
                    print(f"Neuron {tag} could not be posted, error message:{q.json()['data']['createNeuron']['error']}")
            elif tag not in self.neurons_in_sample[self.sample]:
                q = requests.post(self.sampleapi, json={'query': addneuron.read(), 'variables': variables})
                if q.json()['data']['createNeuron']['error'] == None:
                    print(f"Neuron {tag} posted successfully.\n")
                else:
                    print(f"Neuron {tag} could not be posted, error message:{q.json()['data']['createNeuron']['error']}")
            else:
                print(f"{tag} neuron container has already been posted to the database. Input has been skipped. Please delete the existing neuron container first if you want to replace it.\n")

    #posts all neurons from the sample with a completed consensus to the database
    def post_ALL_neurons(self):
        try:

            #uses the parser object to find the consensus complete neurons
            #removes the sample string from the tag so only the neuron tag is used
            for samplestring in self.parser.consensuscompleteList:
                samplestring = samplestring.split("_")
                samplename = samplestring[0]
                neurontag = samplestring[1]

                self.post_neuron(neurontag)

        except requests.exceptions.ConnectionError:
            print("The Neuron Broswer Database is offline. Contact Patrick Edson if this is unexpected.")
        except UnboundLocalError:
            pass

class SWCUploader:
    def __init__(self, sample, GraphQLInstance):
        self.GraphQLInstance = GraphQLInstance
        self.folderpath = r"{}\Database_Related_GUI_Branch".format(appParentDir) 

        #Initializing different variables for each database instance
        #graphql server url:
        if self.GraphQLInstance == "sandbox":
            self.sampleapi = "http://mouselight.int.janelia.org:10671/graphql"
            self.tracingapi = "http://mouselight.int.janelia.org:10651/graphql"
            #self.transformapi = "http://mouselight.int.janelia.org:10661/graphql"
            print("You are now accessing the SANDBOX database instance.")
            
        #Same structure as above for the production database    
        if self.GraphQLInstance == "production":
            self.sampleapi = "http://mouselight.int.janelia.org:9671/graphql"
            self.tracingapi = "http://mouselight.int.janelia.org:9651/graphql"
            #self.transformapi = "http://mouselight.int.janelia.org:9661/graphql"
            print("You are now accessing the PRODUCTION database instance.")

        self.GQLDir = r'prodv_queries&mutations'

        self.sample = sample #sample name entered as a class arg
        self.parser = anw() #parser object associated with the sample
        self.parser.set_activesheet(self.sample)

        self.tracedby = {}
        pairer = np.vectorize(lambda n: self.tracedby.update({n:f"{self.parser.ws['Annotator'][n]}, {self.parser.ws['Annotator'][n+'x']}"}), otypes=[str])
        np.where(pairer(np.array(self.parser.consensuscompleteList)))

        self.neuronids = {}
        self.compile_neuron_ids()
        self.id_tstructure_mapper()

        with open(r"{}\{}\tracingstructures.json".format(self.folderpath, self.GQLDir)) as f:
            q = requests.post(self.tracingapi, json={'query':f.read()})
            q.json()
            self.structure_ids = {'axon':q.json()['data']['tracingStructures'][0]['id'], 'dendrite':q.json()['data']['tracingStructures'][1]['id']}

    def extract_neuron_id(self, array):
        sample = array["injection"]['sample']
        sampledate = datetime.datetime.fromtimestamp(sample["sampleDate"]/1000).strftime('%Y-%m-%dT%H:%M:%SZ')
        samplename = sampledate[:sampledate.index("T")]
        tag = array["tag"]
        neuronid = array["id"]
        self.neuronids[f"{samplename}_{tag}"] = neuronid

    def compile_neuron_ids(self):
        with open(r"{}\{}\neuronids.json".format(self.folderpath, self.GQLDir)) as f:
            q = requests.post(self.sampleapi, json={'query':f.read()})
            q.json()
        jsonarray = np.array(q.json()['data']["neurons"]["items"])
        np_extract_neuron_id = np.vectorize(self.extract_neuron_id, otypes=[dict])
        np.where(np_extract_neuron_id(jsonarray))
    
    #checks which tracing structures have already been uploaded to the selected neuron container
    def id_tstructure_mapper(self):
        with open(r"{}\{}\tracings_present.json".format(self.folderpath, self.GQLDir)) as f:
            q = requests.post(self.tracingapi, json={'query':f.read()})
            response = q.json()

        main_list = response["data"]["tracings"]["tracings"]
        main_list
        self.id_tstructure_map = {}
        for dic in main_list:
            try:
                if dic["neuron"]["id"] not in self.id_tstructure_map:
                    self.id_tstructure_map[dic["neuron"]["id"]] = []
                    self.id_tstructure_map[dic["neuron"]["id"]].append(dic["tracingStructure"]["name"])
                else:
                    self.id_tstructure_map[dic["neuron"]["id"]].append(dic["tracingStructure"]["name"])
            except TypeError:
                print("Uploader found an SWC without an associated container in the database.\nThis may have been caused by an SWC that failed to transform. Try checking the transform manager.\n")      

    def get_neuronFiles(self, tag):
        axonpath = r"\\dm11\mousebrainmicro\tracing_complete\{}\{}\consensus.swc".format(self.sample,tag)
        dendritepath = r"\\dm11\mousebrainmicro\tracing_complete\{}\{}\dendrite.swc".format(self.sample,tag)
        axonfile = open(axonpath, 'rb')
        dendritefile = open(dendritepath, 'rb')
        return {'axon': axonfile, 'dendrite': dendritefile}

    def uploadNeuron(self, tag):

        #grabbing the neuron id, upload will be skipped if the selected neuron does not have a container posted to the database
        try:
            neuron_id = self.neuronids[f"{self.sample}_{tag}"]
        except KeyError:
            print(f"{self.sample}_{tag} sample or neuron container not found in the database; upload has been skipped. Make sure sample and tag have been posted to the database.\n")
            return

        #upload will be skipped if the neuron does not exist in the tracing_complete folder
        if os.path.isdir(r"\\dm11\mousebrainmicro\tracing_complete\{}\{}".format(self.sample, tag)):
            pass
        else:
            print(f"File folder for {tag} does not exist in the Tracing Complete folder, upload skipped.\n")
            return

        #initializing the variables
        axon_variables = {
            'annotator':self.tracedby[f"{self.sample}_{tag}"],
            'neuronid':neuron_id,
            'structureid':self.structure_ids['axon'],
            'file':self.get_neuronFiles(tag)['axon']
        }
        dendrite_variables = {
            'annotator':self.tracedby[f"{self.sample}_{tag}"],
            'neuronid':neuron_id,
            'structureid':self.structure_ids['dendrite'],
            'file':self.get_neuronFiles(tag)['dendrite']
        }

        #initializing the transport service
        transport = AIOHTTPTransport(url=self.tracingapi)
        client = Client(transport=transport)

        #uploading the selected neuron SWCs
        with open(r"{}\{}\uploadswc.json".format(self.folderpath, self.GQLDir)) as upload:
            q = gql(upload.read())

            #uploading the axon SWC, upload will be skipped if the axon has already been uploaded to the selected neuron container
            try:
                if neuron_id in self.id_tstructure_map:
                    if "axon" not in self.id_tstructure_map[neuron_id]:
                        axon_response = client.execute(q, variable_values = axon_variables, upload_files = True)
                        print(f"{tag} axon uploaded")
                    else:
                        print(f"{tag} axon SWC already exists in the database. Upload has been skipped. Please delete the existing SWC first if you want to replace it.\n")
                else:
                    axon_response = client.execute(q, variable_values = axon_variables, upload_files = True)
                    print(f"{tag} axon uploaded")      
            except asyncio.exceptions.TimeoutError:
                print(f"{tag} axon uploaded.")
                pass
            except aiohttp.client_exceptions.ServerDisconnectedError:
                print(f"Database server is down. Seek assistance in the #database channel in Slack.")

            #uploading the dendrite SWC, upload will be skipped if the dendrite has already been uploaded to the selected neuron container
            try:
                if neuron_id in self.id_tstructure_map:
                    if "dendrite" not in self.id_tstructure_map[neuron_id] or neuron_id not in self.id_tstructure_map:
                        dendrite_response = client.execute(q, variable_values = dendrite_variables, upload_files = True)
                        print(f"{tag} dendrite uploaded.")
                    else:
                        print(f"{tag} dendrite SWC already exists in the database. Upload has been skipped. Please delete the existing SWC first if you want to replace it.\n")
                else:
                    dendrite_response = client.execute(q, variable_values = dendrite_variables, upload_files = True)
                    print(f"{tag} dendrite uploaded.")
            except asyncio.exceptions.TimeoutError:
                print(f"{tag} dednrite uploaded.")
                pass
            except aiohttp.client_exceptions.ServerDisconnectedError:
                print(f"Database server is down. Seek assistance in the #database channel in Slack.")

    def uploadALLNeurons(self):
        for neuron in self.parser.consensuscompleteList:
            samplestring = neuron.split("_")
            samplename = samplestring[0]
            neurontag = samplestring[1]

            self.uploadNeuron(neurontag)
        print(f"{self.sample} finished uploading.")


##########################################################################
#example of a post to the sandbox database
#nPoster = Neuronposter("2020-01-23","sandbox")
#nPoster.post_neuron("G-001")
#nPoster.post_ALL_neurons()
#uploader = SWCUploader("2020-09-15","sandbox")
#uploader.uploadALLNeurons()
#print(uploader.get_neuronFiles("G-001"))
#for n in ['G-005', 'G-069']:
#    uploader.uploadNeuron(n)
#print(uploader.uploadNeuron('G-005'))
#print(uploader.structure_ids)
#print(uploader.neuronids)
#print(uploader.tracedby)
##########################################################################