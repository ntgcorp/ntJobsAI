"""
aiSysLog.py - Classe per la gestione dei log
"""

import os
import sys
from datetime import datetime
from typing import Optional

def loc_aiErrorProc(sResult: str, sProc: str) -> str:
    """
    Funzione locale per la gestione errori.
    
    Args:
        sResult: Stringa errore
        sProc: Nome della procedura
    
    Returns:
        str: Stringa formattata o vuota
    """
    if sResult != "":
        return f"{sProc}: Errore {sResult}"
    return ""


def loc_Timestamp(sPostfix: str = "") -> str:
    """
    Funzione interna Timestamp (uguale a aiSysTimestamp.Timestamp).
    
    Args:
        sPostfix: Suffisso opzionale
    
    Returns:
        str: Timestamp formattato
    """
    try:
        now = datetime.now()
        sTimestamp = now.strftime("%Y%m%d:%H%M%S")
        
        if sPostfix:
            return f"{sTimestamp}:{sPostfix.lower()}"
        return sTimestamp
        
    except Exception:
        return ""


class acLog:
    """
    Classe per la gestione dei log.
    """
    
    def __init__(self):
        self.sLog = ""
        self.sAppName = ""
    
    def Start(self, sLogfile: Optional[str] = None, sLogFolder: Optional[str] = None) -> str:
        """
        Inizializza il campo interno self.sLog.
        
        Args:
            sLogfile: Nome file di log
            sLogFolder: Cartella dei log
        
        Returns:
            str: Stringa vuota se successo, errore formattato altrimenti
        """
        sResult = ""
        sProc = "Start"
        
        try:
            if hasattr(sys, 'argv') and len(sys.argv) > 0:
                app_path = sys.argv[0]
                self.sAppName = os.path.splitext(os.path.basename(app_path))[0]
            else:
                self.sAppName = "unknown"
            
            if not sLogFolder:
                sLogFolder = os.getcwd()
            
            if not sLogfile:
                sLogfile = self.sAppName
            
            if not sLogFolder.endswith(os.sep):
                sLogFolder += os.sep
            
            self.sLog = os.path.join(sLogFolder, f"{sLogfile}.log")
            
            os.makedirs(os.path.dirname(self.sLog), exist_ok=True)
            
            return ""
            
        except Exception as e:
            sResult = f"Errore Log.Start: {str(e)}"
            return loc_aiErrorProc(sResult, sProc)
    
    def Log(self, sType: str, sValue: str = "") -> None:
        """
        Salva una riga di log nel file.
        
        Args:
            sType: Tipo di log (postfix per timestamp)
            sValue: Valore del log
        """
        if not self.sLog:
            return
        
        try:
            sLine = f"{loc_Timestamp(sType)}:{sValue}"
            
            print(sLine)
            
            with open(self.sLog, 'a', encoding='utf-8') as f:
                f.write(sLine + '\n')
                
        except Exception:
            pass
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """
        Esegue Log in base al valore di sResult.
        
        Args:
            sResult: Risultato (se vuoto = INFO, altrimenti ERR)
            sValue: Valore del log
        """
        if sResult != "":
            self.Log("ERR", f"{sResult}: {sValue}")
        else:
            self.Log("INFO", sValue)
    
    def Log1(self, sValue: str = "") -> None:
        """
        Esegue Log di tipo INFO.
        
        Args:
            sValue: Valore del log
        """
        self.Log("INFO", sValue)
    
    def Timestamp(self) -> str:
        """
        Ritorna timestamp corrente (uguale a aiSys.Timestamp()).
        
        Returns:
            str: Timestamp formattato
        """
        return loc_Timestamp()


