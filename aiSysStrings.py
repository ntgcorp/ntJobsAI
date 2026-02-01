"""
aiSysStrings.py - Funzioni per la manipolazione di stringhe
"""

import re
from typing import List, Union

def StringBool(sText: str) -> bool:
    """
    Ritorna True se sText è "True" o "False" (case insensitive).
    
    Args:
        sText: Stringa da verificare
    
    Returns:
        bool: True se sText è "True" o "False", False altrimenti
    """
    sProc = "StringBool"
    
    try:
        if not sText:
            return False
        
        sText = sText.strip()
        return sText.lower() in ["true", "false"]
        
    except Exception:
        return False


def isValidPassword(sText: str) -> bool:
    """
    Verifica se sText è una password valida.
    
    Args:
        sText: Stringa da verificare
    
    Returns:
        bool: True se contiene solo caratteri permessi
    """
    sProc = "isValidPassword"
    
    try:
        if not sText:
            return False
        
        # Caratteri permessi: lettere, numeri, _, ., !
        pattern = r'^[A-Za-z0-9_.!]+$'
        return bool(re.match(pattern, sText))
        
    except Exception:
        return False


def isLettersOnly(sText: str) -> bool:
    """
    Verifica se contiene solo lettere e spazi.
    
    Args:
        sText: Stringa da verificare
    
    Returns:
        bool: True se contiene solo lettere e spazi
    """
    sProc = "isLettersOnly"
    
    try:
        if not sText:
            return True
        
        pattern = r'^[A-Za-z\s]+$'
        return bool(re.match(pattern, sText))
        
    except Exception:
        return False


def isEmail(sMail: str) -> bool:
    """
    Verifica se sMail segue le regole di un formato mail.
    
    Args:
        sMail: Stringa da verificare
    
    Returns:
        bool: True se formato mail valido
    """
    sProc = "isEmail"
    
    try:
        if not sMail:
            return False
        
        # Regex base per validazione formato email
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, sMail))
        
    except Exception:
        return False


def StringToArray(sText: str, delimiter: str = ',') -> List[str]:
    """
    Converte una stringa in un array (lista).
    
    Args:
        sText: Stringa da convertire
        delimiter: Carattere delimitatore
    
    Returns:
        List[str]: Lista di stringhe pulite
    """
    sProc = "StringToArray"
    
    try:
        if not sText:
            return []
        
        parts = sText.split(delimiter)
        result = []
        
        for part in parts:
            stripped = part.strip()
            if stripped:
                result.append(stripped)
        
        return result
        
    except Exception:
        return []


def StringToNum(sNumber: str) -> Union[int, float]:
    """
    Converte la stringa sNumber in un numero.
    
    Args:
        sNumber: Stringa da convertire
    
    Returns:
        Union[int, float]: Numero convertito, 0 in caso di errore
    """
    sProc = "StringToNum"
    
    try:
        if not sNumber:
            return 0
        
        # Converte virgola in punto
        sNumber = sNumber.replace(',', '.')
        
        # Controlla se ha decimali
        if '.' in sNumber:
            return float(sNumber)
        else:
            return int(sNumber)
            
    except (ValueError, TypeError):
        return 0
    except Exception:
        return 0


