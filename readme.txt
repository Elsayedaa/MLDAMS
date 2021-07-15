Contents:
--------------------------------------
1) About section

2) Backend Module Documentation
	2.1) Dependencies
	2.2) Modules
		2.21) ANWparser
		2.22) mk_temp_curation
		2.23) move_unf_neurons
		2.24) somalocator
		2.25) Isb
		2.26) MLDB_neuron_enter
		2.27) MLDB_sample_enter
		2.28) mk_result_dir

3) GUI Documentation
	3.1) Overview
	3.2) Modules, in depth
		3.21) main
		3.22) startpage
		3.23) anwgui
		3.24) locatorgui
		3.25) displayrangegui
		3.26) resultmkrgui
		3.27) curationgui
			3.271) Curation_GUI
			3.272) Somacuration_GUI
		3.28) databaseentrygui
			3.281) DBSelect_GUI
			3.282) Entry_GUI
		3.29) mungui
			
                                                                        
                                                  1 
                                                About:
_________________________________________________________________________________________________________
The Mouselight Data Automation Management System is a GUI made to simplify calls to a collection 
of Python scripts used to automate and aid with repetitive tasks in the Mouselight pipeline.

These scripts are located within 8 modules divided into three categories, and described in depth 
in the documentation section:

	Curation Related Modules:
	-ANWparser
	-mk_temp_curation
	-move_unf_neurons
	-somalocator
	
	Database Related Modules:
	-Isb
	-MLDB_neuron_enter
	-MLDB_sample_enter

	Registration Related Modules:
	-mk_result_dir

                                                  2
                                    Backend Module Documentation:
_________________________________________________________________________________________________________

                                                 2.1
                              ::::::::::::::Dependencies::::::::::::::



The MLDAMS is written completely in Python and requires any version of Python 3.8 for compatability
with the Matlab engine api.

The curation helper also calls on the MATLAB engine to run MLCuration.m, a script which:
	-Calls the Allen API to retrieve a likely brain area compartment encapsulating the 
	 root of each tracing.
	-Creates a final sample and neuron folder in the Tracing Complete parent directory which 
	 contains the files to be uploaded to the Neuron Broswer.
	-Generates an image of the coronal slice encapsulating the root of the neuron, and the 
	 corresponding Allen ccf coronal slice.
MATLAB version 2019b or a more recent version is needed to call the MATLAB engine from Python
A guide on how to install the latest version of MATLAB can be found at: 
\\dm11\mousebrainmicro\SOP\How to install latest MATLAB.docx
It's advised to use this guide over the one provided by HHMI since the HHMI guide only shows 
how to install version 2018b.
The MLDAMS currently utilizes MATLAB version 2020b.

The user must also have an installation of Google Chrome on their computer as well as the 
Google Chrome webdriver. The Google Chrome webdriver is already stored on the dm11 drive
at "\\dm11\mousebrainmicro\Mouselight_Data_Management\Chromdriver\chromedriver.exe". 
This path is defined in the Isb module, line 16. The webdriver is for Chrome version 91,
which is the latest version of Google Chrome at the time of writing. If you have installed
an upgraded version of Google Chrome, you will need to update the Google Chrome webdriver 
on dm11. Download the matching webdriver version from https://chromedriver.chromium.org/downloads
then unpack the zip in the Chromedriver folder. If you already have Google Chrome version 91,
you can skip all of this. 

The MLDAMS also relies on several 3rd party Python libraries. These libraries include:
-Matlab Engine API
-openpyxl
-pandas
-numpy
-requests
-gql
-Pillow 
-html-table-parser-python3
-selenium 
	-Google Chrome webdriver corresponding to the user's current version of Chrome is 
	 also needed
	-webdriver path variable is defined 
	-the default path is: 
	 

You can create a virtual environment with the name mldamsenv which contains all necessary
dependencies by running installdependencies.bat
This script must be run from an Adminsistrator account or right click > Run as Administrator.

The MLDAMS also utilizes standard libraries including:
-datetime
-re
-os
-os.path
-pathlib
-requests
-shutil
-sys
-pickle
-csv
-math
-tkinter
-io
-time
-threading (utilized to keep the GUI refreshing while MLCuration.m is running)
-multiprocessing (MLDAMS modules are able to call a multiprocessing start method from the main 
 GUI module if ever needed, but currently no functionalities rely on multiprocessing)

                                    
                                                 2.2
                                :::::::::::::::Modules::::::::::::::


 2.21
