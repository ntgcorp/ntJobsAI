
#!/usr/bin/env python3
# Nomefile: acJobsJobs.py
# -*- coding: utf-8 -*-

"""
acJobsJobs - Classe mixin per il controllo esecuzione dei jobs
"""

import os
import sys
import subprocess
import time
from typing import Dict, Any, Optional, Union, List
from copy import deepcopy
import aiSys


class acJobsJobs:
    """
    Mixin per la gestione dell'esecuzione dei jobs.
    """
    
    def JobsInit(self, sJobPath: str) -> str:
        """
        Predispone all'esecuzione di una sequenza di jobs contenuti nel file jobs.ini.
        """
        sProc = "JobsInit"
        sResult = ""
        
        self.sJobsFile = aiSys.PathMake(sJobPath, "jobs", "ini")
        
        # Legge il file jobs.ini
        sResult, dictTemp = aiSys.read_ini_to_dict(self.sJobsFile)
        
        if sResult != "":
            sResult = f"Errore lettura path {self.sJobsFile}"
        
        if sResult == "":
            self.dictJobs = deepcopy(dictTemp)
            self.sJobsPath = sJobPath
            self.tsJobsStart = aiSys.TimeStamp()
            
            sResult = self.ConfigUpdate()
            
            if sResult == "":
                sResult = self.JobsUserLogin()
        
        if sResult == "":
            self.Log0(sResult, f"Caricato jobs.ini {sJobPath}")
        else:
            self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsEnd(self, sResultJobs: str = "") -> str:
        """
        Fine esecuzione jobs.ini corrente e salvataggio jobs.end.
        """
        sProc = "JobsEnd"
        sResult = sResultJobs
        
        sFileEnd = self.JobsFileEnd()
        
        if sFileEnd:
            sResult = aiSys.save_dict_to_ini(self.dictJobs, sFileEnd)
        
        if sResult == "":
            sResult = self.JobsMail()
        
        self.JobsUserLogoff()
        
        # Reset campi
        self.dictJobs = {}
        self.sJobsPath = ""
        self.sJob = ""
        self.asJobs = []
        self.asJobFiles = []
        self.sScript = ""
        self.tsJobStart = ""
        self.tsJobsStart = ""
        self.sJobsFile = ""
        
        self.Log0(sResult, f"Salvato {sFileEnd}")
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsFileEnd(self) -> str:
        """
        Restituisce il path del file jobs.end.
        """
        if not self.sJobsFile:
            self.Log1("Errore interno, sJobsFile non avvalorato")
            return ""
        
        sDir = os.path.dirname(self.sJobsFile)
        sBase = os.path.splitext(os.path.basename(self.sJobsFile))[0]
        return aiSys.PathMake(sDir, sBase, "end")
    
    def JobsMail(self) -> str:
        """
        Invio mail per dichiarare all'utente la fine esecuzione di un file jobs.ini.
        """
        sProc = "JobsMail"
        sResult = ""
        
        sText = sResult if sResult else ""
        sTemp = ""
        
        # Legge jobs.end se presente
        sJobsEnd = aiSys.PathMake("", "jobs", "end")
        if aiSys.FileExists(sJobsEnd):
            sResultRead, dictTemp = aiSys.read_ini_to_dict(sJobsEnd)
            if sResultRead == "":
                sTemp = aiSys.DictToString(dictTemp, "ini.sect")
                sText = sResult + "\n\n" + sTemp if sResult else sTemp
        
        sResult = self.JobsMailUser("Completamento jobs.ini", sText)
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobAction(self) -> str:
        """
        Verifica se l'azione esiste ed è eseguibile per i gruppi dell'utente.
        """
        sProc = "JobAction"
        sResult = ""
        
        self.sAction = self.dictJob.get("ACTION", "").upper()
        self.sCommand = self.dictJob.get("COMMAND", "")
        
        if not self.sAction:
            sResult = "ACTION non specificata"
        elif self.sAction not in self.asActions:
            sResult = f"Errore Azione non presente {self.sAction}"
        else:
            self.dictAction = deepcopy(self.JOBS_TAB_ACTIONS[self.sAction])
            bEnabled = aiSys.StringBool(self.dictAction.get("ACT_ENABLED", "False"))
            
            if not bEnabled:
                sResult = f"Action {self.sAction} disabilitata"
        
        if sResult == "":
            # Verifica permessi gruppi
            user_groups = self.dictUser.get("USER_GROUPS", [])
            action_groups = aiSys.StringToArray(self.dictAction.get("ACT_GROUPS", ""), ",")
            
            if action_groups and not aiSys.isGroups(user_groups, action_groups):
                sResult = f"Azione non eseguibile per gruppi incompatibili {self.sAction}"
            
            self.sScript = self.dictAction.get("ACT_SCRIPT", "")
            if not self.sScript:
                sResult = "Script non assegnato"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobExec(self, sJob: str) -> str:
        """
        Esegue il singolo job.
        """
        sProc = "JobExec"
        sResult = ""
        
        try:
            # 1. INIZIALIZZAZIONE JOB
            self.sJob = sJob
            self.dictJob = deepcopy(self.dictJobs[sJob])
            self.tsJobStart = aiSys.TimeStamp()
            
            # 2. VALIDAZIONE PRE-ESECUZIONE
            sResult = self.JobValidate()
            if sResult != "":
                return self.JobEnd(sResult, "")
            
            # 3. INTERPRETAZIONE AZIONE
            sResult = self.JobAction()
            if sResult != "":
                return self.JobEnd(sResult, "")
            
            # 4. PREPARAZIONE PARAMETRI
            sResult = self.JobPrepare()
            if sResult != "":
                return self.JobEnd(sResult, "")
            
            # 5. DETERMINA SE AZIONE INTERNA O ESTERNA
            if self.sAction.startswith("SYS."):
                sResult = self.JobInternal(self.sAction)
                return self.JobEnd(sResult, "")
            
            # 6. AVVIO PROCESSO ESTERNO
            sResult = self.JobStartProcess()
            if sResult != "":
                return self.JobEnd(sResult, "")
            
            # 7. ATTESA COMPLETAMENTO
            if sResult == "":
                sResult = self.JobExecWait()
            
            # 8. BILLING (solo per azioni esterne)
            if sResult == "":
                sResult = self.JobBilling()
            
            # 9. TERMINA JOB
            return self.JobEnd(sResult, "")
            
        except Exception as e:
            return self.JobEnd(f"{sProc}: Errore non gestito - {str(e)}", "")
    
    def JobExecWait(self) -> str:
        """
        Attende la terminazione del processo esterno.
        """
        sProc = "JobExecWait"
        sResult = ""
        
        sTimeOut = self.dictAction.get("ACT_TIMEOUT", "")
        nTimeout2 = aiSys.StringToNum(sTimeOut)
        
        if nTimeout2 == 0:
            nTimeout = aiSys.StringToNum(self.Config("TIMEOUT"))
        else:
            nTimeout = nTimeout2
        
        if nTimeout < 50:
            self.Log1(f"Timeout specificato per job {self.sJob} troppo basso, impostato a 50")
            nTimeout = 50
        
        nElapsed = 0
        nInterval = 10
        
        while nElapsed < nTimeout:
            # Verifica file ntjobsapp.end
            sFileAppend = aiSys.PathMake(self.sJobsPath, "ntjobsapp", "end")
            if aiSys.FileExists(sFileAppend):
                break
            
            # Verifica se processo è terminato
            if hasattr(self, 'pidJob') and self.pidJob:
                if self.pidJob.poll() is not None:
                    break
            
            time.sleep(nInterval)
            nElapsed += nInterval
        
        if nElapsed >= nTimeout:
            sResult = f"Timeout esecuzione {self.sJob},{self.sJobsFile}"
            self.JobCleanup()
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobCleanup(self) -> str:
        """
        Pulizia risorse del job corrente.
        """
        sProc = "JobCleanup"
        sResult = ""
        
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
            sResult = f"{sProc}: Errore - {str(e)}"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobValidate(self) -> str:
        """
        Validazione del job prima dell'esecuzione.
        """
        sProc = "JobValidate"
        sResult = ""
        
        # 1. Verifica campi obbligatori
        if "ACTION" not in self.dictJob:
            return f"{sProc}: Campo ACTION mancante nel job {self.sJob}"
        
        # 2. Verifica file associati
        self.asJobFiles = []
        for sKey, sValue in self.dictJob.items():
            if sKey.startswith("FILE.") or sKey.startswith("RETURN.FILE."):
                sJobFile = aiSys.PathMake(self.sJobsPath, sValue, "")
                if not aiSys.FileExists(sJobFile):
                    return f"{sProc}: File {sKey}:{sJobFile} non trovato: {sValue} in job {self.sJob}"
                else:
                    self.asJobFiles.append(sJobFile)
        
        # 3. Verifica permessi utente
        if hasattr(self, 'sUser') and self.sUser:
            sAction = self.dictJob.get("ACTION", "")
            if sAction and sAction in self.JOBS_TAB_ACTIONS:
                dictAction = self.JOBS_TAB_ACTIONS[sAction]
                user_groups = self.dictUser.get("USER_GROUPS", [])
                action_groups = aiSys.StringToArray(dictAction.get("ACT_GROUPS", ""), ",")
                
                if action_groups and not aiSys.isGroups(user_groups, action_groups):
                    sResult = f"{sProc}: Permessi insufficienti per azione {sAction}"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobPrepare(self) -> str:
        """
        Preparazione parametri e ambiente per l'esecuzione.
        """
        sProc = "JobPrepare"
        sResult = ""
        
        try:
            # 1. Imposta directory di lavoro
            sCurDir = self.dictAction.get("ACT_PATH", "")
            if not sCurDir:
                sCurDir = self.sJobsPath
            
            # 2. Espansione variabili nei parametri
            dictExpanded = {}
            for sKey, sValue in self.dictJob.items():
                if sKey not in ["ACTION", "COMMAND"]:
                    dictExpanded[sKey] = aiSys.Expand(sValue, self.dictConfig)
            
            # 3. Rinomina campi speciali
            if "ACTION" in dictExpanded:
                dictExpanded["ACTION.ROOT"] = dictExpanded.pop("ACTION")
            
            if "COMMAND" in dictExpanded:
                dictExpanded["ACTION"] = dictExpanded.pop("COMMAND")
                self.sAction = dictExpanded["ACTION"].upper()
            
            # 4. Aggiorna dictJob con valori espansi
            self.dictJob.update(dictExpanded)
            
            # 5. Crea ntjobsapp.ini solo se azione esterna
            if not self.sAction.startswith("SYS."):
                dictTemp = {**self.dictConfig, **self.dictJob}
                sFileIni = aiSys.PathMake(self.sJobsPath, "ntjobsapp", "ini")
                sResult = aiSys.save_dict_to_ini(dictTemp, sFileIni)
                if sResult != "":
                    sResult = f"{sProc}: Errore creazione ntjobsapp.ini: {sResult}"
        
        except Exception as e:
            sResult = f"{sProc}: Errore preparazione - {str(e)}"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobStartProcess(self) -> str:
        """
        Avvia il processo esterno per azioni non-sys.
        """
        sProc = "JobStartProcess"
        
        if not aiSys.FileExists(self.sScript):
            return f"{sProc}: Script non trovato: {self.sScript}"
        
        try:
            sCmd = self.sScript
            if self.dictAction.get("ACT_PARAMS", ""):
                sCmd += " " + self.dictAction["ACT_PARAMS"]
            
            self.pidJob = subprocess.Popen(
                sCmd,
                shell=True,
                cwd=self.sJobsPath,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.Log0("", f"Avviato processo {self.pidJob.pid} per job {self.sJob}")
            return ""
        
        except Exception as e:
            self.JobCleanup()
            sResult = f"{sProc}: Errore avvio processo - {str(e)}"
            return aiSys.ErrorProc(sResult, sProc)
    
    def JobEnd(self, sResult: str, sValue: str = "") -> str:
        """
        Aggiunge i risultati di esecuzione del job corrente a self.dictJob e conclude il job.
        """
        sProc = "JobEnd"
        
        # 1. AGGIORNA TIMESTAMP
        self.dictJob["TS.START"] = self.tsJobStart
        self.dictJob["TS.END"] = aiSys.TimeStamp()
        
        # 2. IMPOSTA RISULTATO
        if sResult == "":
            self.dictJob["RETURN.TYPE"] = "S"
            self.dictJob["RETURN.VALUE"] = sValue if sValue else "Completato"
        else:
            self.dictJob["RETURN.TYPE"] = "E"
            self.dictJob["RETURN.VALUE"] = f"Errore: {sResult}"
        
        # 3. PULIZIA
        self.sAction = self.sAction.upper() if hasattr(self, 'sAction') else ""
        
        if not self.sAction.startswith("SYS."):
            if hasattr(self, 'pidJob') and self.pidJob:
                self.JobCleanup()
            else:
                sFileIni = aiSys.PathMake(self.sJobsPath, "ntjobsapp", "ini")
                if aiSys.FileExists(sFileIni):
                    aiSys.FileDelete(sFileIni)
        
        # 4. AGGIORNA DIZIONARIO PRINCIPALE
        self.dictJobs[self.sJob] = deepcopy(self.dictJob)
        
        # 5. LOG E RESET
        sLogMsg = f"Job {self.sJob} completato"
        if sResult != "":
            sLogMsg += f" con errore: {sResult}"
        self.Log0(sResult, sLogMsg)
        
        # Reset campi job
        self.sJob = ""
        self.tsJobStart = ""
        self.dictJob = None
        self.sAction = ""
        self.dictAction = None
        self.sScript = ""
        if hasattr(self, 'pidJob'):
            self.pidJob = None
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobInternal(self, sAction: str) -> str:
        """
        Esegue azioni interne a aiJobsOS (comandi SYS.*).
        """
        sProc = "JobInternal"
        sResult = ""
        
        sAction = sAction.upper()
        
        if sAction == "SYS.RELOAD":
            sFileReload = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "reload")
            try:
                with open(sFileReload, 'w') as f:
                    f.write(aiSys.TimeStamp())
                self.Log0("", "Comando SYS.RELOAD eseguito")
            except Exception as e:
                sResult = f"Errore creazione file reload: {str(e)}"
        
        elif sAction == "SYS.QUIT":
            sFileQuit = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "quit")
            try:
                with open(sFileQuit, 'w') as f:
                    f.write(aiSys.TimeStamp())
                self.bExitOS = True
                self.Log0("", "Comando SYS.QUIT eseguito")
            except Exception as e:
                sResult = f"Errore creazione file quit: {str(e)}"
        
        elif sAction == "SYS.SHUTDOWN":
            sFileShutdown = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "shutdown")
            try:
                with open(sFileShutdown, 'w') as f:
                    f.write(aiSys.TimeStamp())
                self.bExitOS = True
                self.Log0("", "Comando SYS.SHUTDOWN eseguito")
            except Exception as e:
                sResult = f"Errore creazione file shutdown: {str(e)}"
        
        elif sAction == "SYS.REBOOT":
            sFileReboot = aiSys.PathMake(self.sSys_PathRoot, "aiJobsOS", "reboot")
            try:
                with open(sFileReboot, 'w') as f:
                    f.write(aiSys.TimeStamp())
                self.bExitOS = True
                self.Log0("", "Comando SYS.REBOOT eseguito")
            except Exception as e:
                sResult = f"Errore creazione file reboot: {str(e)}"
        
        elif sAction == "SYS.EMAIL.ADMIN":
            sResult = self.JobsMailAdmin("Notifica da aiJobsOS", f"Mail inviata dall'utente {self.sUser}")
        
        elif sAction == "SYS.EMAIL.USER":
            sResult = self.JobsMailUser("Notifica da aiJobsOS", f"Mail inviata dall'utente {self.sUser}")
        
        else:
            sResult = f"Azione interna non riconosciuta: {sAction}"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobBilling(self, sAction: str = "", sCommand: str = "", sNotes: str = "", sTags: str = "") -> str:
        """
        Accoda un record di Billing al file CSV.
        """
        sProc = "JobBilling"
        sResult = ""
        
        if not self.sSys_BillFile:
            self.sSys_BillFile = aiSys.PathMake(self.sSys_PathRoot, "ntjobs_billing", "csv")
        
        asHeader = ("TS_START", "TS_END", "USER", "ACTION", "COMMAND", "TAGS", "NOTES")
        
        dictRecord = {
            "TS_START": self.tsJobStart,
            "TS_END": aiSys.TimeStamp(),
            "USER": self.sUser if hasattr(self, 'sUser') else "",
            "ACTION": sAction if sAction else (self.sAction if hasattr(self, 'sAction') else ""),
            "COMMAND": sCommand if sCommand else (self.sCommand if hasattr(self, 'sCommand') else ""),
            "TAGS": sTags,
            "NOTES": sNotes
        }
        
        dictBilling = {"BILL": dictRecord}
        sResult = aiSys.save_dict_to_csv(self.sSys_BillFile, asHeader, dictBilling, "a", ";")
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Config(self, sKey: str) -> str:
        """
        Ritorna una configurazione salvata in self.dictConfig.
        """
        if not hasattr(self, 'dictConfig') or not self.dictConfig:
            return ""
        return aiSys.ConfigDefault(self.dictConfig, sKey, "")
    
    def ConfigUpdate(self) -> str:
        """
        Aggiorna self.dictConfig con la fusione di JOBS_TAB_CONFIG e dictJobs["CONFIG"].
        """
        sProc = "ConfigUpdate"
        sResult = ""
        
        if self.JOBS_TAB_CONFIG is None:
            sResult = "Tabella Config.ini non caricata"
        
        if sResult == "":
            dictTemp = deepcopy(self.JOBS_TAB_CONFIG)
            dictTemp2 = deepcopy(self.dictJobs.get("CONFIG", {}))
            
            dictTemp = aiSys.DictMerge(dictTemp, dictTemp2)
            aiSys.ExpandDict(dictTemp, dictTemp)
            
            self.dictConfig = deepcopy(dictTemp)
        
        if sResult != "":
            self.Log1(sResult)
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def Log(self, sType: str, sValue: str) -> None:
        """Wrapper per jLog.Log."""
        if hasattr(self, 'jLog') and self.jLog:
            self.jLog.Log(sType, sValue)
    
    def Log0(self, sResult: str, sValue: str) -> None:
        """Wrapper per jLog.Log0."""
        if hasattr(self, 'jLog') and self.jLog:
            self.jLog.Log0(sResult, sValue)
    
    def Log1(self, sResult: str) -> None:
        """Wrapper per jLog.Log1."""
        if hasattr(self, 'jLog') and self.jLog:
            self.jLog.Log1(sResult)


