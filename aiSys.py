# aiSys.py
import os
import re
import csv
import configparser
import sys
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import subprocess
import time

# ============================================================================
# FUNZIONI AUTONOME
# ============================================================================

def Timestamp(sPostfix: str = "") -> str:
    """
    Calcola la stringa di default TimeStamp in questa forma: AAAAMMGG:HHMMSS
    
    Se viene passato sPostfix, allora aggiungi in minuscolo sPostfix nella
    forma TimeStamp() + ":" + sPotfix
    
    Args:
        sPostfix (str, optional): Suffisso da aggiungere al timestamp
    
    Returns:
        str: Timestamp nel formato AAAAMMGG:HHMMSS o AAAAMMGG:HHMMSS:sPostfix
    """
    sProc = "Timestamp"
    
    try:
        from datetime import datetime
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d:%H%M%S")
        
        if sPostfix:
            return f"{timestamp}:{sPostfix.lower()}"
        return timestamp
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return ""

# ----------------------------------------------------------------------------

def Expand(sText: str, dictConfig: Dict[str, str]) -> str:
    """
    Converte una stringa espandendo sequenze di escape e variabili.
    
    FASE 1: GESTIONE SEQUENZE DI ESCAPE (elabora da sinistra a destra)
    FASE 2: ESPANSIONE VARIABILI (dopo aver gestito tutti gli escape)
    
    Args:
        sText (str): Testo da espandere
        dictConfig (Dict[str, str]): Dizionario con le variabili
    
    Returns:
        str: Testo espanso
    """
    sProc = "Expand"
    
    try:
        if not sText or not isinstance(sText, str):
            return sText if sText else ""
        
        # FASE 1: Gestione sequenze di escape
        result = ""
        i = 0
        n = len(sText)
        
        while i < n:
            if i + 1 < n and sText[i] == '\\':
                # Controlla il carattere successivo
                next_char = sText[i + 1]
                if next_char == '\\':
                    # Due backslash → un backslash singolo
                    result += '\\'
                    i += 2
                elif next_char == '"':
                    # Backslash + virgolette → virgolette
                    result += '"'
                    i += 2
                elif next_char == 'n':
                    # Backslash + n → newline
                    result += '\n'
                    i += 2
                elif next_char == '$':
                    # Backslash + dollaro → dollaro singolo
                    result += '$'
                    i += 2
                else:
                    # Altro carattere dopo backslash, mantieni il backslash
                    result += sText[i]
                    i += 1
            else:
                # Carattere normale
                result += sText[i]
                i += 1
        
        # FASE 2: Espansione variabili
        # Pattern per trovare $VAR ma non \$VAR
        # (?!<\\ ) cerca $ non preceduto da backslash
        pattern = r'(?<!\\)\$([a-zA-Z0-9_.]+)'
        
        def replace_var(match):
            var_name = match.group(1)
            return dictConfig.get(var_name, "UNKNOWN")
        
        # Applica la sostituzione
        expanded_text = re.sub(pattern, replace_var, result)
        
        return expanded_text
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return sText

# ----------------------------------------------------------------------------

def ExpandDict(dictExpand: Dict[str, Any], dictParams: Dict[str, str]) -> Dict[str, Any]:
    """
    Utilizza la funzione Expand() applicata ad un dizionario.
    
    Args:
        dictExpand (Dict[str, Any]): Dizionario da convertire
        dictParams (Dict[str, str]): Dizionario per la conversione
    
    Returns:
        Dict[str, Any]: Dizionario espanso
    """
    sProc = "ExpandDict"
    
    try:
        if not dictExpand or not isinstance(dictExpand, dict):
            return {}
        
        result = {}
        
        for sKey, xValue in dictExpand.items():
            if isinstance(xValue, str):
                # Espande le stringhe
                result[sKey] = Expand(xValue, dictParams)
            elif isinstance(xValue, dict):
                # Richiama ricorsivamente per i dizionari
                result[sKey] = ExpandDict(xValue, dictParams)
            else:
                # Altri tipi di dati, mantieni invariato
                result[sKey] = xValue
        
        return result
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return dictExpand

# ----------------------------------------------------------------------------

