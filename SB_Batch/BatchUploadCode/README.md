# science-base-automation
__Automatically create and populate ScienceBase pages with metadata and data files.__ Given a ScienceBase (SB) landing page and a directory tree with data and metadata, this script creates SB pages mimicking the directory structure, updates the XML files with new SB links, and populates the SB pages from the data.

### Overall process
1. Set up a local directory structure for your data release.
2. Set up a ScienceBase landing page.
3. Modify script parameters in config_autoSB.py.
4. Run (first install necessary python modules).
5. Check ScienceBase pages and make manual modifications.   

### Limitations
(besides soon-to-be-discovered bugs)

- The metadata population routine is hard-coded to the FGDC CSDGM structure.
- It does not change the XML files within zipped files nor recreate the zip file with the updated XML. You will need to do this afterward to make sure that the XML is in the zip file is updated.
- It does not add networkr links to individual files on the data page. 

## How to execute, from the top:
### 1. Set up a local directory structure for your data release.
See below for an explanation of how SB pages will mimic the directory structure. Each directory within the parent directory that contains (at some level) an XML file will become a ScienceBase page within the landing page. An SB page will be created for each XML file. The page will be located within the page corresponding to its containing directory. The title of that page is taken from the title of the dataset recorded in the XML file. Ensure there is one and only one XML file for each desired SB page. These XML files should pass MP error checking.

- Filenames should use this pattern: data_1.shp, data_1.shp.xml (or data_1_meta.xml), data_1_browse.png, where 'data_1' is the _basename_ of the dataset and the suffixes '.shp' or '\_meta' and '\_browse' indicate metadata or browse graphics respectively. If the metadata filename is data_1.shp.xml, all files in the folder containing the XML file that begin with 'data_1' will be uploaded. This would include data_12.shp

![Example file structure for SB upload](docs/filestructure_eg.png)

### 2. Set up a ScienceBase landing page.
Create the data release landing page before running the script.
Begin either by uploading an XML file to the File section, which SB will use to automatically populate fields or go straight to working manually with the page. Make manual revisions, such as to the citation, the body, the purpose, etc. If desired, create a preview image by uploading an image to the File section; this will automatically be used as the preview image. You can choose any of these fields to be copied over to child pages (including the preview image).
It is also possible for the script to automatically create the SB page from an XML file. If desired, that file should be checked for errors using MP and placed in the top directory.

### 3. Modify parameters.

Open config_autoSB.py in your Python/text editor and revise the value of each input variable as indicated in the comments.

- Input variables that must be updated before running:
	- useremail (SB username)
	- landing_link (URL for SB landing page)
	- parentdir (path to top directory) OSX/Windows variations
	- dr_doi (data release DOI)

- Specify which fields will be “inherited” between pages in the following optional lists:
	- landing_fields_from_xml – landing page fields that will populate from the top XML
	- subparent_inherits – fields that aggregate pages copy (inherit) from the landing page
	- data_inherits – fields that data pages inherit from their immediate parent page
	- landing_fields_from_xml – landing page fields that will populate from the top XML

- Choose which processes to conduct. The default values will suit most purposes, but these fields allow you to tune the processes to save time.
	- update_subpages
	- update_XML
	- update_data
	- update_extent
	- quality_check_pages
	- verbose
	- max_MBsize - maximum file size (in MB) to upload
	- add_preview_image_to_all
	- replace_subpages
	- restore_original_xml

- Optional...
	- find_and_replace - dictionary of {find pattern : replace string} values to replaced in all XML files.
	- metadata_additions - dictionary of {container tag : element XML} items to be added to all XML files.
	- metadata_replacements - dictionary of {container tag : element XML} items to be replaced in all XML files.

### 4. Run script sb_automation.py!
#### INSTALL
Install additional required python modules: lxml, pysb, science-base-automation. sb_automation is compatible with Python 3 on OSX and Windows.

Download/fork/clone __science-base-automation__.

Install __lxml__ and __pysb__ using pip (requires Git):

	easy_install pip
	pip install lxml
	pip install -e git+https://my.usgs.gov/stash/scm/sbe/pysb.git#egg=pysb

... or using Conda...

	conda create -n sb_py3 python=3 lxml
	source activate sb_py3 # OSX. Windows would be activate sb_py3
	pip install -e git+https://my.usgs.gov/stash/scm/sbe/pysb.git#egg=pysb

#### RUN
__In your bash console (Terminal on OSX):__

	# If using Conda:
	source activate sb_py3 # OSX. Windows would be activate sb_py3
	# Start here if not using Conda:
	cd [path]\[to]\science-base-automation
	python sb_automation.py

__From Finder:__ Right click and run with your python launcher of choice.

__In your Python IDE of choice:__ Open the script (sb_automation.py) and run it line by line or however you choose.

Once I learn how to properly set up a program to be installed and run, I will update this to describe that process. It will begin like this...

	conda create -n sb_py3 python=3
	source activate sb_py3
	pip install git+https://github.com/esturdivant-usgs/science-base-automation.git
	pip install -e git+https://my.usgs.gov/stash/scm/sbe/pysb.git#egg=pysb


### 5. Check ScienceBase pages and make manual modifications.   

If you want to start fresh, an easy way to delete all items pertaining to the parent page, is to set `parentdir` to an empty directory and set the variable `replace_subpages` to True. 

## What the script does:
- Starts a ScienceBase session.
- Works in the landing page and top directory as specified by the input parameters.
- Loops through the sub-directories to create or find a matching SB page.
	- For each sub-directory, it checks for a matching child page (child title==directory name and parent page=parent directory). If the child does not already exist, it creates a new page. For each page (regardless of whether it already existed), it copies fields from the landing page, as indicated in the input parameters.

