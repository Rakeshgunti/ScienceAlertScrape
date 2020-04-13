# ScienceAlertScrape
Webcrawler to scrape data from sciencealert.com using spiders of scrapy and store data in MongoDB

Requirements
 - Python 3.5 or above
 - Virtual
 - MongoDB setup (locally or remotely)
 
 Make sure to update MongoDB URI, Database in settings.py file

Install virtual environments:
 - To create python virtual environment using pip, Please refer link - https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
 
 - To create python vitual environment using Anaconda, Please refer link - https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/

Install requirements from requirements.txt using below commands
 - For pip vitual environment
     - pip install -r requirements.txt
 - For conda virtual environment
     - conda install --file requirements.txt
 
 No need to create scrapy project for now
 
 In future or for other projects:
 Create scrapy project
  - scrapy startproject <projectname>
  