def StringBoolean(sText: str) -> bool:
    """
    Converte una stringa in valore booleano.
    
    Args:
        sText (str): Stringa da convertire
    
    Returns:
        bool: True se sText="True" o "TRUE", False altrimenti
    """
    sProc = "StringBoolean"
    
    try:
        if not sText:
            return False
        
        sClean = sText.strip().upper()
        return sClean == "TRUE"
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def isBool(sText: str) -> bool:
    """
    Verifica se una stringa contiene un valore booleano valido.
    
    Args:
        sText (str): Stringa da verificare
    
    Returns:
        bool: True se la stringa contiene True/False/TRUE/FALSE, False altrimenti
    """
    sProc = "isBool"
    
    try:
        if sText is None:
            return False
        
        sClean = sText.strip().upper()
        return sClean in ["TRUE", "FALSE", ""]
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def isGroups(asGroups1: List[str], asGroups2: List[str]) -> bool:
    """
    Verifica se almeno un elemento di asGroups1 è contenuto in asGroups2.
    
    Args:
        asGroups1 (List[str]): Prima lista di gruppi
        asGroups2 (List[str]): Seconda lista di gruppi
    
    Returns:
        bool: True se c'è almeno una corrispondenza, False altrimenti
    """
    sProc = "isGroups"
    
    try:
        if not asGroups1 or not asGroups2:
            return False
        
        for group1 in asGroups1:
            if group1 in asGroups2:
                return True
        
        return False
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def Config(sKey: str, dictConfig: Dict[str, Any]) -> Any:
    """
    Estrae un valore dal dizionario di configurazione.
    
    Args:
        sKey (str): Chiave da estrarre
        dictConfig (Dict[str, Any]): Dizionario di configurazione
    
    Returns:
        Any: Valore della chiave o "" se non trovato
    """
    sProc = "Config"
    
    try:
        if not dictConfig:
            return ""
        
        return dictConfig.get(sKey, "")
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return ""

# ----------------------------------------------------------------------------

def read_csv_to_dict(csv_file_path: str, delimiter: str = ';') -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file CSV e lo converte in un dizionario di dizionari.
    
    Args:
        csv_file_path (str): Percorso completo del file CSV
        delimiter (str, optional): Carattere delimitatore, default=';'
    
    Returns:
        Tuple[str, Dict[str, Dict[str, str]]]: (sResult, dizionario dei dati)
    """
    sProc = "read_csv_to_dict"
    sResult = ""
    data_dict = {}
    
    try:
        # Verifica che il file esista
        if not os.path.exists(csv_file_path):
            sResult = f"Errore apertura file CSV: {csv_file_path}"
            return sResult, {}
        
        # Legge il file CSV
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Usa DictReader per leggere le righe come dizionari
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Ottieni i nomi delle colonne
            fieldnames = reader.fieldnames
            if not fieldnames:
                sResult = "Errore: file CSV vuoto o senza header"
                return sResult, {}
            
            # La prima colonna sarà usata come chiave principale
            key_column = fieldnames[0]
            
            # Leggi tutte le righe
            for row_num, row in enumerate(reader, start=2):  # start=2 per considerare l'header
                # Pulisci tutti i valori
                clean_row = {k: v.strip() if v else "" for k, v in row.items()}
                
                # Ottieni la chiave dalla prima colonna
                key_value = clean_row.get(key_column, "")
                
                # Controlla se la chiave è vuota
                if not key_value:
                    sResult = f"Errore chiavi nulle alla riga {row_num}"
                    return sResult, {}
                
                # Controlla se la chiave è duplicata
                if key_value in data_dict:
                    sResult = f"Errore chiave duplicata '{key_value}' alla riga {row_num}"
                    return sResult, {}
                
                # Aggiungi al dizionario
                data_dict[key_value] = clean_row
        
        return sResult, data_dict
        
    except csv.Error as e:
        sResult = f"Errore lettura file CSV {csv_file_path}: {str(e)}"
        return sResult, {}
    except Exception as e:
        sResult = f"{sProc}: Errore - {str(e)}"
        return sResult, {}

# ----------------------------------------------------------------------------

def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file INI e lo converte in un dizionario di dizionari.
    
    Args:
        ini_file_path (str): Percorso completo del file INI
    
    Returns:
        Tuple[str, Dict[str, Dict[str, str]]]: (sResult, dizionario dei dati)
    """
    sProc = "read_ini_to_dict"
    sResult = ""
    data_dict = {}
    
    try:
        # Verifica che il file esista
        if not os.path.exists(ini_file_path):
            sResult = f"Errore apertura file INI: {ini_file_path}"
            return sResult, {}
        
        # Crea il parser INI
        config = configparser.ConfigParser()
        # Mantieni il case originale delle chiavi
        config.optionxform = str
        
        # Leggi il file
        config.read(ini_file_path, encoding='utf-8')
        
        # Converti in dizionario
        for section in config.sections():
            data_dict[section] = {}
            for key, value in config.items(section):
                data_dict[section][key] = value
        
        return sResult, data_dict
        
    except configparser.Error as e:
        sResult = f"Errore lettura file INI {ini_file_path}: {str(e)}"
        return sResult, {}
    except Exception as e:
        sResult = f"{sProc}: Errore - {str(e)}"
        return sResult, {}

