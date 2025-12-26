# ntJobsPy
NewTechJobs - Python Version 

Python Framework but also Batch Launch Jobs Platform for batch working using cloud and webservice input/output and mailing as frontend with end user

Alpha Release - Not working - Under development

See index.xlsx for files list

Requirements: For Windows, PythonX64.7z (Portable Linux) or apply requirements.txt if you have your Python Virtual Enviroment or Linux Pyyhon. See ntjobs_download.link to download it

http://www.ntgcorp.it/ntjobs

https://drive.google.com/drive/folders/1LE2lc7mdW9kKMZOPh1Yoo6eADkx8E5JT?usp=drive_link

Execution: Python ntJobs.py action -parameter_key -parameter_value eccc...


----------------- ntJobsPy Conventions --------------------------

  sResult = Return string as ntJobs in case of single returns
  lResult = Return list with multiple returns since it is not possible to modify global variables or byRef in Python. Where 0 = sResult
  NF_ErrorProc = Construction of the return error string with the name of the Proc where it occurs
  
  na*     = ntJobs Applications (FrontEnd for special cases) 
  ntJobs  = ntJobsOS Start Applications. Special naJobs Unique FrontEndApp
  nl*     = ntJobs Libraries
  nc*     = OS and FrontEnd Class (called from ntJobs Apps)