- Loops through the XML files to create or find a data page. For each XML file (excluding the landing page XML), it:
	- creates (or finds) a data page,
	- revises the XML to: include DOI and URLs for the landing page, data page, and direct data download; replaces any instance of 'http:' with 'https:'; adds a new element (such as new cross reference) to the XML
	- uploads files matching the XML filename to the new page, except those greater than an indicated maximum file size.
	- copies fields from the parent page to the data page as indicated in the input parameters.

- Sets bounding box coordinates for parents based on the spatial extent of the data in their child pages.
- During processing it stores values in three dictionaries, which are then saved in the top directory as a time-saving measure for future processing.

## Background

### Terms
- landing page: the top-level ScienceBase page of the data release. The DOI will direct here. Corresponds to the local top directory.
- top directory: the top local directory housing all files in the data release. Corresponds to the SB landing page.
- data pages: the final page/s in a page chain that holds the data files.
- [aggregate]/subparent pages: the mid-level pages that organize data pages
- parent and child [pages or directories]: relational terms for page at any level of the hierarchy. Parent always contains the child.
- item: SB JSON item. The JSON-formatted version of a given page.
- field: One component of a SB page. Fields include title, citation, body… Field values will be displayed under the headings on a SB page. Examples:
	- citation – Recommended citation for the data release. ScienceBase will automatically populate using the XML, but this may not agree with our format.
	- body = abstract. The summary will automatically be created from body.
	- purpose
	- previewImage – a.k.a. browse graphic. SB will automatically use an image file uploaded to the page.
	- summary – this is automatically populated based on the body.
- element: One piece of an XML file. XML holds nested elements that are specified by tags. Also a class in lxml. Elements can be referenced by the tags and the values are the text __ property of the element.

### Directory structure
Each directory will become a ScienceBase page within your data release. The directories will maintain their hierarchy. Each (error-free) XML file will populate a ScienceBase page. If a directory contains a single XML file, the corresponding ScienceBase page will be populated with that XML file. If the directory contains multiple XML files, each XML will become a child page linked on the page corresponding to its parent directory. ScienceBase pages that correspond to directories will use the directory name as their title. ScienceBase pages that correspond to XML files will use the Title in the metadata (Identity Information > Citation > Citation Information > Title) as their title. Pages that correspond to directories with a single XML file will still use the directory name rather than the metadata title. Here is an example of how a local file structure will become a ScienceBase page structure:

#### Local directories and files

##### DATA_RELEASE_1 - top directory
- North Carolina - sub-directory

      - NC Central - sub-directory

		- NCcentral_baseline.cpg - 1st data file
		- NCcentral_baseline.dbf - 1st data file
		- NCcentral_baseline.prj - 1st data file
		- NCcentral_baseline.sbn - 1st data file
		- NCcentral_baseline.shp - 1st data file
		- NCcentral_baseline.shp.xml - metadata for 1st data file

			<idinfo><citation><citeinfo><title>Coastal baseline for North Carolina…</title></citeinfo></citation></idinfo> - excerpt of title element from within metadata file
		- NCcentral_baseline.shx - 1st data file
		- NCcentral_baseline_browse.png - browse graphic for 1st data file
		- NCcentral_shorelines.cpg - 2nd data file
		- NCcentral_shorelines.dbf - 2nd data file
		- NCcentral_shorelines.prj - 2nd data file
		- NCcentral_shorelines.sbn - 2nd data file
		- NCcentral_shorelines.shp - 2nd data file
		- NCcentral_shorelines.shp.xml - metadata for 2nd data file
		

			<idinfo><citation><citeinfo><title>Shorelines of North Carolina…</title></citeinfo></citation></idinfo>” - excerpt of title element from within metadata file
		- NCcentral_shorelines.shx - 2nd data file

#### ScienceBase pages

##### Shorelines of U.S. Atlantic - landing page
- North Carolina - sub-page
	- NC Central - sub-page
		- Coastal baseline for North Carolina… - data page
- Shorelines of North Carolina… - data page

### ScienceBase features

Reference for ScienceBase item services: https://my.usgs.gov/confluence/display/sciencebase/ScienceBase+Item+Services
PYSB, the ScienceBase python module: https://my.usgs.gov/bitbucket/projects/SBE/repos/pysb/browse

#### Intelligent content from uploaded files
ScienceBase automatically detects the file type and in some cases the contents of uploaded files and makes intelligent decisions about how to use them. For instance, an image file uploaded to a page will be used as the preview image. It will pull information from an XML file to populate fields, and it will detect components of a shapefile or raster file and present them as a shapefile or raster “facet”, which can be downloaded as a package. Even if an XML file is later removed from the Files, the fields populated from it will remain.

#### Direct download
SB has a URL for direct download of all files from a page. It is https://www.sciencebase.gov/catalog/file/get/[item ID]
There is also the option for direct download of a single file, which adds a query onto the get file URL: https://www.sciencebase.gov/catalog/file/get/[item ID]/?name=[file name]. However, this should only be used when the data has been zipped before upload to ensure that a user retrieves all necessary files (including metadata).
If a facet was created, a URL for direct download of the all files in the facets can be retrieved from the JSON item.

## Tips

- Accessing files on a server: In OSX, paths: r'/Volumes/[server directory name]'. Replace [server directory] with the name of the directory on the server, not the server itself. The server must first be mounted and visible in your Volumes. Then get the directory name by viewing the volumes mounted on your computer. Example:


	parentdir = r'/Volumes/myserverfolder/data_release'

- Although not necessary, you can use find_and_replace variable in config_autoSB.py to replace text in the XML based on placeholder values. The default configuration will search for the strings https://doi.org/XXXXX and DOI:XXXXX and replace the X's with the input DOI value. Note those are __five__ capital X's. 
