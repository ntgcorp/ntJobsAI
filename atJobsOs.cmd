:START
ECHO NTJOBSOS.START
FOR %%A IN (ntjobs.reload ntjobs.restart. ntjobs.shutdown) IF EXIST "%%A" del "%%A"

@REM EVENTUALE RESTART
IF EXIST ntjobs.restart" GOTO :START
IF EXIST ntjobs.shutdown" CALL K:\NTROBOT\ADMIN_SHUTDOWN.CMD

:END
ECHO NTJOBSOS.END