-ANWparser: this module is used to parse the Active Neuron Worksheet excel file and generate 
----------- reports. Many of the services in the MLDAMS rely on the content of these reports.

	An ANWparser object can be initialized as such:
		variablename = anw(), conventionally the variablename is set as 'parser'
	
	Initialization of an anw object:
		-creates an openpyxl workbook object (in read only mode and data only mode) for 
		 the Active Neuron Worksheet and saves it in an instance variable called self.anw
			-Note: creating an openpyxl object in read only mode uses lazy loading, 
			 meaning the object remains open until manually closed
			-object closing is handled by the GUI
			-Be aware that leaving an openpyxl object open can interfere with Onedrive 
			 syncing. You shouldn't have to worry about that issue since object 
			 closing is handled by the GUI, but this knowledge may help with 
			 troubleshooting if things go terribly wrong.
			-Update: ANWparser now utilizes the binary of a requests.get() return
			 to retrieve the Active Neuron Worksheet from the shared OneDrive link.
			 Therefore, it is utilizing a copy of the worksheet rather than the 
			 original. This should completely prevent syncing issues.
			 
		-creates a list of active samples within the Active Neuron Worksheet and saves 
		 it in an instance variable called self.sheets

	To set a sample as the target for parsing, use the set_activesheet method:
		-ex:	parser.set_activesheet(sample)

	Running the set_activesheet method:
		-saves the name of the chosen sample in an instance variable called self.sample
		-creates a pandas dataframe of the sample sheet and saves it in an instance 
		 variable called self.ws
		-runs all the methods necessary for creating the report lists and saves the 
		 outputs in instance variables, discussed further below...


	-------
	Methods:
	-------

	The list making methods: These methods are run on set_activesheet and the output of these 
	methods is saved into instance variables, the reason for this is because each of the 
	list making methods has a corresponding method to echo the report to the terminal. 
	One of the functionalities of the report echoing methods is to return a count of 
	the neurons captured by the list making methods using the len built in function. 
	This causes the list making methods to be called twice within each report 
	echoing method. Once to iterate over the list and once to find the length of the list. 
	By saving the output of the list making methods into instance varaibles, they 
	can be cached, making it so the list making methods never have to be called 
	again to retrieve the relevant info. 

        secpassneeded_make_list():
		-Makes a list of neurons from the chosen sample that need a second pass.
		-These are defined as neurons with a first pass marked as 'Complete' and 
		 a second pass marked as 'Waiting' or 'In Progress'.
		-On running set_activesheet, the output of secpassneeded_make_list is saved in
		 an instance variable called self.secpassneededList.
		-You can run the method on it's own to return a 'refreshed' list by running 
		 'parser.secpassneeded_make_list()'.
		-However, running the method on its own won't resave the output into its 
		 corresponding instance variable.
		-You can use the 'secpassneeded' method to echo the contents of 
		 self.secpassneededList to the terminal.
		-ie:	parser.secpassneeded()

        secpassdone_make_list():
		-Makes a list of neurons from the chosen sample that have a completed first pass
		 and second pass.
		-These are defined as neurons with a first pass marked as 'Complete' and a 
		 second pass also marked as 'Complete'.
		-On running set_activesheet, the output of secpassdone_make_list is saved in 
		 an instance variable called self.secpassdoneList.
		-You can run the method on it's own to return a 'refreshed' list by running 
		 'parser.secpassdone_make_list()'.
		-However, running the method on its own won't resave the output into its 
		 corresponding instance variable.
		-You can use the 'secpassdone' method to echo the contents of 
		 self.secpassdoneList to the terminal.
		-ie:	parser.secpassdone()

        needsdendrites_make_list():
		-Makes a list of neurons from the chosen sample that need to have the dendrites 
		 traced.
		-These are defined as neurons with a first pass marked as 'Complete' and 
		 dendrites marked as 'HOLD' or 'Waiting'.
		-The method will split the needed dendrites into those with or without 
		 a completed second pass.
		-On running set_activesheet, the output of needsdendrites_make_list 
		 is saved in an instance variable called self.needsdendritesList.
		-You can run the method on it's own to return a 'refreshed' list 
		 by running 'parser.needsdendrites_make_list()'.
		-However, running the method on its own won't resave the output 
		 into its corresponding instance variable.
		-You can use the 'needsdendrites' method to echo the contents 
		 of self.needsdendritesList to the terminal.
		-ie:	parser.needsdendrites()

        needssplit_make_list():
		-Makes a list of neurons from the chosen sample that need to be split.
		-These are defined as neurons with a completed first pass and completed second 
		 pass and a 'Consensus Date' that is either empty or marked as 'Split in Progress'.
		-This means that neurons without a completed second pass will never be captured 
		 by this method, even if they haven't been split.
		-Make sure that all neurons you want to capture with this method have a
		 completed second pass first.
		-On running set_activesheet, the output of needssplit_make_list is saved in an 
		 instance variable called self.needssplitList.
		-You can run the method on it's own to return a 'refreshed' list by 
		 running 'parser.needssplit_make_list()'.
		-However, running the method on its own won't resave the output into 
		 its corresponding instance variable.
		-You can use the 'needssplit' method to echo the contents of 
		 self.needssplitList to the terminal.
		-ie:	parser.needssplit()
 
        needsconsensus_make_list():
		-Makes a list of neurons from the chosen sample that are awaiting consensus.
		-These are defined as neurons which have been split but have not had a consensus.
		-This means that neurons without a split will never be captured by this method.
		-Make sure that all neurons you want to capture with this method have been split 
		 first.
		-On running set_activesheet, the output of needsconsensus_make_list is saved in 
		 an instance variable called self.needsconsensusList.
		-You can run the method on it's own to return a 'refreshed' list by running 
		 'parser.needsconsensus_make_list()'.
		-However, running the method on its own won't resave the output into its 
		 corresponding instance variable.
		-You can use the 'needsconsensus' method to echo the contents of 
		 self.needsconsensusList to the terminal.
		-ie:	parser.needsconsensus()

        consensuscomplete_make_list():
		-Makes a list of neurons from the chosen sample that are completely finished 
		 and have a consensus.
		-These are defined as neurons with a datetime object in the 'Consensus Date' 
		 column and have a first pass and second pass marked as complete.
		-This means that neurons without a completed first pass, second pass, split, 
		 and consensus will never be captured by this method.
		-As such, make sure the neurons that you want to capture with this method are 
		 completely finished.
		-On running set_activesheet, the output of consensuscomplete_make_list is 
		 saved in an instance variable called self.consensuscompleteList.
		-You can run the method on it's own to return a 'refreshed' list by running 
		 'parser.consensuscomplete_make_list()'.
		-However, running the method on its own won't resave the output into its 
		 corresponding instance variable.
		-You can use the 'consensuscomplete' method to echo the contents of 
		 self.consensuscompleteList to the terminal.
		-ie:	parser.consensuscomplete()

	Other methods:

	coords_make_list():
		-Makes a list of the coordinates for the complete neurons in the sample.
		-Since a count is not needed by the report echoing method for this list 
		 making method, the report echoing method calls this directly.
		 to echo the coordinate list, run the returncoords method
		-ie: 	parser.returncoords()
	
	percentcomplete():
		-Returns a percentage corresponding to how completion status of the sample.
		-This percentage is defined as the number of consensus complete neurons over 
		 the number of second pass needed neurons and second pass complete neurons.
		-ie:	numerator = consensuscomplete
			denominator = secpassneeded+secpassdone

	all
		-Echoes an aggregate report of all the previously mentioned reports 
		 (excluding coordinates) to the terminal.

 2.22
-mk_temp_curation: This module contains just one function used to make a temporary folder for 
------------------ consensus tracings.


	copyto_Temp_Curation(dir): 
		-Use this function with a directory as the argument to create a subfolder inside 
		 the desired sample folder containing all consensus and dendrite swcs.
		-This function also checks and reports whether a neuron is missing important 
		 files including: 2 swcs for the split uniques, a base swc, a consensus swc, 
		 or a dendites swc.

 2.23
-move_unf_neurons: This module also contains just one function used to move unfinished neurons 
------------------ from a sample to the unfinished neurons directory.

	copyto_unf(anw, *samplename): 
		-Use this function to move all the unfinished neurons in a sample to the 
		 unfinished neurons folder. Unfinished neurons are defined as all neurons 
		 which are not captured by the anw class' consensuscomplete() function. 
		-copyto_unf takes the anw() class as an obligatory argument and takes the 
		 sample name as an optional argument.
		-If the sample name option argument is not given, an input function will be 
		 triggered for the user to enter the desired sample.
		-The function will move all neurons not captured by consensuscomplete() 
		 to the unfinished neurons folder.

		-!!!Make sure the sample is no longer in use before using this function!!!

		example uses:
			input: copyto_unf(anw())
			output: Enter the sample you would like to parse.|

			input: copyto_unf(anw(), '2020-11-16')
			output: f'{neuron directory} moved to {unfinished neurons directory}'

 2.24
