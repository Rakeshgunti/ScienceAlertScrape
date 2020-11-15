@REM Please provide the project location and environment location as command line arguments when executing script or scheduling batch file
SET arg1=%1
cd %arg1%
SET arg2=%2
SET log_file=%cd%\logfile.txt
call C:/ProgramData/Anaconda3/Scripts/activate.bat
cd sciencealertscrape\sciencealertscrape\spiders
%arg2% SAspider.py daily > %log_file%
exit