"""
aiSysConfig.py - Funzioni per la gestione della configurazione
"""

import re
from typing import Dict, Any, List

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


def Expand(sText: str, dictConfig: Dict[str, str]) -> str:
    """
    Converte una stringa espandendo sequenze di escape e variabili.
    
    Args:
        sText: Stringa da espandere
        dictConfig: Dizionario di configurazione
    
    Returns:
        str: Stringa convertita
    """
    sProc = "Expand"
    
    try:
        if not sText:
            return ""
        
        # Fase 1: Gestione sequenze di escape
        replacements = {
            '%%': '%',
            '%"': '"',
            '%n': '\n',
            '%$': '$',
            '%\\': '\\'
        }
        
        for old, new in replacements.items():
            sText = sText.replace(old, new)
        
        # Fase 2: Espansione variabili $NOME_VARIABILE
        def replace_var(match):
            var_name = match.group(1)
            return dictConfig.get(var_name, "UNKNOWN")
        
        pattern = r'\$([A-Za-z_][A-Za-z0-9_]*)'
        sText = re.sub(pattern, replace_var, sText)
        
        return sText
        
    except Exception as e:
        return loc_aiErrorProc(str(e), sProc)


def ExpandDict(dictExpand: Dict[str, Any], dictParam: Dict[str, str]) -> Dict[str, Any]:
    """
    Applica Expand() ricorsivamente a un dizionario.
    
    Args:
        dictExpand: Dizionario da espandere
        dictParam: Dizionario di configurazione
    
    Returns:
        Dict[str, Any]: Dizionario espanso
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
        return loc_aiErrorProc(str(e), sProc)


def isGroups(asGroups1: List[str], asGroups2: List[str]) -> bool:
    """
    Verifica se almeno un elemento di asGroups1 è contenuto in asGroups2.
    
    Args:
        asGroups1: Prima lista di stringhe
        asGroups2: Seconda lista di stringhe
    
    Returns:
        bool: True se c'è almeno una corrispondenza
    """
    sProc = "isGroups"
    
    try:
        if not asGroups1 or not asGroups2:
            return False
        
        for group1 in asGroups1:
            if group1 in asGroups2:
                return True
        
        return False
        
    except Exception:
        return False


def Config(dictConfig: Dict[str, Any], sKey: str) -> Any:
    """
    Legge un valore da un dizionario di configurazione.
    
    Args:
        dictConfig: Dizionario di configurazione
        sKey: Chiave da leggere
    
    Returns:
        Any: Valore della chiave o "" se non esiste
    """
    sProc = "Config"
    
    try:
        if not dictConfig:
            return ""
        
        if sKey not in dictConfig:
            return ""
        
        return dictConfig[sKey]
        
    except Exception:
        return ""


def ConfigDefault(sKey: str, xValue: Any, dictConfig: Dict[str, Any]) -> Dict[str, Any]:
    """
    Imposta un valore di default in un dizionario se non presente.
    
    Args:
        sKey: Chiave da impostare
        xValue: Valore di default
        dictConfig: Dizionario da aggiornare
    
    Returns:
        Dict[str, Any]: Dizionario aggiornato
    """
    sProc = "ConfigDefault"
    
    try:
        if dictConfig is None:
            dictConfig = {}
        
        if sKey not in dictConfig:
            dictConfig[sKey] = xValue
        else:
            current_value = dictConfig[sKey]
            if current_value is None or current_value == "":
                dictConfig[sKey] = xValue
        
        return dictConfig
        
    except Exception:
        return dictConfig if dictConfig else {}


def ConfigSet(dictConfig: Dict[str, Any], sKey: str, xValue: Any = "") -> Dict[str, Any]:
    """
    Aggiunge o sostituisce una chiave in un dizionario.
    
    Args:
        dictConfig: Dizionario da aggiornare
        sKey: Chiave da aggiungere/sostituire
        xValue: Valore da assegnare
    
    Returns:
        Dict[str, Any]: Dizionario aggiornato
    """
    sProc = "ConfigSet"
    
    try:
        if dictConfig is None:
            dictConfig = {}
        
        dictConfig[sKey] = xValue
        return dictConfig
        
    except Exception:
        return dictConfig if dictConfig else {}


