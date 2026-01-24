# ntJobsOS and ntJobsApp Kit
Python Framework but also Batch Launch Jobs Platform for batch working using cloud and webservice input/output and mailing as frontend with end user

Beta Release - Not working - Under Testing

See index.xlsx for files list

Requirements: For Windows, PythonX64.7z (Portable Linux) or apply requirements.txt if you have your Python Virtual Enviroment or Linux Pyyhon. See ntjobs_download.link to download it

http://www.ntgcorp.it/ntjobs

https://drive.google.com/drive/folders/1LE2lc7mdW9kKMZOPh1Yoo6eADkx8E5JT?usp=drive_link

Execution:  
   
   pyn.cmd ntJobsOS.py
   
   pyn.cmd ntJobsApp.py action -parameter_key -parameter_value eccc...
   
   pyn.cmd ntJobsApp.py ntjobsapp.ini 
   
   See ntjobs_app_man_*.pdf for info
   
----------------- ntJobsPy Conventions --------------------------

  sResult = Return string as ntJobs in case of single returns
  lResult = Return list with multiple returns since it is not possible to modify global variables or byRef in Python. Where 0 = sResult
  NF_ErrorProc = Construction of the return error string with the name of the Proc where it occurs
  
  ntj_    = ntJobs Applications (FrontEnd for special cases) 
  ntJobsOS= ntJobsOS Start Applications.
  aiJobsOS= ntJobsOS AI Generated Application
  ai*     = ntJobs Manual Application & Funcions Libraries AI Generated
  ac*     =  ntJos Only Classes AI Generated
  nl*     = ntJobs Libraries
  nc*     = OS and FrontEnd Class (called from ntJobs Apps)
