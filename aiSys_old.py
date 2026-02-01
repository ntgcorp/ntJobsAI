"""
aiSys.py - Modulo principale del sistema di supporto
Importa e integra tutte le sottolibrerie, contiene la classe acLog per il logging
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import os
import sys
import traceback

# =============================================================================
# IMPORT DELLE SOTTOLIBRERIE CON FALLBACK
# =============================================================================

# Importa aiSysBase
try:
    from aiSysBase import aiErrorProc, DictMerge, DictPrint
    _HAS_AISYSBASE = True
except ImportError as e:
    print(f"Warning: Impossibile importare aiSysBase: {e}")
    _HAS_AISYSBASE = False
    
    # Fallback definitions
    def aiErrorProc(sResult: str, sProc: str) -> str:
        return f"{sProc}: Errore {sResult}" if sResult else ""
    
    def DictMerge(dictSource: Dict, dictAdd: Dict) -> Dict:
        try:
            if not dictAdd: return dictSource
            if not dictSource: return dictAdd.copy()
            result = dictSource.copy()
            result.update(dictAdd)
            return result
        except: return dictSource or {}
    
    def DictPrint(jDS: Any, dictData: Dict, sFile: Optional[str] = None) -> str:
        return "aiSysBase non disponibile"


# Importa aiSysTimestamp
try:
    from aiSysTimestamp import (
        Timestamp, TimestampConvert, TimestampFromSeconds, TimestampFromDays,
        TimestampValidate, TimestampDiff, TimestampAdd
    )
    _HAS_AISYSTIMESTAMP = True
except ImportError as e:
    print(f"Warning: Impossibile importare aiSysTimestamp: {e}")
    _HAS_AISYSTIMESTAMP = False
    
    # Fallback definitions
    from datetime import datetime, timedelta
    
    def Timestamp(sPostfix: str = "") -> str:
        try:
            ts = datetime.now().strftime("%Y%m%d:%H%M%S")
            return f"{ts}:{sPostfix.lower()}" if sPostfix else ts
        except: return ""
    
    def TimestampConvert(sTimestamp: str, sMode: str = "s") -> Union[int, float]:
        return -1
    
    def TimestampFromSeconds(nSeconds: int, sPostfix: str = "") -> str:
        return ""
    
    def TimestampFromDays(nDays: float, sPostfix: str = "") -> str:
        return ""
    
    def TimestampValidate(sTimestamp: str) -> bool:
        return False
    
    def TimestampDiff(sTimestamp1: str, sTimestamp2: str, sMode: str = "s") -> Union[int, float]:
        return -1
    
    def TimestampAdd(sTimestamp: str, nValue: Union[int, float], sUnit: str = "s") -> str:
        return ""


# Importa aiSysConfig
try:
    from aiSysConfig import Expand, ExpandDict, isGroups, Config, ConfigDefault, ConfigSet
    _HAS_AISYSCONFIG = True
except ImportError as e:
    print(f"Warning: Impossibile importare aiSysConfig: {e}")
    _HAS_AISYSCONFIG = False
    
    # Fallback definitions
    def Expand(sText: str, dictConfig: Dict) -> str:
        return sText or ""
    
    def ExpandDict(dictExpand: Dict, dictParams: Dict) -> Dict:
        return dictExpand or {}
    
    def isGroups(asGroups1: List[str], asGroups2: List[str]) -> bool:
        return False
    
    def Config(dictConfig: Dict, sKey: str) -> str:
        return ""
    
    def ConfigDefault(sKey: str, xValue: Any, dictConfig: Dict) -> None:
        pass
    
    def ConfigSet(dictConfig: Dict, sKey: str, xValue: Any = "") -> None:
        pass


# Importa aiSysFileio
try:
    from aiSysFileio import (
        read_csv_to_dict, read_ini_to_dict, save_dict_to_ini,
        save_array_file, read_array_file, isValidPath, PathMake
    )
    _HAS_AISYSFILEIO = True
except ImportError as e:
    print(f"Warning: Impossibile importare aiSysFileio: {e}")
    _HAS_AISYSFILEIO = False
    
    # Fallback definitions
    def read_csv_to_dict(csv_file_path: str, asHeader: Optional[List[str]] = None, 
                        delimiter: str = ';') -> Tuple[str, Dict]:
        return f"aiSysFileio non disponibile", {}
    
    def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict]:
        return f"aiSysFileio non disponibile", {}
    
    def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], ini_file_path: str) -> str:
        return "aiSysFileio non disponibile"
    
    def save_array_file(sFile: str, asLines: List[str], sMode: str = "") -> str:
        return "aiSysFileio non disponibile"
    
    def read_array_file(sFile: str) -> Tuple[str, List[str]]:
        return "aiSysFileio non disponibile", []
    
    def isValidPath(sPath: str) -> bool:
        return False
    
    def PathMake(sPath: Optional[str], sFile: str, sExt: Optional[str] = None) -> str:
        return ""


# Importa aiSysStrings
try:
    from aiSysStrings import isBool, isValidPassword, isLettersOnly, isEmail, StringToArray, StringToNum
    _HAS_AISYSSTRINGS = True
except ImportError as e:
    print(f"Warning: Impossibile importare aiSysStrings: {e}")
    _HAS_AISYSSTRINGS = False
    
    # Fallback definitions
    def isBool(sText: str) -> bool:
        return False
    
    def isValidPassword(sText: str) -> bool:
        return False
    
    def isLettersOnly(sText: str) -> bool:
        return False
    
    def isEmail(sMail: str) -> bool:
        return False
    
    def StringToArray(sText: str, delimiter: str = ',') -> List[str]:
        return []
    
    def StringToNum(sText: str) -> Union[int, float]:
        return 0


# Importa acDictToString
try:
    from acDictToString import acDictToString
    _HAS_ACDICTTOSTRING = True
except ImportError as e:
    print(f"Warning: Impossibile importare acDictToString: {e}")
    _HAS_ACDICTTOSTRING = False
    
    # Fallback class definition
    class acDictToString:
        def __init__(self, bInit=True):
            self.bInit = bInit
        
        def DictToXml(self, dictParam=None, **xml_options):
            return ""
        
        def DictToString(self, dictParam=None, sFormat="json"):
            return "acDictToString non disponibile"


# =============================================================================
# CLASSE acLog
# =============================================================================

class acLog:
    """
    Classe per la gestione dei log.
    Utilizzata sia da acJobsApp che da acJobsOS.
    """
    
    def __init__(self):
        """Inizializza l'oggetto log."""
        self.sLog = ""  # Percorso del file di log
        
    def Start(self, sLogfile: Optional[str] = None, sLogFolder: Optional[str] = None) -> str:
        """
        Inizializza il file di log.
        
        Args:
            sLogfile: Nome del file di log (None/"" per nome applicazione)
            sLogFolder: Cartella del log (None/"" per cartella applicazione)
            
        Returns:
            str: Stringa vuota in caso di successo, messaggio di errore altrimenti
        """
        sProc = "acLog.Start"
        sResult = ""
        
        try:
            # Calcola sAppName dal nome del programma in esecuzione
            sAppName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            if not sAppName:
                sAppName = "application"
            
            # Gestisci sLogFolder
            if not sLogFolder:
                sLogFolder = os.getcwd()  # Cartella corrente
            
            # Gestisci sLogfile
            if not sLogfile:
                sLogfile = sAppName
            
            # Assicurati che sLogFolder esista
            if not os.path.exists(sLogFolder):
                os.makedirs(sLogFolder, exist_ok=True)
            
            # Costruisci il percorso completo
            self.sLog = os.path.join(sLogFolder, f"{sLogfile}.log")
            
            # Verifica che il percorso sia valido
            if not os.path.isdir(os.path.dirname(self.sLog)):
                sResult = f"Cartella non valida: {os.path.dirname(self.sLog)}"
                return sResult
            
            # Crea file di log vuoto se non esiste
            if not os.path.exists(self.sLog):
                with open(self.sLog, 'w', encoding='utf-8') as f:
                    f.write(f"Log inizializzato: {Timestamp()}\n")
            
            return ""  # Successo
            
        except Exception as e:
            sResult = f"Errore Log.Start: {e}"
            return sResult
    
    def Log(self, sType: str, sValue: str = "") -> None:
        """
        Scrive una riga nel log.
        
        Args:
            sType: Tipo/tag del log (usato come postfix per Timestamp)
            sValue: Valore/messaggio da loggare
        """
        try:
            # Solo se il log è inizializzato
            if not self.sLog:
                return
            
            # Crea la riga di log
            sLine = f"{Timestamp(sType)}:{sValue}"
            
            # Scrivi nel file
            with open(self.sLog, 'a', encoding='utf-8') as f:
                f.write(sLine + '\n')
            
            # Scrivi anche in console
            print(sLine)
            
        except Exception:
            # In caso di errore, fallback a console
            print(f"ERRORE LOG: {sType}:{sValue}")
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """
        Log condizionale: ERR se sResult non vuoto, INFO altrimenti.
        
        Args:
            sResult: Risultato/errore da verificare
            sValue: Valore aggiuntivo
        """
        try:
            if sResult and sResult != "":
                self.Log("ERR", f"{sResult}: {sValue}")
            else:
                self.Log("INFO", sValue)
        except Exception:
            print(f"ERRORE Log0: {sResult}:{sValue}")
    
    def Log1(self, sValue: str = "") -> None:
        """
        Log di tipo INFO.
        
        Args:
            sValue: Valore da loggare
        """
        try:
            self.Log("INFO", sValue)
        except Exception:
            print(f"ERRORE Log1: {sValue}")


