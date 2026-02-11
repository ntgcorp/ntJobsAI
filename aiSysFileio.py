#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aiSysFileio.py - Funzioni per l'I/O dei file
"""

import os
import sys
import csv
import configparser
from typing import Dict, Any, Optional, Union, List, Tuple

# Import delle funzioni base e stringhe
from aiSysBase import ErrorProc
from aiSysStrings import StringWash, StringAppend

# Crea alias locali
loc_ErrorProc = ErrorProc

def read_csv_to_dict(csv_file_path: str, asHeader: List[str] = None, 
                    delimiter: str = ';') -> Tuple[str, Dict]:
    """
    Legge un file CSV e lo converte in un dizionario di dizionari.
    
    Args:
        csv_file_path: Percorso completo del file CSV
        asHeader: Array di nomi dei campi (facoltativo)
        delimiter: Carattere delimitatore (default=';')
    
    Returns:
        Tuple[str, Dict]: (sResult, dictCSV)
    """
    sProc = "read_csv_to_dict"
    sResult = ""
    dictCSV = {}
    
    try:
        # Verifica che il file esista
        if not os.path.exists(csv_file_path):
            sResult = f"File non valido {csv_file_path}"
            print(sResult)
            return (sResult, {})
        
        # Legge il file CSV con codifica UTF-8
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=delimiter)
            
            # Legge l'header
            file_header = next(reader, None)
            if not file_header:
                sResult = f"File vuoto {csv_file_path}"
                print(sResult)
                return (sResult, {})
            
            # Verifica header se specificato
            if asHeader:
                if len(file_header) != len(asHeader):
                    sResult = f"Numero campi header non corrispondente. File: {len(file_header)}, Richiesti: {len(asHeader)}"
                    print(sResult)
                    return (sResult, {})
                
                for i, expected in enumerate(asHeader):
                    if file_header[i].strip() != expected:
                        sResult = f"Campo header non corrispondente in posizione {i}: '{file_header[i]}' != '{expected}'"
                        print(sResult)
                        return (sResult, {})
            
            nFieldsHeader = len(file_header)
            nRow = 1  # Contatore righe (inizia da 1 per l'header)
            
            # Legge le righe
            for row in reader:
                nRow += 1
                nFieldsRead = len(row)
                
                # Verifica numero campi
                if nFieldsRead != nFieldsHeader:
                    sResult = f"Numero campi non corretto, record: {nRow}, Letti: {nFieldsRead}, Previsti: {nFieldsHeader}, File: {csv_file_path}"
                    print(sResult)
                    return (sResult, {})
                
                # Prima colonna come chiave
                key = row[0].strip()
                
                # Verifica chiave
                if not key:
                    sResult = f"Errore chiavi nulle alla riga {nRow}"
                    print(sResult)
                    return (sResult, {})
                
                if key in dictCSV:
                    sResult = f"Errore chiave duplicata '{key}' alla riga {nRow}"
                    print(sResult)
                    return (sResult, {})
                
                # Crea dizionario interno
                inner_dict = {}
                for i in range(len(file_header)):
                    field_name = file_header[i].strip()
                    field_value = row[i].strip()
                    inner_dict[field_name] = field_value
                
                dictCSV[key] = inner_dict
        
        sResult = f"File letto correttamente: {csv_file_path}, righe: {nRow-1}"
        return (sResult, dictCSV)
        
    except FileNotFoundError:
        sResult = f"Errore apertura file CSV: {csv_file_path}"
        print(sResult)
        return (sResult, {})
    except Exception as e:
        sResult = f"Errore lettura file {csv_file_path}: {str(e)}"
        print(sResult)
        return (sResult, {})

def save_dict_to_csv(csv_file_name: str, asHeader: List[str], 
                    dictData: Dict, sMode: str, sDelimiter: str = ';') -> str:
    """
    Scrive un dizionario in un file CSV.
    
    Args:
        csv_file_name: Percorso completo del file CSV
        asHeader: Array di nomi dei campi
        dictData: Dizionario dei dati da scrivere
        sMode: "a" per append, "w" per write
        sDelimiter: Carattere delimitatore (default=';')
    
    Returns:
        str: Risultato dell'operazione
    """
    sProc = "save_dict_to_csv"
    sResult = ""
    
    try:
        # Validazioni
        if not csv_file_name:
            sResult = "Nome file non valido"
            print(sResult)
            return loc_ErrorProc(sResult, sProc)
        
        if not asHeader:
            sResult = "Header vuoto"
            print(sResult)
            return loc_ErrorProc(sResult, sProc)
        
        if not dictData:
            sResult = "Dati vuoti"
            print(sResult)
            return loc_ErrorProc(sResult, sProc)
        
        if sMode not in ['a', 'w']:
            sResult = f"Modalita' {sMode} non valida"
            print(sResult)
            return loc_ErrorProc(sResult, sProc)
        
        file_exists = os.path.exists(csv_file_name)
        
        # Gestione file esistente/non esistente
        if not file_exists:
            try:
                os.makedirs(os.path.dirname(csv_file_name), exist_ok=True)
                with open(csv_file_name, 'w', encoding='utf-8', newline='') as hFile:
                    header_line = sDelimiter.join(asHeader)
                    hFile.write(header_line + '\n')
            except Exception as e:
                sResult = f"Errore creazione file: {e}"
                print(sResult)
                return loc_ErrorProc(sResult, sProc)
        
        # Determina modalità apertura
        write_header = False
        if sMode == 'w':
            mode = 'w'
            write_header = True  # Sempre in modalità write
        else:  # sMode == 'a'
            mode = 'a'
            write_header = not file_exists  # Header solo se file nuovo
        
        # Apri file e scrivi dati
        with open(csv_file_name, mode, encoding='utf-8', newline='') as hFile:
            # Scrivi header se necessario
            if write_header:
                header_line = sDelimiter.join(asHeader)
                hFile.write(header_line + '\n')
            
            # Processa ogni record
            for sKeyRecord, dictRecord in dictData.items():
                # Verifica che sia un dizionario
                if not isinstance(dictRecord, dict):
                    continue
                
                sLinea = ""
                
                # Per ogni campo nell'header (in ordine)
                for sKeyField in asHeader:
                    # Gestione campo mancante
                    if sKeyField not in dictRecord:
                        sValue = ""
                    else:
                        # Ottieni e converti valore
                        raw_value = dictRecord[sKeyField]
                        sValue = str(raw_value)
                        
                        # Applica StringWash (pulisce)
                        sValue = StringWash(sValue)
                        
                        # Proteggi se contiene spazi
                        if ' ' in sValue:
                            sValue = f'"{sValue}"'
                    
                    # Aggiungi a sLinea
                    sLinea = StringAppend(sLinea, sValue, sDelimiter)
                
                # Accoda la riga completata al file
                hFile.write(sLinea + '\n')
        
        sResult = f"File salvato correttamente: {csv_file_name}"
        return loc_ErrorProc(sResult, sProc)
        
    except Exception as e:
        sResult = f"Errore in save_dict_to_csv: {str(e)}"
        print(sResult)
        return loc_ErrorProc(sResult, sProc)

def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict]:
    """
    Legge un file INI e lo converte in un dizionario di dizionari.
    
    Args:
        ini_file_path: Percorso completo del file INI
    
    Returns:
        Tuple[str, Dict]: (sResult, dictINI)
    """
    sProc = "read_ini_to_dict"
    sResult = ""
    dictINI = {}
    
    try:
        # Verifica che il file esista
        if not os.path.exists(ini_file_path):
            sResult = f"File non esistente: {ini_file_path}"
            print(sResult)
            return (sResult, {})
        
        # Configura configparser
        config = configparser.ConfigParser(
            interpolation=None,  # disattiva %
            comment_prefixes=(';',),  # solo ; come commento
            inline_comment_prefixes=()  # disattiva commenti inline
        )
        config.optionxform = str  # mantiene case originale
        
        # Legge il file
        config.read(ini_file_path, encoding='utf-8')
        
        # Converte in dizionario
        for section in config.sections():
            dictINI[section] = {}
            for key in config[section]:
                dictINI[section][key] = config[section][key]
        
        sResult = f"Letto file .ini {ini_file_path}, Numero Sezioni: {len(dictINI)}"
        print(sResult)
        return (sResult, dictINI)
        
    except FileNotFoundError:
        sResult = f"Errore apertura file INI: {ini_file_path}"
        print(sResult)
        return (sResult, {})
    except Exception as e:
        sResult = f"Errore lettura file INI {ini_file_path}: {str(e)}"
        print(sResult)
        return (sResult, {})

def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], 
                    ini_file_path: str) -> str:
    """
    Salva un dizionario di dizionari in un file INI.
    
    Args:
        data_dict: Dizionario da salvare
        ini_file_path: Percorso del file INI
    
    Returns:
        str: Risultato dell'operazione
    """
    sProc = "save_dict_to_ini"
    sResult = ""
    
    try:
        # Configura configparser
        config = configparser.ConfigParser()
        config.optionxform = str  # mantiene case originale
        
        # Aggiunge sezioni e chiavi
        for section, section_dict in data_dict.items():
            config[section] = {}
            for key, value in section_dict.items():
                config[section][key] = str(value)
        
        # Crea directory se necessario
        os.makedirs(os.path.dirname(ini_file_path), exist_ok=True)
        
        # Salva il file
        with open(ini_file_path, 'w', encoding='utf-8') as f:
            config.write(f)
        
        sResult = f"File INI salvato: {ini_file_path}"
        return sResult
        
    except Exception as e:
        sResult = loc_ErrorProc(f"Errore - {str(e)}", sProc)
        print(sResult)
        return sResult

def save_array_file(sFile: str, asLines: List[str], sMode: str = "") -> str:
    """
    Salva un array di stringhe in un file.
    
    Args:
        sFile: Nome del file
        asLines: Array di stringhe
        sMode: "a" per append, altrimenti sovrascrive
    
    Returns:
        str: Risultato dell'operazione
    """
    sProc = "save_array_file"
    sResult = ""
    
    try:
        # Determina modalità
        mode = 'a' if sMode == "a" else 'w'
        
        # Crea directory se necessario
        os.makedirs(os.path.dirname(sFile), exist_ok=True)
        
        # Salva il file
        with open(sFile, mode, encoding='utf-8') as f:
            for line in asLines:
                f.write(line + '\n')
        
        sResult = f"Array salvato in {sFile}"
        return loc_ErrorProc(sResult, sProc)
        
    except Exception as e:
        sResult = f"Errore salvataggio array in {sFile}, Errore: {str(e)}"
        print(sResult)
        return loc_ErrorProc(sResult, sProc)

def read_array_file(sFile: str) -> Tuple[str, List[str]]:
    """
    Legge un file di testo e lo converte in un array di stringhe.
    
    Args:
        sFile: Nome del file
    
    Returns:
        Tuple[str, List[str]]: (sResult, asLines)
    """
    sProc = "read_array_file"
    sResult = ""
    asLines = []
    
    try:
        if not os.path.exists(sFile):
            sResult = f"File non esistente: {sFile}"
            print(sResult)
            return (sResult, [])
        
        with open(sFile, 'r', encoding='utf-8') as f:
            asLines = [line.rstrip('\n') for line in f]
        
        sResult = f"File letto: {sFile}, righe: {len(asLines)}"
        return (sResult, asLines)
        
    except Exception as e:
        sResult = f"Errore lettura array di stringhe in {sFile}, Errore: {str(e)}"
        print(sResult)
        return (sResult, [])

def isValidPath(sPath: str) -> bool:
    """
    Verifica se un percorso è valido ed esiste.
    
    Args:
        sPath: Percorso da verificare
    
    Returns:
        bool: True se valido ed esiste, False altrimenti
    """
    sProc = "isValidPath"
    try:
        return os.path.exists(sPath)
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

def isFilename(sFilename: str) -> bool:
    """
    Verifica che un nome di file sia corretto.
    
    Args:
        sFilename: Nome del file da verificare
    
    Returns:
        bool: True se corretto, False altrimenti
    """
    sProc = "isFilename"
    try:
        if not sFilename:
            return False
        
        # Controlla caratteri nel nome file (prima del punto)
        name_parts = sFilename.split('.')
        if len(name_parts) < 2:
            # Senza estensione
            base_name = sFilename
            pattern = r'^[a-zA-Z0-9_]+$'
            return bool(re.match(pattern, base_name))
        else:
            # Con estensione
            base_name = '.'.join(name_parts[:-1])
            ext = name_parts[-1]
            
            # Verifica nome base
            base_pattern = r'^[a-zA-Z0-9_]+$'
            if not re.match(base_pattern, base_name):
                return False
            
            # Verifica estensione
            ext_pattern = r'^[a-zA-Z0-9_.]+$'
            return bool(re.match(ext_pattern, ext))
            
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return False

def PathMake(sPath: Optional[str] = None, sFile: str = "", 
            sExt: Optional[str] = None) -> str:
    """
    Crea un percorso completo combinando cartella, file ed estensione.
    
    Args:
        sPath: Percorso della cartella (se None, usa cartella corrente)
        sFile: Nome del file (obbligatorio)
        sExt: Estensione del file (opzionale)
    
    Returns:
        str: Percorso completo, stringa vuota in caso di errore
    """
    sProc = "PathMake"
    try:
        # Verifica parametri obbligatori
        if not sFile:
            return ""
        
        # Gestisci sPath
        if not sPath:
            sPath = os.getcwd()  # cartella corrente
        
        # Normalizza il percorso
        sPath = os.path.normpath(sPath)
        
        # Assicurati che sPath finisca con il separatore corretto
        if not sPath.endswith(os.sep):
            sPath += os.sep
        
        # Gestisci sExt
        sFullFile = sFile
        if sExt:
            # Rimuovi eventuale punto iniziale se già presente
            if sExt.startswith('.'):
                sExt = sExt[1:]
            sFullFile = f"{sFile}.{sExt}"
        
        # Combina percorso e file
        sFullPath = os.path.join(sPath, sFullFile)
        
        # Normalizza di nuovo per sicurezza
        sFullPath = os.path.normpath(sFullPath)
        
        # Verifica che il percorso sia valido (non assoluto per drive Windows)
        if sys.platform == "win32":
            # Su Windows, verifica che non ci siano caratteri non validi
            if ':' in sFullPath.replace(':\\', ''):
                return ""
        
        return sFullPath
        
    except Exception as e:
        print(f"{sProc}: Errore - {str(e)}")
        return ""

# Test locale se eseguito direttamente
if __name__ == "__main__":
    # Test save_dict_to_csv
    test_data = {
        'user1': {'id': '1', 'nome': 'Mario Rossi', 'età': '30'},
        'user2': {'id': '2', 'nome': 'Luigi Verdi', 'età': '25'}
    }
    header = ['id', 'nome', 'età']
    
    print("Test save_dict_to_csv:")
    result = save_dict_to_csv('test.csv', header, test_data, 'w', ';')
    print(f"Risultato: {result}")
    
    print("\nTest read_csv_to_dict:")
    result, data = read_csv_to_dict('test.csv', header, ';')
    print(f"Risultato: {result}")
    print(f"Dati letti: {data}")
    
    # Pulisci
    if os.path.exists('test.csv'):
        os.remove('test.csv')