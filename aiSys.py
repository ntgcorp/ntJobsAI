"""
aiSys.py - Modulo principale che integra tutte le librerie aiSys*.py
"""

import sys
import os
from typing import Dict, Any, Optional, Union, List

# =============================================================================
# IMPORT DEI MODULI (NON FALLBACK - se mancano, errore)
# =============================================================================

try:
    # Import dei moduli di supporto
    from aiSysTimestamp import *
    from aiSysConfig import *
    from aiSysFileio import *
    from aiSysStrings import *
    from aiSysDictToString import *
    from aiSysBase import *
    from aiSysLog import *
    
except ImportError as e:
    print(f"ERRORE: Modulo mancante - {str(e)}")
    print("Tutti i moduli aiSys*.py devono essere presenti nella stessa directory.")
    sys.exit(1)


# =============================================================================
# ESPORTAZIONE DEL NAMESPACE
# =============================================================================

# Espone tutte le funzioni e classi nel namespace aiSys.*
__all__ = [
    # Funzioni di base (aiSysBase.py)
    "aiErrorProc",
    "DictMerge",
    "DictExist",
    "loc_aiErrorProc",
    
    # Funzioni timestamp (aiSysTimestamp.py)
    "Timestamp",
    "TimestampConvert",
    "TimestampFromSeconds",
    "TimestampFromDays",
    "TimestampValidate",
    "TimestampDiff",
    "TimestampAdd",
    
    # Funzioni config (aiSysConfig.py)
    "Expand",
    "ExpandDict",
    "isGroups",
    "Config",
    "ConfigDefault",
    "ConfigSet",
    
    # Funzioni file I/O (aiSysFileio.py)
    "read_csv_to_dict",
    "read_ini_to_dict",
    "save_dict_to_ini",
    "save_array_file",
    "read_array_file",
    "isValidPath",
    "isFilename",
    "PathMake",
    
    # Funzioni stringhe (aiSysStrings.py)
    "StringBool",
    "isValidPassword",
    "isLettersOnly",
    "isEmail",
    "StringToArray",
    "StringToNum",
    
    # Funzioni dizionari (aiSysDictToString.py)
    "DictPrint",
    "DictToXml",
    "DictToString",
    
    # Classe log (aiSysLog.py)
    "acLog",
]


# =============================================================================
# FUNZIONI GLOBALI DI SUPPORTO
# =============================================================================

def local_aiErrorProc(sResult: str, sProc: str) -> str:
    """
    Funzione di gestione errori per uso interno nei moduli importati.
    
    Args:
        sResult: Stringa del risultato/errore
        sProc: Nome della funzione chiamante
        
    Returns:
        str: Stringa vuota se sResult vuoto, altrimenti "sProc: Errore sResult"
    """
    sProc_local = "local_aiErrorProc"
    
    try:
        if sResult != "":
            return f"{sProc}: Errore {sResult}"
        return ""
    except Exception as e:
        return f"{sProc_local}: Errore - {str(e)}"


# =============================================================================
# FUNZIONE MAIN PER TEST
# =============================================================================
def __main__():
    """
    Funzione principale per test del modulo aiSys.
    """
    sProc = "__main__"
    
    try:
        print("=" * 60)
        print("aiSys.py - Test modulo principale")
        print("=" * 60)
        
        # Verifica che tutti i moduli siano stati importati correttamente
        print("\n1. Verifica moduli importati:")
        
        moduli = [
            ("aiSysBase", "aiErrorProc"),
            ("aiSysTimestamp", "Timestamp"),
            ("aiSysConfig", "Expand"),
            ("aiSysFileio", "read_csv_to_dict"),
            ("aiSysStrings", "StringBool"),
            ("aiSysDictToString", "DictToString"),
            ("aiSysLog", "acLog"),
        ]
        
        for modulo, funzione in moduli:
            try:
                if funzione in globals():
                    print(f"   ✓ {modulo}.{funzione} - OK")
                else:
                    print(f"   ✗ {modulo}.{funzione} - MANCANTE")
            except:
                print(f"   ✗ {modulo}.{funzione} - ERRORE")
        
        # Test funzione di base
        print("\n2. Test funzioni di base:")
        result = aiErrorProc("", "test_func")
        print(f"   aiErrorProc('', 'test_func') = '{result}'")
        
        result = aiErrorProc("test_error", "test_func")
        print(f"   aiErrorProc('test_error', 'test_func') = '{result}'")
        
        # Test timestamp
        print("\n3. Test funzioni timestamp:")
        ts = Timestamp()
        print(f"   Timestamp() = '{ts}'")
        
        valid = TimestampValidate(ts)
        print(f"   TimestampValidate('{ts}') = {valid}")
        
        # Test funzione locale
        print("\n4. Test funzione locale di errore:")
        result = local_aiErrorProc("", "test_func")
        print(f"   local_aiErrorProc('', 'test_func') = '{result}'")
        
        result = local_aiErrorProc("errore_test", "test_func")
        print(f"   local_aiErrorProc('errore_test', 'test_func') = '{result}'")
        
        print("\n" + "=" * 60)
        print("Test completato con successo!")
        print("=" * 60)
        
        return ""
        
    except Exception as e:
        return f"{sProc}: Errore durante il test - {str(e)}"


# =============================================================================
# PUNTO DI INGRESSO
# =============================================================================
if __name__ == "__main__":
    """
    Esecuzione dei test quando il file viene eseguito direttamente.
    """
    result = __main__()
    if result:
        print(f"\nERRORE: {result}")
        sys.exit(1)
    else:
        print("\nTutti i test sono stati eseguiti con successo.")
        sys.exit(0)