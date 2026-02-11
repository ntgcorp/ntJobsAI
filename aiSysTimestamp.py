#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aiSysTimestamp.py - Libreria per la gestione dei timestamp
"""

import os
import sys
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta

# Import delle funzioni base
from aiSysBase import ErrorProc

# Crea alias locali
loc_ErrorProc = ErrorProc

def Timestamp(sPostfix: str = "") -> str:
    """
    Genera un timestamp nel formato AAAAMMGG:HHMMSS.
    
    Args:
        sPostfix: Suffisso opzionale da aggiungere al timestamp
    
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore
    """
    sProc = "Timestamp"
    try:
        # Ottieni la data/ora corrente
        now = datetime.now()
        
        # Formatta nel formato richiesto: AAAAMMGG:HHMMSS
        sResult = now.strftime("%Y%m%d:%H%M%S")
        
        # Se è stato fornito un postfix, aggiungilo in minuscolo
        if sPostfix:
            sResult = f"{sResult}:{sPostfix.lower()}"
        
        return sResult
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampConvert(sTimestamp: str, sMode: str = "s") -> Union[int, float, None]:
    """
    Converte l'output della funzione Timestamp() in giorni o secondi.
    
    Args:
        sTimestamp: Stringa nel formato "AAAAMMGG:HHMMSS" o "AAAAMMGG:HHMMSS:postfix"
        sMode: "d" per giorni (float), "s" per secondi (int)
    
    Returns:
        - In modalità "d": float (giorni con decimali)
        - In modalità "s": int (secondi totali)
        - None in caso di errore
    """
    sProc = "TimestampConvert"
    try:
        if not sTimestamp:
            sTimestamp = Timestamp("")
        
        if ':' in sTimestamp:
            parts = sTimestamp.split(':')
            if len(parts) >= 2:
                date_part = parts[0]
                time_part = parts[1]
            else:
                return None
        else:
            return None
        
        if len(date_part) != 8 or len(time_part) != 6:
            return None
        
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        dt = datetime(year, month, day, hour, minute, second)
        epoch = datetime(1970, 1, 1)
        
        if sMode.lower() == "d":
            delta = dt - epoch
            return delta.total_seconds() / 86400.0
        elif sMode.lower() == "s":
            delta = dt - epoch
            return int(delta.total_seconds())
        else:
            return None
    except (ValueError, TypeError) as e:
        return loc_ErrorProc(str(e), sProc)
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampFromSeconds(nSeconds: int, sPostfix: str = "") -> str:
    """
    Converte secondi dall'epoch nel formato Timestamp().
    
    Args:
        nSeconds: Secondi dall'epoch (1 gennaio 1970)
        sPostfix: Suffisso opzionale
    
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore
    """
    sProc = "TimestampFromSeconds"
    try:
        dt = datetime(1970, 1, 1) + timedelta(seconds=nSeconds)
        sTimestamp = dt.strftime("%Y%m%d:%H%M%S")
        
        if sPostfix:
            return f"{sTimestamp}:{sPostfix.lower()}"
        return sTimestamp
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampFromDays(nDays: float, sPostfix: str = "") -> str:
    """
    Converte giorni dall'epoch nel formato Timestamp().
    
    Args:
        nDays: Giorni dall'epoch (1 gennaio 1970)
        sPostfix: Suffisso opzionale
    
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore
    """
    sProc = "TimestampFromDays"
    try:
        seconds = int(nDays * 86400.0)
        return TimestampFromSeconds(seconds, sPostfix)
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampValidate(sTimestamp: str) -> bool:
    """
    Valida se una stringa è nel formato Timestamp valido.
    
    Args:
        sTimestamp: Stringa da validare
    
    Returns:
        bool: True se valido, False altrimenti
    """
    sProc = "TimestampValidate"
    try:
        if not sTimestamp:
            return False
        
        if ':' in sTimestamp:
            parts = sTimestamp.split(':')
            if len(parts) < 2:
                return False
            date_part = parts[0]
            time_part = parts[1]
        else:
            return False
        
        if len(date_part) != 8 or len(time_part) != 6:
            return False
        
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        if not (1 <= month <= 12):
            return False
        if not (1 <= day <= 31):
            return False
        if not (0 <= hour <= 23):
            return False
        if not (0 <= minute <= 59):
            return False
        if not (0 <= second <= 59):
            return False
        
        # Controlla giorni nel mese considerando gli anni bisestili
        days_in_month = [31, 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,
                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        if day > days_in_month[month - 1]:
            return False
        
        return True
    except (ValueError, TypeError):
        return False

def TimestampDiff(sTimestamp1: str, sTimestamp2: str, sMode: str = "s") -> Union[int, float, None]:
    """
    Calcola la differenza tra due timestamp.
    
    Args:
        sTimestamp1: Primo timestamp
        sTimestamp2: Secondo timestamp
        sMode: "d" per giorni, "s" per secondi
    
    Returns:
        Differenza in giorni o secondi, None in caso di errore
    """
    sProc = "TimestampDiff"
    try:
        if not TimestampValidate(sTimestamp1) or not TimestampValidate(sTimestamp2):
            return None
        
        sec1 = TimestampConvert(sTimestamp1, "s")
        sec2 = TimestampConvert(sTimestamp2, "s")
        
        if sec1 is None or sec2 is None:
            return None
        
        diff_seconds = abs(sec1 - sec2)
        
        if sMode.lower() == "d":
            return diff_seconds / 86400.0
        elif sMode.lower() == "s":
            return diff_seconds
        else:
            return None
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampAdd(sTimestamp: str, nValue: Union[int, float], sUnit: str = "s") -> str:
    """
    Aggiunge tempo a un timestamp.
    
    Args:
        sTimestamp: Timestamp di partenza
        nValue: Valore da aggiungere
        sUnit: "s" per secondi, "d" per giorni, "m" per minuti, "h" per ore
    
    Returns:
        str: Nuovo timestamp, stringa vuota in caso di errore
    """
    sProc = "TimestampAdd"
    try:
        if not TimestampValidate(sTimestamp):
            return loc_ErrorProc("Timestamp non valido", sProc)
        
        seconds = TimestampConvert(sTimestamp, "s")
        if seconds is None:
            return loc_ErrorProc("Conversione timestamp fallita", sProc)
        
        if sUnit.lower() == "s":
            seconds_to_add = nValue
        elif sUnit.lower() == "m":
            seconds_to_add = nValue * 60
        elif sUnit.lower() == "h":
            seconds_to_add = nValue * 3600
        elif sUnit.lower() == "d":
            seconds_to_add = nValue * 86400
        else:
            return loc_ErrorProc(f"Unita' non valida: {sUnit}", sProc)
        
        new_seconds = seconds + int(seconds_to_add)
        return TimestampFromSeconds(new_seconds)
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampIsoFrom(ts: str, milliseconds: str = "000", tz: str = "Z") -> str:
    """
    Converte 'AAAAMMGG:HHMMSS' in stringa ISO 8601.
    
    Args:
        ts: Timestamp nel formato AAAAMMGG:HHMMSS
        milliseconds: Millisecondi (default: '000')
        tz: Timezone (default: 'Z')
    
    Returns:
        str: Stringa ISO 8601
    """
    sProc = "TimestampIsoFrom"
    try:
        date_part, time_part = ts.split(":")
        year = date_part[0:4]
        month = date_part[4:6]
        day = date_part[6:8]
        hour = time_part[0:2]
        minute = time_part[2:4]
        second = time_part[4:6]
        
        return f"{year}-{month}-{day}T{hour}:{minute}:{second}.{milliseconds}{tz}"
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

def TimestampIsoTo(iso_ts: str) -> str:
    """
    Converte una stringa ISO 8601 in 'AAAAMMGG:HHMMSS'.
    
    Args:
        iso_ts: Stringa ISO 8601
    
    Returns:
        str: Timestamp nel formato AAAAMMGG:HHMMSS
    """
    sProc = "TimestampIsoTo"
    try:
        # Gestione 'Z' → UTC
        if iso_ts.endswith("Z"):
            iso_ts = iso_ts.replace("Z", "+00:00")
        
        dt = datetime.fromisoformat(iso_ts)
        return dt.strftime("%Y%m%d:%H%M%S")
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)

# Test locale se eseguito direttamente
if __name__ == "__main__":
    print(f"Timestamp corrente: {Timestamp()}")
    print(f"Timestamp con postfix: {Timestamp('test')}")
    
    ts = Timestamp()
    print(f"Timestamp validato: {TimestampValidate(ts)}")
    print(f"Timestamp in secondi: {TimestampConvert(ts, 's')}")
    print(f"Timestamp in giorni: {TimestampConvert(ts, 'd')}")
    
    ts_iso = TimestampIsoFrom(ts)
    print(f"Timestamp ISO: {ts_iso}")
    print(f"Timestamp da ISO: {TimestampIsoTo(ts_iso)}")