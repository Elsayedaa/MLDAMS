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
3) GUI Documentation (in progress)
                                                                        
                                             1 
                                           About:
_______________________________________________________________________________________________
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

*Note, this file does not contain documentation for the GUI menu modules.

                                               2
                                  Backend Module Documentation:
_______________________________________________________________________________________________

                                              2.1
                           ::::::::::::::Dependencies::::::::::::::



The MLDAMS is written completely in Python 3 and as such, a working installation of Python 3 
(Anaconda recommended) is needed to start the GUI app.

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

The MLDAMS also relies on several 3rd party Python libraries, most of which are included in 
a default installation of Anaconda. These libraries include:
-openpyxl
-pandas
-numpy
-requests
-Pillow (not included by default in Anaconda)
-html_table_parser (not inluded by default in Anaconda)
-selenium (not included by default in Anaconda)
	-Google Chrome webdriver corresponding to the user's current version of Chrome is 
	 also needed
	-webdriver path variable is defined in the Isb module, line 13
	-the default path is: 
	 "\\dm11\mousebrainmicro\Google Chrome Webdriver\chromedriver.exe"

The MLDAMS also utilizes standard libraries including:
-datetime
-re
-os
-os.path
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

	isb(username, password): 
		-The isb function takes the username and password of the user's HHMI account to 
		 as arguments to access the wiki automatically via the chrome webdriver and 
		 selenium library.

 2.26
-MLDB_sample_enter: This module contains the class MLDB_sample_enter, which is used to 
------------------- automatically enter the data of samples into the Neuron Broswer 
                    sample manager database.

	Initialization of the object takes one argument, the url of the GraphQL instance for 
	Neuron Browser sample manager database. An MLDB_sample_enter object can be initialized 
	as such (variable names are customizable, but conventional names are used below):
		-Sandbox = MLDB_sample_enter('http://localhost:9671/graphql')
		-Production = MLDB_sample_enter('http://mouselight.int.janelia.org:9671/graphql')

	Initialization of the MLDB_sampler_enter object:
		-initializes a dataframe of the imaged samples board via the isb() function 
		 and saves it in an instance variable called self.isbdf.
			-for authentication, the initialization function will read a text 
			 file saved at \GUI_Branch\Database_Related_GUI_Branch\auth.txt
			-you will have to make this file yourself if you are cloning from 
			 github since the file is on the gitignore list
			-to swap the credentials used for authentication simply switch 
			 them out in the text file
			-username as the top line
			-password as the second line
		-saves the parent directory of the folder containing the required graphql queries 
		 and mutations in the instance variable named self.folderpath
		-saves the url of the graphql instance in the instance variable named 
		 self.GQLInstance
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
                  _________________________|________________________
                 /   |             |              |                 \
                /    |             |              |                  \
               /     |             |              |                   \
              /      |             |              |                    \
             /       |             |              |                     \
            /        |             |              |              make_registration
get_animal_id     get_tag    make_strain_id       |                      ^
	                           ^              |                     / \
				 /   \            |    get_transform_name   get_transform_path
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
-MLDB_neuron_enter: This module contains the class Neuronposter, which is used to automatically
------------------- enter the data of neurons into the Neuron Broswer sample manager database.



	Initialization of the object takes two argumenst, the name of the sample and url of 
	the GraphQL instance for Neuron Browser sample manager database.An Neuronbroswer object 
	can be initialized as such (variable names are customizable, 
	but conventional names are used below):
		-nPoster = MLDB_sample_enter('2020-11-26', graphqlurl)
	
	Initialization of the Neuronposter object:
		-saves the parent directory of the folder containing the required graphql 
		 queries and mutations in the instance variable named self.folderpath
		-saves the url of the graphql instance in the instance variable 
		 named self.GQLInstance
		-saves the name of the folder containing the required graphql query and 
		 mutation jsons in the instance variable named self.GQLDir
		-saves the name of the sample entered as an argument when creating the 
		 class in the instance variable named self.sample
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
________________________________________________________________________________________________
*In progres...