-somalocator: This module consists of a handful of functions used to cache and retrieve the soma
------------- brain area compartments for complete neurons.


	locCompiler(): 
		-This function compiles all the soma brain area compartments from the MLCuraion.m
		 output text files in the Tracing Complete directory and caches them in a pickled 
		 pandas dataframe. 
	
	datereader(datetimestr): 
		-This function reads the last modified date of the Tracing Complete directory and 
		 outputs a 'True' boolean if the date has changed from the last logged date.
		-datetimestr is the last modified date cast as a string. 
		 Ex: str(os.path.getmtime(directory path)) 

	dataloader(reload=None): 
		-This function determines whether the locCompiler function runs again when the 
		 soma brain area locations are parsed by the locator function.
		-locCompiler will be rerun if:
			-The datereader function (which is always run inside dataloader) 
			 returns 'True'.
			-If the user explicitly passes reload = True as an argument to
			 the function.

	locator(sample, *tag, reload=None): 
		-This function will return the soma brain area locations of desired neurons.
		-The only obligatory argument for this function is the sample. The function 
		 will return the soma brain area locations of all neurons in the sample.
		-If the tag argument is passed, the function will return the soma brain area 
		 location of the specific neuron tag entered.
		-The user can choose to explicitly recompile the soma brain area location 
		 cache by passing reload=True.

	availInSamp(*s, reload=None): 
		-This function will return all the available samples and tags in the 
		 Tracing Complete directory.
		-No obligatory arguments for this function.
		-Running the function with no arguments will return a dictionary with the 
		 samples as keys and corresponding neurons as values.
		-The user can pass the sample name as the s argument to return the neurons 
		 within that sample.
		-the user can choose to explicitly recompile the soma brain area location 
		 cache by passing reload=True.

 2.25
-Isb: This module contains a single function which converts the HTML table in the Imaged Samples 
----- Board in the Mouselight Wiki into a Pandas dataframe. This dataframe is used by 
      MLDB_sample_enter to automate sample data entry into the Neuron Broswer database.

	isb(*auth): 
		-The isb function takes takes an optional argument "auth", which should be a tuple of
		 the user's username and password of the user's HHMI account. The isb function will
		 still run without the argument; if this is the case, the user will be prompted
		 to enter their username and password directly into the browser window that pops
		 up when the function is run. 

 2.26
-MLDB_sample_enter: This module contains the class MLDB_sample_enter, which is used to 
------------------- automatically enter the data of samples into the Neuron Broswer 
                    sample manager database.

	Initialization of the object takes one argument, a string representing the GraphQL instance the 
        the user is accessing. An MLDB_sample_enter object can be initialized as such (variable names 
        are customizable, but conventional names are used below):

		-Sandbox = MLDB_sample_enter('sandbox')
		-Production = MLDB_sample_enter('production')

	Initialization of the MLDB_sampler_enter object:
		-initializes a dataframe of the imaged samples board via the isb() function 
		 and saves it in an instance variable called self.isbdf.
			-for automatic authentication, the __init__ function will read a text 
			 file saved at \GUI_Branch\Database_Related_GUI_Branch\auth.txt
			-you will have to make this file yourself if you are cloning from 
			 github since the file is on the gitignore list
			-to swap the credentials used for authentication simply switch 
			 them out in the text file
			-username as the top line
			-password as the second line
		-saves the parent directory of the folder containing the required graphql queries 
		 and mutations in the instance variable named self.folderpath
		-initializes the url of sample manager api for the chosen graphql instance 
		 in the instance variable named self.sampleapi
		-saves the name of the folder containing the required graphql query and mutation 
		 jsons in the instance variable named self.GQLDir
		-saves the keys used to access required values of certain graphql mutation 
		 response jsons:
			-self.make_strain_id_source
        		-self.make_virus_id_source
        		-self.make_fluor_id_source
        		-self.createSample_source

	-------
	Methods:
	-------


	get_animalID(sample):
		-Retrieves animal ID from imaged samples board for any sample entered as an 
		 argument.
	
	get_tag(sample):
		-Retrieves tag from imaged samples board for any sample entered as an argument.
    		-Is called by the get_injection_viruses() method because it requires similar 
		 operations.

	---


	get_strain(sample):
		-Retrieves the name of mouse strain from the imaged samples board for any sample
		 entered as an argument.

	strain_ids():
		-Compiles the strain ids that have already been defined in the Neuron Broswer 
		 database into a dictionary with the names of the strains as keys.
	
	make_strain_id(mousstrainname):
		-Returns the id of the mouse strain name entered as an argument. Conventionally
		 takes the return of get_strain as an argument. Parses through the return of 
		 strain_ids and returns the id if the strain argument exists as a key in 
		 strain_ids. Otherwise, will send a mutation to the graphql api to create 
		 a new strain/id pair in the Neuron Browser databse and return the newly 
		 made id.

	---


	get_injection_viruses(sample):
		-Retrieves names of the injection viruses from the imaged samples board for 
		 any sample entered as an argument.
	
	virus_ids():
		-Compiles the injection virus ids that have already been defined in the 
		 Neuron Broswer database into a dictionary with the names of the injection 
		 viruses as keys.

	make_virus_id(sample):
		 -Returns an id for the list of injection viruses associated with a sample 
		  entered as an argument. Calls get_injection_viruses within the method to 
		  find the injection virus names. 
		  Parses through the return dictionary of virus_ids and returns the id if 
		  the virus list exists as a key. Otherwise, will send a mutation to the 
		  graphql api to create a new virus list/id pair in the Neuron Browser 
		  databse and return the newly made id.

	---


	get_fluors(sample):
		-Retrieves names of the injection flurophores from the imaged samples board for 
		 any sample entered as an argument.

	fluor_ids():
		-Compiles the injection fluorophore ids that have already been defined in the 
		 Neuron Broswer database into a dictionary with the names of the injection 
		 fluorophores as keys.

	make_fluor_id(sample):
		 -Returns an id for the list of injection flurophores associated with a sample
		  entered as an argument. Calls get_fluors within the method to find the 
		  injection fluorophore names. Parses through the return dictionary of 
		  fluor_ids and returns the id if the fluorophore list exists as a key. 
		  Otherwise, will send a mutation to the graphql api to create a new
		  fluorophore list/id pair in the neuron browser databse and return 
		  the newly made id.

	---


	get_injection_area(sample)
		-Retrieves names of the injection brain areas from the imaged samples board 
		 for any sample entered as an argument.
		-Retro orbital injections return as 'Whole brain' by default.

	brainarea_ids()
		-Compiles the injection area ids that have already been defined in the 
		 database into a dictionary with the names of the injection areas as keys.
		-These correspond to all brain areas defined in the Allen Mouse Brain 
		 Atlas ontology, therefore, no new ones ever need to be added to the database.

	make_injectionarea_ids(sample):
		-Will call the get_injection_area and brainarea_ids methods within the method 
		 to produce the injection area names and a dictionary of brainarea/id key/value
		 pairs.
		-Will return a list of ids for each brain area associted with the sample 
		 entered as an argument.
		-However, currently the method is only designed to run within the 
		 make_injection method (discussed below) if there is only one injection area. 
		-Since most samples now take retro-orbital injections, this method 
		 typically just returns the id for 'Whole brain'.


 	---


	make_injection(sample, id):
		-Is run as part of the post_sample method (discussed further below).
		-Will enter the injection details retrieved from make_virus_id, make_fluro_id, 
		 and make_injectionarea_ids into the sample entry in the Neuron Browser sample
		 manager database via a graphql mutation.
		-Takes the sample name and its database id as an argument. The sample 
		 database id is generated when the sample entry is made to the 
		 database via post_sample.

	---


	get_transform_name(sample):
		-Returns the transform file name for the sample entered as an argument.

	get_transform_path(sample):
		-Returns the tranform file path for the sample entered as an argument.


	---


	make_registration(sample, id):
		-Is run as part of the post_sample method (discussed below).
		-Will call the get_transform_name and get_transform_path methods to enter the 
		 registration details for the sample entry in the Neuron Browser sample 
		 manager database via a graphql mutation.
		-Takes the sample name and its database id as an argument. The sample 
		 database id is generated when the sample entry is made to the 
		 database via post_sample.

	---


	post_sample(sample):
		-Will post all available sample data to the Neruon Browser sample manager 
		 database via a graphql mutation.
		-The post_sample method retrieves all data to be posted via the above 
		 defined methods.
		-The graph below illustrates the call structure from within the 
		 post_sample method:
			-Each branch points to a call made by the upstream method.
		

                                            post_sample
					         |
		               	                 |
                         ________________________|________________________
                        /  |             |              |                 \
                       /   |             |              |                  \
                      /    |             |              |                   \
                     /     |             |              |                    \
                    /      |             |              |                     \
                   /       |             |              |              make_registration
      get_animal_id     get_tag    make_strain_id       |                 /         \
	                              /    \            |    get_transform_name   get_transform_path
	                      get_strain   strain_ids   |                                 |
			                                |                                 |
			     		                |                              get_tag
	                                                |
					                |
						        |
						        |
                                                  make_injection                                      
                                                 /       |      \                                                                                        
                                                /        |       \                                      
                          make_injectionarea_ids  make_fluor_id   make_virus_id           
                           /    \                        ^                /    \
                          /      \                      / \              /      \
        get_injection_area   brainarea_ids     get_fluors  fluor_ids  virus_ids  get_injection_viruses

 2.27
