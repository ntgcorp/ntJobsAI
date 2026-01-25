"""
aiSysFileio.py - Funzioni per l'input/output di file
Contiene funzioni per leggere/scrivere CSV, INI, array di stringhe e gestire percorsi
"""

from typing import Dict, List, Tuple, Optional, Any
import os
import csv
import configparser


def read_csv_to_dict(csv_file_path: str, asHeader: Optional[List[str]] = None, 
                    delimiter: str = ';') -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file CSV e lo converte in un dizionario di dizionari.
    
    Args:
        csv_file_path: Percorso completo del file CSV
        asHeader: Array di nomi di campi per validazione (opzionale)
        delimiter: Carattere delimitatore (default: ';')
        
    Returns:
        Tuple[str, Dict]: (sResult, dictCSV) dove:
            sResult: Stringa vuota in caso di successo, messaggio di errore altrimenti
            dictCSV: Dizionario con chiave=prima colonna, valore=dizionario della riga
            
    Example:
        >>> result, data = read_csv_to_dict("data.csv")
        >>> if result == "": print(f"Letti {len(data)} record")
    """
    sProc = "read_csv_to_dict"
    sResult = ""
    dictCSV = {}
    
    try:
        # Verifica che il file esista
        if not os.path.exists(csv_file_path):
            sResult = f"File non valido {csv_file_path}"
            return sResult, {}
        
        # Verifica che non sia una directory
        if os.path.isdir(csv_file_path):
            sResult = f"Percorso è una directory: {csv_file_path}"
            return sResult, {}
        
        # Apri il file CSV
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Leggi il file CSV
            csv_reader = csv.reader(csvfile, delimiter=delimiter)
            
            # Leggi l'header (prima riga)
            try:
                header = next(csv_reader)
            except StopIteration:
                sResult = f"File vuoto o non Valido {csv_file_path}"
                return sResult, {}
            
            # Valida header se asHeader è fornito e non vuoto
            if asHeader and len(asHeader) > 0:
                # Verifica che l'header contenga esattamente i campi specificati
                if len(header) != len(asHeader):
                    sResult = f"Numero campi header non corretto, Letti: {len(header)}, Previsti: {len(asHeader)}, File: {csv_file_path}"
                    return sResult, {}
                
                # Verifica che i nomi dei campi corrispondano
                for i, (hdr, expected) in enumerate(zip(header, asHeader)):
                    if hdr.strip() != expected.strip():
                        sResult = f"Campo header {i+1} non corrisponde: '{hdr}' != '{expected}', File: {csv_file_path}"
                        return sResult, {}
            
            nFieldsHeader = len(header)
            seen_keys = set()  # Per rilevare chiavi duplicate
            line_num = 1  # Contatore di righe (header è riga 1)
            
            # Leggi le righe di dati
            for row in csv_reader:
                line_num += 1
                nFieldsRead = len(row)
                
                # Verifica numero di campi
                if nFieldsRead != nFieldsHeader:
                    sResult = f"Numero campi non corretto, record: {line_num}, Letti: {nFieldsRead}, Previsti: {nFieldsHeader}, File: {csv_file_path}"
                    return sResult, {}
                
                # La prima colonna è la chiave
                key = row[0].strip()
                
                # Verifica chiave non vuota
                if not key:
                    sResult = f"Errore chiavi nulle alla riga {line_num}, File: {csv_file_path}"
                    return sResult, {}
                
                # Verifica chiave duplicata
                if key in seen_keys:
                    sResult = f"Errore chiave duplicata '{key}' alla riga {line_num}, File: {csv_file_path}"
                    return sResult, {}
                
                seen_keys.add(key)
                
                # Crea dizionario per la riga
                row_dict = {}
                for i in range(nFieldsHeader):
                    field_name = header[i].strip()
                    field_value = row[i].strip() if i < len(row) else ""
                    row_dict[field_name] = field_value
                
                # Aggiungi al dizionario principale
                dictCSV[key] = row_dict
        
        # Successo
        return "", dictCSV
        
    except FileNotFoundError:
        sResult = f"Errore apertura file CSV: {csv_file_path}"
        return sResult, {}
    except csv.Error as e:
        sResult = f"Errore lettura file CSV {csv_file_path}: {e}"
        return sResult, {}
    except Exception as e:
        sResult = f"Errore generico: {e}"
        return sResult, {}


def read_ini_to_dict(ini_file_path: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
    """
    Legge un file INI e lo converte in un dizionario di dizionari.
    
    Args:
        ini_file_path: Percorso completo del file INI
        
    Returns:
        Tuple[str, Dict]: (sResult, dictINI) dove:
            sResult: Stringa vuota in caso di successo, messaggio di errore altrimenti
            dictINI: Dizionario con chiave=sezione, valore=dizionario chiave-valore
            
    Example:
        >>> result, data = read_ini_to_dict("config.ini")
        >>> if result == "": print(f"Lette {len(data)} sezioni")
    """
    sProc = "read_ini_to_dict"
    sResult = ""
    dictINI = {}
    
    try:
        # Verifica che il file esista
        if not os.path.exists(ini_file_path):
            sResult = f"File non esistente: {ini_file_path}"
            return sResult, {}
        
        # Verifica che non sia una directory
        if os.path.isdir(ini_file_path):
            sResult = f"Percorso è una directory: {ini_file_path}"
            return sResult, {}
        
        # Configura configparser
        config = configparser.ConfigParser(
            interpolation=None,  # disattiva %
            comment_prefixes=(';',),  # solo ; come commento
            inline_comment_prefixes=()  # disattiva commenti inline
        )
        config.optionxform = str  # mantiene case originale
        
        # Leggi il file
        config.read(ini_file_path, encoding='utf-8')
        
        # Converti in dizionario
        for section in config.sections():
            dictINI[section] = {}
            for key, value in config.items(section):
                dictINI[section][key] = value
        
        # Successo
        print(f"Letto file .ini {ini_file_path}, Numero Sezioni: {len(dictINI)}")
        return "", dictINI
        
    except configparser.Error as e:
        sResult = f"Errore lettura file INI {ini_file_path}: {e}"
        return sResult, {}
    except FileNotFoundError:
        sResult = f"Errore apertura file INI: {ini_file_path}"
        return sResult, {}
    except Exception as e:
        sResult = f"Errore generico: {e}"
        return sResult, {}


def save_dict_to_ini(data_dict: Dict[str, Dict[str, str]], ini_file_path: str) -> str:
    """
    Salva un dizionario di dizionari in un file INI.
    
    Args:
        data_dict: Dizionario da salvare
        ini_file_path: Percorso del file INI da creare/sovrascrivere
        
    Returns:
        str: Stringa vuota in caso di successo, messaggio di errore altrimenti
        
    Example:
        >>> data = {"sezione1": {"chiave1": "valore1"}}
        >>> result = save_dict_to_ini(data, "output.ini")
        >>> if result == "": print("Salvataggio riuscito")
    """
    sProc = "save_dict_to_ini"
    
    try:
        # Verifica che data_dict sia valido
        if not data_dict or not isinstance(data_dict, dict):
            return f"{sProc}: Errore - Dizionario non valido"
        
        # Configura configparser
        config = configparser.ConfigParser()
        config.optionxform = str  # mantiene case originale
        
        # Aggiungi sezioni e chiavi
        for section, section_dict in data_dict.items():
            if not isinstance(section_dict, dict):
                continue
                
            config[section] = {}
            for key, value in section_dict.items():
                config[section][key] = str(value) if value is not None else ""
        
        # Crea directory se non esiste
        directory = os.path.dirname(ini_file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Salva il file
        with open(ini_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        return ""  # Successo
        
    except Exception as e:
        return f"{sProc}: Errore - {str(e)}"


def save_array_file(sFile: str, asLines: List[str], sMode: str = "") -> str:
    """
    Salva un array di stringhe in un file.
    
    Args:
        sFile: Percorso del file
        asLines: Array di stringhe da salvare
        sMode: "a" per append, altrimenti sovrascrive
        
    Returns:
        str: Stringa vuota in caso di successo, messaggio di errore altrimenti
        
    Example:
        >>> save_array_file("log.txt", ["linea1", "linea2"], "a")
        ''
    """
    sProc = "save_array_file"
    
    try:
        # Verifica input
        if not sFile:
            return f"{sProc}: Errore - Nome file non valido"
        
        if asLines is None:
            asLines = []
        
        # Determina la modalità di apertura
        mode = 'a' if sMode == "a" else 'w'
        
        # Crea directory se non esiste
        directory = os.path.dirname(sFile)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Salva il file
        with open(sFile, mode, encoding='utf-8') as f:
            for line in asLines:
                f.write(str(line) + '\n')
        
        return ""  # Successo
        
    except Exception as e:
        return f"{sProc}: Errore salvataggio array in {sFile}, Errore: {e}"


def read_array_file(sFile: str) -> Tuple[str, List[str]]:
    """
    Legge un file di testo e lo converte in un array di stringhe.
    
    Args:
        sFile: Percorso del file da leggere
        
    Returns:
        Tuple[str, List[str]]: (sResult, asLines) dove:
            sResult: Stringa vuota in caso di successo, messaggio di errore altrimenti
            asLines: Array di stringhe lette dal file
            
    Example:
        >>> result, lines = read_array_file("log.txt")
        >>> if result == "": print(f"Lette {len(lines)} righe")
    """
    sProc = "read_array_file"
    asLines = []
    
    try:
        # Verifica che il file esista
        if not os.path.exists(sFile):
            sResult = f"Errore lettura array di stringhe in {sFile}, Errore: File non trovato"
            return sResult, []
        
        # Verifica che non sia una directory
        if os.path.isdir(sFile):
            sResult = f"Errore lettura array di stringhe in {sFile}, Errore: Percorso è una directory"
            return sResult, []
        
        # Leggi il file
        with open(sFile, 'r', encoding='utf-8') as f:
            for line in f:
                # Rimuovi il newline finale ma mantieni altri whitespace
                cleaned_line = line.rstrip('\n\r')
                asLines.append(cleaned_line)
        
        return "", asLines
        
    except Exception as e:
        sResult = f"Errore lettura array di stringhe in {sFile}, Errore: {e}"
        return sResult, []


def isValidPath(sPath: str) -> bool:
    """
    Verifica se un percorso è valido ed esiste.
    
    Args:
        sPath: Percorso da verificare
        
    Returns:
        bool: True se il percorso esiste, False altrimenti
        
    Example:
        >>> isValidPath("/home/user")
        True
        >>> isValidPath("/percorso/inesistente")
        False
    """
    sProc = "isValidPath"
    
    try:
        if not sPath:
            return False
        
        return os.path.exists(sPath)
        
    except Exception:
        return False


def PathMake(sPath: Optional[str], sFile: str, sExt: Optional[str] = None) -> str:
    """
    Crea un percorso completo combinando cartella, file ed estensione.
    
    Args:
        sPath: Percorso della cartella (None/"" per cartella corrente)
        sFile: Nome del file (obbligatorio)
        sExt: Estensione del file (opzionale, aggiunge '.' se fornita)
        
    Returns:
        str: Percorso completo formattato, stringa vuota in caso di errore
        
    Example:
        >>> PathMake("/home/user", "documento", "txt")
        '/home/user/documento.txt'
        >>> PathMake("", "config", "ini")
        './config.ini'
    """
    sProc = "PathMake"
    
    try:
        # Verifica input obbligatorio
        if not sFile:
            print(f"{sProc}: Errore - Nome file non specificato")
            return ""
        
        # Gestisci percorso
        if not sPath:
            sPath = os.getcwd()  # Cartella corrente
        
        # Normalizza il percorso
        sPath = os.path.normpath(sPath)
        
        # Assicurati che il percorso finisca con il separatore corretto
        if not sPath.endswith(os.sep):
            sPath += os.sep
        
        # Costruisci il nome file completo
        full_file = sFile
        
        # Aggiungi estensione se fornita
        if sExt:
            # Rimuovi eventuale punto iniziale e aggiungilo
            sExt = sExt.lstrip('.')
            if sExt:
                full_file = f"{full_file}.{sExt}"
        
        # Combina percorso e file
        full_path = os.path.join(sPath, full_file)
        
        # Normalizza il percorso finale (rimuove doppi separatori, etc.)
        full_path = os.path.normpath(full_path)
        
        return full_path
        
    except Exception as e:
        print(f"{sProc}: Errore - {e}")
        return ""


# Test delle funzioni se eseguito direttamente
if __name__ == "__main__":
    print("Test aiSysFileio.py")
    print("=" * 50)
    
    import tempfile
    import shutil
    
    # Crea directory temporanea per i test
    temp_dir = tempfile.mkdtemp()
    print(f"Directory temporanea: {temp_dir}")
    
    try:
        # Test isValidPath
        print("\n1. Test isValidPath:")
        print(f"   isValidPath('{temp_dir}') = {isValidPath(temp_dir)}")
        print(f"   isValidPath('/percorso/inesistente/12345') = {isValidPath('/percorso/inesistente/12345')}")
        
        # Test PathMake
        print("\n2. Test PathMake:")
        path1 = PathMake(temp_dir, "test", "txt")
        path2 = PathMake("", "config", "ini")
        path3 = PathMake(temp_dir, "nofile", "")
        print(f"   PathMake('{temp_dir}', 'test', 'txt') = '{path1}'")
        print(f"   PathMake('', 'config', 'ini') = '{path2}'")
        print(f"   PathMake('{temp_dir}', 'nofile', '') = '{path3}'")
        
        # Test save_array_file e read_array_file
        print("\n3. Test save_array_file e read_array_file:")
        test_file = os.path.join(temp_dir, "test_array.txt")
        test_lines = ["Linea 1", "Linea 2", "Linea 3"]
        
        # Salva
        result = save_array_file(test_file, test_lines)
        print(f"   save_array_file -> risultato: '{result}'")
        
        # Leggi
        result, lines = read_array_file(test_file)
        print(f"   read_array_file -> risultato: '{result}', righe: {len(lines)}")
        if result == "":
            print(f"   Contenuto letto: {lines}")
        
        # Test append
        result = save_array_file(test_file, ["Linea 4"], "a")
        result, lines = read_array_file(test_file)
        print(f"   Dopo append -> righe: {len(lines)}")
        
        # Test save_dict_to_ini e read_ini_to_dict
        print("\n4. Test save_dict_to_ini e read_ini_to_dict:")
        ini_file = os.path.join(temp_dir, "test.ini")
        test_ini_data = {
            "sezione1": {
                "chiave1": "valore1",
                "chiave2": "valore2"
            },
            "sezione2": {
                "nome": "test",
                "abilitato": "true"
            }
        }
        
        # Salva INI
        result = save_dict_to_ini(test_ini_data, ini_file)
        print(f"   save_dict_to_ini -> risultato: '{result}'")
        
        # Leggi INI
        result, ini_data = read_ini_to_dict(ini_file)
        print(f"   read_ini_to_dict -> risultato: '{result}'")
        if result == "":
            print(f"   Dati letti: {ini_data}")
        
        # Test read_csv_to_dict
        print("\n5. Test read_csv_to_dict:")
        csv_file = os.path.join(temp_dir, "test.csv")
        
        # Crea file CSV di test
        csv_content = """ID;Nome;Età;Città
1;Mario Rossi;30;Roma
2;Luigi Verdi;25;Milano
3;Anna Bianchi;35;Napoli"""
        
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(csv_content)
        
        # Leggi senza validazione header
        result, csv_data = read_csv_to_dict(csv_file, delimiter=';')
        print(f"   read_csv_to_dict senza validazione -> risultato: '{result}', record: {len(csv_data)}")
        if result == "":
            print(f"   Primo record: {list(csv_data.items())[0]}")
        
        # Leggi con validazione header
        header = ["ID", "Nome", "Età", "Città"]
        result, csv_data = read_csv_to_dict(csv_file, asHeader=header, delimiter=';')
        print(f"   read_csv_to_dict con validazione -> risultato: '{result}'")
        
        # Test con header errato
        wrong_header = ["ID", "Nome", "Errato", "Città"]
        result, csv_data = read_csv_to_dict(csv_file, asHeader=wrong_header, delimiter=';')
        print(f"   read_csv_to_dict con header errato -> risultato: '{result}'")
        
    finally:
        # Pulisci directory temporanea
        shutil.rmtree(temp_dir)
        print(f"\nDirectory temporanea rimossa: {temp_dir}")
    
    print("\nTest completati!")