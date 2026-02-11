#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aiSys.py - Libreria principale di funzioni di supporto
Importa tutti i moduli e li espone nel namespace aiSys
"""

import os
import sys

# Importa TUTTE le funzioni da tutti i moduli
# =============================================================================
# Da aiSysTimestamp.py
# =============================================================================
try:
    from aiSysTimestamp import (
        Timestamp,
        TimestampConvert,
        TimestampFromSeconds,
        TimestampFromDays,
        TimestampValidate,
        TimestampDiff,
        TimestampAdd,
        TimestampIsoFrom,
        TimestampIsoTo
    )
except ImportError as e:
    print(f"Errore import aiSysTimestamp: {e}")
    sys.exit(1)

# =============================================================================
# Da aiSysConfig.py (se esiste)
# =============================================================================
try:
    from aiSysConfig import (
        Expand,
        ExpandConvert,
        ExpandDict,
        isGroups,
        Config,
        ConfigDefault,
        SplitSettings,
        ConfigSet
    )
except ImportError:
    # Inizializza funzioni placeholder se il modulo non esiste ancora
    def Expand(sText, dictConfig):
        return sText
    
    def ExpandConvert(sString):
        return sString
    
    def ExpandDict(dictExpand, dictParam):
        return dictExpand
    
    def isGroups(asGroups1, asGroups2):
        return False
    
    def Config(dictConfig, sKey):
        return ""
    
    def ConfigDefault(sKey, xValue, dictConfig):
        return dictConfig
    
    def SplitSettings(sString, dictConfig=None):
        return {}
    
    def ConfigSet(dictConfig, sKey, xValue=""):
        return dictConfig

# =============================================================================
# Da aiSysFileio.py
# =============================================================================
try:
    from aiSysFileio import (
        read_csv_to_dict,
        save_dict_to_csv,
        read_ini_to_dict,
        save_dict_to_ini,
        save_array_file,
        read_array_file,
        isValidPath,
        isFilename,
        PathMake
    )
except ImportError as e:
    print(f"Errore import aiSysFileio: {e}")
    sys.exit(1)

# =============================================================================
# Da aiSysStrings.py
# =============================================================================
try:
    from aiSysStrings import (
        StringAppend,
        StringBool,
        isValidPassword,
        isLettersOnly,
        isEmail,
        StringToArray,
        StringToNum,
        StringWash
    )
except ImportError as e:
    print(f"Errore import aiSysStrings: {e}")
    sys.exit(1)

# =============================================================================
# Da aiSysDictToString.py (se esiste)
# =============================================================================
try:
    from aiSysDictToString import (
        DictPrint,
        DictToXml,
        DictToString
    )
except ImportError:
    # Placeholder functions
    def DictPrint(dictParam, sFile=None):
        print(dictParam)
        return ""
    
    def DictToXml(dictParam, **xml_options):
        return ""
    
    def DictToString(dictParam, sFormat="json"):
        return ("", "")

# =============================================================================
# Da aiSysBase.py
# =============================================================================
try:
    from aiSysBase import (
        ErrorProc,
        DictMerge,
        DictExist
    )
except ImportError as e:
    print(f"Errore import aiSysBase: {e}")
    sys.exit(1)

# =============================================================================
# Da aiSysLog.py (se esiste)
# =============================================================================
try:
    from aiSysLog import acLog
except ImportError:
    # Classe placeholder
    class acLog:
        def __init__(self):
            self.sLog = ""
        
        def Start(self, sLogfile=None, sLogFolder=None):
            return ""
        
        def Log(self, sType: str, sValue: str = ""):
            print(f"{sType}: {sValue}")
        
        def Log0(self, sResult, sValue=""):
            if sResult:
                self.Log("ERR", f"{sResult}: {sValue}")
            else:
                self.Log("INFO", sValue)
        
        def Log1(self, sValue=""):
            self.Log("INFO", sValue)

# =============================================================================
# Crea alias locale per ErrorProc in ogni modulo (per compatibilità)
# =============================================================================
loc_ErrorProc = ErrorProc

# =============================================================================
# ELENCO COMPLETO DI TUTTE LE FUNZIONI ESPOSTE NEL NAMESPACE aiSys
# =============================================================================

# Da aiSysTimestamp
__all__ = [
    'Timestamp',
    'TimestampConvert',
    'TimestampFromSeconds',
    'TimestampFromDays',
    'TimestampValidate',
    'TimestampDiff',
    'TimestampAdd',
    'TimestampIsoFrom',
    'TimestampIsoTo',
]

# Da aiSysConfig
__all__.extend([
    'Expand',
    'ExpandConvert',
    'ExpandDict',
    'isGroups',
    'Config',
    'ConfigDefault',
    'SplitSettings',
    'ConfigSet',
])

# Da aiSysFileio
__all__.extend([
    'read_csv_to_dict',
    'save_dict_to_csv',
    'read_ini_to_dict',
    'save_dict_to_ini',
    'save_array_file',
    'read_array_file',
    'isValidPath',
    'isFilename',
    'PathMake',
])

# Da aiSysStrings
__all__.extend([
    'StringAppend',
    'StringBool',
    'isValidPassword',
    'isLettersOnly',
    'isEmail',
    'StringToArray',
    'StringToNum',
    'StringWash',
])

# Da aiSysDictToString
__all__.extend([
    'DictPrint',
    'DictToXml',
    'DictToString',
])

# Da aiSysBase
__all__.extend([
    'ErrorProc',
    'DictMerge',
    'DictExist',
    'loc_ErrorProc',  # Alias locale
])

# Da aiSysLog
__all__.extend([
    'acLog',
])

# =============================================================================
# FUNZIONE PRINCIPALE
# =============================================================================

def __main__():
    """
    Funzione principale di aiSys.py.
    Non contiene test, solo logica di inizializzazione se necessaria.
    """
    print("=" * 60)
    print("aiSys.py - Libreria di funzioni di supporto")
    print("=" * 60)
    print(f"Version: {sys.version}")
    print(f"Moduli esportati: {len(__all__)} funzioni/classi")
    print("\nFunzioni disponibili nel namespace 'aiSys':")
    for i, func in enumerate(sorted(__all__), 1):
        print(f"{i:3}. {func}")
    print("=" * 60)

# Se eseguito direttamente
if __name__ == "__main__":
    __main__()