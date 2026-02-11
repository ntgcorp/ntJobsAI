
#!/usr/bin/env python3
# Nomefile: acJobsOS.py
# -*- coding: utf-8 -*-

"""
acJobsOS - Classe principale di aiJobsOS
Eredita da tutti i mixin per comporre le funzionalità complete.
"""

import os
import sys
import time
from typing import Dict, Any, Optional, Union, List
from copy import deepcopy

# Import dei mixin
from acJobsStart import acJobsStart
from acJobsUsers import acJobsUsers
from acJobsJobs import acJobsJobs
from acJobsMail import acJobsMail


class acJobsOS(acJobsStart, acJobsUsers, acJobsJobs, acJobsMail):
    """
    Classe principale che eredita da tutti i mixin.
    Contiene i campi e i metodi core del sistema.
    """
    
    def __init__(self):
        """Inizializza l'istanza della classe."""
        # Campi della classe
        self.sJobsPath = ""                 # Path del file jobs.ini corrente
        self.sJob = ""                     # ID del job corrente
        self.sJobsFile = ""               # Path completo del file jobs.ini corrente
        self.asJobs = []                 # ID dei jobs nel file corrente
        self.asJobFiles = []             # File associati al job corrente
        self.asPaths = []               # Array dei paths da scandire
        self.asUsers = []              # Array degli utenti
        self.asActions = []           # Array delle azioni riconosciute
        self.asGroups = []           # Array dei gruppi
        
        self.dictConfig = {}         # Configurazione corrente (fusa)
        self.dictJobs = {}          # Dizionario del file jobs.ini corrente
        self.dictJobsConfig = {}   # Copia readonly della sezione CONFIG
        self.dictJob = None       # Dizionario del job corrente
        self.dictPaths = {}      # Path associati agli utenti
        self.dictUser = None    # Dizionario utente corrente
        self.sUser = ""        # User corrente
        
        self.sAction = ""      # Azione corrente
        self.sCommand = ""    # Comando corrente
        self.dictAction = None
        self.sActionPath = ""
        self.sScript = ""
        
        # JOBS_DAT_* arrays
        self.JOBS_DAT_USERS = ["USER", "USER_NAME", "USER_NOTES", "USER_GROUPS", "USER_PATHS", "USER_MAIL"]
        self.JOBS_DAT_GROUPS = ["GROUP_ID", "GROUP_NAME", "GROUP_NOTES"]
        self.JOBS_DAT_ACTIONS = ["ACT_ID", "ACT_NAME", "ACT_GROUPS", "ACT_SCRIPT", "ACT_ENABLED", "ACT_PATH", "ACT_HELP", "ACT_TIMEOUT"]
        self.JOBS_DAT_CONFIG_SMTP = ["SMTP.FROM", "SMTP.PASSWORD", "SMTP.PORT", "SMTP.SERVER", "SMTP.SSL", "SMTP.TLS", "SMTP.USER"]
        
        # JOBS_TAB_* dizionari
        self.JOBS_TAB_USERS = {}
        self.JOBS_TAB_GROUPS = {}
        self.JOBS_TAB_ACTIONS = {}
        self.JOBS_TAB_CONFIG = {}
        
        # Campi vari interni
        self.bExitJobs = False
        self.bExitOS = False
        self.jLog = None
        self.tsStart = ""
        self.tsJobsStart = ""
        self.tsJobStart = ""
        self.tsSearch = ""
        self.sMailEngine = ""
        self.sMailAdmin = ""
        self.pidJob = None
        
        # Campi inizializzati da config
        self.sSys_PathRoot = ""
        self.sSys_PathInbox = ""
        self.sSys_PathArchive = ""
        self.sSys_PathOlk = ""
        self.sSys_Olk = ""
        self.sSys_BillFile = ""
        self.nCycleCounter = 0
        self.nCycleWait = 60
        self.nSearchWait = 900
        
        self.jMail = None
    
    def Run(self) -> str:
        """
        Ciclo principale di esecuzione.
        Esegue Search, Get, Archive, CycleEnd in sequenza.
        """
        sProc = "Run"
        sResult = ""
        
        while not self.bExitOS:
            # 1. Metodo Search
            sResult = self.Search()
            
            # 2. Metodo Get - solo se Search OK
            if sResult == "":
                sResult = self.Get()
            
            # 3. Metodo Archive - solo se precedenti OK
            if sResult == "":
                sResult = self.Archive()
            
            # 4. Metodo CycleEnd - SOLO se tutto OK
            if sResult == "":
                sResult = self.CycleEnd()
            
            # Alla fine dei 4 metodi: se errore, imposta bExitOS=True
            if sResult != "":
                self.bExitOS = True
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Search(self) -> str:
        """
        Scansiona le cartelle predefinite per cercare file jobs.ini.
        """
        sProc = "Search"
        sResult = ""
        
        for sPath in self.asPaths:
            sUser = self.dictPaths.get(sPath, "")
            sFileJobs = aiSys.PathMake(sPath, "jobs", "ini")
            
            if aiSys.FileExists(sFileJobs):
                sResultTemp = self.Move(sPath, sUser)
                if sResultTemp:
                    sResult += sResultTemp + ", "
                self.Log(sResult, f"Trovato jobs.ini in {sPath} dell'utente {sUser}")
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Move(self, sPath: str, sUser: str) -> str:
        """
        Sposta il file jobs.ini e i file associati in una cartella inbox.
        """
        sProc = "Move"
        sResult = ""
        
        sFileJobs = aiSys.PathMake(sPath, "jobs", "ini")
        sResult, dictTemp = aiSys.read_ini_to_dict(sFileJobs)
        
        if sResult != "":
            return self.MoveError(sResult, sPath)
        
        if "CONFIG" not in dictTemp:
            sResult = f"File senza CONFIG {sFileJobs}"
            return self.MoveError(sResult, sPath)
        
        # Crea cartella inbox univoca
        nCounter = 0
        while True:
            sPathInbox = f"jobs_{aiSys.TimeStamp()}_{nCounter}"
            sPathInboxFull = aiSys.PathMake(self.sSys_PathInbox, sPathInbox)
            if not os.path.exists(sPathInboxFull):
                break
            nCounter += 1
        
        try:
            os.makedirs(sPathInboxFull, exist_ok=True)
        except Exception as e:
            sResult = f"Errore creazione path inbox {sPathInboxFull}: {str(e)}"
            return self.MoveError(sResult, sPath)
        
        sLogMove = ""
        
        # Aggiunge USER alla sezione CONFIG
        dictTemp["CONFIG"]["USER"] = sUser
        
        # Scrive jobs.ini nella nuova cartella
        sResult = aiSys.save_dict_to_ini(dictTemp, aiSys.PathMake(sPathInboxFull, "jobs", "ini"))
        if sResult != "":
            return self.MoveError(sResult, sPathInboxFull)
        
        sLogMove = f"Spostato jobs.ini in {sPathInboxFull}"
        
        # Sposta file associati
        for dictSection in dictTemp.values():
            if isinstance(dictSection, dict):
                for sKey, sValue in dictSection.items():
                    if sKey.startswith("FILE."):
                        sFileMove = sValue
                        srcFile = aiSys.PathMake(sPath, sFileMove)
                        dstFile = aiSys.PathMake(sPathInboxFull, sFileMove)
                        try:
                            shutil.move(srcFile, dstFile)
                            sLogMove += f" Spostato file {sFileMove}."
                        except Exception as e:
                            sResult = f"Non spostabile {sFileMove}: {str(e)}"
                            break
        
        if sResult != "":
            return self.MoveError(sResult, sPath)
        
        self.Log(sLogMove)
        return ""
    
    def MoveError(self, sResult: str, sPath: str) -> str:
        """
        Gestisce errori durante lo spostamento.
        """
        sProc = "MoveError"
        
        sFileIni = aiSys.PathMake(sPath, "jobs", "ini")
        self.JobsMailUser("Errore in esecuzione jobs.ini", sResult)
        
        sFileTemp = aiSys.PathMake(sPath, "jobs", "end")
        try:
            os.rename(sFileIni, sFileTemp)
        except Exception as e:
            sResult = f"Errore rinomina ini in end: {sFileTemp}: {str(e)}"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Get(self) -> str:
        """
        Ricerca dei file jobs.ini in self.sSys_PathInbox.
        """
        sProc = "Get"
        sResult = ""
        
        if not os.path.exists(self.sSys_PathInbox):
            return aiSys.ErrorProc(sResult, sProc)
        
        for sItem in os.listdir(self.sSys_PathInbox):
            sPath = aiSys.PathMake(self.sSys_PathInbox, sItem)
            if os.path.isdir(sPath):
                sFileJobs = aiSys.PathMake(sPath, "jobs", "ini")
                sFileEnd = aiSys.PathMake(sPath, "jobs", "end")
                
                if aiSys.FileExists(sFileJobs) and not aiSys.FileExists(sFileEnd):
                    sResultExec = self.Exec(sPath)
                    if sResultExec:
                        self.Log1(sResultExec)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Exec(self, sPath: str) -> str:
        """
        Gestisce il file jobs.ini corrente, eseguendo i jobs in esso contenuti.
        """
        sProc = "Exec"
        sResult = ""
        
        self.bExitJobs = False
        
        # Startup del Jobs
        sResult = self.JobsInit(sPath)
        
        if sResult != "":
            self.bExitJobs = True
            sResult = f"Errore JobsInit: {sResult} {sPath}"
            self.Log1(sResult)
            return aiSys.ErrorProc(sResult, sProc)
        
        # Esecuzione dei singoli Jobs
        for sJob in self.asJobs:
            self.sJob = sJob
            sResult = self.JobExec(sJob)
            
            if sResult != "" and aiSys.StringBool(self.dictConfig.get("EXIT", "False")):
                self.bExitJobs = True
            
            if self.bExitJobs:
                break
        
        # JobsEnd
        sResult = self.JobsEnd(sResult)
        self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def CycleEnd(self) -> str:
        """
        Completa un ciclo di Ricerca ed Elaborazione.
        """
        sProc = "CycleEnd"
        sResult = ""
        
        self.nCycleCounter += 1
        print(f"Ciclo Run: {self.nCycleCounter}, Time: {aiSys.TimeStamp()}, Attesa: {self.nCycleWait}")
        
        time.sleep(self.nCycleWait)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Archive(self) -> str:
        """
        Archiviazione dei Job terminati.
        """
        sProc = "Archive"
        sResult = ""
        
        if not os.path.exists(self.sSys_PathInbox):
            return aiSys.ErrorProc(sResult, sProc)
        
        for sItem in os.listdir(self.sSys_PathInbox):
            sPath = aiSys.PathMake(self.sSys_PathInbox, sItem)
            if os.path.isdir(sPath):
                sFileJobs = aiSys.PathMake(sPath, "jobs", "ini")
                sFileEnd = aiSys.PathMake(sPath, "jobs", "end")
                
                if aiSys.FileExists(sFileJobs) and aiSys.FileExists(sFileEnd):
                    try:
                        dstPath = aiSys.PathMake(self.sSys_PathArchive, sItem)
                        shutil.move(sPath, dstPath)
                    except Exception as e:
                        sResult += f"Errore spostamento, Folder: {sItem}: {str(e)}. "
        
        if sResult:
            self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)


