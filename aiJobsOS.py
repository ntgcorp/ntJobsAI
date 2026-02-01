import os
import sys
import time
import subprocess
import json

# Import librerie di supporto
import aiSys
from acDictToString import acDictToString

class acJobsOS:
    def __init__(self):
        self.sProc = "acJobsOS.__init__"
        
        # Inizializzazione campi principali
        self.sSys_PathRoot = os.path.dirname(os.path.abspath(__file__))
        
        # Campi JOBS_DAT_*
        self.JOBS_DAT_USERS = ["USER_ID", "USER_PASSWORD", "USER_NAME", "USER_NOTES", 
                              "USER_GROUPS", "USER_PATHS", "USER_MAIL"]
        self.JOBS_DAT_GROUPS = ["GROUP_ID", "GROUP_NAME", "GROUP_NOTES"]
        self.JOBS_DAT_ACTIONS = ["ACT_ID", "ACT_NAME", "ACT_GROUPS", "ACT_SCRIPT", 
                                "ACT_ENABLED", "ACT_PATH", "ACT_HELP", "ACT_TIMEOUT"]
        self.JOBS_DAT_CONFIG_SMTP = ["SMTP.FROM", "SMTP.PASSWORD", "SMTP.PORT", 
                                    "SMTP.SERVER", "SMTP.SSL", "SMTP.TLS", "SMTP.USER"]
        
        # Campi JOBS_TAB_*
        self.JOBS_TAB_CONFIG = None
        self.JOBS_TAB_USERS = None
        self.JOBS_TAB_GROUPS = None
        self.JOBS_TAB_ACTIONS = None
        
        # Campi di lavoro
        self.dictConfig = {}
        self.dictJobs = {}
        self.dictJobsConfig = {}
        self.dictJob = None
        self.dictPaths = {}
        self.dictUser = None
        self.dictAction = None
        
        self.sUser = ""
        self.sAction = ""
        self.sActionPath = ""
        self.sScript = ""
        self.sJob = ""
        self.sJobsPath = ""
        self.sJobsFile = ""
        
        # Array di supporto
        self.asJobs = []
        self.asJobFiles = []
        self.asPaths = []
        self.asUsers = []
        self.asActions = []
        self.asGroups = []
        
        # Flag di controllo
        self.bExitJob = False
        self.bExitOS = False
        
        # Istance helper
        self.jLog = None
        self.jDTS = None
        self.jMail = None
        
        # Campi temporali e contatori
        self.tsStart = ""
        self.sJobTS = ""
        self.nCycleCounter = 0
        self.nCycleWait = 60
        
        # Campi mail
        self.sMailEngine = ""
        self.sMailAdmin = ""
        self.sSys_PathInbox = ""
        self.sSys_PathArchive = ""
        self.sSys_PathOlk = ""
        self.sSys_Olk = ""
        
        # Processo esterno
        self.pidJob = None
        
        print("Inizializzata istanza acJobsOS")

    # =========================================================================
    # METODI DI STARTUP
    # =========================================================================
    def Start(self):
        sProc = "Start"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            # Inizializzazione timestamp
            self.tsStart = aiSys.Timestamp()
            
            # Istanza DTS
            self.jDTS = acDictToString()
            print("Istanziata DTS")
            
            # Istanza LOG
            sLogFile = self.Config("LOG")
            if sLogFile == "":
                sLogFile = aiSys.PathMake(self.sSys_PathRoot, "aiSysJobOS", "log")
            
            self.jLog = aiSys.acLog()
            sResult = self.jLog.Start(sLogFile)
            if sResult != "":
                return f"{sProc}: {sResult}"
            print("Istanziata LOG")
            
            # Sequenza di inizializzazione
            methods = [
                self.Start_ReadIni,
                self.Start_ReadDat,
                self.Start_ReadPaths,
                self.Start_Expand,
                self.Start_Verify,
                self.Start_Mail
            ]
            
            for method in methods:
                sResult = method()
                if sResult != "":
                    self.Log1(sResult)
                    self.Start_End()
                    return f"{sProc}: {sResult}"
            
            print("aiJobsOS inizializzato con successo")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Start_ReadIni(self):
        sProc = "Start_ReadIni"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            sFileIni = aiSys.PathMake(self.sSys_PathRoot, "ntjobs_config", "ini")
            print(f"Lettura file {sFileIni}")
            
            sResult, dictTemp = aiSys.read_ini_to_dict(sFileIni)
            if sResult != "":
                self.Log1(sResult)
                return f"{sProc}: {sResult}"
            
            # Impostazioni di default
            print("Impostazioni di default")
            sLogFile = aiSys.PathMake(self.sSys_PathRoot, "aiSysJobOS", "log")
            
            defaults = [
                ("PATHROOT", self.sSys_PathRoot),
                ("TIMEOUT", "60"),
                ("EXPAND", "True"),
                ("MAIL.ENGINE", "SMTP"),
                ("LOG", sLogFile)
            ]
            
            # Verifica/inserimento chiavi mancanti
            print("Set chiavi mancanti")
            for sKey, sValue in defaults:
                if sKey not in dictTemp:
                    sResult = aiSys.ConfigSet(dictTemp, sKey, sValue)
                    if sResult != "":
                        self.Log1(sResult)
                        return f"{sProc}: {sResult}"
            
            # Espansione dizionario
            print("Espansione diionario")
            dictTemp2 = dictTemp.copy()
            sResult = aiSys.ExpandDict(dictTemp, dictTemp2)
            if sResult != "":
                self.Log1(sResult)
                return f"{sProc}: {sResult}"
            
            # Assegnazione a JOBS_TAB_CONFIG
            self.JOBS_TAB_CONFIG = dictTemp2.copy()
            
            # Aggiornamento configurazione
            sResult = self.ConfigUpdate()
            if sResult != "":
                self.Log1(sResult)
                return f"{sProc}: {sResult}"
            
            # Inizializzazione campi da config
            self.sSys_PathInbox = self.Config("INBOX")
            self.sSys_PathArchive = self.Config("ARCHIVE")
            self.nCycleCounter = 0
            
            sTemp = self.Config("CYCLE.WAIT")
            if sTemp == "":
                self.nCycleWait = 60
            else:
                self.nCycleWait = aiSys.StringToNum(sTemp)
            
            print("Caricata CONFIG.INI")
            print("Dizionario letto ed espanso")
            aiSys.DictPrint(self.dictConfig)
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Start_ReadDat(self):
        sProc = "Start_ReadDat"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            # Mappatura file -> array campi -> dizionario destinazione
            files_config = [
                ("ntjobs_actions.csv", self.JOBS_DAT_ACTIONS, "JOBS_TAB_ACTIONS"),
                ("ntjobs_groups.csv", self.JOBS_DAT_GROUPS, "JOBS_TAB_GROUPS"),
                ("ntjobs_users.csv", self.JOBS_DAT_USERS, "JOBS_TAB_USERS")
            ]
            
            for sFileName, avHeader, sDictName in files_config:
                sFileCSV = aiSys.PathMake(self.sSys_PathRoot, sFileName.split('.')[0], "csv")
                
                sResult, dictTemp = aiSys.read_csv_to_dict(sFileCSV, avHeader)
                if sResult != "":
                    self.Log1(sResult)
                    return f"{sProc}: {sResult}"
                
                # Assegnazione al dizionario corrispondente
                setattr(self, sDictName, dictTemp)
            
            # Inizializzazione array di supporto
            self.asActions = list(self.JOBS_TAB_ACTIONS.keys()) if self.JOBS_TAB_ACTIONS else []
            self.asGroups = list(self.JOBS_TAB_GROUPS.keys()) if self.JOBS_TAB_GROUPS else []
            self.asUsers = list(self.JOBS_TAB_USERS.keys()) if self.JOBS_TAB_USERS else []
            
            print("Caricati DAT")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Start_ReadPaths(self):
        sProc = "Start_ReadPaths"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            dictTemp = {}
            
            if self.JOBS_TAB_USERS:
                for sUser, dictUser in self.JOBS_TAB_USERS.items():
                    sPaths = dictUser.get("USER_PATHS", "")
                    if sPaths:
                        asPaths = aiSys.StringToArray(sPaths)
                        for sPathSingle in asPaths:
                            sPathSingle = aiSys.Expand(sPathSingle, self.dictConfig)
                            sPathSingle = sPathSingle.strip()
                            if sPathSingle:
                                dictTemp[sPathSingle] = sUser
            
            self.dictPaths = dictTemp.copy()
            self.asPaths = list(self.dictPaths.keys())
            
            # Verifica esistenza paths
            for sPath in self.asPaths:
                if not aiSys.isValidPath(sPath):
                    sResult += f"Non trovato Path {sPath}. "
            
            if sResult != "":
                self.Log1(sResult)
            
            print("Caricati PATHS")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Start_Expand(self):
        sProc = "Start_Expand"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            if not aiSys.StringBoolean(self.Config("EXPAND")):
                return sResult
            
            # Espansione dictConfig
            sResult = aiSys.ExpandDict(self.dictConfig, self.dictConfig)
            if sResult != "":
                return f"{sProc}: {sResult}"
            
            # Espansione tabelle
            tables = [self.JOBS_TAB_USERS, self.JOBS_TAB_GROUPS, self.JOBS_TAB_ACTIONS]
            for dictTable in tables:
                if dictTable:
                    sResult = aiSys.ExpandDict(dictTable, self.dictConfig)
                    if sResult != "":
                        return f"{sProc}: {sResult}"
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Start_Verify(self):
        sProc = "Start_Verify"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            # Verifica JOBS_TAB_CONFIG
            if self.JOBS_TAB_CONFIG:
                # ADMIN.EMAIL
                sValue = self.JOBS_TAB_CONFIG.get("ADMIN.EMAIL", "")
                if sValue and not aiSys.isEmail(sValue):
                    sResult += "ADMIN.MAIL non corretta. "
                
                # TYPE
                sValue = self.JOBS_TAB_CONFIG.get("TYPE", "")
                if sValue != "NTJOBS.CONFIG.1":
                    sResult += "TYPE non corretta. "
                
                # INBOX
                sValue = self.JOBS_TAB_CONFIG.get("INBOX", "")
                if sValue and not aiSys.isValidPath(sValue):
                    sResult += "INBOX non corretta. "
                
                # LOG
                sValue = self.JOBS_TAB_CONFIG.get("LOG", "")
                if sValue:
                    sPath = os.path.dirname(sValue)
                    if not aiSys.isValidPath(sPath):
                        sResult += "LOG non corretta. "
                
                # ARCHIVE
                sValue = self.JOBS_TAB_CONFIG.get("ARCHIVE", "")
                if sValue and not aiSys.isValidPath(sValue):
                    sResult += "ARCHIVE non corretta. "
                
                # MAIL.ENGINE
                sValue = self.JOBS_TAB_CONFIG.get("MAIL.ENGINE", "")
                if sValue not in ["OLK", "SMTP"]:
                    sResult += "MAIL.ENGINE non corretta. "
                
                # MAIL.PATH
                sValue = self.JOBS_TAB_CONFIG.get("MAIL.PATH", "")
                if sValue and not aiSys.isValidPath(sValue):
                    sResult += "MAIL.PATH non corretta. "
                
                # Verifica SMTP se necessario
                if self.JOBS_TAB_CONFIG.get("MAIL.ENGINE") == "SMTP":
                    for sKey in self.JOBS_DAT_CONFIG_SMTP:
                        sValue = self.JOBS_TAB_CONFIG.get(sKey, "")
                        if sValue == "":
                            sResult += f"Config non presente {sKey}. "
                    
                    # SMTP.FROM
                    sValue = self.JOBS_TAB_CONFIG.get("SMTP.FROM", "")
                    if sValue and not aiSys.isEmail(sValue):
                        sResult += "SMTP.FROM non è email. "
                    
                    # SMTP.SSL
                    sValue = self.JOBS_TAB_CONFIG.get("SMTP.SSL", "")
                    if sValue and not aiSys.isBool(sValue):
                        sResult += "SMTP.SSL non corretto. "
                    
                    # SMTP.TLS
                    sValue = self.JOBS_TAB_CONFIG.get("SMTP.TLS", "")
                    if sValue and not aiSys.isBool(sValue):
                        sResult += "SMTP.TLS non corretto. "
            
            # Verifica JOBS_TAB_USERS
            if self.JOBS_TAB_USERS:
                for sUser, dictValue in self.JOBS_TAB_USERS.items():
                    # USER_ID
                    sValue = dictValue.get("USER_ID", "")
                    if sValue and not sValue.isalnum():
                        sResult += f"Errore verifica USER_ID, per user {sUser}. "
                    
                    # USER_PASSWORD
                    sValue = dictValue.get("USER_PASSWORD", "")
                    if sValue:
                        import re
                        if not re.match(r'^[a-zA-Z0-9_\.!#]+$', sValue):
                            sResult += f"Errore verifica USER_PASSWORD, per user {sUser}. "
                    
                    # USER_NAME
                    sValue = dictValue.get("USER_NAME", "")
                    if sValue and not sValue.replace(" ", "").isalpha():
                        sResult += f"Errore verifica USER_NAME, per user {sUser}. "
                    
                    # USER_GROUPS
                    sValue = dictValue.get("USER_GROUPS", "")
                    if sValue:
                        groups = aiSys.StringToArray(sValue)
                        for group in groups:
                            if group not in self.asGroups:
                                sResult += f"Errore verifica USER_GROUPS, per user {sUser}. "
                    
                    # USER_PATHS
                    sValue = dictValue.get("USER_PATHS", "")
                    if sValue:
                        paths = aiSys.StringToArray(sValue)
                        for path in paths:
                            if not aiSys.isValidPath(path):
                                sResult += f"Errore verifica USER_PATHS, per user {sUser}. "
                    
                    # USER_MAIL
                    sValue = dictValue.get("USER_MAIL", "")
                    if sValue and not aiSys.isEmail(sValue):
                        sResult += f"Errore verifica USER_MAIL, per user {sUser}. "
            
            # Verifica JOBS_TAB_GROUPS
            if self.JOBS_TAB_GROUPS:
                for sGroup, dictValue in self.JOBS_TAB_GROUPS.items():
                    # GROUP_ID
                    sValue = dictValue.get("GROUP_ID", "")
                    if sValue and not sValue.isalnum():
                        sResult += f"Errore verifica GROUP_ID, per Gruppo {sGroup}. "
                    
                    # GROUP_NAME
                    sValue = dictValue.get("GROUP_NAME", "")
                    if sValue and not sValue.replace(" ", "").isalpha():
                        sResult += f"Errore verifica GROUP_NAME, per Gruppo {sGroup}. "
            
            # Verifica JOBS_TAB_ACTIONS
            if self.JOBS_TAB_ACTIONS:
                for sAction, dictValue in self.JOBS_TAB_ACTIONS.items():
                    # ACT_ID
                    sValue = dictValue.get("ACT_ID", "")
                    if sValue and not sValue.isalnum():
                        sResult += f"Errore verifica ACT_ID, per action {sAction}. "
                    
                    # ACT_NAME
                    sValue = dictValue.get("ACT_NAME", "")
                    if sValue and not sValue.replace(" ", "").isalpha():
                        sResult += f"Errore verifica ACT_NAME, per action {sAction}. "
                    
                    # ACT_GROUPS
                    sValue = dictValue.get("ACT_GROUPS", "")
                    if sValue:
                        groups = aiSys.StringToArray(sValue)
                        for group in groups:
                            if group not in self.asGroups:
                                sResult += f"Errore verifica ACT_GROUPS, per action {sAction}. "
                    
                    # ACT_ENABLED
                    sValue = dictValue.get("ACT_ENABLED", "")
                    if sValue and not aiSys.isBool(sValue):
                        sResult += f"Errore verifica ACT_ENABLED, per action {sAction}. "
                    
                    # ACT_PATH
                    sValue = dictValue.get("ACT_PATH", "")
                    if sValue and not aiSys.isValidPath(sValue):
                        sResult += f"Errore verifica ACT_PATH, per action {sAction}. "
            
            if sResult != "":
                self.Log1(sResult)
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Start_Mail(self):
        sProc = "Start_Mail"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            sEngine = self.Config("MAIL.ENGINE")
            
            if sEngine == "SMTP":
                # Import dinamico di ncMailSimple
                try:
                    from ncMailSimple import ncMailSimple
                    self.jMail = ncMailSimple()
                except ImportError as e:
                    sResult = f"Impossibile importare ncMailSimple: {str(e)}"
                    self.Log1(sResult)
                    return f"{sProc}: {sResult}"
                
                if sResult == "":
                    self.sMailAdmin = self.Config("ADMIN.EMAIL")
                    sSmtp_User = self.Config("SMTP.USER")
                    sSmtp_Pwd = self.Config("SMTP.PASSWORD")
                    sSmtp_Port = self.Config("SMTP.PORT")
                    sSmtp_Host = self.Config("SMTP.SERVER")
                    bSmtp_SSL = aiSys.StringBoolean(self.Config("SMTP.SSL"))
                    sSmtp_From = self.Config("SMTP.FROM")
                    
                    # Verifica campi obbligatori
                    required = [sSmtp_User, sSmtp_Pwd, sSmtp_Port, sSmtp_Host, sSmtp_From]
                    if any(field == "" for field in required):
                        sResult = "Settings mail non presenti in config"
                    
                    if sResult == "":
                        nSmtp_Port = aiSys.StringToNum(sSmtp_Port)
                        sResult = self.jMail.Start(sSmtp_User, sSmtp_Pwd, sSmtp_Host, 
                                                   nSmtp_Port, 30, bSmtp_SSL, True)
                        
                        if sResult == "":
                            self.sMailEngine = "SMTP"
            
            elif sEngine == "OLK":
                self.sSys_PathOlk = self.Config("MAIL.PATH")
                self.sSys_Olk = aiSys.PathMake(self.sSys_PathOlk, "ntj_sendmail_olk", "cmd")
                
                if not os.path.exists(self.sSys_Olk):
                    sResult = "OLK MAIL NON PRESENTE"
                else:
                    self.sMailEngine = "OLK"
            
            else:
                sResult = f"Mail engine non riconosciuto: {sEngine}"
            
            if sResult != "":
                self.Log1(sResult)
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Start_End(self):
        sProc = "Start_End"
        sResult = ""
        
        try:
            sResult = self.JobsEnd()
            if sResult != "":
                return f"{sProc}: {sResult}"
            
            # Creazione file jobs.end di errore
            sFileEnd = aiSys.PathMake(self.sSys_PathRoot, "jobs", "end")
            dictError = {
                "CONFIG": {
                    "TYPE": "NTJOBS.CONFIG.1",
                    "ERROR": "Startup failed"
                }
            }
            sResult = aiSys.save_dict_to_ini(dictError, sFileEnd)
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    # =========================================================================
    # METODI PRINCIPALI DI ESECUZIONE
    # =========================================================================
    def Run(self):
        sProc = "Run"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            while not self.bExitOS:
                # Sequenza di operazioni principali
                methods = [self.Search, self.Get, self.Archive]
                for method in methods:
                    sResult = method()
                    if sResult != "":
                        self.Log1(sResult)
                        self.bExitOS = True
                        break
                
                if not self.bExitOS:
                    sResult = self.CycleEnd()
                    if sResult != "":
                        self.Log1(sResult)
                
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult

    def Search(self):
        sProc = "Search"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            for sPath in self.asPaths:
                sFileJobs = aiSys.PathMake(sPath, "jobs", "ini")
                if os.path.exists(sFileJobs):
                    sResultTemp = self.Move(sPath)
                    if sResultTemp != "":
                        sResult += sResultTemp + ", "
                    else:
                        self.Log(sResultTemp, f"Trovato jobs.ini in {sPath}")
            
            if sResult.endswith(", "):
                sResult = sResult[:-2]
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Move(self, sPath):
        sProc = "Move"
        sResult = ""
        
        try:
            sFileJobs = aiSys.PathMake(sPath, "jobs", "ini")
            sResult, dictTemp = aiSys.read_ini_to_dict(sFileJobs)
            
            if sResult != "":
                return self.MoveError(sResult, sPath)
            
            if "CONFIG" not in dictTemp:
                sResult = f"File senza CONFIG {sFileJobs}"
                return self.MoveError(sResult, sPath)
            
            # Creazione cartella inbox
            sPathInbox = aiSys.PathMake(self.sSys_PathInbox, f"job_{aiSys.Timestamp()}", "")
            try:
                os.makedirs(sPathInbox, exist_ok=True)
            except Exception as e:
                sResult = f"Errore creazione path inbox {sPathInbox}: {str(e)}"
                return self.MoveError(sResult, sPath)
            
            sLogMove = ""
            
            # Spostamento jobs.ini
            sDestJobs = aiSys.PathMake(sPathInbox, "jobs", "ini")
            try:
                os.rename(sFileJobs, sDestJobs)
                sLogMove = f"Spostato jobs.ini in {sPathInbox}"
            except Exception as e:
                sResult = f"Non spostabile {sFileJobs}: {str(e)}"
                return self.MoveError(sResult, sPath)
            
            # Spostamento file associati
            for sSection in dictTemp.values():
                if isinstance(sSection, dict):
                    for sKey, sValue in sSection.items():
                        if sKey.startswith("FILE."):
                            sFileMove = sValue
                            sSrcFile = aiSys.PathMake(sPath, sFileMove, "")
                            sDestFile = aiSys.PathMake(sPathInbox, sFileMove, "")
                            
                            if os.path.exists(sSrcFile):
                                try:
                                    os.rename(sSrcFile, sDestFile)
                                    sLogMove += f" Spostato file {sFileMove}. "
                                except Exception as e:
                                    sResult = f"Non spostabile {sFileMove}: {str(e)}"
                                    break
            
            if sResult != "":
                return self.MoveError(sResult, sPath)
            
            if sLogMove:
                self.Log(sLogMove, "")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            return self.MoveError(sResult, sPath)
        
        return sResult

    def MoveError(self, sResult, sPath):
        sProc = "MoveError"
        
        try:
            sFileIni = aiSys.PathMake(sPath, "jobs", "ini")
            sFileTemp = aiSys.PathMake(sPath, "jobs", "end")
            
            # Invio mail all'utente
            sMailResult = self.MailUser("Errore in esecuzione jobs.ini", sResult)
            
            # Rinominazione file
            if os.path.exists(sFileIni):
                try:
                    os.rename(sFileIni, sFileTemp)
                except Exception as e:
                    sResult = f"Errore rinomina ini in end: {sFileTemp}: {str(e)}"
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Get(self):
        sProc = "Get"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            if not os.path.exists(self.sSys_PathInbox):
                return sResult
            
            for sFolder in os.listdir(self.sSys_PathInbox):
                sFolderPath = aiSys.PathMake(self.sSys_PathInbox, sFolder, "")
                if os.path.isdir(sFolderPath):
                    sFileJobs = aiSys.PathMake(sFolderPath, "jobs", "ini")
                    sFileEnd = aiSys.PathMake(sFolderPath, "jobs", "end")
                    
                    if os.path.exists(sFileJobs) and not os.path.exists(sFileEnd):
                        sResult = self.Exec(sFolderPath)
                        if sResult != "":
                            self.Log1(sResult)
                        
                        # Esegui JobsEnd comunque
                        sResultEnd = self.JobsEnd()
                        if sResultEnd != "":
                            self.Log1(sResultEnd)
                        
                        # Solo un job per ciclo
                        break
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Exec(self, sPath):
        sProc = "Exec"
        sResult = ""
        print(f"Esecuzione aiJobsOS {sProc}")
        
        try:
            bExitJobs = False
            
            # Startup del Jobs
            sResult = self.JobsInit(sPath)
            if sResult != "":
                bExitJobs = True
                sResult = f"Errore JobsInit: {sResult} {sPath}"
                self.Log1(sResult)
                return sResult
            
            # Esecuzione singoli jobs
            for sKey in self.dictJobs.keys():
                if sKey == "CONFIG" or bExitJobs:
                    continue
                
                self.sJob = sKey
                sResult = self.JobExec()
                if sResult != "":
                    bExitJobs = True
                
                sResultEnd = self.JobEnd(sResult, "")
                if sResultEnd != "":
                    self.Log1(sResultEnd)
            
            # Fine elaborazione jobs.ini
            sResult = self.JobsEnd()
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        self.Log1(sResult)
        return sResult

    def CycleEnd(self):
        sProc = "CycleEnd"
        
        self.nCycleCounter += 1
        print(f"Ciclo Run: {self.nCycleCounter}, Time: {aiSys.Timestamp()}, Attesa: {self.nCycleWait}")
        
        time.sleep(self.nCycleWait)
        return ""

    # =========================================================================
    # METODI DI SUPPORTO
    # =========================================================================
    def JobsInit(self, sJobPath):
        sProc = "JobsInit"
        sResult = ""
        
        try:
            self.sJobsFile = aiSys.PathMake(sJobPath, "jobs", "ini")
            
            sResult, dictTemp = aiSys.read_ini_to_dict(self.sJobsFile)
            if sResult != "":
                sResult = f"Errore lettura path {self.sJobsFile}"
                return sResult
            
            self.dictJobs = dictTemp.copy()
            self.sJobsPath = sJobPath
            self.sJobTS = aiSys.Timestamp()
            
            # Aggiornamento configurazione
            sResult = self.ConfigUpdate()
            if sResult != "":
                return sResult
            
            # Login utente
            sResult = self.Login()
            if sResult != "":
                return sResult
            
            self.Log0(sResult, f"Caricato jobs.ini {sJobPath}")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def JobsEnd(self):
        sProc = "JobsEnd"
        sResult = ""
        
        try:
            # Rimozione USER e PASSWORD dalla sezione CONFIG
            if "CONFIG" in self.dictJobs:
                config_section = self.dictJobs["CONFIG"]
                if "USER" in config_section:
                    del config_section["USER"]
                if "PASSWORD" in config_section:
                    del config_section["PASSWORD"]
            
            # Salvataggio jobs.end
            sFileEnd = self.JobsFileEnd()
            if sFileEnd:
                sResult = aiSys.save_dict_to_ini(self.dictJobs, sFileEnd)
                if sResult != "":
                    return sResult
            
            # Invio mail
            sResult = self.JobsMail(sResult)
            
            # Logoff
            self.Logoff()
            
            # Reset campi
            self.dictJobs = {}
            self.sJobsPath = ""
            self.sJob = ""
            self.asJobs = []
            self.asJobFiles = []
            self.sScript = ""
            self.sJobTS = ""
            
            self.Log0(sResult, f"Salvato {sFileEnd}")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def JobsFileEnd(self):
        if not self.sJobsFile:
            self.Log1("Errore interno, sJobsFile non avvalorato")
            return ""
        
        base_name = os.path.splitext(os.path.basename(self.sJobsFile))[0]
        sTemp = aiSys.PathMake(os.path.dirname(self.sJobsFile), base_name, "end")
        return sTemp

    def JobsMail(self, sResult):
        sProc = "JobsMail"
        
        try:
            sText = sResult if sResult else ""
            
            sJobsEnd = aiSys.PathMake(self.sJobsPath, "jobs", "end")
            if os.path.exists(sJobsEnd):
                sResultRead, dictTemp = aiSys.read_ini_to_dict(sJobsEnd)
                if sResultRead == "" and "CONFIG" in dictTemp:
                    config_section = dictTemp["CONFIG"]
                    if "USER" in config_section:
                        del config_section["USER"]
                    if "PASSWORD" in config_section:
                        del config_section["PASSWORD"]
                    
                    sTemp = self.jDTS.DictToString(dictTemp, "ini.sect")
                    sText = sResult + "\n\n" + sTemp if sResult else sTemp
            
            sResult = self.MailUser("Completamento jobs.ini", sText)
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def JobAction(self):
        sProc = "JobAction"
        sResult = ""
        
        try:
            self.sAction = self.dictJob.get("ACTION", "")
            
            if self.sAction not in self.asActions:
                sResult = f"Errore Azione non presente {self.sAction}"
                return sResult
            
            self.dictAction = self.JOBS_TAB_ACTIONS.get(self.sAction, {}).copy()
            
            bEnabled = aiSys.StringBoolean(self.dictAction.get("ACT_ENABLED", "False"))
            if not bEnabled:
                sResult = f"Action {self.sAction} disabilitata"
                return sResult
            
            # Verifica gruppi
            sUserGroups = self.dictUser.get("USER_GROUPS", "")
            sActionGroups = self.dictAction.get("ACT_GROUPS", "")
            
            if not aiSys.isGroups(sUserGroups, sActionGroups):
                sResult = f"Azione non eseguibile per gruppi incompatibili {self.sAction}"
                return sResult
            
            sScript = self.dictAction.get("ACT_SCRIPT", "")
            if not sScript:
                sResult = "Script non assegnato"
                return sResult
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def JobExec(self):
        sProc = "JobExec"
        sResult = ""
        
        try:
            self.dictJob = self.dictJobs.get(self.sJob, {}).copy()
            self.tsJob = aiSys.Timestamp()
            
            # Interpreta azione
            sResult = self.JobAction()
            if sResult != "":
                sResult = f"Errore interpretazione azione {self.sAction}, Err: {sResult}"
                return sResult
            
            # Imposta directory corrente
            sCurDir = self.dictAction.get("ACT_PATH", "")
            if sCurDir:
                try:
                    os.chdir(sCurDir)
                except:
                    sResult = f"Impossibile cambiare directory in {sCurDir}"
                    return sResult
            else:
                sCurDir = self.sJobsPath
            
            # Espansione valori nel dictJob
            for sKey, sValue in list(self.dictJob.items()):
                if sKey == "ACTION":
                    self.dictJob["ACTION.ROOT"] = sValue
                    del self.dictJob[sKey]
                elif sKey == "COMMAND":
                    self.dictJob["ACTION"] = sValue
                    del self.dictJob[sKey]
                else:
                    self.dictJob[sKey] = aiSys.Expand(sValue, self.dictConfig)
            
            # Azioni interne che iniziano con "sys."
            if self.sAction.startswith("sys."):
                sResult = self.JobInternal(self.sAction)
                return sResult
            
            # Esecuzione comando esterno
            self.sScript = self.dictAction.get("ACT_SCRIPT", "")
            self.sActionPath = self.dictAction.get("ACT_PATH", "")
            
            # Creazione dizionario combinato
            dictTemp = {}
            dictTemp.update(self.dictConfig)
            dictTemp.update(self.dictJob)
            
            # Salvataggio ntjobsapp.ini
            sFileIni = aiSys.PathMake(os.getcwd(), "ntjobsapp", "ini")
            sResult = aiSys.save_dict_to_ini(dictTemp, sFileIni)
            if sResult != "":
                return sResult
            
            # Esecuzione comando
            try:
                self.pidJob = subprocess.Popen(self.sScript, shell=True)
            except Exception as e:
                sResult = f"Non eseguibile in job {self.sJob}, {self.sScript}: {str(e)}"
                return sResult
            
            # Attesa completamento
            sResult = self.JobExecWait()
            if sResult != "":
                return sResult
            
            # Fine job
            sResult = self.JobEnd(sResult, "")
            
            self.Log(sResult, f"Eseguito job {self.sJob}")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        # Reset finali
        self.sJob = ""
        self.dictJob = None
        
        return sResult

    def JobExecWait(self):
        sProc = "JobExecWait"
        sResult = ""
        
        try:
            sTimeOut = self.dictAction.get("ACT_TIMEOUT", "")
            if sTimeOut:
                nTimeout2 = aiSys.StringToNum(sTimeOut)
            else:
                nTimeout2 = 0
            
            if nTimeout2 == 0:
                sTimeoutConfig = self.Config("TIMEOUT")
                nTimeout = aiSys.StringToNum(sTimeoutConfig)
            else:
                nTimeout = nTimeout2
            
            if nTimeout < 50:
                sResult = f"Errore timeout specificato per job {self.sJob}"
                return sResult
            
            start_time = time.time()
            sFileAppEnd = aiSys.PathMake(os.getcwd(), "ntjobsapp", "end")
            
            while time.time() - start_time < nTimeout:
                if os.path.exists(sFileAppEnd):
                    break
                
                if self.pidJob.poll() is not None:
                    break
                
                time.sleep(10)
            else:
                sResult = f"Timeout esecuzione {self.sJob},{self.sJobsFile}"
                self.JobCleanup()
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def JobCleanup(self):
        sProc = "JobCleanup"
        
        try:
            if hasattr(self, 'pidJob') and self.pidJob:
                if self.pidJob.poll() is None:
                    self.pidJob.terminate()
                    try:
                        self.pidJob.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.pidJob.kill()
                        self.pidJob.wait()
                self.pidJob = None
        except Exception as e:
            return f"{sProc}: Errore - {str(e)}"
        
        return ""

    def JobEnd(self, sResult, sValue=""):
        sProc = "JobEnd"
        
        try:
            # Skip lettura ntjobsapp.end per azioni sys.*
            if not self.sAction.startswith("sys."):
                # Lettura ntjobsapp.end
                dictTemp = {}
                sJobFileEnd = aiSys.PathMake(os.getcwd(), "ntjobsapp", "end")
                
                if os.path.exists(sJobFileEnd):
                    sResultRead, dictTemp = aiSys.read_ini_to_dict(sJobFileEnd)
                    if sResultRead == "":
                        try:
                            os.remove(sJobFileEnd)
                        except:
                            pass
                        
                        # Togli entry CONFIG se esiste
                        if "CONFIG" in dictTemp:
                            del dictTemp["CONFIG"]
                        
                        # Aggiorna dictJob con valori dal file end
                        if dictTemp:
                            self.dictJob.update(dictTemp)
            
            # Aggiornamento self.dictJob
            self.dictJob["TS.START"] = self.tsJob
            self.dictJob["TS.END"] = aiSys.Timestamp()
            
            if sResult == "":
                self.dictJob["RETURN.VALUE"] = sValue
                self.dictJob["RETURN.TYPE"] = "S"
            else:
                self.dictJob["RETURN.VALUE"] = f"Errore: {sResult}, Valore: {sValue}"
                self.dictJob["RETURN.TYPE"] = "E"
            
            # Aggiorna il job nel dictJobs
            self.dictJobs[self.sJob] = self.dictJob.copy()
            
            # Reset
            self.sScript = ""
            self.sAction = ""
            self.dictAction = None
            
            self.Log(sResult, f"Eseguito Job {self.sJob}: {sValue}")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def JobInternal(self, sAction):
        sProc = "JobInternal"
        sResult = ""
        
        try:
            if sAction == "sys.reload":
                sFileReload = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "reload")
                with open(sFileReload, "w") as f:
                    f.write(aiSys.Timestamp())
            
            elif sAction == "sys.quit":
                sFileQuit = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "quit")
                with open(sFileQuit, "w") as f:
                    f.write(aiSys.Timestamp())
                self.bExitOS = True
            
            elif sAction == "sys.shutdown":
                sFileShutdown = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "shutdown")
                with open(sFileShutdown, "w") as f:
                    f.write(aiSys.Timestamp())
                self.bExitOS = True
            
            elif sAction == "sys.reboot":
                sFileReboot = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "reboot")
                with open(sFileReboot, "w") as f:
                    f.write(aiSys.Timestamp())
                self.bExitOS = True
            
            elif sAction == "sys.email.admin":
                sResult = self.MailAdmin("Notifica da aiJobsOS", 
                                        f"Comando eseguito dall'utente {self.sUser}")
            
            elif sAction == "sys.email.user":
                sResult = self.MailUser("ntJobs Test Email utente corrente", 
                                       f"Prova di invio mail da parte dell'utente corrente {self.sUser}")
            
            else:
                sResult = f"Azione interna non riconosciuta: {sAction}"
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Login(self):
        sProc = "Login"
        sResult = ""
        
        try:
            if "CONFIG" not in self.dictJobs:
                sResult = "Sezione CONFIG non trovata in jobs.ini"
                return sResult
            
            dictTemp = self.dictJobs["CONFIG"].copy()
            sUserVerify = dictTemp.get("USER", "")
            sPwdVerify = dictTemp.get("PASSWORD", "")
            
            if not sUserVerify or sUserVerify not in self.JOBS_TAB_USERS:
                sResult = f"Utente non trovato {sUserVerify}"
                return sResult
            
            dictUserTemp = self.JOBS_TAB_USERS[sUserVerify].copy()
            sUser = dictUserTemp.get("USER_ID", "")
            sPwd = dictUserTemp.get("USER_PASSWORD", "")
            
            if sPwd != sPwdVerify or sUser != sUserVerify:
                sResult = f"Credenziali non valide per utente {sUserVerify}"
                return sResult
            
            # Conversione USER_GROUPS in array
            sGroups = dictUserTemp.get("USER_GROUPS", "")
            if sGroups:
                dictUserTemp["USER_GROUPS"] = aiSys.StringToArray(sGroups)
            
            self.sUser = sUser
            self.dictUser = dictUserTemp
            
            self.Log0(sResult, f"Login utente {sUser}, Risultato: {sResult}")
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Logoff(self):
        self.dictUser = None
        self.sUser = ""
        return ""

    def MailUser(self, sSubject, sText):
        sProc = "MailUser"
        sResult = ""
        
        try:
            if not self.dictUser:
                sResult = "Utente non loggato"
                return sResult
            
            sUserMail = self.dictUser.get("USER_MAIL", "")
            if not sUserMail:
                sResult = "Email utente non definita"
                return sResult
            
            sResult = self.Mail(sUserMail, sSubject, sText, [])
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def MailAdmin(self, sSubject, sText):
        sProc = "MailAdmin"
        sResult = ""
        
        try:
            sMail = self.Config("ADMIN.EMAIL")
            if not sMail:
                sResult = "Email amministratore non definita"
                return sResult
            
            sResult = self.Mail(sMail, sSubject, sText, [])
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    def Archive(self):
        sProc = "Archive"
        sResult = ""
        
        try:
            # 1. Esiste la cartella inbox?
            if not os.path.exists(self.sSys_PathInbox):
                return sResult  # Niente da archiviare
            
            # 2. VERIFICA NECESSARIA: Esiste la cartella archivio?
            # (Devi verificarla per poter controllare le sue sottocartelle)
            if not os.path.exists(self.sSys_PathArchive):
                # Se non esiste, non possiamo controllare duplicati né spostare
                # Questo È l'errore che dici "viene ritornato in sResult"
                sResult = f"Cartella archivio non esiste: {self.sSys_PathArchive}"
                self.Log1(sResult)
                return sResult
            
            # 3. Scansione delle sottocartelle
            for sFolder in os.listdir(self.sSys_PathInbox):
                sPathFound = aiSys.PathMake(self.sSys_PathInbox, sFolder, "")
                
                if os.path.isdir(sPathFound):
                    sFileJobs = aiSys.PathMake(sPathFound, "jobs", "ini")
                    sFileEnd = aiSys.PathMake(sPathFound, "jobs", "end")
                    
                    # 4. Job completato?
                    if os.path.exists(sFileJobs) and os.path.exists(sFileEnd):
                        sDestPath = aiSys.PathMake(self.sSys_PathArchive, sFolder, "")
                        
                        # 5. Se esiste già: log e skip
                        if os.path.exists(sDestPath):
                            self.Log1(f"Errore doppio folder {sPathFound}")
                            continue  # "non fare nulla"
                        
                        # 6. Spostamento
                        try:
                            os.rename(sPathFound, sDestPath)
                            self.Log0("", f"Archiviata cartella {sFolder}")
                        except Exception as e:
                            error_msg = f"Errore spostamento {sPathFound} in {self.sSys_PathArchive}. {str(e)}."
                            sResult += error_msg + " "
            
            # 7. Pulizia
            if sResult.endswith(" "):
                sResult = sResult[:-1]
                
            if sResult != "":
                self.Log1(sResult)
                
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
            self.Log1(sResult)
        
        return sResult
    
    def Mail(self, sTo, sSubject, sText, asFiles=None):
        sProc = "Mail"
        sResult = ""
        
        if asFiles is None:
            asFiles = []
        
        try:
            if not sTo:
                sResult = "Destinatario non specificato"
                return sResult
            
            # Verifica file allegati
            for sFile in asFiles:
                if not os.path.exists(sFile):
                    sResult = "File allegati non tutti esistenti"
                    return sResult
            
            if self.sMailEngine == "SMTP":
                if not self.jMail:
                    sResult = "Mail engine SMTP non inizializzato"
                    return sResult
                
                sResult = self.jMail.Send([sTo], sSubject, sText, asFiles, "TXT")
                
            elif self.sMailEngine == "OLK":
                # Creazione file JSON per OLK
                mail_data = {
                    "config": {
                        "nWaitStart": 3,
                        "nWaitMail": 20,
                        "bOlkStart": True,
                        "bOlkEnd": False
                    },
                    "mail_1": {
                        "id": "mail_001",
                        "to": [sTo],
                        "cc": [""],
                        "ccn": [],
                        "subject": sSubject,
                        "format": "txt",
                        "body": sText,
                        "attach": asFiles
                    }
                }
                
                sJsonFile = aiSys.PathMake(self.sSys_PathOlk, "ntjobs_mail", "json")
                try:
                    with open(sJsonFile, "w") as f:
                        json.dump(mail_data, f, indent=2)
                except Exception as e:
                    sResult = f"Errore creazione file JSON: {str(e)}"
                    return sResult
                
                sCmd = f'"{self.sSys_Olk}" "{sJsonFile}"'
                try:
                    subprocess.Popen(sCmd, shell=True)
                except Exception as e:
                    sResult = f"Errore esecuzione comando OLK: {str(e)}"
            else:
                sResult = "Mail Engine non inizializzato"
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        return sResult

    # =========================================================================
    # METODI DI CONFIGURAZIONE E LOG
    # =========================================================================
    def Config(self, sKey):
        """
        Ritorna una configurazione salvata in self.dictConfig
        Parametro sKey: Stringa "Obbligatorio".
        
        Logica:
        1. Se sKey è stringa vuota, ritorna ""
        2. Se dictConfig è None, ritorna ""
        3. Se sKey non esiste in dictConfig, ritorna ""
        4. Se il valore è None, ritorna ""
        5. Altrimenti converte il valore in stringa
        6. Se la conversione fallisce, ritorna ""
        """
        sProc = "Config"
        
        # 1. Se sKey è vuota
        if sKey == "":
            return ""
        
        # 2. Se dictConfig è None
        if self.dictConfig is None:
            return ""
        
        # 3. Se la chiave non esiste in dictConfig
        if sKey not in self.dictConfig:
            return ""
        
        # 4. Ottieni il valore
        value = self.dictConfig[sKey]
        
        # 5. Se il valore è None, ritorna ""
        if value is None:
            return ""
        
        # 6. Converti in stringa
        try:
            sResult = str(value)
            # Verifica che la conversione non abbia prodotto "None" come stringa
            # (nel caso improbabile che qualcuno abbia salvato la stringa "None")
            if sResult == "None" and value is not None:
                # Questo caso non dovrebbe mai verificarsi perché value != None
                # ma è una sicurezza aggiuntiva
                return ""
            return sResult
        except Exception as e:
            # 7. Se la conversione fallisce, ritorna ""
            # Opzionale: log dell'errore (commentato per non appesantire i log)
            # self.Log1(f"{sProc}: Errore conversione valore '{sKey}': {str(e)}")
            return ""

    def ConfigUpdate(self):
        sProc = "ConfigUpdate"
        sResult = ""
        
        try:
            if self.JOBS_TAB_CONFIG is None:
                sResult = "Tabella Config.ini non caricata"
                return sResult
            
            dictTemp = self.JOBS_TAB_CONFIG.copy()
            
            if "CONFIG" in self.dictJobs:
                sResult = aiSys.DictMerge(dictTemp, self.dictJobs["CONFIG"])
                if sResult != "":
                    return sResult
            
            sResult = aiSys.ExpandDict(dictTemp, dictTemp)
            if sResult != "":
                return sResult
            
            self.dictConfig = dictTemp.copy()
            
        except Exception as e:
            sResult = f"Eccezione in {sProc}: {str(e)}"
        
        if sResult != "":
            self.Log1(sResult)
        
        return sResult

    def Log(self, sType, sValue):
        if self.jLog:
            self.jLog.Log(sType, sValue)

    def Log0(self, sResult, sValue):
        if self.jLog:
            self.jLog.Log0(sResult, sValue)

    def Log1(self, sResult):
        if self.jLog:
            self.jLog.Log1(sResult)


# =============================================================================
# FUNZIONE MAIN
# =============================================================================
def main():
    print("=== AVVIO aiJobsOS ===")
    
    # Istanza della classe
    jData = acJobsOS()
    
    # Inizializzazione
    sResult = jData.Start()
    if sResult != "":
        print(f"Errore in esecuzione ntJobs: {sResult}")
        return 1
    
    # Ciclo principale
    jData.bExitOS = False
    while not jData.bExitOS:
        sResult = jData.Run()
        if sResult != "":
            jData.Log1(f"Errore in Esecuzione Run: {sResult}")
        
        # CycleEnd solo se non ci sono errori
        if sResult == "":
            sResult = jData.CycleEnd()
            if sResult != "":
                jData.Log1(sResult)
    
    print("=== TERMINE aiJobsOS ===")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)