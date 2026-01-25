"""
acJobsApp.py - Classe per applicazioni batch ntJobApp
"""

import sys
import os
import re
from typing import Dict, List, Tuple, Union, Any, Optional, Callable
from pathlib import Path

# Import della libreria aiSys
try:
    import aiSys
except ImportError:
    print("ERRORE: Libreria aiSys.py non trovata")
    sys.exit(1)


class acJobsApp:
    """
    Classe per gestire applicazioni batch ntJobApp
    """
    
    def __init__(self):
        """Inizializza l'istanza di acJobsApp"""
        self.sProc = "acJobsApp.__init__"
        
        # Attributi della classe
        self.sJobIni = ""          # File .ini dei parametri
        self.bErrExit = True       # Esce in caso di errore di un job
        self.bExpand = False       # Modalità espansione settings
        self.sName = ""            # Nome dell'applicazione
        self.tsStart = ""          # Timestamp inizio applicazione
        self.sType = ""            # Tipo e versione applicazione
        self.sLog = ""             # Nome facoltativo del file di Log
        self.sJobId = ""           # ID del job corrente
        self.sCommand = ""         # ID del comando corrente
        self.dictJob = {}          # Dizionario del comando corrente
        self.dictJobs = {}         # Dizionario contenitore principale
        self.sJobEnd = ""          # Nome del file .end risultato
        
        # Oggetto log
        self.objLog = None
        
        print(f"Eseguita {self.sProc}: Inizializzazione completata")
    
    def Start(self) -> str:
        """
        Metodo Start - Legge/crea il file .ini e inizializza l'applicazione
        
        Returns:
            str: Stringa vuota se OK, altrimenti messaggio di errore
        """
        sProc = "acJobsApp.Start"
        sResult = ""
        
        try:
            # Inizializzazione timestamp
            self.tsStart = aiSys.Timestamp()
            
            # Inizializzazione oggetto log
            self.objLog = aiSys.acLog()
            sResultLog = self.objLog.Start()
            if sResultLog != "":
                sResult = f"Errore inizializzazione log: {sResultLog}"
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            # Verifica parametri
            if len(sys.argv) < 2:
                sResult = "NTJOBSAPP: Eseguire con parametro file .ini o nella forma ntjobsapp.py command parametro valore ecc."
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            # Gestione primo parametro
            first_param = sys.argv[1]
            
            if not first_param.endswith(".ini"):
                # Creazione file .ini dai parametri
                sResult = self.MakeIni()
                if sResult != "":
                    print(f"Eseguita {sProc}: {sResult}")
                    return sResult
            else:
                # File .ini fornito
                self.sJobIni = first_param
            
            # Verifica esistenza file
            if not os.path.exists(self.sJobIni):
                sResult = f"File .ini non esistente {self.sJobIni}"
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            # Inizializzazione nome file .end
            base_name = os.path.splitext(self.sJobIni)[0]
            self.sJobEnd = f"{base_name}.end"
            
            # Lettura file .ini
            sResult, self.dictJobs = aiSys.read_ini_to_dict(self.sJobIni)
            if sResult != "":
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            print(f"Letto {self.sJobIni}")
            
            # Verifica chiavi riservate
            reserved_keys = ["TS.START", "TS.END", "RETURN.TYPE", "RETURN.VALUE"]
            reserved_prefixes = ["RETURN.FILE."]
            
            for section, values in self.dictJobs.items():
                for key in values.keys():
                    key_upper = key.upper()
                    # Verifica chiavi riservate
                    if key_upper in reserved_keys:
                        sResult = f"Usate chiavi riservate {key}"
                        print(f"Eseguita {sProc}: {sResult}")
                        return sResult
                    # Verifica prefissi riservati
                    for prefix in reserved_prefixes:
                        if key_upper.startswith(prefix):
                            sResult = f"Usate chiavi riservate {key}"
                            print(f"Eseguita {sProc}: {sResult}")
                            return sResult
            
            print(f"Processato {self.sJobIni}, Sezioni {', '.join(self.dictJobs.keys())}")
            
            # Verifica sezione CONFIG
            if "CONFIG" not in self.dictJobs:
                sResult = f"Sezione CONFIG non trovata in file {self.sJobIni}"
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            # Verifica sezioni job
            for section_key in self.dictJobs.keys():
                if section_key != "CONFIG":
                    dict_temp = self.dictJobs[section_key].copy()
                    
                    # Verifica presenza COMMAND
                    if "COMMAND" not in dict_temp:
                        sResult += f"Per questa sezione COMMAND non presente: {section_key}\n"
                    
                    # Verifica file richiesti
                    for key, value in dict_temp.items():
                        if key.upper().startswith("FILE."):
                            # Estrai nome file
                            sFile = os.path.basename(str(value))
                            
                            # Verifica esistenza
                            if not os.path.exists(sFile):
                                sResult += f"File richiesto non presente {sFile}\n"
            
            if sResult != "":
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            # Inizializzazione parametri configurazione
            self.sLog = self.Config("LOG")
            self.sType = self.Config("TYPE")
            self.sName = self.Config("NAME")
            
            # Conversione valori booleani
            exit_str = self.Config("EXIT")
            self.bErrExit = aiSys.isBool(exit_str) if exit_str != "" else True
            
            expand_str = self.Config("EXPAND")
            self.bExpand = aiSys.isBool(expand_str) if expand_str != "" else False
            
            # Rimozione password per sicurezza
            config_section = self.dictJobs.get("CONFIG", {})
            if "PASSWORD" in config_section:
                del self.dictJobs["CONFIG"]["PASSWORD"]
            
            # Espansione dizionario se richiesto
            if self.bExpand and sResult == "":
                aiSys.ExpandDict(self.dictJobs, self.dictJobs.get("CONFIG", {}))
            
            # Verifiche finali
            if self.sName == "":
                sResult = "NAME non precisato"
            elif not self.sType.startswith("NTJOBS.APP."):
                sResult = "Type INI non NTJOBSAPP"
        
        except Exception as e:
            sResult = f"Errore in {sProc}: {str(e)}"
        
        # Log e ritorno
        self.Log0(sResult)
        print(f"Eseguita {sProc}: {sResult}")
        return sResult
    
    def MakeIni(self) -> str:
        """
        Crea un file .ini dai parametri della riga di comando
        
        Returns:
            str: Stringa vuota se OK, altrimenti messaggio di errore
        """
        sProc = "acJobsApp.MakeIni"
        sResult = ""
        
        try:
            self.sJobIni = ""
            dict_temp = {}
            
            # Verifica numero parametri (1 + multiplo di 2)
            if (len(sys.argv) - 1) % 2 != 1:
                sResult = "Errore numero parametri comando chiave=valore ecc."
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            # Estrazione comando (primo parametro)
            sCommand = sys.argv[1]
            
            # Estrazione coppie chiave-valore
            i = 2
            while i < len(sys.argv):
                key = sys.argv[i].strip('"\'')
                if i + 1 < len(sys.argv):
                    value = sys.argv[i + 1].strip('"\'')
                    dict_temp[key] = value
                i += 2
            
            # Creazione file .ini
            sFileTemp = "ntjobsapp.ini"
            
            # Creazione struttura dati
            ini_data = {
                "CONFIG": {
                    "TYPE": "NTJOBS.APP.2"
                },
                "APP": {
                    "COMMAND": sCommand
                }
            }
            
            # Aggiunta parametri alla sezione APP
            ini_data["APP"].update(dict_temp)
            
            # Salvataggio file
            sResult = aiSys.save_dict_to_ini(ini_data, sFileTemp)
            if sResult != "":
                print(f"Eseguita {sProc}: {sResult}")
                return sResult
            
            self.sJobIni = sFileTemp
        
        except Exception as e:
            sResult = f"Errore in {sProc}: {str(e)}"
        
        print(f"Eseguita {sProc}: {sResult}")
        return sResult
    
    def Config(self, sKey: str) -> str:
        """
        Ritorna il valore di un setting dalla sezione CONFIG
        
        Args:
            sKey: Chiave del setting
            
        Returns:
            str: Valore del setting o stringa vuota
        """
        try:
            # Normalizzazione chiave
            key_norm = sKey.upper().replace(" ", "")
            
            # Ricerca nella sezione CONFIG
            config_section = self.dictJobs.get("CONFIG", {})
            
            # Ricerca case-insensitive
            for key, value in config_section.items():
                if key.upper().replace(" ", "") == key_norm:
                    return str(value)
            
            return ""
        except Exception:
            return ""
    
    def AddTimestamp(self, dictTemp: Dict) -> None:
        """
        Aggiunge timestamp a un dizionario
        
        Args:
            dictTemp: Dizionario da aggiornare
        """
        dictTemp["TS.START"] = self.tsStart
        dictTemp["TS.END"] = aiSys.Timestamp()
    
    def Return(self, sResult: str, sValue: str = "", dictFiles: Dict = None) -> str:
        """
        Aggiorna il risultato dell'elaborazione corrente
        
        Args:
            sResult: Risultato dell'elaborazione
            sValue: Valore facoltativo
            dictFiles: Dizionario file risultato
            
        Returns:
            str: sResult (eventualmente modificato)
        """
        sProc = "acJobsApp.Return"
        
        try:
            # Determinazione tipo di ritorno
            sReturnType = "E" if sResult != "" else "S"
            
            # Gestione valore
            if sValue == "" and sReturnType == "E":
                sValue = sResult
            
            # Gestione file risultato
            if dictFiles is not None:
                for file_id, file_path in dictFiles.items():
                    # Estrazione nome file senza path
                    file_name = os.path.basename(str(file_path))
                    
                    # Verifica esistenza nella cartella corrente
                    if not os.path.exists(file_name):
                        sResult = f"Errore file non presente: {file_name}"
                        print(f"Eseguita {sProc}: {sResult}")
                        return sResult
                    
                    # Aggiunta al dizionario job
                    key_name = f"RETURN.FILE.{file_id}"
                    self.dictJob[key_name] = file_name
            
            # Aggiornamento dizionario job
            self.dictJob["RETURN.TYPE"] = sReturnType
            self.dictJob["RETURN.VALUE"] = sValue
            
            # Aggiunta timestamp
            self.AddTimestamp(self.dictJob)
        
        except Exception as e:
            sResult = f"Errore in {sProc}: {str(e)}"
        
        print(f"Eseguita {sProc}: {sResult}")
        return sResult
    
    def Run(self, cbCommands: Callable) -> str:
        """
        Esegue i comandi definiti nel file .ini
        
        Args:
            cbCommands: Funzione callback per eseguire i comandi
            
        Returns:
            str: Risultato dell'esecuzione
        """
        sProc = "acJobsApp.Run"
        sResult = ""
        
        try:
            # Ciclo attraverso le sezioni
            for section_key in self.dictJobs.keys():
                if section_key == "CONFIG":
                    continue
                
                print(f"Esecuzione Action {section_key}")
                
                # Copia del dizionario della sezione corrente
                self.dictJob = self.dictJobs[section_key].copy()
                self.sJobId = section_key
                
                # Estrazione comando
                self.sCommand = self.dictJob.get("COMMAND", "")
                
                # Log inizio esecuzione
                self.Log1(f"Eseguo il comando: {self.sCommand}, Sezione: {section_key}, "
                         f"TS: {aiSys.Timestamp()}")
                
                # Esecuzione comando
                sResult = cbCommands(self.dictJob)
                
                # Aggiornamento dizionario principale
                self.dictJobs[section_key] = self.dictJob.copy()
                
                # Log fine esecuzione
                self.Log1(f"Eseguito il comando: {self.sCommand}, Sezione: {section_key}, "
                         f"TS: {aiSys.Timestamp()}, Risultato: {sResult}")
                
                # Uscita anticipata se richiesto
                if sResult != "" and self.bErrExit:
                    break
        
        except Exception as e:
            sResult = f"Errore in {sProc}: {str(e)}"
        
        print(f"Eseguita {sProc}: {sResult}")
        return sResult
    
    def End(self, sResult: str) -> None:
        """
        Finalizza l'applicazione e salva i risultati
        
        Args:
            sResult: Risultato finale dell'applicazione
        """
        sProc = "acJobsApp.End"
        
        try:
            bIsFatalError = False
            nResult = 0
            
            # FASE 1: Determinazione codice di uscita
            if not self.dictJobs:
                nResult = 1
                bIsFatalError = True
                # Creazione struttura minima
                self.dictJobs = {"CONFIG": {}}
            elif sResult != "":
                nResult = 2
                bIsFatalError = True
            
            # FASE 2: Aggiornamento dati in caso di errore
            if bIsFatalError:
                dictTemp = {
                    "RETURN.TYPE": "E",
                    "RETURN.VALUE": sResult
                }
                
                # Aggiunta timestamp
                self.AddTimestamp(dictTemp)
                
                # Unione con sezione CONFIG
                if "CONFIG" in self.dictJobs:
                    self.dictJobs["CONFIG"].update(dictTemp)
                else:
                    self.dictJobs["CONFIG"] = dictTemp
            
            # FASE 3: Salvataggio, log e uscita
            if self.sJobEnd:
                sResultSave = aiSys.save_dict_to_ini(self.dictJobs, self.sJobEnd)
                if sResultSave != "":
                    print(f"Errore salvataggio file .end: {sResultSave}")
            
            # Log finale
            self.Log(sResult, f"Fine applicazione {self.sName}")
            
            # Uscita con codice di errore
            if nResult != 0:
                sys.exit(nResult)
        
        except Exception as e:
            print(f"Errore in {sProc}: {str(e)}")
            sys.exit(1)
    
    # Metodi di log (remapping)
    def Log(self, sType: str, sValue: str = "") -> None:
        """Remapping di objLog.Log()"""
        if self.objLog:
            self.objLog.Log(sType, sValue)
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """Remapping di objLog.Log0()"""
        if self.objLog:
            self.objLog.Log0(sResult, sValue)
    
    def Log1(self, sValue: str = "") -> None:
        """Remapping di objLog.Log1()"""
        if self.objLog:
            self.objLog.Log1(sValue)


# Variabile globale jData
jData = acJobsApp()


# Esempio di utilizzo
if __name__ == "__main__":
    # Logica di funzionamento principale
    sResult = jData.Start()
    
    if sResult != "":
        jData.End(sResult)
        sys.exit(1)
    
    # Definizione funzione callback (esempio)
    def example_callback(dictJob):
        """Esempio di funzione callback per i comandi"""
        print(f"Esecuzione comando: {dictJob.get('COMMAND', 'N/A')}")
        return ""  # Nessun errore
    
    # Esecuzione comandi
    sResult = jData.Run(example_callback)
    
    # Finalizzazione
    jData.End(sResult)