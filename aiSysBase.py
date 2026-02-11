"""Modulo base con funzioni fondamentali per aiSys"""
from typing import Dict, Any, Optional, Union, List


def ErrorProc(sResult: str, sProc: str) -> str:
    """
    Ritorno con Errore sProc aggiunto.
    
    Args:
        sResult: Stringa di errore (obbligatoria)
        sProc: Nome della funzione chiamante (obbligatorio)
        
    Returns:
        str: Stringa formattata con errore o stringa vuota
    """
    if sResult != "":
        return f"{sProc}: Errore {sResult}"
    else:
        return sResult


def DictMerge(dictSource: Dict, dictAdd: Dict) -> None:
    """
    Aggiunge le chiavi di dictAdd a dictSource.
    
    Args:
        dictSource: Dizionario da aggiornare
        dictAdd: Dizionario da aggiungere
    """
    sProc = "DictMerge"
    
    try:
        if not dictAdd or not isinstance(dictAdd, dict):
            return
        
        if not dictSource or not isinstance(dictSource, dict):
            if isinstance(dictAdd, dict):
                dictSource.clear()
                dictSource.update(dictAdd)
            return
        
        # Aggiunge o sovrascrive le chiavi
        for key, value in dictAdd.items():
            dictSource[key] = value
            
    except Exception as e:
        return ErrorProc(str(e), sProc)


def DictExist(dictParam: Dict, sKey: str, xDefault: Any) -> Any:
    """
    Ritorna valore di una chiave oppure un valore di default.
    
    Args:
        dictParam: Dizionario da esaminare
        sKey: Chiave da cercare
        xDefault: Valore di default
        
    Returns:
        Any: Valore della chiave o default
    """
    sProc = "DictExist"
    
    try:
        xResult = None
        
        if not isinstance(dictParam, dict):
            return xDefault
        
        if sKey not in dictParam:
            xResult = xDefault
        else:
            xResult = dictParam[sKey]
            
        return xResult
        
    except Exception as e:
        return ErrorProc(str(e), sProc)


