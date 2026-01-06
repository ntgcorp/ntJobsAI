#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ncJobsApp.py - Classe per applicazioni ntJobsApp batch
Versione: 1.0
Python: 3.10+
"""

import os
import sys
import configparser
from typing import Dict, Callable, Optional

# Import libreria di supporto
import aiSys


class ncJobsApp:
    """
    Classe per orchestrare micro applicazioni batch ntJobsApp
    
    Le ntJobsApp leggono un file .ini in ingresso, eseguono job,
    e restituiscono un file .end con i risultati
    """
    
    def __init__(self):
        """Inizializzazione attributi della classe"""
        
        # File I/O
        self.sJobIni = ""
        self.sJobEnd = ""
        
        # Configurazione
        self.bErrExit = False
        self.bExpand = False
        self.sName = ""
        self.tsStart = ""
        self.sType = ""
        self.sLog = ""
        
        # Job corrente
        self.sJobId = ""
        self.sCommand = ""
        self.dictJob = {}
        
        # Dati globali
        self.objIni = None
        self.dictJobs = {}
        self.dictConfig = {}
        
        # Log
        self.objLog = None
        
        # Chiavi riservate
        self.asKeyReserved = [
            "RETURN.TYPE", "TS.START", "TS.END", "RETURN.VALUE"
        ]
    
    # ========== METODO START ==========
    
    def Start(self) -> str:
        """
        Inizializza l'applicazione leggendo o creando il file .ini
        
        Returns:
            Stringa vuota se successo, messaggio di errore altrimenti
        """
        sProc = "Start"
        sResult = ""
        
        try:
            # Inizializzazioni
            self.tsStart = aiSys.Timestamp()
            self.objLog = aiSys.acLog()
            self.objLog.Start()
            
            # Reset campi
            self.dictJobs = {}
            self.dictConfig = {}
            self.sJobIni = ""
            self.sJobEnd = ""
            
            # Verifica parametri
            if len(sys.argv) < 2:
                sResult = "NTJOBSAPP: Eseguire con parametro file .ini o nella forma ntjobsapp.py command parametro valore ecc."
                print(sResult)
                return sResult
            
            # Determina modalità: file .ini o creazione dinamica
            if not sys.argv[1].lower().endswith(".ini"):
                # Crea file .ini dai parametri
                sResult = self.MakeIni()
                if sResult:
                    return sResult
            else:
                # Usa file .ini esistente
                self.sJobIni = sys.argv[1]
            
            # Verifica esistenza file
            if not os.path.exists(self.sJobIni):
                sResult = f"File .ini non esistente {self.sJobIni}"
                return sResult
            
            # Inizializza file end
            self.sJobEnd = os.path.splitext(self.sJobIni)[0] + ".end"
            
            # Inizializza ConfigParser
            self.objIni = configparser.ConfigParser()
            self.objIni.optionxform = str
            
            # Leggi file .ini
            try:
                self.objIni.read(self.sJobIni, encoding='utf-8')
                print(f"Letto {self.sJobIni}")
            except Exception as e:
                sResult = f"Errore lettura {self.sJobIni}: {str(e)}"
                return sResult
            
            # Converti in dizionario
            asSections = []
            for section in self.objIni.sections():
                # Normalizza nome sezione
                sSection = section.upper().replace(" ", "")
                asSections.append(sSection)
                
                self.dictJobs[sSection] = {}
                
                for key, value in self.objIni[section].items():
                    # Normalizza chiave
                    sKey = key.upper().replace(" ", "")
                    
                    # Verifica chiavi riservate
                    if sKey in self.asKeyReserved or sKey.startswith("RETURN.FILE."):
                        sResult += f"Chiave riservata non utilizzabile: {sKey}\n"
                        continue
                    
                    self.dictJobs[sSection][sKey] = value
            
            print(f"Processato {self.sJobIni}, Sezioni: {', '.join(asSections)}")
            
            # Verifica sezione CONFIG
            if "CONFIG" not in self.dictJobs:
                sResult = "Sezione CONFIG non trovata"
                return sResult
            
            # Estrai configurazione
            self.dictConfig = self.dictJobs["CONFIG"].copy()
            
            # Rimuovi PASSWORD se presente
            if "PASSWORD" in self.dictConfig:
                del self.dictConfig["PASSWORD"]
            
            # Verifica COMMAND e FILE per ogni job
            for sSection, dictSection in self.dictJobs.items():
                if sSection == "CONFIG":
                    continue
                
                # Verifica COMMAND presente
                if "COMMAND" not in dictSection:
                    sResult += f"Per questa sezione COMMAND non presente: {sSection}\n"
                
                # Verifica file esistono
                for sKey, sValue in dictSection.items():
                    if sKey.startswith("FILE."):
                        sFile = sValue
                        # Estrai solo nome file se contiene path
                        sFile = os.path.basename(sFile)
                        
                        if not os.path.exists(sFile):
                            sResult += f"File richiesto non presente {sFile}\n"
            
            # Se ci sono errori, esci
            if sResult:
                return sResult
            
            # Inizializza parametri config
            self.sLog = self.Config("LOG")
            self.sType = self.Config("TYPE")
            self.sName = self.Config("NAME")
            
            sExit = self.Config("EXIT")
            self.bErrExit = sExit.upper() == "TRUE" if sExit else False
            
            sExpand = self.Config("EXPAND")
            self.bExpand = sExpand.upper() == "TRUE" if sExpand else True
            
            # Verifiche parametri config
            if not self.sName:
                sResult = "NAME non precisato"
                return sResult
            
            if not self.sType.startswith("NTJOBS.APP."):
                sResult = "Type INI non NTJOBSAPP"
                return sResult
            
            # Espansione variabili
            if self.bExpand:
                self.Expand()
            
            self.Log0(sResult, f"Start {self.sName} {self.sJobIni}")
        
        except Exception as e:
            sResult = f"Errore Start: {str(e)}"
        
        # Diagnostica
        if sResult:
            print(f"Eseguita ntjobsapp.{sProc}: {sResult}")
        
        return sResult
    
    # ========== METODO MAKEINI ==========
    
    def MakeIni(self) -> str:
        """
        Crea file .ini dai parametri command line
        
        Returns:
            Stringa vuota se successo, messaggio di errore altrimenti
        """
        sProc = "MakeIni"
        sResult = ""
        
        try:
            self.sJobIni = ""
            dictTemp = {}
            
            # Verifica numero parametri (deve essere dispari: 1 + multipli di 2)
            nParams = len(sys.argv)
            if (nParams - 1) % 2 != 0 and nParams > 1:
                # Accettiamo anche solo il comando senza parametri
                if nParams == 2:
                    pass  # OK: solo comando
                else:
                    sResult = "Errore numero parametri comando chiave=valore ecc."
                    return sResult
            
            # Primo parametro è il comando
            sCommand = sys.argv[1].strip('"\'')
            
            # Parametri successivi a coppie
            for i in range(2, nParams, 2):
                if i + 1 < nParams:
                    sKey = sys.argv[i].strip('"\'')
                    sValue = sys.argv[i + 1].strip('"\'')
                    dictTemp[sKey] = sValue
            
            # Crea file ntjobsapp.ini
            sFileTemp = os.path.join(os.path.dirname(__file__), "ntjobsapp.ini")
            
            config = configparser.ConfigParser()
            config.optionxform = str
            
            # Sezione CONFIG
            config["CONFIG"] = {
                "TYPE": "NTJOBS.APP.2"
            }
            
            # Sezione APP
            config["APP"] = {
                "COMMAND": sCommand
            }
            
            # Aggiungi parametri
            for sKey, sValue in dictTemp.items():
                config["APP"][sKey] = sValue
            
            # Salva file
            try:
                with open(sFileTemp, 'w', encoding='utf-8') as f:
                    config.write(f)
                
                self.sJobIni = sFileTemp
            except Exception as e:
                sResult = f"Errore creazione file {sFileTemp}: {str(e)}"
        
        except Exception as e:
            sResult = f"Errore MakeIni: {str(e)}"
        
        # Diagnostica
        if sResult:
            print(f"Eseguita ntjobsapp.{sProc}: {sResult}")
        
        return sResult
    
    # ========== METODI CONFIGURAZIONE ==========
    
    def Config(self, sKey: str) -> str:
        """
        Ritorna valore configurazione
        
        Args:
            sKey: Chiave da cercare
            
        Returns:
            Valore della chiave o stringa vuota
        """
        # Normalizza chiave
        sKey = sKey.upper().replace(" ", "")
        
        return self.dictConfig.get(sKey, "")
    
    def AddTimestamp(self, dictTemp: Dict) -> None:
        """
        Aggiunge timestamp a dizionario
        
        Args:
            dictTemp: Dizionario da aggiornare
        """
        dictTemp["TS.START"] = self.tsStart
        dictTemp["TS.END"] = aiSys.Timestamp()
    
    # ========== METODO RETURN ==========
    
    def Return(self, sResult: str, sValue: str = "", 
               dictFiles: Optional[Dict[str, str]] = None) -> str:
        """
        Aggiorna risultato elaborazione corrente
        
        Args:
            sResult: Risultato elaborazione ("" = successo)
            sValue: Valore di ritorno opzionale
            dictFiles: Dizionario file di ritorno {id: filename}
            
        Returns:
            sResult
        """
        sProc = "Return"
        
        try:
            # Determina tipo ritorno
            if sResult:
                sReturnType = "E"
                if not sValue:
                    sValue = sResult
            else:
                sReturnType = "S"
            
            # Gestione file di ritorno
            if dictFiles:
                for sFileId, sFileName in dictFiles.items():
                    # Estrai solo nome file
                    sFileName = os.path.basename(sFileName)
                    
                    # Verifica esistenza nella cartella corrente
                    if not os.path.exists(sFileName):
                        sResult = f"Errore file non presente: {sFileName}"
                        sReturnType = "E"
                        break
                    
                    # Aggiungi a dictJob
                    self.dictJob[f"RETURN.FILE.{sFileId}"] = sFileName
                
                # Se non c'era già un tipo ritorno, impostalo a S
                if not sReturnType:
                    sReturnType = "S"
            
            # Aggiungi risultati
            self.dictJob["RETURN.TYPE"] = sReturnType
            self.dictJob["RETURN.VALUE"] = sValue
            
            # Aggiungi timestamp
            self.AddTimestamp(self.dictJob)
        
        except Exception as e:
            sResult = f"Errore Return: {str(e)}"
        
        # Diagnostica
        if sResult:
            print(f"Eseguita ntjobsapp.{sProc}: {sResult}")
        
        return sResult
    
    # ========== METODO EXPAND ==========
    
    def Expand(self) -> None:
        """Espande variabili nei settings usando $VARIABILE"""
        sProc = "Expand"
        
        try:
            if not self.bExpand:
                return
            
            print("Espansione dei settings")
            
            # Espandi tutti i job eccetto CONFIG
            for sSection, dictSection in self.dictJobs.items():
                if sSection == "CONFIG":
                    continue
                
                # Espandi ogni valore
                for sKey in list(dictSection.keys()):
                    sValue = dictSection[sKey]
                    
                    if isinstance(sValue, str):
                        dictSection[sKey] = aiSys.Expand(sValue, self.dictConfig)
        
        except Exception as e:
            print(f"Errore Expand: {str(e)}")
    
    # ========== METODO RUN ==========
    
    def Run(self, cbCommands: Callable[[], str]) -> str:
        """
        Esegue tutti i job in sequenza
        
        Args:
            cbCommands: Funzione callback da eseguire per ogni job
            
        Returns:
            Stringa vuota se successo, messaggio di errore altrimenti
        """
        sProc = "Run"
        sResult = ""
        
        try:
            # Esegui ogni job
            for sKey, dictSection in self.dictJobs.items():
                if sKey == "CONFIG":
                    continue
                
                print(f"Esecuzione Action {sKey}")
                
                # Copia job corrente
                self.dictJob = dictSection.copy()
                self.sJobId = sKey
                self.sCommand = self.dictJob.get("COMMAND", "")
                
                # Log inizio
                self.Log1(f"Eseguo il comando: {self.sCommand}, Sezione: {sKey}, "
                         f"TS: {aiSys.Timestamp()}")
                
                # Esegui callback
                sResult = cbCommands()
                
                # Aggiorna job in dictJobs
                self.dictJobs[sKey] = self.dictJob.copy()
                
                # Log fine
                self.Log1(f"Eseguito il comando: {self.sCommand}, Sezione: {sKey}, "
                         f"TS: {aiSys.Timestamp()}, Risultato: {sResult}")
                
                # Esci se errore e bErrExit attivo
                if sResult and self.bErrExit:
                    break
        
        except Exception as e:
            sResult = f"Errore Run: {str(e)}"
        
        return sResult
    
    # ========== METODO END ==========
    
    def End(self, sResult: str) -> int:
        """
        Finalizza applicazione e salva risultati
        
        Args:
            sResult: Risultato finale elaborazione
            
        Returns:
            Codice uscita (0=OK, 1=errore Start, 2=errore Run)
        """
        sProc = "End"
        nResult = 0
        bIsFatalError = False
        
        try:
            # FASE 1: Determinazione codice uscita
            if not self.dictJobs:
                nResult = 1
                
                if sResult:
                    # Inizializza struttura minima per salvare errore
                    self.dictJobs = {"CONFIG": {}}
                    bIsFatalError = True
            
            elif sResult:
                # Errore da Run
                nResult = 2
                bIsFatalError = True
            
            # FASE 2: Aggiornamento dati errore
            if bIsFatalError:
                dictTemp = {
                    "RETURN.TYPE": "E",
                    "RETURN.VALUE": sResult
                }
                
                self.AddTimestamp(dictTemp)
                
                # Aggiorna CONFIG
                self.dictConfig.update(dictTemp)
                self.dictJobs["CONFIG"] = self.dictConfig.copy()
            
            # FASE 3: Salvataggio e uscita
            # Salva file .end
            config = configparser.ConfigParser()
            config.optionxform = str
            
            for sSection, dictSection in self.dictJobs.items():
                config[sSection] = {}
                for sKey, sValue in dictSection.items():
                    config[sSection][sKey] = str(sValue)
            
            try:
                with open(self.sJobEnd, 'w', encoding='utf-8') as f:
                    config.write(f)
                
                print(f"Salvato {self.sJobEnd}")
            except Exception as e:
                print(f"Errore salvataggio {self.sJobEnd}: {str(e)}")
                if nResult == 0:
                    nResult = 1
            
            # Log finale
            self.Log(sResult, f"Fine applicazione {self.sName}")
        
        except Exception as e:
            print(f"Errore End: {str(e)}")
            if nResult == 0:
                nResult = 1
        
        # Diagnostica
        if sResult:
            print(f"Eseguita ntjobsapp.{sProc}: {sResult}")
        
        return nResult
    
    # ========== METODI LOG ==========
    
    def Log(self, sResult: str = "", sValue: str = "") -> None:
        """Log generico"""
        if self.objLog:
            self.objLog.Log("INFO" if not sResult else "ERR", 
                           f"{sResult}: {sValue}" if sResult else sValue)
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """Log con verifica errore"""
        if self.objLog:
            self.objLog.Log0(sResult, sValue)
    
    def Log1(self, sValue: str) -> None:
        """Log info"""
        if self.objLog:
            self.objLog.Log1(sValue)


# ========== VARIABILE GLOBALE ==========

jData: Optional[ncJobsApp] = None


# ========== FUNZIONE CALLBACK ESEMPIO ==========

def cbCommands() -> str:
    """
    Funzione callback di esempio per eseguire comandi
    
    Questa funzione deve essere personalizzata dall'utente per
    implementare la logica specifica dell'applicazione.
    
    La funzione ha accesso a:
    - jData.sCommand: comando da eseguire
    - jData.dictJob: dizionario parametri job corrente
    - jData.sJobId: ID del job corrente
    
    Deve chiamare jData.Return() per registrare il risultato
    
    Returns:
        Stringa vuota se successo, messaggio errore altrimenti
    """
    sResult = ""
    
    try:
        print(f"Esecuzione comando: {jData.sCommand}")
        
        # Esempio: gestione comandi base
        if jData.sCommand == "TEST":
            # Test semplice
            sResult = ""
            sValue = "Test eseguito con successo"
            jData.Return(sResult, sValue)
        
        elif jData.sCommand == "ECHO":
            # Echo parametri
            sMessage = jData.dictJob.get("MESSAGE", "Hello World")
            sResult = ""
            jData.Return(sResult, f"Echo: {sMessage}")
        
        elif jData.sCommand == "ERROR":
            # Simula errore
            sResult = "Errore simulato per test"
            jData.Return(sResult)
        
        else:
            # Comando non riconosciuto
            sResult = f"Comando non riconosciuto: {jData.sCommand}"
            jData.Return(sResult)
    
    except Exception as e:
        sResult = f"Errore esecuzione comando: {str(e)}"
        jData.Return(sResult)
    
    return sResult


# ========== FUNZIONE PRINCIPALE ==========

def main() -> int:
    """
    Funzione principale dell'applicazione
    
    Returns:
        Codice uscita (0=OK, 1=errore Start, 2=errore Run)
    """
    global jData
    
    try:
        # Inizializza istanza globale
        jData = ncJobsApp()
        
        # Start
        sResult = jData.Start()
        
        if sResult:
            print(f"Errore Start: {sResult}")
            return jData.End(sResult)
        
        # Run
        sResult = jData.Run(cbCommands)
        
        # End
        nResult = jData.End(sResult)
        
        return nResult
    
    except KeyboardInterrupt:
        print("\nInterruzione da tastiera")
        return 1
    
    except Exception as e:
        print(f"Errore fatale: {str(e)}")
        return 1


# ========== ENTRY POINT ==========

if __name__ == "__main__":
    sys.exit(main())