# ----------------------------------------------------------------------------

def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], ini_file_path: str) -> str:
    """
    Salva un dizionario di dizionari in un file INI.
    
    Args:
        data_dict (Dict[str, Dict[str, str]]): Dizionario da salvare
        ini_file_path (str): Percorso del file INI
    
    Returns:
        str: Stringa vuota in caso di successo, stringa di errore altrimenti
    """
    sProc = "save_dict_to_ini"
    
    try:
        # Crea le directory se non esistono
        os.makedirs(os.path.dirname(ini_file_path), exist_ok=True)
        
        # Crea il parser INI
        config = configparser.ConfigParser()
        # Mantieni il case originale delle chiavi
        config.optionxform = str
        
        # Aggiungi le sezioni e le chiavi-valore
        for section, section_dict in data_dict.items():
            config[section] = section_dict
        
        # Salva il file
        with open(ini_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        return ""
        
    except Exception as e:
        return f"{sProc}: Errore - {str(e)}"

# ----------------------------------------------------------------------------

def StringToArray(sText: str, delimiter: str = ',') -> List[str]:
    """
    Converte una stringa in una lista (array).
    
    Args:
        sText (str): Stringa da convertire
        delimiter (str, optional): Carattere delimitatore, default=','
    
    Returns:
        List[str]: Lista di stringhe pulite
    """
    sProc = "StringToArray"
    
    try:
        if not sText:
            return []
        
        # Splitta la stringa
        items = sText.split(delimiter)
        
        # Pulisci e filtra gli elementi
        result = []
        for item in items:
            cleaned = item.strip()
            if cleaned:  # Inserisce solo se non è vuoto
                result.append(cleaned)
        
        return result
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return []

# ----------------------------------------------------------------------------

def StringToNum(sText: str) -> int:
    """
    Converte una stringa in un numero intero.
    
    Args:
        sText (str): Stringa da convertire
    
    Returns:
        int: Numero convertito, 0 se la conversione fallisce
    """
    sProc = "StringToNum"
    
    try:
        if not sText:
            return 0
        
        sClean = sText.strip()
        if not sClean:
            return 0
        
        # Prova a convertire in intero
        return int(sClean)
    except ValueError:
        # Se fallisce, prova a convertire in float e poi in int
        try:
            return int(float(sClean))
        except (ValueError, TypeError):
            return 0
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return 0

# ----------------------------------------------------------------------------

def isEmail(sMail: str) -> bool:
    """
    Verifica se una stringa ha formato email valido (validazione base).
    
    Args:
        sMail (str): Stringa da verificare
    
    Returns:
        bool: True se il formato è valido, False altrimenti
    """
    sProc = "isEmail"
    
    try:
        if not sMail:
            return False
        
        sClean = sMail.strip()
        if not sClean:
            return False
        
        # Regex base per validazione email
        # Formato: local-part@domain
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        return bool(re.match(email_pattern, sClean))
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def isValidPath(sPath: str) -> bool:
    """
    Verifica se un path esiste nel filesystem.
    
    Args:
        sPath (str): Path da verificare
    
    Returns:
        bool: True se il path esiste, False altrimenti
    """
    sProc = "isValidPath"
    
    try:
        if not sPath:
            return False
        
        sClean = sPath.strip()
        if not sClean:
            return False
        
        # Verifica se il path esiste
        return os.path.exists(sClean)
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def isAlphanumeric(sText: str, sExtraChars: str = "") -> bool:
    """
    Verifica se una stringa contiene solo caratteri alfanumerici e caratteri extra specificati.
    
    Args:
        sText (str): Stringa da verificare
        sExtraChars (str, optional): Caratteri extra permessi
    
    Returns:
        bool: True se la stringa contiene solo caratteri permessi, False altrimenti
    """
    sProc = "isAlphanumeric"
    
    try:
        if sText is None:
            return False
        
        sClean = sText.strip()
        if not sClean:
            return True  # Stringa vuota è considerata valida
        
        # Crea pattern con caratteri alfanumerici e caratteri extra
        pattern = f"^[a-zA-Z0-9{re.escape(sExtraChars)}]+$"
        
        return bool(re.match(pattern, sClean))
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def isLettersOnly(sText: str, bAllowSpaces: bool = True, bAllowAccents: bool = True) -> bool:
    """
    Verifica se una stringa contiene solo lettere.
    
    Args:
        sText (str): Stringa da verificare
        bAllowSpaces (bool, optional): Permette spazi, default=True
        bAllowAccents (bool, optional): Permette lettere accentate, default=True
    
    Returns:
        bool: True se la stringa contiene solo lettere, False altrimenti
    """
    sProc = "isLettersOnly"
    
    try:
        if sText is None:
            return False
        
        sClean = sText.strip()
        if not sClean:
            return True  # Stringa vuota è considerata valida
        
        # Costruisci pattern in base ai parametri
        if bAllowAccents:
            # Pattern che include lettere accentate comuni
            letter_pattern = r'a-zA-ZÀ-ÿ'
        else:
            # Solo lettere ASCII
            letter_pattern = r'a-zA-Z'
        
        if bAllowSpaces:
            pattern = f"^[{letter_pattern}\\s]+$"
        else:
            pattern = f"^[{letter_pattern}]+$"
        
        return bool(re.match(pattern, sClean))
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ----------------------------------------------------------------------------

def isValidPassword(sText: str) -> bool:
    """
    Verifica se una password rispetta i criteri di sicurezza.
    Permette: lettere (a-zA-Z), numeri (0-9), underscore (_), punto (.),
    punto esclamativo (!), cancelletto (#).
    
    Args:
        sText (str): Password da verificare
    
    Returns:
        bool: True se la password è valida, False altrimenti
    """
    sProc = "isValidPassword"
    
    try:
        if sText is None:
            return False
        
        sClean = sText.strip()
        if not sClean:
            return False  # Password non può essere vuota
        
        # Pattern per caratteri permessi: lettere, numeri, _ . ! #
        password_pattern = r'^[a-zA-Z0-9_\.!#]+$'
        
        # Verifica che contenga almeno un carattere
        if len(sClean) == 0:
            return False
        
        # Verifica che contenga solo caratteri permessi
        return bool(re.match(password_pattern, sClean))
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

# ============================================================================
# CLASSE acLog
# ============================================================================

class acLog:
    """
    Piccola classe utilizzata per log, usata sia da acJobsApp che da acJobsOS.
    """
    
    def __init__(self):
        """Inizializza l'oggetto log."""
        self.sLog = ""
        self.sAppName = ""
    
    def Start(self, sLogfile: str = "", sLogFolder: str = "") -> None:
        """
        Inizializza il campo interno self.sLog.
        
        Args:
            sLogfile (str, optional): Nome file di log
            sLogFolder (str, optional): Cartella per il log
        """
        sProc = "acLog.Start"
        
        try:
            # Calcola sAppName dal nome del programma python
            if getattr(sys, 'frozen', False):
                # Applicazione eseguibile (pyinstaller)
                app_path = sys.executable
            else:
                # Script Python normale
                app_path = sys.argv[0]
            
            self.sAppName = Path(app_path).stem
            
            # Se sLogFolder non è specificato, usa la cartella corrente
            if not sLogFolder:
                sLogFolder = os.path.dirname(os.path.abspath(app_path))
            
            # Se sLogfile non è specificato, crea il nome di default
            if not sLogfile:
                self.sLog = os.path.join(sLogFolder, f"{self.sAppName}.log")
            else:
                self.sLog = sLogfile
            
            # Crea la directory se non esiste
            log_dir = os.path.dirname(self.sLog)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
        except Exception as e:
            print(f"{sProc}: Errore - {str(e)}")
            self.sLog = ""
    
    def Log(self, sType: str, sValue: str = "") -> None:
        """
        Salva nel file di log una riga con TimeStamp.
        
        Args:
            sType (str): Tipo di log (ERR, INFO, etc.)
            sValue (str, optional): Valore del log
        """
        try:
            if not self.sLog:
                return
            
            # Crea la riga di log
            sLine = f"{Timestamp(sType)}:{sValue}"
            
            # Scrive nel file
            with open(self.sLog, 'a', encoding='utf-8') as f:
                f.write(sLine + '\n')
            
            # Scrive anche in console
            print(sLine)
            
        except Exception as e:
            print(f"acLog.Log: Errore - {str(e)}")
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """
        Esegue Log con 2 modalità:
        - Se sResult diverso da "": Log("ERR", sResult + ": " + sValue)
        - Se sResult = "": Log("INFO", sValue)
        
        Args:
            sResult (str): Risultato/errore
            sValue (str, optional): Valore aggiuntivo
        """
        if sResult:
            self.Log("ERR", f"{sResult}: {sValue}")
        else:
            self.Log("INFO", sValue)
    
    def Log1(self, sValue: str = "") -> None:
        """
        Esegue Log con tipo "INFO".
        
        Args:
            sValue (str): Valore del log
        """
        self.Log("INFO", sValue)

# ============================================================================
# FUNZIONE MAIN PER TEST (se eseguito direttamente)
# ============================================================================

if __name__ == "__main__":
    # Test delle funzioni principali
    print("Test modulo aiSys.py")
    print("=" * 50)
    
    # Test Timestamp
    print(f"Timestamp(): {Timestamp()}")
    print(f"Timestamp('test'): {Timestamp('test')}")
    
    # Test Expand
    config = {"USER": "Mario", "HOME": "/home/user"}
    print(f"\nExpand:")
        
    # Test StringBoolean e isBool
    print(f"\nStringBoolean:")
    print(f"  'True' -> {StringBoolean('True')}")
    print(f"  'False' -> {StringBoolean('False')}")
    print(f"  'TRUE' -> {StringBoolean('TRUE')}")
    
    print(f"\nisBool:")
    print(f"  'True' -> {isBool('True')}")
    print(f"  'False' -> {isBool('False')}")
    print(f"  'test' -> {isBool('test')}")
    
    # Test isGroups
    groups1 = ["admin", "user"]
    groups2 = ["guest", "user"]
    print(f"\nisGroups({groups1}, {groups2}) -> {isGroups(groups1, groups2)}")
    
    # Test StringToArray
    print(f"\nStringToArray:")
    print(f"  'a,b,c' -> {StringToArray('a,b,c')}")
    print(f"  ' item1, item2 ,, item3 ' -> {StringToArray(' item1, item2 ,, item3 ')}")
    print(f"  '' -> {StringToArray('')}")
    
    # Test StringToNum
    print(f"\nStringToNum:")
    print(f"  '123' -> {StringToNum('123')}")
    print(f"  '45.67' -> {StringToNum('45.67')}")
    print(f"  'abc' -> {StringToNum('abc')}")
    print(f"  '' -> {StringToNum('')}")
    
    # Test isEmail
    print(f"\nisEmail:")
    print(f"  'test@example.com' -> {isEmail('test@example.com')}")
    print(f"  'invalid-email' -> {isEmail('invalid-email')}")
    print(f"  '' -> {isEmail('')}")
    
    # Test isValidPath
    print(f"\nisValidPath:")
    current_file = __file__
    print(f"  '{current_file}' -> {isValidPath(current_file)}")
    print(f"  '/path/non/esistente' -> {isValidPath('/path/non/esistente')}")
    print(f"  '' -> {isValidPath('')}")
    
    # Test isAlphanumeric
    print(f"\nisAlphanumeric:")
    print(f"  'abc123' -> {isAlphanumeric('abc123')}")
    print(f"  'abc_123' -> {isAlphanumeric('abc_123', '_')}")
    print(f"  'abc-123' -> {isAlphanumeric('abc-123', '_-')}")
    print(f"  'abc 123' -> {isAlphanumeric('abc 123', ' ')}")
    
    # Test isLettersOnly
    print(f"\nisLettersOnly:")
    print(f"  'Mario Rossi' -> {isLettersOnly('Mario Rossi')}")
    print(f"  'Mario123' -> {isLettersOnly('Mario123')}")
    print(f"  'Mário Rössi' -> {isLettersOnly('Mário Rössi')}")
    print(f"  'Mário Rössi' (no accents) -> {isLettersOnly('Mário Rössi', bAllowAccents=False)}")
    print(f"  'MarioRossi' (no spaces) -> {isLettersOnly('MarioRossi', bAllowSpaces=False)}")
    
    # Test isValidPassword
    print(f"\nisValidPassword:")
    print(f"  'password123' -> {isValidPassword('password123')}")
    print(f"  'pass_word.123!' -> {isValidPassword('pass_word.123!')}")
    print(f"  'pass#word!123' -> {isValidPassword('pass#word!123')}")
    print(f"  'pass@word' -> {isValidPassword('pass@word')}")  # @ non permesso
    print(f"  '' -> {isValidPassword('')}")
    
    # Test classe acLog
    print(f"\nTest classe acLog:")
    log = acLog()
    log.Start()  # Userà il nome file di default
    log.Log("INFO", "Test log info")
    log.Log0("", "Test log0 senza errore")
    log.Log0("ErroreTest", "Test log0 con errore")
    log.Log1("Test log1")
    
    print("\nTest completato!")