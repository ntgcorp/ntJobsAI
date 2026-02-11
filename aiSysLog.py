"""Modulo per la gestione dei log"""
from typing import Dict, Any, Optional, Union, List
import os
import sys
from aiSysTimestamp import Timestamp
from aiSysBase import ErrorProc

# Crea alias locali
loc_Timestamp = Timestamp
loc_ErrorProc = ErrorProc


class acLog:
    """Classe per la gestione dei log"""
    
    def __init__(self):
        """Inizializza l'oggetto log"""
        self.sLog = ""
        self.sAppName = ""
        
    def Start(self, sLogfile: Optional[str] = None, sLogFolder: Optional[str] = None) -> str:
        """
        Inizializza il file di log.
        
        Args:
            sLogfile: Nome file log (opzionale)
            sLogFolder: Cartella log (opzionale)
            
        Returns:
            str: sResult
        """
        sProc = "Start"
        
        try:
            sResult = ""
            
            # Calcola nome applicazione
            self.sAppName = self._get_app_name()
            
            # Determina cartella log
            if not sLogFolder or sLogFolder == "":
                sLogFolder = os.path.dirname(os.path.abspath(sys.argv[0]))
            
            # Determina nome file log
            if not sLogfile or sLogfile == "":
                sLogfile = self.sAppName
            
            # Crea percorso completo
            self.sLog = os.path.join(sLogFolder, f"{sLogfile}.log")
            
            # Crea directory se non esiste
            os.makedirs(os.path.dirname(self.sLog), exist_ok=True)
            
            return sResult
            
        except Exception as e:
            sResult = f"Errore Log.Start: {str(e)}"
            return loc_ErrorProc(sResult, sProc)
    
    def _get_app_name(self) -> str:
        """Ottiene il nome dell'applicazione corrente."""
        try:
            app_path = sys.argv[0]
            app_filename = os.path.basename(app_path)
            app_name, _ = os.path.splitext(app_filename)
            return app_name
        except:
            return "unknown_app"
    
    def Log(self, sType: str, sValue: str = "") -> None:
        """
        Scrive una riga nel log.
        
        Args:
            sType: Tipo di log (postfix)
            sValue: Valore da loggare
        """
        if not self.sLog:
            return
            
        try:
            # Crea riga di log
            timestamp = loc_Timestamp(sType)
            sLine = f"{timestamp}:{sValue}"
            
            # Scrivi su console
            print(sLine)
            
            # Scrivi su file
            with open(self.sLog, 'a', encoding='utf-8') as f:
                f.write(sLine + "\n")
                
        except Exception:
            # Ignora errori di scrittura log
            pass
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """
        Logga con gestione automatica del tipo.
        
        Args:
            sResult: Risultato (se vuoto = INFO, altrimenti ERR)
            sValue: Valore aggiuntivo
        """
        if sResult != "":
            self.Log("ERR", f"{sResult}: {sValue}")
        else:
            self.Log("INFO", sValue)
    
    def Log1(self, sValue: str = "") -> None:
        """
        Logga come INFO.
        
        Args:
            sValue: Valore da loggare
        """
        self.Log("INFO", sValue)


