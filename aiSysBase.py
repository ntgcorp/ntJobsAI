"""
aiSysBase.py - Libreria di funzioni base per aiSys.py
"""

import sys
import os
from typing import Dict, Any, Optional, Union, List


# =============================================================================
# FUNZIONE: aiErrorProc
# =============================================================================
def aiErrorProc(sResult: str, sProc: str) -> str:
    """
    Ritorna sResult con prefisso sProc se sResult non è vuoto.
    
    Args:
        sResult: Stringa del risultato/errore
        sProc: Nome della funzione chiamante
        
    Returns:
        str: sResult se vuoto, altrimenti "sProc: Errore sResult"
    """
    sProc_func = "aiErrorProc"
    
    try:
        if sResult != "":
            return f"{sProc}: Errore {sResult}"
        else:
            return sResult
    except Exception as e:
        return f"{sProc_func}: Errore - {str(e)}"


# =============================================================================
# FUNZIONE: DictMerge
# =============================================================================
def DictMerge(dictSource: Optional[Dict], dictAdd: Optional[Dict]) -> Optional[Dict]:
    """
    Unisce dictAdd in dictSource con priorità a dictAdd.
    
    Args:
        dictSource: Dizionario destinazione (può essere None o vuoto)
        dictAdd: Dizionario da aggiungere (può essere None o vuoto)
        
    Returns:
        Dict: Dizionario risultante, o None in caso di errore
    """
    sProc = "DictMerge"
    
    try:
        # Se dictSource non esiste o è vuoto, ma dictAdd esiste
        if (dictSource is None or dictSource == {}) and dictAdd:
            return dictAdd.copy()
        
        # Se dictAdd è None o vuoto, non fare nulla
        if dictAdd is None or dictAdd == {}:
            return dictSource
        
        # Assicurati che dictSource sia un dizionario
        if not isinstance(dictSource, dict):
            return None
        
        # Assicurati che dictAdd sia un dizionario
        if not isinstance(dictAdd, dict):
            return None
        
        # Unisci i dizionari (dictAdd ha priorità)
        result = dictSource.copy()
        for key, value in dictAdd.items():
            result[key] = value
            
        return result
        
    except Exception as e:
        return None


# =============================================================================
# FUNZIONE: DictExist
# =============================================================================
def DictExist(dictParam: Any, sKey: str, xDefault: Any = None) -> Any:
    """
    Ritorna il valore di una chiave o un valore di default.
    
    Args:
        dictParam: Dizionario da esaminare
        sKey: Chiave da cercare
        xDefault: Valore di default se la chiave non esiste
        
    Returns:
        Any: Valore della chiave o xDefault
    """
    sProc = "DictExist"
    
    try:
        xResult = None
        
        # Se dictParam non è un dizionario
        if not isinstance(dictParam, dict):
            return xResult
        
        # Se la chiave non esiste
        if sKey not in dictParam:
            xResult = xDefault
        else:
            xResult = dictParam[sKey]
            
        return xResult
        
    except Exception as e:
        return None


# =============================================================================
# FUNZIONE: loc_aiErrorProc (per uso interno nei moduli)
# =============================================================================
def loc_aiErrorProc(sResult: str, sProc: str) -> str:
    """
    Versione locale di aiErrorProc per uso nei moduli.
    
    Args:
        sResult: Stringa del risultato/errore
        sProc: Nome della funzione chiamante
        
    Returns:
        str: sResult se vuoto, altrimenti "sProc: Errore sResult"
    """
    try:
        if sResult != "":
            return f"{sProc}: Errore {sResult}"
        return ""
    except Exception:
        return ""