-MLDB_neuron_enter: This module contains the code for two separate but related services. The first is the
------------------- class Neuronposter, which is used to automatically enter the data of neurons into 
                    the Neuron Broswer sample manager database. The other is the class SWCUploader, which
                    helps the user upload the swc files associated with the entered neurons into the 
                    Neuron Browser Database. 
    2.271
    Neuronposter:

	Initialization of the object takes two argumensts, a string representing the name of the sample 
        the user wants to parse and a string representing the GraphQL instance the the user is accessing.
	An Neuronbroswer object can be initialized as such (variable names are customizable, but 
	conventional names are used below):

		-sandbox_poster = MLDB_sample_enter('2020-11-26', 'sandbox')
		-production_poster = MLDB_sample_enter('2020-11-26', 'production')
	
	Initialization of the Neuronposter object:
		-saves the parent directory of the folder containing the required graphql 
		 queries and mutations in the instance variable named self.folderpath
		-initializes the url of sample manager api for the chosen graphql instance 
		 in the instance variable named self.sampleapi
		-saves the name of the folder containing the required graphql query and 
		 mutation jsons in the instance variable named self.GQLDir
		-saves the name of the sample entered as an argument in the instance variable 
		 named self.sample
		-saves an instance of the anw object in the instance variable 
		 named self.parser
		-sets the active sheet for the anw object via self.parser.set_activesheet()
		-saves the output of functions that would be called multiple times for 
		 iterative neuron posts into class variables to prevent multiple calls
			these include:
				-self.brainarea_ids = self.brainarea_ids()
				-self.sampledata = self.sampledata()
			these methods are discussed further below


	-------
	Methods:
	-------


	brainarea_ids():
		-Compiles the injection area ids that have already been defined in the database 
		 into a dictionary with the names of the injection areas as keys.
		-These correspond to all brain areas defined in the Allen Mouse Brain Atlas 
		 ontology, therefore, no new ones ever need to be added to the database.
		-This method is equivalent to brainarea_ids() in MLDB_sample_enter.
		-For the purpose of posting neurons, the database id for the brain area 
		 is needed to represent the neuron's soma compartment.
		-Therefore, the brainarea_ids dictionary is indexed with the return 
		 of the locator function for the particular neuron.
			ie:	self.brainarea_ids[locator(sample, tag)]
	
	sampledata(*samplestr):
		-Saves all sample database IDs and injection database IDs currently in the 
		 Neuron Browser database into a dictionary with the sample names as keys.
		-These IDs are needed later to make the graphql mutation necessary to 
		 post a neuron to the database.
		-The 'samplestr' optional argument can be passed to return the 
		 values of the specific sample.

	***Since the above methods just return static dictionaries, it is unecessary to run 
	them multiple times when posting multiple neurons, therefore the output of these 
	methods is saved as instance variables.

	coordinateRetriever(tag):
		-Returns the coordinates of the neuron tag passed as an argument as a
		 dictionary with keys 'x', 'y', 'z' for each individual coordinate. 

	idnum():
		-Queries the Neruon Broswer sample manager database to find the latest 
		 'AA####' ID posted to the database and returns the NUMBER portion of 
		  the next ID (cast as string) to be posted.
			-ie: The latest id in the database is AA0000, idnum will 
			 return 0001 and so on.
	
	post_neuron(tag):
		-Posts the data for the neuron tag passed as an argument to the Neruon 
		 Browser sample manager database.
		-Does this by posting the data retrieved from the above methods with a 
		 graphql mutation to the database.
		-Call structure is much more simple than post_sample. Only coordinateRetriever 
		 and idnum need to be called. For brainarea_ids and sampledata, their 
		 corresponding saved dictionaries are indexed.

	post_ALL_neurons():
		-Loops over each tag returned from the anw consensuscomplete method for the 
		 sample and calls post_neuron with the tag as an argument.
		-Essentially, it just posts all the neurons in the sample to the Neuron 
		 Browser sample manager database. 
		-This method is the main reason why brainarea_ids and sampledata outputs are 
		 cached as an instance variables. Without caching, this method runs many 
		 times slower.

    2.272
    SWCUploader:

	Just like the Neuronposter class,  SWCUploader also takes same two arguments, a string 
	representing the name of the sample the user wants to parse and a string representing 
	the GraphQL instance the the user is accessing. An SWCUploader object can be initialized 
	as such (variable names are customizable, but conventional names are used below):
		-sandbox_uploader = SWCUploader('2020-11-26', 'sandbox')
		-production_uploader = SWCUploader('2020-11-26', 'production')

	Initialization of the SWCUploader object:
		-saves the parent directory of the folder containing the required graphql 
		 queries and mutations in the instance variable named self.folderpath
		-initializes the urls of the two apis that are utilized for the upload mutation
		 for the chosen graphql instance and saves them into instance variables:
			-self.sampleapi
			-self.tracingapi
		-saves the name of the folder containing the required graphql query and 
		 mutation jsons in the instance variable named self.GQLDir
		-saves the name of the sample entered as an argument in the instance variable 
		 named self.sample
		-saves an instance of the anw object in the instance variable named self.parser
		-sets the active sheet for the anw object via self.parser.set_activesheet()
		-creates a lookup dictionary called self.tracedby which contains the first 
		 names of the annotators who traced each complete neuron in the initialized
		 sample. Keys are the sample_tag strings of each complete neuron in the sample
 		 and values are strings containing the names of each tracer. The dictionary 
		 is populated in the class' __init__ function. 
		-initializes the a lookup dictionary called self.neuronids which has the
		 database neuron container ids (the placeholders that are posted with the
		 Neuronposter class). Keys are the sample_tag strings of each neuron container
		 available in the database and values are strings of thier database ids. The
		 dictionary is populated via a method called self.compile_neuron_ids() which 
		 called within the class' __init__ function. 
		-creates a lookup dictionary called self.structure_ids which contains the
		 database ids used to denote tracing structures (axons vs dendrites). The 
		 keys are "axon" and "dendrite" and the values are their corresponding
		 database ids. The dictionary is populated via the return of a graphql query
		 made in the class' __init__ function. 

	-------
	Methods:
	-------
	
	extract_neuron_id(array):
		-Extracts the database id of a single neuron container from the the response
		 json of the relevant database graphql query. Each response object from
		 a database graphql query typically takes the structure: 
		 {"data":{"neurons":{"items":{Further nested relevant data}}}. The array 
		 argument must be the nested json value at the "items" key cast as a np.array.
		 After the id is extracted it is stored as a value in the self.neuronid lookup
		 dictionary with its corresponding sample_tag string as a key.

	compile_neuron_ids():
		-Iterates through all the jsons values nested in the "items" key of the graphql
		 response jsons and calls extract_neuron_id() for each one. 

	get_neuronFiles(tag):
		-Returns a lookup dictionary with the axon and dendrite swc binaries associated with
		 the self.sample attibute and tag argument as values. Keys are "axon" for the axon swc
		 and "dendrite" for the dendrite swc. 

	uploadNeuron(tag):
		-Uploads a neuron's axon and dendrite swcs to the associated neuron container in the 
		 database. Utilizes the gql library to send the upload mutation rather than the 
		 requests library as usual. An example mutation using this library is documented
		 here: https://gql.readthedocs.io/en/v3.0.0a6/usage/file_upload.html. Swc files 
		 are uploaded to the neuron container which is associated with the self.sample 
		 attribute and tag argument. 

	uploadALLNeurons():
		-Runs the uploadNeuron() method for each neuron returned by anw.consensuscompleteList


 2.28
-mk_result_dir: Yet another module that contains just one fuction. This function is used to 
--------------- quickly make a result folder during sample registration. 


	copyto_results(dir):
		-Moves and renames the transform file of each pass done for a registration 
		 to a folder named 'result'.
		-This operation is needed as a step in the wider protocol for sample 
		 registration. 


                                                  3
                                          GUI Documentation:
_________________________________________________________________________________________________________
The GUI for MLDAMS is written using the tkinter library and has the same dependencies that are mentioned
in the backend module documentation.

3.1
Overview:
---------
The GUI consists of 8 modules, all of which are in the GUI_Menu_Related folder. Here is a 
quick overview of the modules:

	-main.py: The controller module for the rest of the modules. Handles starting all 
	 the other modules in the app. Also handles starting and joining extra processes. 
	 Currently, no extra processes are started in the app but the capability to start 
	 extra processes is there.

	-startpage.py: Handles the start menu for the app.

	-anwgui.py: Handles the Neuron Worksheet Report Generator service, which utilizes 
	 the anw.py backend module.

	-locatorgui.py: Handles the Soma Brain Area Locator service, which utilizes the 
	 somalocator.py backend module.

	-resultmkrgui.py: Handles the Registration Result Folder Maker service, which 
	 utilizes the mk_result_dir.py backend module. 

	-mungui.py: Handles the Unfinished Neuron Mover service which utlizes the 
	 move_unf_neurons.py backend module.

	-curationgui.py: Handles two separate services in the app, both of which are 
	 involved in the curation process of the annotator pipeline. The first service is 
	 Temporary Curation Folder Maker, which utilizes the mk_temp_curation.py backend 
	 module. The second service is the Curation Helper, which helps the user document 
	 the curation process and calls the MLCuration.m script to create the final tracing 
	 files to be uploaded to the Neuron Browser. 

	-databaseentrygui.py: Handles the Database Sample & Neuron Entry services which 
	 utilizes the MLDB_neuron_enter.py and MLDB_sample_enter.py backend modules. 

To get a better idea of how I organized the GUI code, refer to the top answer on this stackoverflow 
thread: https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
                                         
					         3.2
                          :::::::::::::::Modules, in depth::::::::::::::
		   
3.21		   
main: This module consists of the controller class for the app, MLDAMS, which inherits
----- the Tk class to create the main app window when the MLDAMS class is called. Upon calling
      the class, the base app window configurations are defined. This includes creating a 
      template frame which will be taken as an argument for all other services that are 
      initialized. The template frame is saved as an instance variable called self.mainframe. 
      Then, the show_frame method (detailed in the methods section) is called on the StartPage 
      class to raise the main page of the app. 


	-------
	Methods:
	-------
	
	show_frame(cont, *args, **kwargs):
		-Takes classes for other services (which inherit the Frame class from tkinter)
		 in the app as the 'cont' argument.
		-Service classes are initialized and a new frame for the service is raised, 
		 the service class is saved as an instance variabe called self.frame.
		-self.frame is then added to the grid via self.frame.grid()
		-If another service classe has already been initialized when show_frame is 
		 called for another service class, self.frame.destroy() is called on the 
		 service class that has already been initialized. The newly initialzed 
		 service class' frame will then be raised.
		-When a new service class is initialized, it takes self.mainframe, self, *args
		 and **kwargs as arguments.
			-self.mainframe is the template frame for each service. In a service
			 class, this argument is named 'parent'.
			-self is the main class object itself, which allows the main object's
			 methods to be called from other service modules. In a service
			 class, this argument is named 'controller'.
			 
	startproc(proc): 
		-This method allows for the initialization of multiprocessing processes.
	
	joinproc(proc):
		-This method allows for the joining of multiprocessing processes. 
		 		 
3.22
startpage: This module contains the code for the start menu page of the app. The start menu
---------- is a class by the name of StartPage, which inherits the Frame class from tkinter. 
           The StartPage class takes two arguments when it is initialialized that are common
	   for each service class. These include parent and controller. The parent argument
	   refers to the self.mainframe attribute from the main MLDAMS class and the controller
	   argument refers to the self attribut from the main MLDAMS class. 
	   
	   The key items this class defines are the topmenu and the buttons that lead to each
	   of the services in the app. These buttons call controller.show_frame(cont) on their
	   respective services.
	   
	   No methods are defined in this class. 
	   
3.23
awngui: This module contains the code for the Neuron Worksheet Report Generator service. The
------- The service is defined in a class called ANWparser_GUI which inherits the Frame class 
        from tkinter. The ANWparser_GUI class takes parent and controller as arguments, which
	are described above. 
	
	The main elements defined in this service are two dropdown menus, a textbox and a 
	button to return to the main menu. The top dropdown menu allows the user to select
	a sample to parse. The second dropdown menu allows the user to select a report to 
	generate. The generated reports will be echoed to the textbox where the user can
	copy the contents if they wish.
	
	-------
	Methods:
	-------
	
	selectsample(event):
		-Runs anw's set_activesheet method behind the scenes for a sample selected
		 from the dropdown menu. Closes the openpyxl object right after the sample
		 is selected. Echoes a label to the GUI indicating that the sample has been
		 selected. The event argument is a mouseclick event to a sample in the 
		 samples dropdown menu.
		 
	generate(event):
		-Generates a report based on the user selection and echoes it to the textbox.
		 The event argument is a mouseclick event to a report in the report dropdown 
		 menu.
	
	anwExit():
		-Returns the user to the main menu and simultaneously closes the openpyxl object
		 in case it wasn't closed. 
		
3.24	
locatorgui: This module contains the code for the Soma Brain Area Locator service. The service
----------- is defined in a class called Locator_GUI which inherits the Frame class from tkinter.
            The Locator_GUI class takes parent and controller as arguments, which are described
	    above.
	    
	    The main elements defined in this service are two dropdown menus, a button, a checkbox,
	    a textbox, and an exit button. The first dropdown menu allows the user to select a 
	    sample. The second dropdown menu allows the user to select a neuron tag from the 
	    selected sample. The button allows the user to give the soma location(s) for what is 
	    selected. The checkbox allows the user to return the soma locations as a list rather 
	    than a table. The textbox is where all the locations are echoed.
	    
	-------
	Methods:
	-------	
	
	unlock_tagdropdown(event):
		-Feeds the neuron tag dropdown menu with the available neurons in a sample once a 
		 sample is selected from the upper dropdown menu. The event argument is a 
		 mouseclick event to a sample in the samples dropdown menu.
	
	returnloc():
		-Echoes the soma location(s) for the selected items to the textbox.

3.25
displayrangegui: This module contains the code for the Registration Display Settings Record service.
---------------- The service is defined in a class called displayRangeTree which inherits the Frame
                 class from tkinter. The displayRangeTree class takes parent and controller as 
                 arguments, which are described above. 

                 The main elements defined in this service are a treeview widget which contains the
                 display range record, three entry boxes to enter the sample name, display minimum,
                 and display maximum respectively, a button to add a new row, a button to update a
                 selected row, a button to delete a selected row, and a button to return to main
                 menu. When the class is initialized, the values from the display settings json file
		 at "\\dm11\mousebrainmicro\registration\Database\displaySettings.json" is loaded into
		 the treeview. Display range values are copyable from the treeview view a left mouse 
		 button click. When a user clicks a display range value, a small Toplevel window appears
                 next to the value for one second with the message "copied". 

	-------
	Methods:
	-------	
	
	add_row():
		-Adds a new row to the display settings record treeview. Also adds a a new dictionary
		 to the "Samples" list that is in displaySettings.json and saves it. 

	update_row():
		-Updates the currently selected row in the display settings record treeview. Also
		 updates the corresponding dictionary in the "Samples" list within the 
		 displaySettings.json and saves it.

	delete_row():
		-Deletes the currently selected row in the display settings record treeview. Also
		 delets the corresponding dictionary in the "Samples" list within the
		 displaySettings.json and saves it.
	
	get_clicked_index(event):
		-Gets the row index of the selected row in the display settings record treeview. The
		 event argument is a mouseclick event. Passes the argument to the copier() method.

	copier(event):
		-If a display range value is clicked with the left mouse button, this method copies 
		 the value to the user's clipboard. The event argument is the same mouseclick that
		 is passed as an argument in get_clicked_index.	
	
	
                 		
3.26		
resultmkrgui: This module contains the code for the Registration Result Folder Maker service. The
------------- service is defined in a class called RegResultDir_GUI which inherits the Frame class
              from tkinter. The RegResultDir_GUI class takes parent and controller as arguments, 
	      which are described above. 
	      
	      The main elements defined in this service are two buttons, a textbox, and an exit
	      button. The first button opens a file dialogue box within the registration folder
	      for the user to select a registration sample folder. The second button allows the
	      user to create a result directory for the selected registration sample. Messages are
	      echoed to the textbox regarding the status of the result folder making process. 

	-------
	Methods:
	-------	
	
	FileDialog():
		-Opens a file dialogue box in the registration folder directory.
		
	make():
		-Calls the copyto_results function from the mk_result_dir.py module to create 
		 the result folder for the selected registration sample path.
		 


3.27
curationgui: This module contains the code for two separate but related services. The first service is 
------------ the Temporary Curation Folder Maker, which is defined in a class called Curation_GUI and 
             inherits the Frame class from tkinter. The other service is the Curation Helper, which 
             is defined in a class called Somacuration_GUI and also inherits the Frame class from 
             tkinter. 
    
    3.271
    Curation_GUI:
	
	The main elements defined in this service are the 'Select sample directory button', the 
	'Make temporary curation folder' button, the 'Show missing files button', two textboxes, 
	and an exit button. The 'Select sample directory' button opens a file dialogue in the 
	Finished Neurons folder and allows the user to select a sample folder in which to create
	a temporary curation folder. The 'Make temporary curation folder' button calls the 
	copyto_Temp_Curation function from the mk_temp_curation.py module to create a temporary 
	curation folder within the selected sample folder. Status updates regarding this process 
	are echoed to the textbox beneath the 'Make temporary curation folder button. The 'Show 
	missing files' button echoes a report of whatever files are missing within the sample 
	folder to the textbox beneath it.
		
	
	-------
	Methods:
	-------	
	
	FileDialoge():
		-Opens a file dialogue box within the Finished Neurons Folder.
	
	make():
		-Calls the copyto_Temp_Curation function to create the temporary curation folder.
		
	ShowMissing():
		-Echoes the missing files to the second textbox.
    
    3.272
    Somacuration_GUI:

   	
	This service is more complex than the ones previously defined so far in the GUI 
	documentation. Therefore, I will list each element defined in this service as a bullet 
        point before listing and describing the meothds. An in depth instruction on usage can 
        be found in the User Instructions Microsoft Word document. The main elements defined in 
        this service are:

	    -Sample selection dropdown menu, which populates the Completed Neurons listbox 
             column on sample selection.
	     
	    -The queue all and unqueue all buttons, which handle bulk moving tags to and from 
             each listbox column.
	     
	    -The 'Completed neurons' listbox column, which is populated on sample selection. 
	    
	    -The 'Queued for review' listbox column, which is populated on tag selection from 
             the Completed Neurons column. Clicking a neuron tag in this column will also return 
             it to the 'Completed neurons' column. 
	     
	    -The review table (a tkinter treeview widget), which contains data entered by the 
             user during the Curation process.
	     
	    -The 'Create final tracing files' button, which runs the MLCuration.m script when 
	     clicked for all neurons in the 'Queued for review' column.
	     
	    -The root review checkboxes, which help the user track the root review steps.
	    
	    -The 'Update selected' button, which updates a single review table row.
	    
	    -The 'Clear selected' button, which clears a single review table row.
	    
	    -The 'Save and export selected' button, which saves the entry for a single review 
	     table row.
	     
	    -The 'Compartment from mesh' entrybox, which takes any text entry.
  
	    -The 'Compartment from manual review' entrybox, which takes any text entry.
	    
	    -The 'Final Decision' entrybox, which only takes valid text entries from the popup 
	     menu that appears when the user starts typing in the entrybox.
	     
	    -The 'Final Decision' search and complete popup menu which appears when the user
	     starts typing in the 'Final Decision' entrybox.
	    
	    -The 'Additional comments' entrybox, which takes any text entry.
	    
	    -The 'Save and export all' button, which saves an exports all data in the review 
             table to an external dataframe.
	     
	    -The 'Clear all data in review' button, which clears all rows in the review table.
	     However, if the MLCuration.m script has been run and the 'Compartment from script'
	     column is populated, it will not be cleared. 
	    
	    -A warning popup window if user attempts to curate previously curated neurons.
	    
	    -A warning popup window if user attempts to enter an invalid 'Final Decision' entry.
	    
	    -A popup window that shows a loading bar when the MLCuration.m script is running.
	    
	-------
	Methods:
	-------
	  
	insertcomplete(event):
		-Inserts tags from a selected sample from the dropdown menu into the 'Completed
		 Neurons' listbox column. The event argument is a mouseclick event on a sample
		 from the dropdown menu.
		 	
	get_reviewTree_index(text):
		-Retrieves the index integer for a neruon tag present in the review table.
		 The text argument is the tag string of the neuron whose index is to be 
		 retrieved.
	
	makeTree_fromSaved(nstring, selection):
		-Enters data into the review table from the external dataframe containing
		 previously saved data. The nstring argument is the full sample_tag string
		 of the neuron to be entered. The selection argument is only the tag string
		 of the neuron to be entered.
		 
	OnCSelect(event): 
		-Transfers a neuron tag from the 'Completed Neurons' listbox column to the 
		 'Queued for review' listbox column. For any tag selected from the 'Completed
		 Neurons' column, its place in the column will be preserved and appear as a
		 blank space after selection. If a tag is unqued it will return to its place 
		 in the 'Completed Neurons' column. This way, the order of the neurons is always 
		 maintained in the 'Completed Neurons' column. The event argument can either be 
		 a mouseclick event or a tuple consisting of a tag and its index number from 
		 consensuscomplete_List (retrieved via the anw class).

	OnSSelect(event):
		-Transfers a neuron tag from the 'Queued for Review' listbox column back to the
		 'Completed Neurons' listbox column. The event argument can either be a 
                 mouseclick event or a neuron tag string.
		 
	insertall(completelist):
		-Runs the OnCSelect method for every neuron tag present in the 'Conmpleted 
                 Neurons' listbox column. The completelist argument is a list of neurons present 
                 in the listbox.
	
	uninsertall(selectedlist):
		-Runs the OnSSelect method for every neuron tag present in the 'Queued for 
                 Review' listbox column. The selectedlist argument is a list of neurons present 
                 in the listbox.
	
	createEntryFrame(event):
		-Creates a frame for the data entry widgets for a selected neuron tag. If the 
                 entry frame for a selected neuron tag already exists, the frame is raised 
                 instead. The event argument can either be a mouseclick event or a neuron tag 
                 string. 

	RRupdate(instance):
		-Updates the user entries from the entry frame widgets into the review table. 
		 Instance argument is the sample_tag combo string for the neuron that is being 
		 entered. 
	
	RRClear(instance):
		-Clears the existing entries (except 'Compartment from Script') for the selected 
		 neuron in the review table. Instance argument is the sample_tag combo string for
		 the neuron that is being cleared.
	
	cleartree():
		-Runs the RRClear method for every neuron tag that has data entered in the review
		 table. 
	 	 	 
	save_to_df(*args):
		-Saves all user entered data for the currently selected neuron to an external 
		 dataframe. This method is called with the optional *args when the MLCuration.m 
		 script is run via the ML_DL_Tfunc method (described further below). The 
                 optional arguments are the soma compartmnet string output by the MLCuration.m 
                 script and the sample_tag combo string of the neuron being processed. This 
                 method will trigger one of three different save condtions:
		 	1) If a neuron has been previously saved and has not been modified in 
                           the current user session, no changes are made to the dataframe.
			2) If a neuron has been previously saved and was modified in the current 
			   user session, all modified entries will take the place of thier 
                           respective entries in the dataframe and all unmodified entries will 
                           remain unchanged.
			3) If a neuron is newly added before or during the running of the 
                           MLCuration.m script, a new series for the neuron will be appended 
                           to the dataframe.
	
	exportFinalDecision(treeindex, tagonly, savename):
		-Exports the user entry in the 'Final Decision' entrybox to the soma.txt file
		 generated by the MLCuration.m script if the Final Decision entry does not 
		 match the output of the script. This addtion to the soma.txt file will be
		 appenended as a new line consisting of 'Curated compartment: brain area'. 
		 If the user decides to delete the Final Decision entry or switch to an
		 entry that matches the output of MLCuration.m, the 'Curated compartment'
		 line will be removed. The treeindex argument is the index number of the 
		 selected neuron from the review table, the tagonly argument is the tag
		 string of the selected neuron, and the savename argument is the sample_tag
		 combo string of the selected neuron.
		 
	save_all_qd():
		-Runs the save_to_df method for every neuron present in the 'Queued for Review'
		 listbox column. 
	
	ML_DL_Tfunc(sample, includelist):
		-Calls and runs the MLCuration.m script via the MATLAB enginge. After the script
		 is finished running, the locator function from the somalocator module is run
		 with the reload=True argument to retrieve the soma location output of the
		 MLCuration.m script. The retrieved outputs are then entered into the review 
                 table and all neurons in the 'Queued for reivew' column are saved via the 
                 save_to_df method. The sample argument is the string of the currently selected 
                 sample, and the includelist is a list of the tags in the 'Queued for review' 
                 column. These are the main arguments that go into the MLCuration.m script. 
	
	runner(sample, includelist):
		-Runs a loading popup window while the MLCuration.m script is running. The method
		 does this by running a ttk.Progressbar and the ML_DL_Tfunc method in separate
		 threads. The sample argument is the string of the currently selected sample, and
		 the includelist is a list of the tags in the 'Queued for review' column. These 
		 arguments are fed into the ML_DL_Tfunc method which is called within the runner
		 method. 
			 
	runML():
		-This method initializes the MATLAB engine and calls the runner method. If the 
                 user attempts to run the MLCuration.m script on neurons that have already been 
                 run through the script, this method will also generate a popup window warning. 
                 If the user confirms to run the script by clicking 'Yes' on the popup window, 
                 the runner method will proceed to run. 
		 
	raiseNBMenu(event):
		-This method raises a popup menu with valid entries for the 'Final Decision' 
		 entrybox when the user starts typing in the entrybox. The number of entries
		 is narrowed down to match whatever the user is typing. The event argument is
		 a KeyRelease event.
	 
	popFinal(event):
		-Popuplates the 'Final Decision' entrybox when the user selects an entry from 
                 the popup menu. The event argument is a mouseclick event to an entry in the 
                 popup menu. 
	
	NBmenu_offclick(event):
		-Retracts the popup menu if the user clicks off the menu. The event argument is 
                 a mouseclick event to anywhere on the GUI.
	
	invalidDataWarning():
		-Shows a warning popup window if the user attempts to bypass selecting an entry 
                 from the popup window and tries to enter a custom entry.

	runRaiser(event):
		-Deiconifies the loading bar window on main window focus and click. Event 
                 argument can be either a '<Button-1>' event or a '<FocusIn>' event.

