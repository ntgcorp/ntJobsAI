
#!/usr/bin/env python3
# Nomefile: acJobsStart.py
# -*- coding: utf-8 -*-

"""
acJobsStart - Classe mixin per l'inizializzazione dell'ambiente aiJobsOS
"""

import os
import sys
import time
from typing import Dict, Any, Optional, Union, List
from copy import deepcopy

# Import da aiSys (si assume sia disponibile)
import aiSys


class acJobsStart:
    """
    Mixin per l'inizializzazione dell'ambiente aiJobsOS.
    Contiene i metodi per il caricamento delle configurazioni,
    utenti, gruppi, azioni e inizializzazione del sistema.
    """
    
    def JobsStart(self) -> str:
        """
        Inizializza l'istanza della classe acJobsOS.
        Esegue in sequenza i metodi di inizializzazione.
        """
        sProc = "JobsStart"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        # Timestamp inizio sessione
        self.tsStart = aiSys.TimeStamp()
        self.tsSearch = self.tsStart
        
        # Cartella di esecuzione dell'applicazione
        self.sSys_PathRoot = os.path.dirname(os.path.abspath(__file__))
        
        # Inizializza log
        sLogFile = self.Config("LOG")
        self.jLog = aiSys.acLog()
        sResult = self.jLog.Start(sLogFile)
        
        if sResult == "":
            print("Istanziata LOG")
            sResult = self.JobsStart_ReadIni()
        
        if sResult == "":
            # Inizializza variabili da config
            self.sSys_PathInbox = self.Config("INBOX")
            self.sSys_PathArchive = self.Config("ARCHIVE")
            self.nCycleCounter = 0
            
            self.ConfigUpdate()
            
            sTemp = self.Config("CYCLE.WAIT")
            if sTemp == "":
                self.nCycleWait = 60
            else:
                self.nCycleWait = aiSys.StringToNum(sTemp)
            
            sTemp = self.Config("SEARCH.WAIT")
            if sTemp == "":
                self.nSearchWait = 900
            else:
                self.nSearchWait = aiSys.StringToNum(sTemp)
            
            print("Caricata CONFIG.INI")
        
        if sResult == "":
            sResult = self.JobsStart_ReadDat()
            if sResult == "":
                print("Caricati DAT")
        
        if sResult == "":
            sResult = self.JobsStart_ReadPaths()
            if sResult == "":
                print("Caricati PATHS")
        
        if sResult == "":
            sResult = self.JobsStart_Expand()
        
        if sResult == "":
            sResult = self.JobsStart_Verify()
        
        if sResult == "":
            sResult = self.JobsStart_Mail()
        
        if sResult != "":
            self.JobsStart_End()
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_ReadIni(self) -> str:
        """
        Legge il file ntjobs_config.ini di configurazione dell'applicazione.
        """
        sProc = "JobsStart_ReadIni"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        sFileIni = aiSys.PathMake(self.sSys_PathRoot, "ntjobs_config", "ini")
        print("Lettura file " + sFileIni)
        
        sResult, dictTemp = aiSys.read_ini_to_dict(sFileIni)
        
        if sResult == "":
            print("Impostazioni di default")
            
            sLogFile = aiSys.PathMake(self.sSys_PathRoot, "JobOS", "log")
            
            # Default settings
            default_config = {
                "PATHROOT": self.sSys_PathRoot,
                "TIMEOUT": "60",
                "MAIL.ENGINE": "SMTP",
                "WAIT.CYCLE": "300",
                "WAIT.SEARCH": "900",
                "LOG": sLogFile
            }
            
            for sKey, sValue in default_config.items():
                if sKey not in dictTemp:
                    aiSys.ConfigSet(dictTemp, sKey, sValue)
            
            print("Espansione dizionario Config")
            dictTemp2 = deepcopy(dictTemp)
            aiSys.ExpandDict(dictTemp, dictTemp2)
            
            self.JOBS_TAB_CONFIG = deepcopy(dictTemp)
            self.ConfigUpdate()
            
            print("Dizionario letto, espanso, aggiornato")
            aiSys.DictPrint(self.dictConfig)
        
        self.Log1(sResult)
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_ReadDat(self) -> str:
        """
        Legge tutti i file .csv di configurazione.
        """
        sProc = "JobsStart_ReadDat"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        # Mappatura file CSV -> dizionario target e array header
        csv_files = [
            ("ntjobs_actions.csv", "JOBS_TAB_ACTIONS", self.JOBS_DAT_ACTIONS),
            ("ntjobs_groups.csv", "JOBS_TAB_GROUPS", self.JOBS_DAT_GROUPS),
            ("ntjobs_users.csv", "JOBS_TAB_USERS", self.JOBS_DAT_USERS)
        ]
        
        for sFileName, sTabName, avHeader in csv_files:
            sFileCSV = aiSys.PathMake(self.sSys_PathRoot, sFileName)
            sResult, dictTemp = aiSys.read_csv_to_dict(sFileCSV, avHeader)
            
            if sResult != "":
                self.Log1(sResult)
                break
            
            # Assegna al dizionario corrispondente
            if sTabName == "JOBS_TAB_ACTIONS":
                self.JOBS_TAB_ACTIONS = deepcopy(dictTemp)
                self.asActions = list(self.JOBS_TAB_ACTIONS.keys())
            elif sTabName == "JOBS_TAB_GROUPS":
                self.JOBS_TAB_GROUPS = deepcopy(dictTemp)
                self.asGroups = list(self.JOBS_TAB_GROUPS.keys())
            elif sTabName == "JOBS_TAB_USERS":
                self.JOBS_TAB_USERS = deepcopy(dictTemp)
                self.asUsers = list(self.JOBS_TAB_USERS.keys())
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_ReadPaths(self) -> str:
        """
        Inizializza il dizionario self.dictPaths con tutti i path degli utenti.
        """
        sProc = "JobsStart_ReadPaths"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        dictTemp = {}
        
        for sUser, dictUser in self.JOBS_TAB_USERS.items():
            sPaths = dictUser.get("USER_PATHS", "")
            asPaths = aiSys.StringToArray(sPaths, ",")
            
            for sPathSingle in asPaths:
                sPathSingle = aiSys.Expand(sPathSingle, self.dictConfig)
                sPathSingle = sPathSingle.strip()
                
                if not sPathSingle:
                    self.Log1(f"Path vuoto per user {sUser}")
                    continue
                
                if not aiSys.DirExists(sPathSingle):
                    self.Log1(f"Path non esistente per user {sUser}: {sPathSingle}")
                
                dictTemp[sPathSingle] = sUser
        
        self.dictPaths = deepcopy(dictTemp)
        self.asPaths = list(self.dictPaths.keys())
        
        # Verifica esistenza folder
        for sPath in self.asPaths:
            if not aiSys.DirExists(sPath):
                sResult += f"Non trovato Path {sPath}. "
        
        if sResult:
            self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_Mail(self) -> str:
        """
        Inizializza il sistema di mail (SMTP o OLK).
        """
        sProc = "JobsStart_Mail"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        sEngine = self.Config("MAIL.ENGINE")
        
        if sEngine == "SMTP":
            print("Inizializzazione SMTP")
            
            try:
                from NcMailSimple import NcMailSimple
                self.jMail = NcMailSimple()
            except Exception as e:
                sResult = f"Errore creazione NcMailSimple: {str(e)}"
            
            if sResult == "":
                self.sMailAdmin = self.Config("ADMIN.EMAIL")
                sSmtp_User = self.Config("SMTP.USER")
                sSmtp_Pwd = self.Config("SMTP.PASSWORD")
                nSmtp_Port = aiSys.StringToNum(self.Config("SMTP.PORT"))
                sSmtp_Host = self.Config("SMTP.SERVER")
                bSmtp_SSL = aiSys.StringBool(self.Config("SMTP.SSL"))
                sSmtp_From = self.Config("SMTP.FROM")
                
                if not all([sSmtp_User, sSmtp_Pwd, sSmtp_Host, nSmtp_Port, sSmtp_From]):
                    sResult = "Settings mail non presenti in config"
            
            if sResult == "":
                sResult = self.jMail.Start(sSmtp_User, sSmtp_Pwd, sSmtp_Host, 
                                          nSmtp_Port, 30, bSmtp_SSL, True)
                if sResult == "":
                    self.sMailEngine = "SMTP"
        
        elif sEngine == "OLK":
            print("Inizializzazione OLK")
            self.sSys_PathOlk = self.Config("MAIL.PATH")
            self.sSys_Olk = ""
            
            if not aiSys.DirExists(self.sSys_PathOlk):
                sResult = "OLK MAIL NON PRESENTE"
            else:
                self.sSys_Olk = aiSys.PathMake(self.sSys_PathOlk, "ntj_sendmail_olk", "cmd")
        
        if sResult == "":
            self.sMailEngine = sEngine
        else:
            self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_Expand(self) -> str:
        """
        Espande le variabili e codici escape nelle tabelle di configurazione.
        """
        sProc = "JobsStart_Expand"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        # Espandi dictConfig
        aiSys.ExpandDict(self.dictConfig, self.dictConfig)
        
        # Espandi tabelle
        for dictTemp in [self.JOBS_TAB_USERS, self.JOBS_TAB_GROUPS, self.JOBS_TAB_ACTIONS]:
            if dictTemp:
                aiSys.ExpandDict(dictTemp, self.dictConfig)
        
        print("Conclusione Start.Expand")
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_Verify(self) -> str:
        """
        Verifica la congruità delle tabelle di memoria dei parametri.
        """
        sProc = "JobsStart_Verify"
        sResult = ""
        
        print("Esecuzione aiJobsOS " + sProc)
        
        # Verifica JOBS_TAB_CONFIG
        print("Verifica JOBS_TAB_CONFIG")
        for sKey, sValue in self.JOBS_TAB_CONFIG.items():
            if sKey == "ADMIN.EMAIL":
                if not aiSys.isEmail(sValue):
                    sResult += "ADMIN.MAIL non corretta. "
            elif sKey == "TYPE":
                if sValue != "NTJOBS.CONFIG.1":
                    sResult += "TYPE non corretta. "
            elif sKey == "INBOX":
                if not aiSys.isValidPath(sValue):
                    sResult += "INBOX non corretta. "
            elif sKey == "LOG":
                sPath = os.path.dirname(sValue)
                if not aiSys.isValidPath(sPath):
                    sResult += "LOG non corretta. "
            elif sKey == "ARCHIVE":
                if not aiSys.isValidPath(sValue):
                    sResult += "ARCHIVE non corretta. "
            elif sKey == "MAIL.ENGINE":
                if sValue not in ["OLK", "SMTP"]:
                    sResult += "MAIL.ENGINE non corretta. "
            elif sKey == "MAIL.PATH":
                if sValue and not aiSys.isValidPath(sValue):
                    sResult += "MAIL.PATH non corretta. "
        
        # Verifiche SMTP
        if self.JOBS_TAB_CONFIG.get("MAIL.ENGINE") == "SMTP":
            print("Verifica JOBS_TAB_CONFIG SMTP")
            for sKey in self.JOBS_DAT_CONFIG_SMTP:
                if sKey not in self.JOBS_TAB_CONFIG or not self.JOBS_TAB_CONFIG[sKey]:
                    sResult += f"Config non presente {sKey}. "
                else:
                    sValue = self.JOBS_TAB_CONFIG[sKey]
                    if sKey == "SMTP.FROM" and not aiSys.isEmail(sValue):
                        sResult += "SMTP.FROM non è email. "
                    elif sKey == "SMTP.SSL" and not aiSys.StringBool(sValue):
                        sResult += "SMTP.SSL non corretto. "
                    elif sKey == "SMTP.TLS" and not aiSys.StringBool(sValue):
                        sResult += "SMTP.TLS non corretto. "
        
        # Verifica JOBS_TAB_USERS
        print("Verifica JOBS_TAB_USERS")
        for sUser, dictValue in self.JOBS_TAB_USERS.items():
            for sKey, sVal in dictValue.items():
                if sKey == "USER":
                    if not sVal or not sVal.isalnum():
                        sResult += f"Errore verifica {sKey}, per user {sUser}. "
                elif sKey == "USER_NAME":
                    if sVal and not sVal.replace(" ", "").isalpha():
                        sResult += f"Errore verifica {sKey}, per user {sUser}. "
                elif sKey == "USER_GROUPS":
                    asGroups = aiSys.StringToArray(sVal, ",")
                    for sGroup in asGroups:
                        if sGroup not in self.asGroups:
                            sResult += f"Errore verifica {sKey}, gruppo {sGroup} non esiste per user {sUser}. "
                elif sKey == "USER_PATHS":
                    asPaths = aiSys.StringToArray(sVal, ",")
                    for sPath in asPaths:
                        sPathExp = aiSys.Expand(sPath, self.dictConfig)
                        if not aiSys.DirExists(sPathExp):
                            sResult += f"Errore verifica {sKey}, path {sPathExp} non esiste per user {sUser}. "
                elif sKey == "USER_MAIL":
                    if not aiSys.isEmail(sVal):
                        sResult += f"Errore verifica {sKey}, per user {sUser}. "
        
        # Verifica JOBS_TAB_GROUPS
        print("Verifica JOBS_TAB_GROUPS")
        for sGroup, dictValue in self.JOBS_TAB_GROUPS.items():
            for sKey, sVal in dictValue.items():
                if sKey == "GROUP_ID":
                    if not sVal or not sVal.isalnum():
                        sResult += f"Errore verifica {sKey}, per Gruppo {sGroup}. "
                elif sKey == "GROUP_NAME":
                    if sVal and not sVal.replace(" ", "").isalpha():
                        sResult += f"Errore verifica {sKey}, per Gruppo {sGroup}. "
        
        # Verifica JOBS_TAB_ACTIONS
        print("Verifica JOBS_TAB_ACTIONS")
        for sAction, dictValue in self.JOBS_TAB_ACTIONS.items():
            for sKey, sVal in dictValue.items():
                if sKey == "ACT_ID":
                    if not sVal or not sVal.isalnum():
                        sResult += f"Errore verifica {sKey}, per action {sAction}. "
                elif sKey == "ACT_NAME":
                    if sVal and not sVal.replace(" ", "").isalpha():
                        sResult += f"Errore verifica {sKey}, per action {sAction}. "
                elif sKey == "ACT_GROUPS":
                    asGroups = aiSys.StringToArray(sVal, ",")
                    for sGroup in asGroups:
                        if sGroup not in self.asGroups:
                            sResult += f"Errore verifica {sKey}, gruppo {sGroup} non esiste per action {sAction}. "
                elif sKey == "ACT_ENABLED":
                    if not isinstance(aiSys.StringBool(sVal), bool):
                        sResult += f"Errore verifica {sKey}, per action {sAction}. "
                elif sKey == "ACT_PATH":
                    if sVal and not aiSys.DirExists(sVal):
                        sResult += f"Errore verifica {sKey}, path {sVal} non esiste per action {sAction}. "
        
        if sResult:
            self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsStart_End(self) -> None:
        """
        Determina la fine di una esecuzione di istanza partita male.
        """
        sProc = "JobsStart_End"
        print("Esecuzione aiJobsOS " + sProc)
        print("Fine aiJobsOS.Start")
        self.JobsEnd()


