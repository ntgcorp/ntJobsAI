"""
aiSysFileio.py - Funzioni per I/O su file
"""

import os
import csv
import configparser
from typing import Dict, List, Tuple, Any
import sys

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


def read_csv_to_dict(csv_file_path: str, asHeader: List[str] = None, delimiter: str = ';') -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file CSV e lo converte in un dizionario di dizionari.
    
    Args:
        csv_file_path: Percorso del file CSV
        asHeader: Array di nomi campo per verifica
        delimiter: Carattere delimitatore
    
    Returns:
        Tuple[str, Dict]: (sResult, dictCSV)
    """
    sProc = "read_csv_to_dict"
    
    try:
        sResult = ""
        
        if not os.path.exists(csv_file_path):
            sResult = f"File non valido {csv_file_path}"
            return (sResult, {})
        
        dictCSV = {}
        header = []
        line_number = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=delimiter)
            
            try:
                header = next(csv_reader)
                line_number += 1
            except StopIteration:
                sResult = f"File vuoto o non Valido {csv_file_path}"
                return (sResult, {})
            
            if asHeader:
                if not all(field in header for field in asHeader):
                    sResult = f"Header non contiene tutti i campi richiesti: {asHeader}"
                    return (sResult, {})
            
            nFieldsHeader = len(header)
            
            for row in csv_reader:
                line_number += 1
                
                if not row:
                    continue
                
                nFieldsRead = len(row)
                if nFieldsRead != nFieldsHeader:
                    sResult = f"Numero campi non corretto, record: {line_number}, Letti: {nFieldsRead}, Previsti: {nFieldsHeader}, File: {csv_file_path}"
                    return (sResult, {})
                
                key = row[0].strip()
                
                if not key:
                    sResult = "Errore chiavi nulle"
                    return (sResult, {})
                
                if key in dictCSV:
                    sResult = f"Errore chiave duplicata: {key}"
                    return (sResult, {})
                
                row_dict = {}
                for i, field in enumerate(header):
                    row_dict[field] = row[i].strip()
                
                dictCSV[key] = row_dict
        
        if not dictCSV:
            sResult = f"File vuoto o non Valido {csv_file_path}"
        
        return (sResult, dictCSV)
        
    except FileNotFoundError:
        sResult = f"Errore apertura file CSV: {csv_file_path}"
        return (sResult, {})
    except Exception as e:
        sResult = f"Errore lettura file {csv_file_path}: {str(e)}"
        return (sResult, {})


def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file INI e lo converte in un dizionario di dizionari.
    
    Args:
        ini_file_path: Percorso del file INI
    
    Returns:
        Tuple[str, Dict]: (sResult, dictINI)
    """
    sProc = "read_ini_to_dict"
    
    try:
        sResult = ""
        
        if not os.path.exists(ini_file_path):
            sResult = f"File non esistente: {ini_file_path}"
            return (sResult, {})
        
        config = configparser.ConfigParser(
            interpolation=None,
            comment_prefixes=(';',),
            inline_comment_prefixes=()
        )
        config.optionxform = str
        
        config.read(ini_file_path, encoding='utf-8')
        
        dictINI = {}
        for section in config.sections():
            dictINI[section] = {}
            for key in config[section]:
                dictINI[section][key] = config[section][key]
        
        print(f"Letto file .ini {ini_file_path}, Numero Sezioni: {len(dictINI)}")
        return (sResult, dictINI)
        
    except FileNotFoundError:
        sResult = f"Errore apertura file INI: {ini_file_path}"
        return (sResult, {})
    except Exception as e:
        sResult = f"Errore lettura file INI {ini_file_path}: {str(e)}"
        return (sResult, {})


