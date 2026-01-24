#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aiSys.py - Modulo di funzioni globali di supporto
Autore: Sistema
Data: 2024
"""

import os
import sys
import re
import csv
import json
import configparser
from datetime import datetime, timedelta
from typing import Dict, List, Union, Any, Optional, Tuple


# ============================================================================
# FUNZIONI TIMESTAMP
# ============================================================================

def Timestamp(sPostfix: str = "") -> str:
    """
    Calcola la stringa di default TimeStamp nel formato: AAAAMMGG:HHMMSS
    
    Args:
        sPostfix (str, optional): Suffisso da aggiungere. Default: "".
        
    Returns:
        str: Timestamp nel formato "AAAAMMGG:HHMMSS" o "AAAAMMGG:HHMMSS:suffix"
             Stringa vuota in caso di errore.
    """
    sProc = "Timestamp"
    try:
        sTimestamp = datetime.now().strftime("%Y%m%d:%H%M%S")
        if sPostfix:
            return f"{sTimestamp}:{sPostfix.lower()}"
        return sTimestamp
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


def TimestampConvert(sTimestamp: str, sMode: str = "s") -> Union[int, float]:
    """
    Converte l'output di Timestamp() in giorni o secondi.
    
    Args:
        sTimestamp (str): Stringa nel formato "AAAAMMGG:HHMMSS" o "AAAAMMGG:HHMMSS:postfix"
        sMode (str, optional): "d" per giorni (float), "s" per secondi (int). Default: "s".
        
    Returns:
        Union[int, float]: - In modalità "d": float (giorni con decimali)
                           - In modalità "s": int (secondi totali)
                           - -1 in caso di errore
    """
    sProc = "TimestampConvert"
    try:
        if not sTimestamp:
            sTimestamp = Timestamp()
        
        if ':' in sTimestamp:
            parts = sTimestamp.split(':')
            if len(parts) >= 2:
                date_part = parts[0]
                time_part = parts[1]
            else:
                return -1
        else:
            return -1
        
        if len(date_part) != 8 or len(time_part) != 6:
            return -1
        
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        dt = datetime(year, month, day, hour, minute, second)
        epoch = datetime(1970, 1, 1)
        
        if sMode.lower() == "d":
            delta = dt - epoch
            return delta.total_seconds() / 86400.0
        elif sMode.lower() == "s":
            delta = dt - epoch
            return int(delta.total_seconds())
        else:
            return -1
            
    except (ValueError, TypeError) as e:
        print(f"{sProc}: Errore - {e}")
        return -1
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return -1


def TimestampFromSeconds(nSeconds: int, sPostfix: str = "") -> str:
    """
    Converte secondi dall'epoch nel formato Timestamp().
    
    Args:
        nSeconds (int): Secondi dall'epoch (1 gennaio 1970)
        sPostfix (str, optional): Suffisso opzionale. Default: "".
        
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore.
    """
    sProc = "TimestampFromSeconds"
    try:
        dt = datetime(1970, 1, 1) + timedelta(seconds=nSeconds)
        sTimestamp = dt.strftime("%Y%m%d:%H%M%S")
        if sPostfix:
            return f"{sTimestamp}:{sPostfix.lower()}"
        return sTimestamp
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


def TimestampFromDays(nDays: float, sPostfix: str = "") -> str:
    """
    Converte giorni dall'epoch nel formato Timestamp().
    
    Args:
        nDays (float): Giorni dall'epoch (1 gennaio 1970)
        sPostfix (str, optional): Suffisso opzionale. Default: "".
        
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore.
    """
    sProc = "TimestampFromDays"
    try:
        seconds = int(nDays * 86400.0)
        return TimestampFromSeconds(seconds, sPostfix)
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


def TimestampValidate(sTimestamp: str) -> bool:
    """
    Valida se una stringa è nel formato Timestamp valido.
    
    Args:
        sTimestamp (str): Stringa da validare.
        
    Returns:
        bool: True se valido, False altrimenti.
    """
    sProc = "TimestampValidate"
    try:
        if not sTimestamp:
            return False
        
        if ':' in sTimestamp:
            parts = sTimestamp.split(':')
            if len(parts) < 2:
                return False
            date_part = parts[0]
            time_part = parts[1]
        else:
            return False
        
        if len(date_part) != 8 or len(time_part) != 6:
            return False
        
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        if not (0 <= hour <= 23):
            return False
        if not (0 <= minute <= 59):
            return False
        if not (0 <= second <= 59):
            return False
        
        # Controllo giorni nel mese (considerando anni bisestili)
        days_in_month = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        if day > days_in_month[month - 1]:
            return False
        
        return True
        
    except (ValueError, TypeError):
        return False
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def TimestampDiff(sTimestamp1: str, sTimestamp2: str, sMode: str = "s") -> Union[int, float]:
    """
    Calcola la differenza tra due timestamp.
    
    Args:
        sTimestamp1 (str): Primo timestamp.
        sTimestamp2 (str): Secondo timestamp.
        sMode (str, optional): "d" per giorni, "s" per secondi. Default: "s".
        
    Returns:
        Union[int, float]: Differenza in giorni o secondi, -1 in caso di errore.
    """
    sProc = "TimestampDiff"
    try:
        if not TimestampValidate(sTimestamp1) or not TimestampValidate(sTimestamp2):
            return -1
        
        sec1 = TimestampConvert(sTimestamp1, "s")
        sec2 = TimestampConvert(sTimestamp2, "s")
        
        if sec1 == -1 or sec2 == -1:
            return -1
        
        diff_seconds = abs(sec1 - sec2)
        
        if sMode.lower() == "d":
            return diff_seconds / 86400.0
        elif sMode.lower() == "s":
            return diff_seconds
        else:
            return -1
            
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return -1


def TimestampAdd(sTimestamp: str, nValue: Union[int, float], sUnit: str = "s") -> str:
    """
    Aggiunge tempo a un timestamp.
    
    Args:
        sTimestamp (str): Timestamp di partenza.
        nValue (Union[int, float]): Valore da aggiungere.
        sUnit (str, optional): "s" per secondi, "d" per giorni, "m" per minuti, "h" per ore. Default: "s".
        
    Returns:
        str: Nuovo timestamp, stringa vuota in caso di errore.
    """
    sProc = "TimestampAdd"
    try:
        if not TimestampValidate(sTimestamp):
            return ""
        
        seconds = TimestampConvert(sTimestamp, "s")
        if seconds == -1:
            return ""
        
        if sUnit.lower() == "s":
            seconds_to_add = nValue
        elif sUnit.lower() == "m":
            seconds_to_add = nValue * 60
        elif sUnit.lower() == "h":
            seconds_to_add = nValue * 3600
        elif sUnit.lower() == "d":
            seconds_to_add = nValue * 86400
        else:
            return ""
        
        new_seconds = seconds + int(seconds_to_add)
        return TimestampFromSeconds(new_seconds)
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


# ============================================================================
# FUNZIONI DI ESPANSIONE E CONFIGURAZIONE
# ============================================================================

def Expand(sText: str, dictConfig: Dict[str, str]) -> str:
    """
    Converte una stringa espandendo sequenze di escape e variabili.
    
    Fase 1: Gestione sequenze di escape:
        %% → %
        %" → "
        %n → \n (newline)
        %$ → $
        \\ → \
    
    Fase 2: Espansione variabili $NOME_VARIABILE
    
    Args:
        sText (str): Testo da espandere.
        dictConfig (Dict[str, str]): Dizionario per l'espansione delle variabili.
        
    Returns:
        str: Stringa convertita.
    """
    sProc = "Expand"
    try:
        if not sText:
            return ""
        
        # Fase 1: Gestione sequenze di escape
        result = sText
        result = result.replace("%%", "\x01")  # Placeholder temporaneo
        result = result.replace("%\"", "\"")
        result = result.replace("%n", "\n")
        result = result.replace("%$", "$")
        result = result.replace("\\\\", "\\")
        result = result.replace("\x01", "%")  # Ripristina %
        
        # Fase 2: Espansione variabili
        def replace_var(match):
            var_name = match.group(1)
            return dictConfig.get(var_name, "UNKNOWN")
        
        result = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', replace_var, result)
        
        return result
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return sText


def ExpandDict(dictExpand: Dict, dictParam: Dict[str, str]) -> Dict:
    """
    Applica la funzione Expand() a tutti i valori di un dizionario.
    
    Args:
        dictExpand (Dict): Dizionario da convertire.
        dictParam (Dict[str, str]): Dizionario per l'espansione.
        
    Returns:
        Dict: Dizionario con valori espansi.
    """
    sProc = "ExpandDict"
    try:
        if not dictExpand:
            return {}
        
        result = {}
        for key, value in dictExpand.items():
            if isinstance(value, str):
                result[key] = Expand(value, dictParam)
            elif isinstance(value, dict):
                result[key] = ExpandDict(value, dictParam)
            else:
                result[key] = value
                
        return result
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return dictExpand


def isBool(sText: str) -> bool:
    """
    Verifica se una stringa rappresenta un valore booleano.
    
    Args:
        sText (str): Stringa da verificare.
        
    Returns:
        bool: True se sText="True" o "TRUE" o "False" o "FALSE", False altrimenti.
    """
    sProc = "isBool"
    try:
        if not sText:
            return False
        
        sText = sText.strip()
        return sText.upper() in ["TRUE", "FALSE"]
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def isGroups(asGroups1: List[str], asGroups2: List[str]) -> bool:
    """
    Verifica se almeno un elemento di asGroups1 è contenuto in asGroups2.
    
    Args:
        asGroups1 (List[str]): Prima lista di elementi.
        asGroups2 (List[str]): Seconda lista di elementi.
        
    Returns:
        bool: True se almeno un elemento è comune, False altrimenti.
    """
    sProc = "isGroups"
    try:
        if not asGroups1 or not asGroups2:
            return False
        
        for item in asGroups1:
            if item in asGroups2:
                return True
        return False
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def Config(dictConfig: Dict, sKey: str) -> str:
    """
    Legge un valore da un dizionario di configurazione.
    
    Args:
        dictConfig (Dict): Dizionario da leggere.
        sKey (str): Chiave da estrarre.
        
    Returns:
        str: Valore della chiave o stringa vuota se non trovato.
    """
    sProc = "Config"
    try:
        if dictConfig is None:
            return ""
        
        return str(dictConfig.get(sKey, ""))
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


def ConfigDefault(sKey: str, xValue: Any, dictConfig: Dict) -> None:
    """
    Imposta un valore di default in un dizionario solo se la chiave non esiste
    o ha valore None o stringa vuota.
    
    Args:
        sKey (str): Chiave da impostare.
        xValue (Any): Valore di default.
        dictConfig (Dict): Dizionario da aggiornare.
    """
    sProc = "ConfigDefault"
    try:
        if dictConfig is None:
            return
        
        current_value = dictConfig.get(sKey)
        if current_value is None or current_value == "":
            dictConfig[sKey] = xValue
            
    except Exception as e:
        print(f"{sProc}: Errore - {e}")


def ConfigSet(dictConfig: Dict, sKey: str, xValue: Any = "") -> None:
    """
    Aggiunge o sostituisce una chiave in un dizionario.
    
    Args:
        dictConfig (Dict): Dizionario da aggiornare.
        sKey (str): Chiave da aggiungere/sostituire.
        xValue (Any, optional): Valore da impostare. Default: "".
    """
    sProc = "ConfigSet"
    try:
        if dictConfig is None:
            return
        
        dictConfig[sKey] = xValue
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")


# ============================================================================
# FUNZIONI DI LETTURA/SCRITTURA FILE
# ============================================================================

def read_csv_to_dict(csv_file_path: str, asHeader: List[str] = None, delimiter: str = ';') -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file CSV e lo converte in un dizionario di dizionari.
    
    Args:
        csv_file_path (str): Percorso completo del file CSV.
        asHeader (List[str], optional): Array con i nomi dei campi richiesti. Default: None.
        delimiter (str, optional): Carattere delimitatore. Default: ';'.
        
    Returns:
        Tuple[str, Dict[str, Dict[str, str]]]: (sResult, dictCSV)
            - sResult: Stringa errore o vuota
            - dictCSV: Dizionario dei dati [chiave_primaria, Dict[colonna, valore]]
    """
    sProc = "read_csv_to_dict"
    sResult = ""
    dictCSV = {}
    
    try:
        # Verifica esistenza file
        if not os.path.exists(csv_file_path):
            sResult = f"File non valido {csv_file_path}"
            return sResult, {}
        
        # Leggi file CSV
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Leggi header
            reader = csv.reader(csvfile, delimiter=delimiter)
            try:
                header = next(reader)
            except StopIteration:
                sResult = f"File vuoto o non Valido {csv_file_path}"
                return sResult, {}
            
            # Verifica header se richiesto
            if asHeader:
                if len(header) != len(asHeader):
                    sResult = f"Numero campi non corretto, Letti: {len(header)}, Previsti: {len(asHeader)}, File: {csv_file_path}"
                    return sResult, {}
                
                for i, h in enumerate(header):
                    if h.strip() != asHeader[i]:
                        sResult = f"Campo header non corrisponde: '{h.strip()}' != '{asHeader[i]}', File: {csv_file_path}"
                        return sResult, {}
            
            nFieldsHeader = len(header)
            
            # Leggi righe
            row_num = 1
            for row in reader:
                row_num += 1
                nFieldsRead = len(row)
                
                if nFieldsRead != nFieldsHeader:
                    sResult = f"Numero campi non corretto, record: {row_num}, Letti: {nFieldsRead}, Previsti: {nFieldsHeader}, File: {csv_file_path}"
                    return sResult, {}
                
                # Prima colonna come chiave
                key = row[0].strip()
                if not key:
                    sResult = f"Errore chiavi nulle alla riga {row_num}, File: {csv_file_path}"
                    return sResult, {}
                
                if key in dictCSV:
                    sResult = f"Errore chiave duplicata '{key}' alla riga {row_num}, File: {csv_file_path}"
                    return sResult, {}
                
                # Crea dizionario interno
                inner_dict = {}
                for i in range(nFieldsHeader):
                    inner_dict[header[i]] = row[i].strip()
                
                dictCSV[key] = inner_dict
        
        return sResult, dictCSV
        
    except FileNotFoundError:
        sResult = f"Errore apertura file CSV: {csv_file_path}"
        return sResult, {}
    except Exception as e:
        sResult = f"Errore lettura file {csv_file_path}: {e}"
        return sResult, {}