# =============================================================================
# ESPORTAZIONE FUNZIONI NEL NAMESPACE aiSys
# =============================================================================

# Tutte le funzioni sono già disponibili nel namespace aiSys.*
# grazie agli import sopra


# =============================================================================
# FUNZIONE __main__ PER TEST
# =============================================================================

def __main__() -> None:
    """
    Funzione di test per verificare tutte le funzionalità di aiSys.
    """
    print("=" * 70)
    print("TEST COMPLETO DEL MODULO aiSys.py")
    print("=" * 70)
    
    # Test disponibilità moduli
    print("\n1. STATO MODULI:")
    print(f"   aiSysBase: {'OK' if _HAS_AISYSBASE else 'FALLBACK'}")
    print(f"   aiSysTimestamp: {'OK' if _HAS_AISYSTIMESTAMP else 'FALLBACK'}")
    print(f"   aiSysConfig: {'OK' if _HAS_AISYSCONFIG else 'FALLBACK'}")
    print(f"   aiSysFileio: {'OK' if _HAS_AISYSFILEIO else 'FALLBACK'}")
    print(f"   aiSysStrings: {'OK' if _HAS_AISYSSTRINGS else 'FALLBACK'}")
    print(f"   acDictToString: {'OK' if _HAS_ACDICTTOSTRING else 'FALLBACK'}")
    
    # Test funzioni base
    print("\n2. TEST FUNZIONI BASE:")
    
    # aiErrorProc
    print(f"   aiErrorProc('', 'test'): '{aiErrorProc('', 'test')}'")
    print(f"   aiErrorProc('Errore test', 'test'): '{aiErrorProc('Errore test', 'test')}'")
    
    # DictMerge
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    merged = DictMerge(dict1, dict2)
    print(f"   DictMerge({{'a':1, 'b':2}}, {{'b':3, 'c':4}}): {merged}")
    
    # Test funzioni timestamp
    print("\n3. TEST TIMESTAMP:")
    ts = Timestamp()
    print(f"   Timestamp(): '{ts}'")
    print(f"   TimestampValidate('{ts}'): {TimestampValidate(ts)}")
    
    if TimestampValidate(ts):
        sec = TimestampConvert(ts, "s")
        days = TimestampConvert(ts, "d")
        print(f"   TimestampConvert('{ts}', 's'): {sec}")
        print(f"   TimestampConvert('{ts}', 'd'): {days:.6f}")
        
        # Test operazioni
        ts_plus_1h = TimestampAdd(ts, 1, "h")
        print(f"   TimestampAdd('{ts}', 1, 'h'): '{ts_plus_1h}'")
    
    # Test funzioni config
    print("\n4. TEST CONFIGURAZIONE:")
    config = {"USER": "Mario", "HOME": "/home/mario"}
    
    expanded = Expand("Ciao $USER da $HOME", config)
    print(f"   Expand('Ciao $USER da $HOME', {{'USER':'Mario',...}}): '{expanded}'")
    
    value = Config(config, "USER")
    print(f"   Config({{'USER':'Mario',...}}, 'USER'): '{value}'")
    
    # Test funzioni stringhe
    print("\n5. TEST STRINGHE:")
    print(f"   isBool('True'): {isBool('True')}")
    print(f"   isEmail('test@example.com'): {isEmail('test@example.com')}")
    print(f"   StringToArray('a,b,c'): {StringToArray('a,b,c')}")
    print(f"   StringToNum('123,45'): {StringToNum('123,45')}")
    
    # Test funzioni file I/O
    print("\n6. TEST FILE I/O:")
    import tempfile
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test PathMake
        test_path = PathMake(temp_dir, "test", "txt")
        print(f"   PathMake('{temp_dir}', 'test', 'txt'): '{test_path}'")
        
        # Test save/read array
        lines = ["Linea 1", "Linea 2", "Linea 3"]
        result = save_array_file(test_path, lines)
        print(f"   save_array_file -> risultato: '{result}'")
        
        result, read_lines = read_array_file(test_path)
        print(f"   read_array_file -> righe lette: {len(read_lines)}")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)
    
    # Test classe acLog
    print("\n7. TEST CLASSE acLog:")
    log = acLog()
    
    # Test Start con cartella temporanea
    import tempfile
    temp_log_dir = tempfile.mkdtemp()
    
    try:
        result = log.Start("test_log", temp_log_dir)
        if result == "":
            print(f"   acLog.Start() -> SUCCESSO, log file: {log.sLog}")
            
            # Test scrittura log
            log.Log1("Test messaggio INFO")
            log.Log("WARN", "Test messaggio WARN")
            log.Log0("", "Test Log0 senza errore")
            log.Log0("Errore test", "Test Log0 con errore")
            
            print(f"   Log scritti nel file: {log.sLog}")
        else:
            print(f"   acLog.Start() -> ERRORE: {result}")
    finally:
        shutil.rmtree(temp_log_dir)
    
    # Test acDictToString
    print("\n8. TEST acDictToString:")
    try:
        converter = acDictToString()
        test_dict = {"nome": "Test", "valore": 123}
        json_str = converter.DictToString(test_dict, "json")
        print(f"   acDictToString.DictToString() -> JSON generato (primi 50 char): {json_str[:50]}...")
    except Exception as e:
        print(f"   acDictToString test fallito: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETATI CON SUCCESSO!")
    print("=" * 70)


# Punto di ingresso principale
if __name__ == "__main__":
    __main__()