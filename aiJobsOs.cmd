:START
ECHO NTJOBSOS.START
FOR %%A IN (ntjobs.reload ntjobs.restart ntjobs.shutdown) DO IF EXIST "%%A" del "%%A"

@REM LANCIO NTJOBSOS
call pyn aiJobsOS.py

@REM EVENTUALE RESTART
IF EXIST "ntjobs.restart" GOTO :START
IF EXIST "ntjobs.shutdown" SHUTDOWN.EXE /S 

:END
ECHO NTJOBSOS.END