def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file INI e lo converte in un dizionario di dizionari.
    
    Args:
        ini_file_path (str): Percorso completo del file INI.
        
    Returns:
        Tuple[str, Dict[str, Dict[str, str]]]: (sResult, dictINI)
            - sResult: Stringa errore o vuota
            - dictINI: Dizionario [sezione, Dict[chiave, valore]]
    """
    sProc = "read_ini_to_dict"
    sResult = ""
    dictINI = {}
    
    try:
        # Verifica esistenza file
        if not os.path.exists(ini_file_path):
            sResult = f"File non esistente: {ini_file_path}"
            return sResult, {}
        
        # Configura configparser
        config = configparser.ConfigParser(
            interpolation=None,
            comment_prefixes=(';',),
            inline_comment_prefixes=()
        )
        config.optionxform = str  # Mantieni case originale
        
        # Leggi file
        config.read(ini_file_path, encoding='utf-8')
        
        # Converti in dizionario
        for section in config.sections():
            dictINI[section] = {}
            for key in config[section]:
                dictINI[section][key] = config[section][key]
        
        print(f"Letto file .ini {ini_file_path}, Numero Sezioni: {len(dictINI)}")
        return sResult, dictINI
        
    except FileNotFoundError:
        sResult = f"Errore apertura file INI: {ini_file_path}"
        return sResult, {}
    except Exception as e:
        sResult = f"Errore lettura file INI {ini_file_path}: {e}"
        return sResult, {}


def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], ini_file_path: str) -> str:
    """
    Salva un dizionario di dizionari in un file INI.
    
    Args:
        data_dict (Dict[str, Dict[str, str]]): Dizionario da salvare.
        ini_file_path (str): Percorso completo del file INI.
        
    Returns:
        str: Stringa vuota in caso di successo, stringa di errore altrimenti.
    """
    sProc = "save_dict_to_ini"
    try:
        # Crea directory se non esiste
        os.makedirs(os.path.dirname(ini_file_path), exist_ok=True)
        
        # Configura configparser
        config = configparser.ConfigParser()
        config.optionxform = str  # Mantieni case originale
        
        # Aggiungi sezioni e chiavi
        for section, section_dict in data_dict.items():
            config[section] = section_dict
        
        # Salva file
        with open(ini_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        return ""
        
    except Exception as e:
        return f"{sProc}: Errore - {e}"


def save_array_file(sFile: str, asLines: List[str], sMode: str = "") -> str:
    """
    Salva un array di stringhe in un file.
    
    Args:
        asLines (List[str]): Array di stringhe da salvare.
        sFile (str): Nome del file.
        sMode (str, optional): "a" per append, altri valori per sovrascrivere. Default: "".
        
    Returns:
        str: Stringa vuota in caso di successo, stringa di errore altrimenti.
    """
    sProc = "save_array_file"
    try:
        mode = 'a' if sMode == "a" else 'w'
        
        with open(sFile, mode, encoding='utf-8') as f:
            for line in asLines:
                f.write(line + "\n")
        
        return ""
        
    except Exception as e:
        return f"Errore salvataggio array in {sFile}, Errore: {e}"


def read_array_file(sFile: str) -> Tuple[str, List[str]]:
    """
    Legge un file di testo e lo converte in un array di stringhe.
    
    Args:
        sFile (str): Nome del file da leggere.
        
    Returns:
        Tuple[str, List[str]]: (sResult, asLines)
            - sResult: Stringa errore o vuota
            - asLines: Array di stringhe lette
    """
    sProc = "read_array_file"
    sResult = ""
    asLines = []
    
    try:
        if not os.path.exists(sFile):
            sResult = f"File non esistente: {sFile}"
            return sResult, asLines
        
        with open(sFile, 'r', encoding='utf-8') as f:
            asLines = [line.rstrip('\n') for line in f.readlines()]
        
        return sResult, asLines
        
    except Exception as e:
        sResult = f"Errore lettura array di stringhe in {sFile}, Errore: {e}"
        return sResult, asLines


# ============================================================================
# FUNZIONI DI UTILITY PER STRINGHE
# ============================================================================

def StringBoolean(sText: str) -> bool:
    """
    Converte una stringa in valore booleano.
    
    Args:
        sText (str): Stringa da convertire.
        
    Returns:
        bool: True se sText="True" o "TRUE", False altrimenti.
    """
    sProc = "StringBoolean"
    try:
        if not sText:
            return False
        
        sText = sText.strip().upper()
        return sText == "TRUE"
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def StringToArray(sText: str, delimiter: str = ',') -> List[str]:
    """
    Converte una stringa in un array (lista).
    
    Args:
        sText (str): Stringa da convertire.
        delimiter (str, optional): Carattere delimitatore. Default: ','.
        
    Returns:
        List[str]: Lista di stringhe pulite.
    """
    sProc = "StringToArray"
    try:
        if not sText:
            return []
        
        items = sText.split(delimiter)
        result = []
        
        for item in items:
            stripped = item.strip()
            if stripped:
                result.append(stripped)
        
        return result
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return []


def StringToNum(sText: str) -> Union[int, float]:
    """
    Converte una stringa in un numero.
    
    Args:
        sText (str): Stringa da convertire.
        
    Returns:
        Union[int, float]: Numero convertito, 0 in caso di errore.
    """
    sProc = "StringToNum"
    try:
        if not sText:
            return 0
        
        sText = sText.strip().replace(',', '.')
        
        # Controlla se ci sono più punti decimali
        if sText.count('.') > 1:
            return 0
        
        # Prova a convertire in float
        try:
            num = float(sText)
            # Se è un intero senza decimali, ritorna int
            if num.is_integer():
                return int(num)
            return num
        except ValueError:
            return 0
            
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return 0


def isEmail(sMail: str) -> bool:
    """
    Verifica se una stringa è un formato email valido.
    
    Args:
        sMail (str): Stringa da verificare.
        
    Returns:
        bool: True se formato valido, False altrimenti.
    """
    sProc = "isEmail"
    try:
        if not sMail:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, sMail))
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def isValidPath(sPath: str) -> bool:
    """
    Verifica se un percorso è valido ed esiste.
    
    Args:
        sPath (str): Percorso da verificare.
        
    Returns:
        bool: True se percorso valido ed esiste, False altrimenti.
    """
    sProc = "isValidPath"
    try:
        if not sPath:
            return False
        
        return os.path.exists(sPath)
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def isLettersOnly(sText: str) -> bool:
    """
    Verifica se una stringa contiene solo lettere e spazi.
    
    Args:
        sText (str): Stringa da verificare.
        
    Returns:
        bool: True se solo lettere e spazi, False altrimenti.
    """
    sProc = "isLettersOnly"
    try:
        if not sText:
            return True
        
        return bool(re.match(r'^[A-Za-z\s]+$', sText))
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


def isValidPassword(sText: str) -> bool:
    """
    Verifica se una password contiene solo caratteri permessi.
    
    Args:
        sText (str): Password da verificare.
        
    Returns:
        bool: True se caratteri permessi, False altrimenti.
    """
    sProc = "isValidPassword"
    try:
        if not sText:
            return False
        
        pattern = r'^[A-Za-z0-9_.!]+$'
        return bool(re.match(pattern, sText))
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return False


# ============================================================================
# FUNZIONI PER DIZIONARI
# ============================================================================

def DictMerge(dictSource: Dict, dictAdd: Dict) -> Dict:
    """
    Unisce due dizionari, dando priorità alle chiavi di dictAdd.
    
    Args:
        dictSource (Dict): Dizionario sorgente.
        dictAdd (Dict): Dizionario da aggiungere.
        
    Returns:
        Dict: Dizionario unito.
    """
    sProc = "DictMerge"
    try:
        if not dictAdd:
            return dictSource.copy() if dictSource else {}
        
        if not dictSource:
            return dictAdd.copy() if dictAdd else {}
        
        result = dictSource.copy()
        result.update(dictAdd)
        
        return result
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return dictSource if dictSource else {}


def DictPrint(dictData: Dict, sFile: str = "") -> str:
    """
    Visualizza un dizionario su schermo o su file.
    
    Args:
        dictData (Dict): Dizionario da visualizzare.
        sFile (str, optional): File dove accodare. Default: "" (solo schermo).
        
    Returns:
        str: Stringa vuota in caso di successo, stringa di errore altrimenti.
    """
    sProc = "DictPrint"
    try:
        # Converti in stringa JSON formattata
        sText = json.dumps(dictData, indent=2, ensure_ascii=False)
        
        # Stampa su schermo
        print(sText)
        
        # Scrivi su file se specificato
        if sFile:
            with open(sFile, 'a', encoding='utf-8') as f:
                f.write(sText + "\n")
        
        return ""
        
    except Exception as e:
        return f"{e} {sFile}"


def PathMake(sPath: str, sFile: str, sExt: str = "") -> str:
    """
    Crea un percorso completo combinando cartella, file ed estensione.
    
    Args:
        sPath (str): Percorso della cartella. Se "" o None, usa cartella corrente.
        sFile (str): Nome del file (obbligatorio).
        sExt (str, optional): Estensione del file. Default: "".
        
    Returns:
        str: Percorso completo, stringa vuota in caso di errore.
    """
    sProc = "PathMake"
    try:
        # Gestisci percorso
        if not sPath or sPath == "":
            sPath = os.getcwd()
        
        # Normalizza separatori
        sPath = os.path.normpath(sPath)
        
        # Aggiungi separatore finale se mancante
        if not sPath.endswith(os.sep):
            sPath += os.sep
        
        # Gestisci estensione
        if sExt and not sExt.startswith('.'):
            sExt = '.' + sExt
        
        # Costruisci percorso completo
        full_path = os.path.join(sPath, sFile + sExt)
        
        return os.path.normpath(full_path)
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


# ============================================================================
# CLASSE acLog
# ============================================================================

class acLog:
    """
    Classe per la gestione dei log.
    """
    
    def __init__(self):
        """Inizializza la classe acLog."""
        self.sProc = "acLog"
        self.sLog = ""
    
    def Start(self, sLogfile: str = "", sLogFolder: str = "") -> str:
        """
        Inizializza il file di log.
        
        Args:
            sLogfile (str, optional): Nome del file di log. Default: "".
            sLogFolder (str, optional): Cartella del log. Default: "".
            
        Returns:
            str: Stringa vuota in caso di successo, stringa di errore altrimenti.
        """
        sResult = ""
        try:
            # Calcola nome applicazione
            sAppName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            
            # Gestisci cartella
            if not sLogFolder:
                sLogFolder = os.getcwd()
            
            # Gestisci nome file
            if not sLogfile:
                sLogfile = sAppName
            
            # Costruisci percorso completo
            self.sLog = os.path.join(sLogFolder, sLogfile + ".log")
            
            return sResult
            
        except Exception as e:
            sResult = f"Errore Log.Start: {e}"
            return sResult
    
    def Log(self, sType: str, sValue: str = "") -> None:
        """
        Scrive una riga nel file di log.
        
        Args:
            sType (str): Tipo di log (usato come postfix).
            sValue (str, optional): Valore da loggare. Default: "".
        """
        try:
            if not self.sLog:
                return
            
            sLine = f"{Timestamp(sType)}:{sValue}"
            
            # Stampa su console
            print(sLine)
            
            # Scrivi su file
            with open(self.sLog, 'a', encoding='utf-8') as f:
                f.write(sLine + "\n")
                
        except Exception as e:
            print(f"{self.sProc}.Log: Errore - {e}")
    
    def Log0(self, sResult: str, sValue: str = "") -> None:
        """
        Esegue Log con modalità in base a sResult.
        
        Args:
            sResult (str): Risultato da valutare.
            sValue (str, optional): Valore aggiuntivo. Default: "".
        """
        try:
            if sResult:
                self.Log("ERR", f"{sResult}: {sValue}")
            else:
                self.Log("INFO", sValue)
                
        except Exception as e:
            print(f"{self.sProc}.Log0: Errore - {e}")
    
    def Log1(self, sValue: str = "") -> None:
        """
        Esegue Log di tipo INFO.
        
        Args:
            sValue (str, optional): Valore da loggare. Default: "".
        """
        try:
            self.Log("INFO", sValue)
        except Exception as e:
            print(f"{self.sProc}.Log1: Errore - {e}")


# ============================================================================
# FUNZIONE MAIN PER TEST
# ============================================================================

def __main__() -> None:
    """
    Funzione principale per testare tutte le funzioni e la classe.
    """
    print("=== TEST MODULO aiSys ===")
    
    # Test funzioni Timestamp
    print("\n--- Test funzioni Timestamp ---")
    
    ts1 = Timestamp()
    print(f"Timestamp(): {ts1}")
    
    ts2 = Timestamp("test")
    print(f"Timestamp('test'): {ts2}")
    
    ts_seconds = TimestampConvert(ts1, "s")
    print(f"TimestampConvert('{ts1}', 's'): {ts_seconds}")
    
    ts_days = TimestampConvert(ts1, "d")
    print(f"TimestampConvert('{ts1}', 'd'): {ts_days}")
    
    ts_from_sec = TimestampFromSeconds(ts_seconds)
    print(f"TimestampFromSeconds({ts_seconds}): {ts_from_sec}")
    
    ts_from_days = TimestampFromDays(ts_days)
    print(f"TimestampFromDays({ts_days}): {ts_from_days}")
    
    is_valid = TimestampValidate(ts1)
    print(f"TimestampValidate('{ts1}'): {is_valid}")
    
    ts_diff = TimestampDiff(ts1, ts2, "s")
    print(f"TimestampDiff('{ts1}', '{ts2}', 's'): {ts_diff}")
    
    ts_add = TimestampAdd(ts1, 3600, "s")
    print(f"TimestampAdd('{ts1}', 3600, 's'): {ts_add}")
    
    # Test funzioni di espansione
    print("\n--- Test funzioni di espansione ---")
    
    config = {"USER": "Mario", "VAR": "valore"}
    expanded = Expand("Ciao $USER, %$VAR", config)
    print(f"Expand('Ciao $USER, %$VAR', config): {expanded}")
    
    dict_expand = {"key1": "Ciao $USER", "key2": {"subkey": "Valore %$VAR"}}
    expanded_dict = ExpandDict(dict_expand, config)
    print(f"ExpandDict(dict_expand, config): {expanded_dict}")
    
    # Test funzioni booleane
    print("\n--- Test funzioni booleane ---")
    
    print(f"isBool('True'): {isBool('True')}")
    print(f"isBool('FALSE'): {isBool('FALSE')}")
    print(f"isBool('test'): {isBool('test')}")
    
    groups1 = ["admin", "user"]
    groups2 = ["user", "guest"]
    print(f"isGroups(['admin', 'user'], ['user', 'guest']): {isGroups(groups1, groups2)}")
    
    # Test funzioni di configurazione
    print("\n--- Test funzioni di configurazione ---")
    
    test_dict = {"key1": "value1", "key2": ""}
    print(f"Config(test_dict, 'key1'): {Config(test_dict, 'key1')}")
    
    ConfigDefault("key2", "default2", test_dict)
    ConfigDefault("key3", "default3", test_dict)
    print(f"Dopo ConfigDefault: {test_dict}")
    
    ConfigSet(test_dict, "key4", "value4")
    print(f"Dopo ConfigSet: {test_dict}")
    
    # Test funzioni stringa
    print("\n--- Test funzioni stringa ---")
    
    print(f"StringBoolean('True'): {StringBoolean('True')}")
    print(f"StringBoolean('False'): {StringBoolean('False')}")
    
    array = StringToArray("item1, item2 ,, item3")
    print(f"StringToArray('item1, item2 ,, item3'): {array}")
    
    num1 = StringToNum("123")
    num2 = StringToNum("123.45")
    print(f"StringToNum('123'): {num1} (type: {type(num1)})")
    print(f"StringToNum('123.45'): {num2} (type: {type(num2)})")
    
    # Test funzioni validazione
    print("\n--- Test funzioni validazione ---")
    
    print(f"isEmail('test@example.com'): {isEmail('test@example.com')}")
    print(f"isEmail('invalid'): {isEmail('invalid')}")
    
    print(f"isValidPath('.'): {isValidPath('.')}")
    print(f"isLettersOnly('Solo lettere'): {isLettersOnly('Solo lettere')}")
    print(f"isValidPassword('Pass123!'): {isValidPassword('Pass123!')}")
    
    # Test funzioni dizionario
    print("\n--- Test funzioni dizionario ---")
    
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    merged = DictMerge(dict1, dict2)
    print(f"DictMerge({{'a':1, 'b':2}}, {{'b':3, 'c':4}}): {merged}")
    
    # Test PathMake
    print("\n--- Test PathMake ---")
    
    path = PathMake("/tmp", "test", "txt")
    print(f"PathMake('/tmp', 'test', 'txt'): {path}")
    
    # Test classe acLog
    print("\n--- Test classe acLog ---")
    
    log = acLog()
    result = log.Start("test_log", ".")
    if result:
        print(f"Log.Start errore: {result}")
    else:
        log.Log1("Test messaggio INFO")
        log.Log("WARN", "Test messaggio WARN")
        log.Log0("", "Test Log0 senza errore")
        log.Log0("Errore123", "Test Log0 con errore")
        print("Log test completato")
    
    print("\n=== TEST COMPLETATO ===")


if __name__ == "__main__":
    __main__()