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
        self.folderpath = r"{}\Database_Related_GUI_Branch".format(appParentDir) 
        self.GraphQLInstance = GraphQLInstance

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

    #retrieves a dictionary of ids for Allen Atlas brain areas in the database by querying the database
    def brainarea_ids(self):
        with open(r"{}\{}\brainareaIDs.json".format(self.folderpath, self.GQLDir)) as ba:
            q = requests.post(self.sampleapi, json={'query': ba.read()})
            brainareas = q.json()
            return {dic['name']: dic['id'] for dic in brainareas['data']['brainAreas']}

    #retrieves a dictionary with keys x,y,z for the coordinates of a particular neuron by utilizing the 'parser' anw object
    def coordinateRetriever(self, tag):
        clist = [float(c) for c in self.parser.ws["Neuron Location (µm)"][f"{self.sample}_{tag}"].strip(" ").strip("[]").split(", ")]
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
            try:
                brainAreaID = self.brainarea_ids[locator(self.sample,tag).replace(",","")]
            except KeyError:
                print(f"Brain area for {tag} does not exist in the Allen Atlas. Check for typos in the soma.txt file.")

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
                print(f"Could not retrieve coordinates for {tag} because it was not found in the Active Neuron Worksheet,\nmake sure there are no typos in the Neuron Name.")

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
            q = requests.post(self.sampleapi, json={'query': addneuron.read(), 'variables': variables})
            if q.json()['data']['createNeuron']['error'] == None:
                print(f"Neuron {tag} posted successfully.\n")
            else:
                print(f"Neuron {tag} could not be posted, error message:{q.json()['data']['createNeuron']['error']}")

    #posts all neurons from the sample with a completed consensus to the database
    def post_ALL_neurons(self):
        try:

            #uses the parser object to find the consensus complete neurons
            #removes the sample string from the tag so only the neuron tag is used
            for samplestring in self.parser.consensuscompleteList:
                samplestring = samplestring.split("_")
                samplename = samplestring[0]
                neurontag = samplestring[1]

                #Checks to see if the file folder for the neuron exists before posting
                if os.path.isdir(r"\\dm11\mousebrainmicro\tracing_complete\{}\{}".format(samplename, neurontag)):
                    self.post_neuron(neurontag)
                else:
                    print(f"File folder for {neurontag} does not exist in the Tracing Complete folder, skipping...")
        except requests.exceptions.ConnectionError:
            print("The Neuron Broswer Database is offline. Contact Patrick Edson if this is unexpected.")
        except UnboundLocalError:
            pass

class SWCUploader:
    def __init__(self, sample, GraphQLInstance):
        self.folderpath = r"{}\Database_Related_GUI_Branch".format(appParentDir) 
        self.GraphQLInstance = GraphQLInstance

        #Initializing different variables for each database instance
        #graphql server url:
        if self.GraphQLInstance == "sandbox":
            self.sampleapi = "http://mouselight.int.janelia.org:10671/graphql"
            self.tracingapi = "http://mouselight.int.janelia.org:10651/graphql"
            self.transformapi = "http://mouselight.int.janelia.org:10661/graphql"
            print("You are now accessing the SANDBOX database instance.")
            
        #Same structure as above for the production database    
        if self.GraphQLInstance == "production":
            self.sampleapi = "http://mouselight.int.janelia.org:9671/graphql"
            self.tracingapi = "http://mouselight.int.janelia.org:9651/graphql"
            self.transformapi = "http://mouselight.int.janelia.org:9661/graphql"
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

    def get_neuronFiles(self, tag):
        axonpath = r"\\dm11\mousebrainmicro\tracing_complete\{}\{}\consensus.swc".format(self.sample,tag)
        dendritepath = r"\\dm11\mousebrainmicro\tracing_complete\{}\{}\dendrite.swc".format(self.sample,tag)
        axonfile = open(axonpath, 'rb')
        dendritefile = open(dendritepath, 'rb')
        return {'axon': axonfile, 'dendrite': dendritefile}

    async def uploadNeuron(self, tag):
        axon_variables = {
            'annotator':self.tracedby[f"{self.sample}_{tag}"],
            'neuronid':self.neuronids[f"{self.sample}_{tag}"],
            'structureid':self.structure_ids['axon'],
            'file':self.get_neuronFiles(tag)['axon']
        }
        dendrite_variables = {
            'annotator':self.tracedby[f"{self.sample}_{tag}"],
            'neuronid':self.neuronids[f"{self.sample}_{tag}"],
            'structureid':self.structure_ids['dendrite'],
            'file':self.get_neuronFiles(tag)['dendrite']
        }

        transport = AIOHTTPTransport(url=self.tracingapi)

        async with Client(
            transport=transport, fetch_schema_from_transport=True,
        ) as session:
            with open(r"{}\{}\uploadswc.json".format(self.folderpath, self.GQLDir)) as upload:
                q = gql(upload.read())
                try:
                    axon_response = await session.execute(q, variable_values = axon_variables, upload_files = True)
                    print(f"{tag} axon uploaded")
                except asyncio.exceptions.TimeoutError:
                    print(f"{tag} axon upload took longer than normal but was sucessful.")
                    pass
                try:
                    dendrite_response = await session.execute(q, variable_values = dendrite_variables, upload_files = True)
                    print(f"{tag} dendrite uploaded.")
                except asyncio.exceptions.TimeoutError:
                    print(f"{tag} upload took longer than normal but was sucessful.")
                    pass

    def uploadALLNeurons(self):
        for neuron in self.parser.consensuscompleteList:
            asyncio.run(self.uploadNeuron(neuron.split('_')[1]))
        print(f"{self.sample} finished uploading.")


##########################################################################
#example of a post to the sandbox database
#nPoster = Neuronposter("2019-09-06","sandbox")
#nPoster.post_neuron("G-002")
#nPoster.post_ALL_neurons()
uploader = SWCUploader("2019-10-04","sandbox")
uploader.uploadALLNeurons()
#print(uploader.get_neuronFiles("G-001"))
#asyncio.run(uploader.uploadNeuron("G-001"))
#print(uploader.uploadNeuron('G-005'))
#print(uploader.structure_ids)
#print(uploader.neuronids)
#print(uploader.tracedby)
##########################################################################