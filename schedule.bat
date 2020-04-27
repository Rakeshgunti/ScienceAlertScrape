cd C:\Users\gunti\.spyder-py3\Python-projects\ScienceAlertScrape
SET log_file=%cd%\logfile.txt
call C:/ProgramData/Anaconda3/Scripts/activate.bat
cd sciencealertscrape\sciencealertscrape\spiders
C:\Users\gunti\.conda\envs\sciencescrape\python.exe SAspider.py > %log_file%
exit