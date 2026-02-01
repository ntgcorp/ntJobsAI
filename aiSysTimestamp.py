"""
aiSysTimestamp.py - Funzioni per la gestione del timestamp
"""

from datetime import datetime, timedelta
from typing import Union

def Timestamp(sPostfix: str = "") -> str:
    """
    Calcola la stringa di default TimeStamp.
    
    Args:
        sPostfix: Suffisso opzionale
    
    Returns:
        str: Timestamp formattato AAAAMMGG:HHMMSS[:postfix]
    """
    sProc = "Timestamp"
    
    try:
        now = datetime.now()
        sTimestamp = now.strftime("%Y%m%d:%H%M%S")
        
        if sPostfix:
            return f"{sTimestamp}:{sPostfix.lower()}"
        return sTimestamp
        
    except Exception:
        return ""


def TimestampConvert(sTimestamp: str, sMode: str = "s") -> Union[int, float, None]:
    """
    Converte l'output di Timestamp() in giorni o secondi.
    
    Args:
        sTimestamp: Stringa nel formato "AAAAMMGG:HHMMSS" o "AAAAMMGG:HHMMSS:postfix"
        sMode: "d" per giorni (float), "s" per secondi (int)
    
    Returns:
        Union[int, float, None]: Giorni o secondi dall'epoch, None in caso di errore
    """
    sProc = "TimestampConvert"
    
    try:
        if not sTimestamp:
            sTimestamp = Timestamp()
        
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
            
    except (ValueError, TypeError):
        return None
    except Exception:
        return None


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
        
    except Exception:
        return ""


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
        
    except Exception:
        return ""


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
        
        # Controllo giorni nel mese
        if month == 2:
            is_leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
            days_in_month = 29 if is_leap else 28
        elif month in [4, 6, 9, 11]:
            days_in_month = 30
        else:
            days_in_month = 31
        
        if day > days_in_month:
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
        Union[int, float, None]: Differenza in giorni o secondi, None in caso di errore
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
            
    except Exception:
        return None


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
            return ""
        
        seconds = TimestampConvert(sTimestamp, "s")
        if seconds is None:
            return ""
        
        if sUnit.lower() == "s":
            seconds_to_add = nValue
        elif sUnit.lower() == "m":
            seconds_to_add = nValue * 60
        elif sUnit.lower() == "h":
            seconds_to_add = nValue * 3600
        elif sUnit.lower() == "d":
            seconds_to_add = nValue * 86400
        else:
            return ""
        
        new_seconds = seconds + int(seconds_to_add)
        return TimestampFromSeconds(new_seconds)
        
    except Exception:
        return ""