def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], ini_file_path: str) -> str:
    """
    Salva un dizionario di dizionari in un file INI.
    
    Args:
        data_dict: Dizionario da salvare
        ini_file_path: Percorso del file INI
    
    Returns:
        str: Stringa vuota se successo, stringa di errore altrimenti
    """
    sProc = "save_dict_to_ini"
    
    try:
        if not data_dict:
            return ""
        
        config = configparser.ConfigParser()
        config.optionxform = str
        
        for section, section_data in data_dict.items():
            config[section] = {}
            for key, value in section_data.items():
                config[section][key] = str(value)
        
        os.makedirs(os.path.dirname(ini_file_path), exist_ok=True)
        
        with open(ini_file_path, 'w', encoding='utf-8') as file:
            config.write(file)
        
        return ""
        
    except Exception as e:
        return loc_aiErrorProc(str(e), sProc)


def save_array_file(sFile: str, asLines: List[str], sMode: str = "") -> str:
    """
    Salva un array di stringhe in un file.
    
    Args:
        sFile: Nome del file
        asLines: Array di stringhe
        sMode: "a" per append, altrimenti sovrascrive
    
    Returns:
        str: Stringa vuota se successo, errore formattato altrimenti
    """
    sProc = "save_array_file"
    
    try:
        if not asLines:
            asLines = []
        
        mode = 'a' if sMode == "a" else 'w'
        
        with open(sFile, mode, encoding='utf-8') as file:
            for line in asLines:
                file.write(str(line) + '\n')
        
        return ""
        
    except Exception as e:
        sResult = f"Errore salvataggio array in {sFile}, Errore: {str(e)}"
        return loc_aiErrorProc(sResult, sProc)


def read_array_file(sFile: str) -> Tuple[str, List[str]]:
    """
    Legge un file di testo e lo converte in un array di stringhe.
    
    Args:
        sFile: Nome del file
    
    Returns:
        Tuple[str, List[str]]: (sResult, asLines)
    """
    sProc = "read_array_file"
    
    try:
        if not os.path.exists(sFile):
            sResult = f"File non esistente: {sFile}"
            return (sResult, [])
        
        asLines = []
        with open(sFile, 'r', encoding='utf-8') as file:
            for line in file:
                asLines.append(line.rstrip('\n'))
        
        return ("", asLines)
        
    except Exception as e:
        sResult = f"Errore lettura array di stringhe in {sFile}, Errore: {str(e)}"
        return (sResult, [])


def isValidPath(sPath: str) -> bool:
    """
    Verifica se un percorso è valido ed esiste.
    
    Args:
        sPath: Percorso da verificare
    
    Returns:
        bool: True se percorso valido ed esiste
    """
    sProc = "isValidPath"
    
    try:
        if not sPath:
            return False
        
        return os.path.exists(sPath)
        
    except Exception:
        return False


def isFilename(sFilename: str) -> bool:
    """
    Verifica se un nome di file è corretto.
    
    Args:
        sFilename: Nome del file (senza percorso)
    
    Returns:
        bool: True se nome file valido
    """
    sProc = "isFilename"
    
    try:
        if not sFilename:
            return False
        
        if '.' in sFilename:
            name_part, ext_part = sFilename.split('.', 1)
        else:
            name_part = sFilename
            ext_part = ""
        
        name_pattern = r'^[A-Za-z0-9_]+$'
        if not re.match(name_pattern, name_part):
            return False
        
        if ext_part:
            ext_pattern = r'^[A-Za-z0-9_.]+$'
            if not re.match(ext_pattern, ext_part):
                return False
        
        return True
        
    except Exception:
        return False


def PathMake(sPath: str, sFile: str, sExt: str = "") -> str:
    """
    Crea un percorso completo combinando cartella, file ed estensione.
    
    Args:
        sPath: Percorso della cartella
        sFile: Nome del file
        sExt: Estensione del file
    
    Returns:
        str: Percorso completo o stringa vuota in caso di errore
    """
    sProc = "PathMake"
    
    try:
        if not sFile:
            print(f"{sProc}: Errore - Nome file obbligatorio")
            return ""
        
        if not sPath:
            sPath = os.getcwd()
        
        sPath = os.path.normpath(sPath)
        
        if not sPath.endswith(os.sep):
            sPath += os.sep
        
        if sExt:
            if not sExt.startswith('.'):
                sExt = '.' + sExt
            sFile += sExt
        
        full_path = os.path.join(sPath, sFile)
        
        return full_path
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return ""