3.28
databaseentrygui: This module contains the code for the Database Sample & Neuron Entry service. 
----------------- Just like the curationgui module, this module also contains two classes. The 
                  first class defined in this module is DBSelect_GUI, which inherits the Frame 
                  class from tkinter. This class creates a frame for the user to select which 
                  database they want to make entries to. The second class is called Entry_GUI 
                  and also inherits the Frame class from tkinter. This class creates a frame for 
                  the actual data entry portion of the service.
		  
    3.281
    DBSelected_GUI:
 	
	The main elements defined in this class are two buttons for database selection and an exit
	button. On the left is the button to run Sandbox database entry and on the right is the 
        button to run Production database entry. This is done by passing the url for the GraphQL 
        instance of the selected database to the Entry_GUI class.
	
	No methods are defined in this class.
    
    3.282
    Entry_GUI:
         
	The main elements defined in this class are a dropdown menu for sample selection, a 
        button for sample data entry, a dropdown menu for neuron tag selection, a button for 
        single neuron data entry, a button to enter data for all the neurons in a selected sample, 
	a button to upload the files for a single neuron, a button to upload the files for all neurons,
        a textbox, a button to return to database selection, and an exit button. Status updates 
        on the data entry process are echoed to the textbox when the user selects any of the data 
        entry options. 

	-------
	Methods:
	-------

	unlock_neurondropdown(event):
		-Populates the neuron tag dropdown menu with the completed neurons from the 
                 sample selected via the sampledropdown menu. The event argument is a mouseclick 
                 event to a sample from the dropdown menu.
		 
	enterSamp():
		-Initializes the MLDB_sample_enter class for the selected database GraphQL 
                 instance and calls the post_sample method for the selected sample. Enters the 
                 relevant data from the Imaged Samples Board to the Neruon Browser Sample Manager 
                 Database.
	
	enterNeruon():
		-Initializes the Neruonpower class for the selected database GraphQL instance and 
                 the selected sample from the dropdown menu. Calls the post_neuron method for the 
                 selected neuron. Enters the relevant data for the neuron to the Neruon Browser 
                 Sample Manager Database.
	
	enterAllNeurons():
		-Initializes the Neruonpower class for the selected database GraphQL instance and 
                 the selected sample from the dropdown menu. Calls the post_ALL_neurons method for
		 all the completed neurons in the selected sample. Enters the relevant data for 
                 all complete neurons to the Neruon Browser Sample Manager Database.

	upload_caller(uploadAll):
		-Initializes the SWCUploader class and calls the uploadNeuron or uploadAllNeurons
		 methods depending on the boolean value of the uploadAll arguemnt. 

	upload_controller(uploadAll=False):
		-Calls the upload_caller method within a new thread if all the required dropdown 
		 menu options are selected in the GUI. Generates the loading screen which shows 
		 during the upload.

	runRaiser(event):
		-Deiconifies the loading bar window on main window focus and click. Event 
                 argument can be either a '<Button-1>' event or a '<FocusIn>' event.

3.29		 
mungui: This module contains the code for the Unfinished Neuron Mover service. The service is defined
------- in a class called MUN_GUI which inherits the Frame class from tkinter. The MUN_GUI class
	takes parent and controller as arguments, which are described above.
	
	The main elements defined in this service are a dropdown menu, a button, a textbox, and an
	exit button. The dropdown menu allows the user to select a sample from the Active Neuron
	Worksheet and queue it for moving. The button below the dropdown menu allows the user to
	move all of the unfinished neurons from that sample to the Unfinished Neurons directory.
	Messages are echoed to the textbox regarding the status of the moving process. 

	-------
	Methods:
	-------	
	
	move_now():
		-Calls the copyto_unf function from the move_unf_neurons.py module to move the
		 unfinished neurons from the selected sample.
	
	MUNguiexit():
		-Returns the user to the main menu and closes the openpyxl object for the
		 Active Neuron Worksheet if it hasn't already been closed.