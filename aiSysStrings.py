#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aiSysStrings.py - Funzioni per la manipolazione di stringhe
"""

import os
import sys
import re
from typing import Dict, Any, Optional, Union, List, Tuple

# Import delle funzioni base
from aiSysBase import ErrorProc

# Crea alias locali
loc_ErrorProc = ErrorProc

def StringAppend(sSource: str, sAppend: str, sDelimiter: str = ",") -> str:
    """
    Concatena due stringhe con un delimitatore.
    
    Args:
        sSource: Stringa sorgente (obbligatoria)
        sAppend: Stringa da appendere (obbligatoria)
        sDelimiter: Delimitatore (facoltativo, default=',')
    
    Returns:
        str: Stringa concatenata
    """
    sProc = "StringAppend"
    try:
        if sSource != "":
            sSource = sSource + sDelimiter + sAppend
        else:
            sSource = sAppend
        return sSource
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def StringBool(sText: str) -> bool:
    """
    Converte una stringa in valore booleano.
    
    Args:
        sText: Stringa da convertire
    
    Returns:
        bool: True se sText = "true" o "True", False altrimenti
    """
    sProc = "StringBool"
    try:
        return sText.strip().lower() == "true"
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def isValidPassword(sText: str) -> bool:
    """
    Verifica se una stringa è una password valida.
    
    Args:
        sText: Stringa da verificare
    
    Returns:
        bool: True se contiene solo caratteri permessi, False altrimenti
    """
    sProc = "isValidPassword"
    try:
        if not sText:
            return False
        
        # Caratteri permessi: lettere, numeri, "_", ".", "!"
        pattern = r'^[a-zA-Z0-9_\.!]+$'
        return bool(re.match(pattern, sText))
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def isLettersOnly(sText: str) -> bool:
    """
    Verifica se una stringa contiene solo lettere e spazi.
    
    Args:
        sText: Stringa da verificare
    
    Returns:
        bool: True se contiene solo lettere e spazi, False altrimenti
    """
    sProc = "isLettersOnly"
    try:
        if not sText:
            return False
        
        # Solo lettere (maiuscole/minuscole) e spazi
        pattern = r'^[a-zA-Z\s]+$'
        return bool(re.match(pattern, sText))
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def isEmail(sMail: str) -> bool:
    """
    Verifica formato email con regex media.
    
    Supporta: nome.cognome@gmail.com, nome@dominio.co.uk
    
    Args:
        sMail: Indirizzo email da verificare
    
    Returns:
        bool: True se email valida, False altrimenti
    """
    sProc = "isEmail"
    try:
        # Controlli aggiuntivi base
        if not sMail or '@' not in sMail or '.' not in sMail:
            return False
        
        # Regex principale
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, sMail):
            # Ulteriore controllo: dopo l'ultimo punto ci devono essere almeno 2 caratteri
            parts = sMail.split('@')
            if len(parts) != 2:
                return False
            
            domain_parts = parts[1].split('.')
            if len(domain_parts) < 2 or len(domain_parts[-1]) < 2:
                return False
            
            return True
        
        return False
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def StringToArray(sText: str, delimiter: str = ",") -> List[str]:
    """
    Converte una stringa in un array (lista).
    
    Args:
        sText: Stringa da convertire
        delimiter: Carattere delimitatore (default=',')
    
    Returns:
        List[str]: Lista di stringhe pulite
    """
    sProc = "StringToArray"
    try:
        if not sText:
            return []
        
        # Splitta la stringa usando il delimitatore
        items = sText.split(delimiter)
        
        # Pulisci ogni elemento (rimuovi spazi) e filtra stringhe vuote
        result = [item.strip() for item in items if item.strip()]
        
        return result
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def StringToNum(sNumber: str) -> Union[int, float]:
    """
    Converte una stringa in numero.
    
    Args:
        sNumber: Stringa da convertire
    
    Returns:
        Union[int, float]: Numero convertito, 0 in caso di errore
    """
    sProc = "StringToNum"
    try:
        if not sNumber:
            return 0
        
        # Sostituisci virgola con punto
        sNumber = sNumber.replace(',', '.')
        
        # Controlla se ha decimali
        if '.' in sNumber:
            return float(sNumber)
        else:
            return int(sNumber)
    except (ValueError, TypeError):
        return 0
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def StringWash(sText: str) -> str:
    """
    Rimuove i caratteri non-ASCII e le virgolette doppie da una stringa.
    
    Args:
        sText: Stringa da pulire
    
    Returns:
        str: Stringa pulita
    """
    sProc = "StringWash"
    try:
        # 1. Converte in ASCII ignorando gli errori (rimuove i non-ASCII)
        # 2. Riconverte in stringa (decode)
        # 3. Rimuove le virgolette doppie
        return sText.encode("ascii", "ignore").decode().replace('"', '')
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

# Test locale se eseguito direttamente
if __name__ == "__main__":
    print(f"StringAppend: {StringAppend('test', 'append', ',')}")
    print(f"StringBool 'true': {StringBool('true')}")
    print(f"StringBool 'false': {StringBool('false')}")
    print(f"isValidPassword 'abc123_!': {isValidPassword('abc123_!')}")
    print(f"isValidPassword 'abc@123': {isValidPassword('abc@123')}")
    print(f"isLettersOnly 'Hello World': {isLettersOnly('Hello World')}")
    print(f"isLettersOnly 'Hello123': {isLettersOnly('Hello123')}")
    print(f"isEmail 'test@example.com': {isEmail('test@example.com')}")
    print(f"isEmail 'invalid': {isEmail('invalid')}")
    print(f"StringToArray: {StringToArray('a,b,c,d')}")
    print(f"StringToNum '123': {StringToNum('123')}")
    print(f"StringToNum '123.45': {StringToNum('123.45')}")
