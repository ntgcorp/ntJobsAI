# aiJobsOS.py
# Sistema di automazione batch ntJobsOS
# Principale classe acJobsOS e logica di orchestrazione

import os
import sys
import time
import shutil
import json
import subprocess
from typing import Dict, List, Tuple, Any, Optional
import configparser
from pathlib import Path

# Importa le librerie di supporto
import aiSys
from ncMailSimple import NC_MailSimple

# ============================================================================
# CLASSE PRINCIPALE acJobsOS
# ============================================================================

class acJobsOS:
    """
    Classe principale di ntJobsOS per l'orchestrazione di elaborazioni batch.
    """
    
    def __init__(self):
        """Inizializza l'oggetto acJobsOS."""
        sProc = "__init__"
        
        try:
            # Campi principali
            self.sJobPath = ""
            self.sJob = ""
            self.sJobsFile = ""
            self.asJobs = []
            self.asJobFiles = []
            
            # Dizionari di configurazione
            self.dictConfig = {}
            self.dictJobs = {}
            self.dictJob = {}
            self.dictPaths = {}
            self.asPaths = []
            
            # Gestione utenti e gruppi
            self.asUsers = []
            self.dictUser = {}
            self.sUser = ""
            
            # Gestione azioni
            self.asActions = []
            self.sAction = ""
            self.sActionIni = ""
            self.dictAction = {}
            self.sActionPath = ""
            self.sScript = ""
            
            # Campi DAT e TAB (array e dizionari)
            self.JOBS_DAT_USERS = [
                "USER_ID", "USER_PASSWORD", "USER_NAME", "USER_NOTES",
                "USER_GROUPS", "USER_PATHS", "USER_MAIL"
            ]
            
            self.JOBS_DAT_GROUPS = [
                "GROUP_ID", "GROUP_NAME", "GROUP_NOTES"
            ]
            
            self.JOBS_DAT_ACTIONS = [
                "ACT_ID", "ACT_NAME", "ACT_GROUPS", "ACT_SCRIPT",
                "ACT_ENABLED", "ACT_PATH", "ACT_HELP", "ACT_TIMEOUT"
            ]
            
            self.JOBS_DAT_CONFIG = [
                "ADMIN.EMAIL", "TYPE", "SYSROOT", "INBOX", "ARCHIVE", "MAIL.ENGINE"
            ]
            
            self.JOBS_DAT_CONFIG_SMTP = [
                "SMTP.FROM", "SMTP.PASSWORD", "SMTP.PORT", "SMTP.SERVER",
                "SMTP.SSL", "SMTP.TLS", "SMTP.USER"
            ]
            
            # Tabelle (dizionari di dizionari)
            self.JOBS_TAB_USERS = {}
            self.JOBS_TAB_GROUPS = {}
            self.JOBS_TAB_ACTIONS = {}
            self.JOBS_TAB_CONFIG = {}
            
            # Campi associati all'utente corrente
            self.dictUser = {}
            self.sUser = ""
            
            # Campi vari interni
            self.bExitJob = False
            self.bExitOS = False
            self.jLog = aiSys.acLog()
            self.jIni = configparser.ConfigParser()
            self.jIni.optionxform = str  # Mantieni case originale
            
            # Mail engine
            self.jMail = None
            self.sMailEngine = ""
            self.sMailAdmin = ""
            
            # Timestamps
            self.tsStart = ""
            self.tsJobs = ""
            self.tsJob = ""
            
            # Processi
            self.pidJob = None
            
            # Paths di sistema (inizializzati da config)
            self.sSys_PathRoot = ""
            self.sSys_PathInbox = ""
            self.sSys_PathArchive = ""
            self.sSys_PathOlk = ""
            self.sSys_Olk = ""
            
            # Contatori e timeout
            self.nCycleCounter = 0
            self.nCycleWait = 60
            
            print(f"{sProc}: Inizializzazione acJobsOS completata")
            
        except Exception as e:
            print(f"{sProc}: Errore - {str(e)}")
            raise
    
    # ========================================================================
    # METODI DI INIZIALIZZAZIONE
    # ========================================================================
    
    def Start(self) -> str:
        """
        Inizializza l'applicazione ntJobsOS.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Inizializza timestamp
            self.tsStart = aiSys.Timestamp()
            
            # Configura log
            sLogFile = self.Config("LOG")
            self.jLog.Start(sLogFile)
            
            # Inizializza configparser
            self.jIni = configparser.ConfigParser()
            self.jIni.optionxform = str
            
            # Sequenza di inizializzazione
            sResult = self.Start_ReadIni()
            if sResult:
                return sProc + ": " + sResult
            
            # Inizializza variabili da config
            self.sSys_PathRoot = self.Config("SYSROOT")
            self.sSys_PathInbox = self.Config("INBOX")
            self.sSys_PathArchive = self.Config("ARCHIVE")
            
            # Contatori
            self.nCycleCounter = 0
            sTemp = self.Config("CYCLE.WAIT")
            if not sTemp:
                self.nCycleWait = 60
            else:
                self.nCycleWait = aiSys.StringToNum(sTemp)
            
            # Aggiorna configurazione
            self.ConfigUpdate()
            
            # Continua inizializzazione
            sResult = self.Start_ReadDat()
            if sResult:
                return sProc + ": " + sResult
            
            sResult = self.Start_ReadPaths()
            if sResult:
                return sProc + ": " + sResult
            
            sResult = self.Start_Verify()
            if sResult:
                return sProc + ": " + sResult
            
            sResult = self.Start_Mail()
            if sResult:
                return sProc + ": " + sResult
            
            self.jLog.Log1(f"Inizializzazione ntJobsOS completata: {self.tsStart}")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.Start_End()
            return sProc + ": " + sResult
    
    def Start_ReadIni(self) -> str:
        """
        Legge il file di configurazione ntjobs_config.ini.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start_ReadIni"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Determina path del file config
            sConfigFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ntjobs_config.ini")
            
            if not os.path.exists(sConfigFile):
                sResult = f"File di configurazione non trovato: {sConfigFile}"
                self.jLog.Log1(sResult)
                return sResult
            
            # Leggi file INI
            self.jIni.read(sConfigFile, encoding='utf-8')
            
            # Converti in dizionario
            self.JOBS_TAB_CONFIG = {}
            for section in self.jIni.sections():
                self.JOBS_TAB_CONFIG[section] = {}
                for key, value in self.jIni.items(section):
                    self.JOBS_TAB_CONFIG[section][key] = value
            
            # Verifica sezione CONFIG
            if "CONFIG" not in self.JOBS_TAB_CONFIG:
                sResult = "Sezione CONFIG non trovata in ntjobs_config.ini"
                self.jLog.Log1(sResult)
                return sResult
            
            # Copia sezione CONFIG come dizionario principale
            self.dictConfig = self.JOBS_TAB_CONFIG["CONFIG"].copy()
            
            # Aggiorna configurazione
            self.ConfigUpdate()
            
            # Verifica settings obbligatori
            missing_keys = []
            for key in self.JOBS_DAT_CONFIG:
                if key not in self.dictConfig:
                    missing_keys.append(key)
            
            if missing_keys:
                sResult = f"Settings obbligatori mancanti: {', '.join(missing_keys)}"
                self.jLog.Log1(sResult)
                return sResult
            
            # Imposta valori default se mancanti
            if not self.Config("TIMEOUT"):
                self.ConfigSet("TIMEOUT", "60")
            
            if not self.Config("EXPAND"):
                self.ConfigSet("EXPAND", "True")
            
            if not self.Config("MAIL.ENGINE"):
                self.ConfigSet("MAIL.ENGINE", "SMTP")
            
            # Espandi configurazione
            self.ConfigUpdate()
            sResult = self.Start_Expand(self.dictConfig, self.dictConfig)
            
            if sResult:
                self.jLog.Log1(sResult)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def Start_ReadDat(self) -> str:
        """
        Legge i file CSV di configurazione.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start_ReadDat"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            sRootPath = self.sSys_PathRoot
            
            # Leggi file delle azioni
            sActionsFile = os.path.join(sRootPath, "ntjobs_actions.csv")
            sResult, self.JOBS_TAB_ACTIONS = aiSys.read_csv_to_dict(sActionsFile, ';')
            
            if sResult:
                return f"Errore lettura ntjobs_actions.csv: {sResult}"
            
            # Verifica campi obbligatori per azioni
            for action_id, action_data in self.JOBS_TAB_ACTIONS.items():
                for field in self.JOBS_DAT_ACTIONS:
                    if field not in action_data:
                        return f"Campo {field} mancante in azione {action_id}"
            
            # Leggi file dei gruppi
            sGroupsFile = os.path.join(sRootPath, "ntjobs_groups.csv")
            sResult, self.JOBS_TAB_GROUPS = aiSys.read_csv_to_dict(sGroupsFile, ';')
            
            if sResult:
                return f"Errore lettura ntjobs_groups.csv: {sResult}"
            
            # Verifica campi obbligatori per gruppi
            for group_id, group_data in self.JOBS_TAB_GROUPS.items():
                for field in self.JOBS_DAT_GROUPS:
                    if field not in group_data:
                        return f"Campo {field} mancante in gruppo {group_id}"
            
            # Leggi file degli utenti
            sUsersFile = os.path.join(sRootPath, "ntjobs_users.csv")
            sResult, self.JOBS_TAB_USERS = aiSys.read_csv_to_dict(sUsersFile, ';')
            
            if sResult:
                return f"Errore lettura ntjobs_users.csv: {sResult}"
            
            # Verifica campi obbligatori per utenti
            for user_id, user_data in self.JOBS_TAB_USERS.items():
                for field in self.JOBS_DAT_USERS:
                    if field not in user_data:
                        return f"Campo {field} mancante in utente {user_id}"
            
            # Espandi tutte le tabelle
            for dictData in [self.JOBS_TAB_ACTIONS, self.JOBS_TAB_GROUPS, self.JOBS_TAB_USERS]:
                sResult = self.Start_Expand(dictData, self.dictConfig)
                if sResult:
                    return sResult
            
            # Estrai lista utenti e azioni
            self.asUsers = list(self.JOBS_TAB_USERS.keys())
            self.asActions = list(self.JOBS_TAB_ACTIONS.keys())
            
            self.jLog.Log1(f"Letti {len(self.asUsers)} utenti e {len(self.asActions)} azioni")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def Start_ReadPaths(self) -> str:
        """
        Inizializza i paths da monitorare.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start_ReadPaths"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            self.dictPaths = {}
            
            # Raccogli paths da tutti gli utenti
            for sUser, user_data in self.JOBS_TAB_USERS.items():
                sUserPaths = user_data.get("USER_PATHS", "")
                if sUserPaths:
                    # Converti in array e pulisci
                    asPaths = aiSys.StringToArray(sUserPaths, ',')
                    for sPath in asPaths:
                        sPathClean = sPath.strip()
                        if sPathClean:
                            self.dictPaths[sPathClean] = sUser
            
            # Espandi i paths
            dictPathsExpanded = {}
            for sPath, sUser in self.dictPaths.items():
                sPathExpanded = aiSys.Expand(sPath, self.dictConfig)
                dictPathsExpanded[sPathExpanded] = sUser
            
            self.dictPaths = dictPathsExpanded
            self.asPaths = list(self.dictPaths.keys())
            
            # Verifica esistenza paths
            missing_paths = []
            for sPath in self.asPaths:
                if not os.path.exists(sPath):
                    missing_paths.append(sPath)
            
            if missing_paths:
                sResult = f"Paths non trovati: {', '.join(missing_paths)}"
                self.jLog.Log1(sResult)
            
            self.jLog.Log1(f"Inizializzati {len(self.asPaths)} paths da monitorare")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def Start_Mail(self) -> str:
        """
        Inizializza il sistema di email.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start_Mail"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            sEngine = self.Config("MAIL.ENGINE")
            self.sMailAdmin = self.Config("ADMIN.EMAIL")
            
            if sEngine.upper() == "SMTP":
                # Inizializza SMTP
                self.jMail = NC_MailSimple()
                
                # Ottieni parametri SMTP
                sSmtp_User = self.Config("SMTP.USER")
                sSmtp_Pwd = self.Config("SMTP.PASSWORD")
                sSmtp_Host = self.Config("SMTP.SERVER")
                nSmtp_Port = aiSys.StringToNum(self.Config("SMTP.PORT"))
                bSmtp_SSL = aiSys.StringBoolean(self.Config("SMTP.SSL"))
                sSmtp_From = self.Config("SMTP.FROM")
                
                # Verifica parametri obbligatori
                required_params = [
                    ("SMTP.USER", sSmtp_User),
                    ("SMTP.PASSWORD", sSmtp_Pwd),
                    ("SMTP.SERVER", sSmtp_Host),
                    ("SMTP.PORT", nSmtp_Port),
                    ("SMTP.FROM", sSmtp_From)
                ]
                
                missing = [name for name, value in required_params if not value]
                if missing:
                    sResult = f"Parametri mail SMTP mancanti: {', '.join(missing)}"
                    self.jLog.Log1(sResult)
                    return sResult
                
                # Connetti al server SMTP
                sResult = self.jMail.Start(sSmtp_User, sSmtp_Pwd, sSmtp_Host, 
                                         nSmtp_Port, 30, bSmtp_SSL, True)
                
                if not sResult:
                    self.sMailEngine = "SMTP"
                    self.jLog.Log1("Mail engine SMTP inizializzato")
                else:
                    self.jLog.Log1(f"Errore inizializzazione SMTP: {sResult}")
                    
            elif sEngine.upper() == "OLK":
                # Configura Outlook
                self.sSys_PathOlk = self.Config("MAIL.PATH")
                if not self.sSys_PathOlk:
                    sResult = "MAIL.PATH non configurato per OLK"
                    self.jLog.Log1(sResult)
                    return sResult
                
                self.sSys_Olk = os.path.join(self.sSys_PathOlk, "ntj_sendmail_olk.cmd")
                
                if not os.path.exists(self.sSys_Olk):
                    sResult = f"Script OLK non trovato: {self.sSys_Olk}"
                    self.jLog.Log1(sResult)
                    return sResult
                
                self.sMailEngine = "OLK"
                self.jLog.Log1("Mail engine OLK configurato")
                
            else:
                sResult = f"Mail engine non supportato: {sEngine}"
                self.jLog.Log1(sResult)
                return sResult
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def Start_Expand(self, dictExpand: Dict[str, Any], dictParams: Dict[str, str]) -> str:
        """
        Espande variabili in un dizionario.
        
        Args:
            dictExpand: Dizionario da espandere
            dictParams: Dizionario parametri per espansione
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start_Expand"
        sResult = ""
        
        try:
            # Verifica se l'espansione è abilitata
            if not aiSys.StringBoolean(self.Config("EXPAND")):
                return sResult
            
            # Usa ExpandDict di aiSys
            expanded = aiSys.ExpandDict(dictExpand, dictParams)
            
            # Aggiorna il dizionario originale
            dictExpand.clear()
            dictExpand.update(expanded)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def Start_Verify(self) -> str:
        """
        Verifica la congruità delle configurazioni.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Start_Verify"
        sResult = ""
        errors = []
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Verifica CONFIG
            admin_email = self.Config("ADMIN.EMAIL")
            if not aiSys.isEmail(admin_email):
                errors.append("ADMIN.EMAIL non valida")
            
            config_type = self.Config("TYPE")
            if config_type != "NTJOBS.CONFIG.1":
                errors.append(f"TYPE deve essere 'NTJOBS.CONFIG.1', trovato '{config_type}'")
            
            for path_key in ["SYSROOT", "INBOX", "ARCHIVE"]:
                path = self.Config(path_key)
                if not aiSys.isValidPath(path):
                    errors.append(f"{path_key} non valido: {path}")
            
            mail_engine = self.Config("MAIL.ENGINE")
            if mail_engine not in ["OLK", "SMTP"]:
                errors.append(f"MAIL.ENGINE deve essere 'OLK' o 'SMTP', trovato '{mail_engine}'")
            
            # Verifica USERS
            for user_id, user_data in self.JOBS_TAB_USERS.items():
                if not aiSys.isAlphanumeric(user_id):
                    errors.append(f"USER_ID non alfanumerico: {user_id}")
                
                password = user_data.get("USER_PASSWORD", "")
                if not aiSys.isValidPassword(password):
                    errors.append(f"USER_PASSWORD non valida per utente {user_id}")
                
                user_name = user_data.get("USER_NAME", "")
                if user_name and not aiSys.isLettersOnly(user_name, bAllowSpaces=True):
                    errors.append(f"USER_NAME contiene caratteri non validi: {user_name}")
                
                groups = user_data.get("USER_GROUPS", "")
                if groups:
                    group_list = aiSys.StringToArray(groups, ',')
                    for group in group_list:
                        if not aiSys.isAlphanumeric(group, "._"):
                            errors.append(f"USER_GROUPS contiene gruppo non valido per utente {user_id}: {group}")
                
                user_mail = user_data.get("USER_MAIL", "")
                if not aiSys.isEmail(user_mail):
                    errors.append(f"USER_MAIL non valida per utente {user_id}: {user_mail}")
                
                # Verifica paths
                user_paths = user_data.get("USER_PATHS", "")
                if user_paths:
                    path_list = aiSys.StringToArray(user_paths, ',')
                    for path in path_list:
                        expanded_path = aiSys.Expand(path, self.dictConfig)
                        if not aiSys.isValidPath(expanded_path):
                            errors.append(f"USER_PATHS contiene path non valido per utente {user_id}: {path}")
            
            # Verifica GROUPS
            for group_id, group_data in self.JOBS_TAB_GROUPS.items():
                if not aiSys.isAlphanumeric(group_id):
                    errors.append(f"GROUP_ID non alfanumerico: {group_id}")
                
                group_name = group_data.get("GROUP_NAME", "")
                if group_name and not aiSys.isLettersOnly(group_name, bAllowSpaces=True):
                    errors.append(f"GROUP_NAME contiene caratteri non validi: {group_name}")
            
            # Verifica ACTIONS
            for action_id, action_data in self.JOBS_TAB_ACTIONS.items():
                if not aiSys.isAlphanumeric(action_id):
                    errors.append(f"ACT_ID non alfanumerico: {action_id}")
                
                action_name = action_data.get("ACT_NAME", "")
                if action_name and not aiSys.isLettersOnly(action_name, bAllowSpaces=True):
                    errors.append(f"ACT_NAME contiene caratteri non validi: {action_name}")
                
                groups = action_data.get("ACT_GROUPS", "")
                if groups:
                    group_list = aiSys.StringToArray(groups, ',')
                    for group in group_list:
                        if not aiSys.isAlphanumeric(group, "._"):
                            errors.append(f"ACT_GROUPS contiene gruppo non valido per azione {action_id}: {group}")
                
                enabled = action_data.get("ACT_ENABLED", "")
                if not aiSys.isBool(enabled):
                    errors.append(f"ACT_ENABLED non booleano per azione {action_id}: {enabled}")
                
                action_path = action_data.get("ACT_PATH", "")
                if action_path:
                    expanded_path = aiSys.Expand(action_path, self.dictConfig)
                    if not aiSys.isValidPath(expanded_path):
                        errors.append(f"ACT_PATH non valido per azione {action_id}: {action_path}")
            
            # Verifica mail admin
            if self.sMailAdmin and not aiSys.isEmail(self.sMailAdmin):
                errors.append(f"Mail amministratore non valida: {self.sMailAdmin}")
            
            if errors:
                sResult = "Errori di verifica: " + "; ".join(errors)
                self.jLog.Log1(sResult)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def Start_End(self) -> None:
        """
        Gestisce la fine di un'avvio fallito.
        """
        sProc = "Start_End"
        
        try:
            sResult = f"Avvio ntJobsOS fallito: {self.tsStart}"
            self.Return(sResult)
            self.jLog.Log1(sResult)
            
        except Exception as e:
            print(f"{sProc}: Errore - {str(e)}")
    
    # ========================================================================
    # METODI PRINCIPALI DI ESECUZIONE
    # ========================================================================
    
    def Run(self) -> str:
        """
        Ciclo principale di esecuzione ntJobsOS.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Run"
        sResult = ""
        
        try:
            while not self.bExitOS:
                # Esegui le fasi principali
                sResult = self.Search()
                if sResult:
                    self.jLog.Log0(sResult, "Errore in Search")
                
                sResult = self.Get()
                if sResult:
                    self.jLog.Log0(sResult, "Errore in Get")
                
                sResult = self.Archive()
                if sResult:
                    self.jLog.Log0(sResult, "Errore in Archive")
                
                # Fine ciclo
                sResult = self.CycleEnd()
                if sResult:
                    self.bExitOS = True
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore in Run")
            return sResult
    
    def Search(self) -> str:
        """
        Cerca file jobs.ini nei paths configurati.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Search"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            for sPath in self.asPaths:
                sJobsFile = os.path.join(sPath, "jobs.ini")
                
                if os.path.exists(sJobsFile):
                    # Sposta il file in inbox
                    sResultTemp = self.Move(sPath)
                    
                    if sResultTemp:
                        sResult += sResultTemp + ", "
                        self.jLog.Log0(sResultTemp, f"Errore spostamento jobs.ini da {sPath}")
                    else:
                        self.jLog.Log1(f"Trovato e spostato jobs.ini da {sPath}")
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore in Search")
            return sResult
    
    def Move(self, sPath: str) -> str:
        """
        Sposta un file jobs.ini e allegati in inbox.
        
        Args:
            sPath: Path sorgente
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Move"
        sResult = ""
        
        try:
            sFileJobs = os.path.join(sPath, "jobs.ini")
            
            # Leggi file jobs.ini
            if not os.path.exists(sFileJobs):
                sResult = f"File jobs.ini non trovato: {sFileJobs}"
                return self.MoveError(sResult, sPath)
            
            # Leggi con configparser
            temp_ini = configparser.ConfigParser()
            temp_ini.optionxform = str
            
            try:
                temp_ini.read(sFileJobs, encoding='utf-8')
            except Exception as e:
                sResult = f"Errore lettura jobs.ini: {str(e)}"
                return self.MoveError(sResult, sPath)
            
            # Verifica sezione CONFIG
            if "CONFIG" not in temp_ini.sections():
                sResult = "File jobs.ini senza sezione CONFIG"
                return self.MoveError(sResult, sPath)
            
            # Crea cartella inbox
            sTimestamp = aiSys.Timestamp()
            sPathInbox = os.path.join(self.sSys_PathInbox, f"job_{sTimestamp}")
            
            try:
                os.makedirs(sPathInbox, exist_ok=True)
            except Exception as e:
                sResult = f"Errore creazione cartella inbox: {str(e)}"
                return self.MoveError(sResult, sPath)
            
            # Sposta jobs.ini
            sDestFile = os.path.join(sPathInbox, "jobs.ini")
            try:
                shutil.move(sFileJobs, sDestFile)
            except Exception as e:
                sResult = f"Errore spostamento jobs.ini: {str(e)}"
                return self.MoveError(sResult, sPath)
            
            # Sposta file allegati
            for section in temp_ini.sections():
                for key, value in temp_ini.items(section):
                    if key.startswith("FILE."):
                        sSourceFile = os.path.join(sPath, value)
                        sDestFile = os.path.join(sPathInbox, value)
                        
                        if os.path.exists(sSourceFile):
                            try:
                                shutil.move(sSourceFile, sDestFile)
                            except Exception as e:
                                sResult = f"Errore spostamento file {value}: {str(e)}"
                                return self.MoveError(sResult, sPath)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return self.MoveError(sResult, sPath)
    
    def MoveError(self, sResult: str, sPath: str) -> str:
        """
        Gestisce errori durante lo spostamento.
        
        Args:
            sResult: Messaggio di errore
            sPath: Path sorgente
            
        Returns:
            str: Messaggio di errore
        """
        sProc = "MoveError"
        
        try:
            sFileIni = os.path.join(sPath, "jobs.ini")
            sFileTemp = os.path.join(sPath, "jobs.end")
            
            # Notifica utente via mail
            sUser = self.dictPaths.get(sPath, "")
            if sUser and sUser in self.JOBS_TAB_USERS:
                user_mail = self.JOBS_TAB_USERS[sUser].get("USER_MAIL", "")
                if user_mail:
                    self.Mail(user_mail, "Errore in esecuzione jobs.ini", sResult, [])
            
            # Rinomina file per evitare rielaborazione
            if os.path.exists(sFileIni):
                try:
                    os.rename(sFileIni, sFileTemp)
                except:
                    pass
            
            self.jLog.Log0(sResult, f"Errore in Move per path {sPath}")
            return sResult
            
        except Exception as e:
            return f"{sProc}: Errore - {str(e)}"
    
    def Get(self) -> str:
        """
        Preleva ed esegue jobs dalla inbox.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Get"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Scansiona cartelle inbox
            if not os.path.exists(self.sSys_PathInbox):
                return sResult
            
            for item in os.listdir(self.sSys_PathInbox):
                sFolderPath = os.path.join(self.sSys_PathInbox, item)
                
                if os.path.isdir(sFolderPath):
                    sJobsFile = os.path.join(sFolderPath, "jobs.ini")
                    sJobsEnd = os.path.join(sFolderPath, "jobs.end")
                    
                    # Se c'è jobs.ini ma non jobs.end, esegui
                    if os.path.exists(sJobsFile) and not os.path.exists(sJobsEnd):
                        sResult = self.Exec(sFolderPath)
                        if sResult:
                            self.jLog.Log0(sResult, f"Errore esecuzione in {sFolderPath}")
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore in Get")
            return sResult
    
    def Exec(self, sPath: str) -> str:
        """
        Esegue un file jobs.ini.
        
        Args:
            sPath: Path della cartella con jobs.ini
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Exec"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Inizializza jobs
            sResult = self.JobsInit(sPath)
            if sResult:
                self.bExitJob = True
                sResult = f"Errore JobsInit: {sResult}"
                self.jLog.Log1(sResult)
                return sResult
            
            # Esegui tutti i jobs
            for sKey in self.dictJobs:
                if sKey == "CONFIG":
                    continue
                
                self.sJob = sKey
                sResult = self.JobInit()
                
                if not sResult:
                    sResult = self.JobExec()
                    self.jLog.Log1(sResult)
                
                if self.bExitJob:
                    break
            
            # Fine elaborazione jobs
            sResult = self.JobsEnd()
            
            self.jLog.Log1(sResult)
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def CycleEnd(self) -> str:
        """
        Completa un ciclo di elaborazione.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "CycleEnd"
        sResult = ""
        
        try:
            self.nCycleCounter += 1
            sTimestamp = aiSys.Timestamp()
            
            sMsg = f"Ciclo Run: {self.nCycleCounter}, Time: {sTimestamp}, Attesa: {self.nCycleWait}"
            print(sMsg)
            self.jLog.Log1(sMsg)
            
            # Attesa tra cicli
            time.sleep(self.nCycleWait)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore in CycleEnd")
            return sResult
    
    def Archive(self) -> str:
        """
        Archivia job completati.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Archive"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            if not os.path.exists(self.sSys_PathInbox):
                return sResult
            
            if not os.path.exists(self.sSys_PathArchive):
                os.makedirs(self.sSys_PathArchive, exist_ok=True)
            
            for item in os.listdir(self.sSys_PathInbox):
                sFolderPath = os.path.join(self.sSys_PathInbox, item)
                
                if os.path.isdir(sFolderPath):
                    sJobsIni = os.path.join(sFolderPath, "jobs.ini")
                    sJobsEnd = os.path.join(sFolderPath, "jobs.end")
                    
                    # Se entrambi i file esistono, archivia
                    if os.path.exists(sJobsIni) and os.path.exists(sJobsEnd):
                        sDestPath = os.path.join(self.sSys_PathArchive, item)
                        
                        try:
                            if os.path.exists(sDestPath):
                                # Elimina destinazione esistente
                                shutil.rmtree(sDestPath)
                            
                            shutil.move(sFolderPath, sDestPath)
                            self.jLog.Log1(f"Archiviato job: {item}")
                            
                        except Exception as e:
                            sErr = f"Errore archiviazione {item}: {str(e)}"
                            sResult += sErr + ", "
                            self.jLog.Log0(sErr, "Errore in Archive")
            
            if sResult:
                self.jLog.Log1(sResult)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    # ========================================================================
    # METODI DI GESTIONE JOBS
    # ========================================================================
    
    def JobsInit(self, sJobPath: str) -> str:
        """
        Inizializza l'esecuzione di un file jobs.ini.
        
        Args:
            sJobPath: Path della cartella con jobs.ini
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobsInit"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            self.sJobsFile = os.path.join(sJobPath, "jobs.ini")
            self.sJobPath = sJobPath
            
            # Leggi file jobs.ini
            if not os.path.exists(self.sJobsFile):
                sResult = f"File jobs.ini non trovato: {self.sJobsFile}"
                self.jLog.Log0(sResult, "Errore JobsInit")
                return sResult
            
            self.jIni.read(self.sJobsFile, encoding='utf-8')
            
            # Converti in dizionario
            self.dictJobs = {}
            for section in self.jIni.sections():
                self.dictJobs[section.upper()] = {}
                for key, value in self.jIni.items(section):
                    self.dictJobs[section.upper()][key.upper()] = value
            
            # Inizializza variabili
            self.asJobs = [key for key in self.dictJobs.keys() if key != "CONFIG"]
            self.tsJobs = aiSys.Timestamp()
            self.bExitJob = False
            
            # Aggiorna configurazione e login
            self.ConfigUpdate()
            sResult = self.Login()
            
            self.jLog.Log0(sResult, f"Caricato jobs.ini {sJobPath}")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore JobsInit")
            return sResult
    
    def JobsEnd(self) -> str:
        """
        Termina l'esecuzione di un file jobs.ini.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobsEnd"
        sResult = ""
        
        try:
            # Invia mail di riepilogo
            sResult = self.JobsMail()
            
            # Rimuovi credenziali da CONFIG
            if "CONFIG" in self.dictJobs:
                config_section = self.dictJobs["CONFIG"]
                config_section.pop("USER", None)
                config_section.pop("PASSWORD", None)
            
            # Salva jobs.end
            sResultSave = self.Return(sResult)
            if sResultSave:
                sResult = sResultSave
            
            # Logoff e reset
            self.Logoff()
            
            # Reset variabili job
            self.dictJobs = {}
            self.sJobPath = ""
            self.sJob = ""
            self.asJobs = []
            self.asJobFiles = []
            self.sScript = ""
            self.dictJob = {}
            self.sJobsFile = ""
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore JobsEnd")
            return sResult
    
    def JobsMail(self) -> str:
        """
        Invia mail di riepilogo per jobs completati.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobsMail"
        sResult = ""
        
        try:
            sText = ""
            if sResult:
                sText = sResult + "\n\n"
            
            # Leggi jobs.end se esiste
            sJobsEndFile = os.path.join(self.sJobPath, "jobs.end")
            if os.path.exists(sJobsEndFile):
                temp_ini = configparser.ConfigParser()
                temp_ini.optionxform = str
                temp_ini.read(sJobsEndFile, encoding='utf-8')
                
                for section in temp_ini.sections():
                    sText += f"[{section}]\n"
                    for key, value in temp_ini.items(section):
                        sText += f"{key}={value}\n"
                    sText += "\n"
            
            # Invia mail all'utente
            if self.sUser and self.dictUser.get("USER_MAIL"):
                sResult = self.MailUser("Completamento jobs.ini", sText)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore JobsMail")
            return sResult
    
    def JobInit(self) -> str:
        """
        Inizializza un job singolo.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobInit"
        sResult = ""
        
        try:
            if self.sJob not in self.dictJobs:
                sResult = f"Job non trovato: {self.sJob}"
                self.jLog.Log1(sResult)
                return sResult
            
            # Copia dati job
            self.dictJob = self.dictJobs[self.sJob].copy()
            self.tsJob = aiSys.Timestamp()
            
            # Verifica azione
            sResult = self.JobAction()
            if sResult:
                sResult = f"Errore interpretazione azione {self.sAction}: {sResult}"
                self.jLog.Log1(sResult)
                return sResult
            
            # Imposta directory corrente
            sCurDir = self.dictAction.get("ACT_PATH", "")
            if sCurDir:
                if not os.path.exists(sCurDir):
                    os.makedirs(sCurDir, exist_ok=True)
                os.chdir(sCurDir)
            else:
                os.chdir(self.sJobPath)
            
            # Espandi variabili nel job
            for key, value in list(self.dictJob.items()):
                if isinstance(value, str):
                    self.dictJob[key] = aiSys.Expand(value, self.dictConfig)
            
            # Gestione ACTION/COMMAND
            if "ACTION" in self.dictJob:
                self.dictJob["COMMAND"] = self.dictJob["ACTION"]
                del self.dictJob["ACTION"]
            
            # Crea file ntjobsapp.ini
            sActionIni = os.path.join(os.getcwd(), "ntjobsapp.ini")
            self.sActionIni = sActionIni
            
            # Unisci config e job
            dictTemp = self.dictConfig.copy()
            dictTemp.update(self.dictJob)
            
            # Salva file ini
            config_temp = configparser.ConfigParser()
            config_temp.optionxform = str
            config_temp["CONFIG"] = dictTemp
            
            with open(sActionIni, 'w', encoding='utf-8') as f:
                config_temp.write(f)
            
            self.jLog.Log1(f"Inizializzato job {self.sJob}")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def JobAction(self) -> str:
        """
        Verifica e inizializza l'azione del job.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobAction"
        sResult = ""
        
        try:
            # Ottieni azione
            self.sAction = self.dictJob.get("ACTION", "")
            if not self.sAction:
                sResult = "ACTION non specificata nel job"
                return sResult
            
            # Verifica esistenza azione
            if self.sAction not in self.asActions:
                sResult = f"Azione non presente: {self.sAction}"
                return sResult
            
            # Ottieni dati azione
            self.dictAction = self.JOBS_TAB_ACTIONS.get(self.sAction, {}).copy()
            if not self.dictAction:
                sResult = f"Dati azione non trovati: {self.sAction}"
                return sResult
            
            # Verifica abilitazione
            sEnabled = self.dictAction.get("ACT_ENABLED", "")
            if not aiSys.StringBoolean(sEnabled):
                sResult = f"Azione {self.sAction} disabilitata"
                return sResult
            
            # Verifica gruppi
            user_groups = aiSys.StringToArray(self.dictUser.get("USER_GROUPS", ""), ',')
            action_groups = aiSys.StringToArray(self.dictAction.get("ACT_GROUPS", ""), ',')
            
            if not aiSys.isGroups(user_groups, action_groups):
                sResult = f"Azione {self.sAction} non eseguibile per gruppi utente"
                return sResult
            
            # Imposta script e path
            self.sScript = self.dictAction.get("ACT_SCRIPT", "")
            self.sActionPath = self.dictAction.get("ACT_PATH", "")
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    def JobExec(self) -> str:
        """
        Esegue un job singolo.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobExec"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Azioni interne (sys.*)
            if self.sAction.startswith("sys."):
                sResult = self.JobInternal(self.sAction)
                return sResult
            
            # Verifica script
            if not self.sScript:
                sResult = "Script non assegnato all'azione"
                self.jLog.Log(sResult, f"Errore in job {self.sJob}")
                return sResult
            
            # Imposta directory
            if self.sActionPath:
                os.chdir(self.sActionPath)
            else:
                os.chdir(self.sJobPath)
            
            # Crea file ntjobsapp.ini
            dictTemp = self.dictConfig.copy()
            dictTemp.update(self.dictJob)
            
            config_temp = configparser.ConfigParser()
            config_temp.optionxform = str
            config_temp["CONFIG"] = dictTemp
            
            sIniFile = os.path.join(os.getcwd(), "ntjobsapp.ini")
            with open(sIniFile, 'w', encoding='utf-8') as f:
                config_temp.write(f)
            
            # Esegui script
            try:
                self.pidJob = subprocess.Popen(self.sScript, shell=True)
            except Exception as e:
                sResult = f"Non eseguibile: {self.sScript}, Errore: {str(e)}"
                self.jLog.Log(sResult, f"Errore in job {self.sJob}")
                return sResult
            
            # Attendi completamento
            sResult = self.JobExecWait()
            if sResult:
                return sResult
            
            # Fine esecuzione
            sResult = self.JobEnd()
            
            self.jLog.Log(sResult, f"Eseguito job {self.sJob}")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log(sResult, f"Errore in job {self.sJob}")
            return sResult
    
    def JobExecWait(self) -> str:
        """
        Attende il completamento di un processo esterno.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobExecWait"
        sResult = ""
        
        try:
            # Determina timeout
            nTimeout = aiSys.StringToNum(self.dictAction.get("ACT_TIMEOUT", "0"))
            if nTimeout == 0:
                nTimeout = aiSys.StringToNum(self.Config("TIMEOUT"))
            
            if nTimeout < 50:
                nTimeout = 300  # Default 5 minuti
            
            # Attendi con polling
            nStartTime = time.time()
            sEndFile = os.path.join(os.getcwd(), "ntjobsapp.end")
            
            while (time.time() - nStartTime) < nTimeout:
                # Verifica se processo è terminato
                if self.pidJob and self.pidJob.poll() is not None:
                    break
                
                # Verifica se esiste file .end
                if os.path.exists(sEndFile):
                    break
                
                time.sleep(10)  # Polling ogni 10 secondi
            
            # Timeout raggiunto
            if (time.time() - nStartTime) >= nTimeout:
                sResult = f"Timeout esecuzione {self.sJob}"
                
                # Termina processo forzatamente
                if self.pidJob and self.pidJob.poll() is None:
                    try:
                        self.pidJob.terminate()
                        self.pidJob.wait(timeout=5)
                    except:
                        try:
                            self.pidJob.kill()
                        except:
                            pass
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    def JobEnd(self, sValue: str = "") -> str:
        """
        Termina un job e salva i risultati.
        
        Args:
            sValue: Valore di ritorno opzionale
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobEnd"
        sResult = ""
        
        try:
            # Leggi file .end se esiste
            sEndFile = os.path.join(os.getcwd(), "ntjobsapp.end")
            dictTemp = {}
            
            if os.path.exists(sEndFile):
                try:
                    temp_ini = configparser.ConfigParser()
                    temp_ini.optionxform = str
                    temp_ini.read(sEndFile, encoding='utf-8')
                    
                    if "CONFIG" in temp_ini.sections():
                        for key, value in temp_ini.items("CONFIG"):
                            dictTemp[key] = value
                    
                    # Elimina file .end
                    os.remove(sEndFile)
                    
                except Exception as e:
                    sResult = f"Errore lettura ntjobsapp.end: {str(e)}"
            
            # Torna alla directory del job
            os.chdir(self.sJobPath)
            
            # Aggiorna dictJob con valori di ritorno
            if dictTemp:
                # Rimuovi CONFIG se presente
                dictTemp.pop("CONFIG", None)
                self.dictJob.update(dictTemp)
            
            # Aggiungi timestamp e risultati
            self.dictJob["TS.START"] = self.tsJob
            self.dictJob["TS.END"] = aiSys.Timestamp()
            
            if not sResult:
                self.dictJob["RETURN.VALUE"] = sValue
                self.dictJob["RETURN.TYPE"] = "S"
            else:
                self.dictJob["RETURN.VALUE"] = f"Errore: {sResult}, Valore: {sValue}"
                self.dictJob["RETURN.TYPE"] = "E"
            
            # Aggiorna dictJobs con risultati
            self.dictJobs[self.sJob] = self.dictJob.copy()
            
            self.jLog.Log(sResult, f"Terminato job {self.sJob}: {sValue}")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    def JobInternal(self, sAction: str) -> str:
        """
        Gestisce azioni interne del sistema.
        
        Args:
            sAction: Azione interna (sys.*)
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "JobInternal"
        sResult = ""
        
        try:
            if sAction == "sys.reload":
                # Crea file per riavvio
                sReloadFile = os.path.join(self.sSys_PathRoot, "ntJobsOS.reload")
                with open(sReloadFile, 'w') as f:
                    f.write("")
                sResult = "Richiesto riavvio ntJobsOS"
                
            elif sAction == "sys.quit":
                # Crea file per uscita
                sQuitFile = os.path.join(self.sSys_PathRoot, "ntJobsOS.quit")
                with open(sQuitFile, 'w') as f:
                    f.write("")
                self.bExitOS = True
                sResult = "Richiesta uscita ntJobsOS"
                
            elif sAction == "sys.shutdown":
                # Crea file per shutdown
                sShutdownFile = os.path.join(self.sSys_PathRoot, "ntJobsOS.shutdown")
                with open(sShutdownFile, 'w') as f:
                    f.write("")
                self.bExitOS = True
                sResult = "Richiesto shutdown ntJobsOS"
                
            elif sAction == "sys.email.admin":
                # Invia mail all'amministratore
                sResult = self.MailAdmin("Notifica da ntJobsOS", 
                                        f"Richiesta da utente {self.sUser}")
                
            else:
                sResult = f"Azione interna non riconosciuta: {sAction}"
            
            # Termina job interno
            self.JobEnd(sResult)
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    # ========================================================================
    # METODI DI UTILITÀ
    # ========================================================================
    
    def Login(self) -> str:
        """
        Autentica l'utente dal file jobs.ini.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Login"
        sResult = ""
        
        print(f"Esecuzione ntjobsos {sProc}")
        
        try:
            # Ottieni credenziali da CONFIG
            config_section = self.dictJobs.get("CONFIG", {})
            sUserVerify = config_section.get("USER", "")
            sPwdVerify = config_section.get("PASSWORD", "")
            
            if not sUserVerify or not sPwdVerify:
                sResult = "Credenziali USER/PASSWORD mancanti in CONFIG"
                self.jLog.Log0(sResult, "Errore Login")
                return sResult
            
            # Verifica utente
            if sUserVerify not in self.JOBS_TAB_USERS:
                sResult = f"Utente non trovato: {sUserVerify}"
                self.jLog.Log0(sResult, "Errore Login")
                return sResult
            
            # Verifica password
            user_data = self.JOBS_TAB_USERS[sUserVerify]
            sUser = user_data.get("USER_ID", "")
            sPwd = user_data.get("USER_PASSWORD", "")
            
            if sUser != sUserVerify or sPwd != sPwdVerify:
                sResult = f"Credenziali non valide per utente {sUserVerify}"
                self.jLog.Log0(sResult, "Errore Login")
                return sResult
            
            # Imposta utente corrente
            self.sUser = sUser
            self.dictUser = user_data.copy()
            
            # Converti gruppi in array
            sGroups = user_data.get("USER_GROUPS", "")
            self.dictUser["USER_GROUPS"] = aiSys.StringToArray(sGroups, ',')
            
            self.jLog.Log0(sResult, f"Login utente {self.sUser} completato")
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResult, "Errore Login")
            return sResult
    
    def Logoff(self) -> None:
        """
        Disconnette l'utente corrente.
        """
        sProc = "Logoff"
        
        try:
            self.dictUser = {}
            self.sUser = ""
            self.jLog.Log1("Logoff utente")
            
        except Exception as e:
            print(f"{sProc}: Errore - {str(e)}")
    
    def Return(self, sResult: str) -> str:
        """
        Salva il file jobs.end con i risultati.
        
        Args:
            sResult: Messaggio di risultato
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Return"
        sResultSave = ""
        
        try:
            sEndFile = os.path.join(self.sJobPath, "jobs.end")
            
            # Usa jIni per salvare
            self.jIni.clear()
            
            for section, values in self.dictJobs.items():
                self.jIni[section] = values
            
            # Salva file
            with open(sEndFile, 'w', encoding='utf-8') as f:
                self.jIni.write(f)
            
            self.jLog.Log1(f"Salvato jobs.end in {self.sJobPath}")
            return sResultSave
            
        except Exception as e:
            sResultSave = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log0(sResultSave, "Errore in Return")
            return sResultSave
    
    def MailUser(self, sSubject: str, sText: str) -> str:
        """
        Invia mail all'utente corrente.
        
        Args:
            sSubject: Oggetto mail
            sText: Testo mail
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "MailUser"
        sResult = ""
        
        try:
            if not self.dictUser:
                sResult = "Nessun utente loggato"
                return sResult
            
            sUserMail = self.dictUser.get("USER_MAIL", "")
            if not sUserMail:
                sResult = "Mail utente non configurata"
                return sResult
            
            sResult = self.Mail(sUserMail, sSubject, sText, [])
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    def MailAdmin(self, sSubject: str, sText: str) -> str:
        """
        Invia mail all'amministratore.
        
        Args:
            sSubject: Oggetto mail
            sText: Testo mail
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "MailAdmin"
        sResult = ""
        
        try:
            if not self.sMailAdmin:
                sResult = "Mail amministratore non configurata"
                return sResult
            
            sResult = self.Mail(self.sMailAdmin, sSubject, sText, [])
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    def Mail(self, sTo: str, sSubject: str, sText: str, asFiles: List[str] = None) -> str:
        """
        Invia una mail.
        
        Args:
            sTo: Destinatario
            sSubject: Oggetto
            sText: Testo
            asFiles: Lista file da allegare
            
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "Mail"
        sResult = ""
        
        try:
            if asFiles is None:
                asFiles = []
            
            # Verifica file allegati
            for sFile in asFiles:
                if not os.path.exists(sFile):
                    sResult = f"File allegato non trovato: {sFile}"
                    return sResult
            
            # Invia in base al mail engine
            if self.sMailEngine == "SMTP" and self.jMail:
                sResult = self.jMail.Send([sTo], sSubject, asFiles, "TXT", sText)
                
            elif self.sMailEngine == "OLK":
                # Crea JSON per OLK
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
                
                # Salva JSON
                sJsonFile = os.path.join(self.sSys_PathOlk, "ntjobs_mail.json")
                with open(sJsonFile, 'w', encoding='utf-8') as f:
                    json.dump(mail_data, f, indent=2)
                
                # Esegui script OLK
                sCmd = f'"{self.sSys_Olk}" "{sJsonFile}"'
                subprocess.Popen(sCmd, shell=True)
                
            else:
                sResult = "Mail Engine non inizializzato"
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            return sResult
    
    def Config(self, sKey: str) -> Any:
        """
        Ottiene un valore di configurazione.
        
        Args:
            sKey: Chiave di configurazione
            
        Returns:
            Valore di configurazione o stringa vuota
        """
        return aiSys.Config(sKey, self.dictConfig)
    
    def ConfigUpdate(self) -> str:
        """
        Aggiorna il dizionario di configurazione.
        
        Returns:
            str: Stringa vuota se successo, stringa di errore altrimenti
        """
        sProc = "ConfigUpdate"
        sResult = ""
        
        try:
            if not self.JOBS_TAB_CONFIG:
                sResult = "Tabella Config.ini non caricata"
                self.jLog.Log1(sResult)
                return sResult
            
            # Inizia con configurazione di sistema
            self.dictConfig = self.JOBS_TAB_CONFIG.get("CONFIG", {}).copy()
            
            # Aggiungi configurazione da jobs.ini
            if self.dictJobs and "CONFIG" in self.dictJobs:
                self.dictConfig.update(self.dictJobs["CONFIG"])
            
            # Espandi configurazione
            sResult = self.Start_Expand(self.dictConfig, self.dictConfig)
            
            if sResult:
                self.jLog.Log1(sResult)
            
            return sResult
            
        except Exception as e:
            sResult = f"{sProc}: Errore - {str(e)}"
            self.jLog.Log1(sResult)
            return sResult
    
    def ConfigSet(self, sKey: str, xValue: Any) -> None:
        """
        Imposta un valore di configurazione.
        
        Args:
            sKey: Chiave di configurazione
            xValue: Valore da impostare
        """
        self.dictConfig[sKey] = xValue
    
    def Log(self, sType: str, sValue: str = "") -> None:
        """Wrapper per jLog.Log."""
        self.jLog.Log(sType, sValue)
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """Wrapper per jLog.Log0."""
        self.jLog.Log0(sResult, sValue)
    
    def Log1(self, sValue: str = "") -> None:
        """Wrapper per jLog.Log1."""
        self.jLog.Log1(sValue)

# ============================================================================
# FUNZIONE PRINCIPALE
# ============================================================================

def main() -> None:
    """
    Funzione principale di ntJobsOS.
    """
    print("Avvio ntJobsOS...")
    
    try:
        # Crea istanza principale
        jData = acJobsOS()
        
        # Inizializza sistema
        sResult = jData.Start()
        
        if sResult:
            print(f"Errore esecuzione ntJobsOS: {sResult}")
            return
        
        # Ciclo principale
        while not jData.bExitOS:
            sResult = jData.Run()
            
            if sResult:
                jData.Log("ERR", f"Errore in Esecuzione Run: {sResult}")
            
            jData.CycleEnd()
        
        print("ntJobsOS terminato correttamente")
        
    except KeyboardInterrupt:
        print("\nntJobsOS interrotto dall'utente")
    except Exception as e:
        print(f"Errore critico in ntJobsOS: {str(e)}")

# ============================================================================
# ESECUZIONE
# ============================================================================

if __name__ == "__main__":
    main()