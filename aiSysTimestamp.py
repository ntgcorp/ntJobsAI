"""
aiSysTimestamp.py - Funzioni per la gestione dei timestamp
Formato: AAAAMMGG:HHMMSS o AAAAMMGG:HHMMSS:postfix
"""

from typing import Union, Optional
from datetime import datetime, timedelta
import re


def Timestamp(sPostfix: str = "") -> str:
    """
    Genera un timestamp nel formato AAAAMMGG:HHMMSS.
    
    Args:
        sPostfix: Suffisso opzionale da aggiungere
        
    Returns:
        str: Timestamp formattato
        
    Example:
        >>> Timestamp()
        '20240125:143055'
        >>> Timestamp("Test")
        '20240125:143055:test'
    """
    sProc = "Timestamp"
    try:
        # Ottieni data e ora corrente
        now = datetime.now()
        
        # Formatta nel formato richiesto
        sTimestamp = now.strftime("%Y%m%d:%H%M%S")
        
        # Aggiungi postfix se fornito
        if sPostfix:
            sTimestamp = f"{sTimestamp}:{sPostfix.lower()}"
            
        return sTimestamp
        
    except Exception:
        return ""


def TimestampConvert(sTimestamp: str, sMode: str = "s") -> Union[int, float]:
    """
    Converte un timestamp in secondi o giorni dall'epoch.
    
    Args:
        sTimestamp: Stringa nel formato AAAAMMGG:HHMMSS o AAAAMMGG:HHMMSS:postfix
        sMode: "d" per giorni (float), "s" per secondi (int)
        
    Returns:
        Union[int, float]: Secondi o giorni dall'epoch, -1 in caso di errore
        
    Example:
        >>> TimestampConvert("20240125:143055", "s")
        1706195455
    """
    sProc = "TimestampConvert"
    try:
        # Se sTimestamp è vuoto, usa timestamp corrente
        if not sTimestamp:
            sTimestamp = Timestamp()
            
        # Rimuovi eventuale postfix per l'analisi
        if ':' in sTimestamp:
            parts = sTimestamp.split(':')
            if len(parts) >= 2:
                date_part = parts[0]
                time_part = parts[1]
            else:
                return -1
        else:
            return -1
            
        # Verifica lunghezza
        if len(date_part) != 8 or len(time_part) != 6:
            return -1
            
        # Estrai componenti della data
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        
        # Estrai componenti dell'ora
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        # Crea oggetto datetime
        dt = datetime(year, month, day, hour, minute, second)
        
        # Data di riferimento (epoch)
        epoch = datetime(1970, 1, 1)
        
        # Calcola differenza
        delta = dt - epoch
        
        # Ritorna in base alla modalità
        if sMode.lower() == "d":
            return delta.total_seconds() / 86400.0
        elif sMode.lower() == "s":
            return int(delta.total_seconds())
        else:
            return -1
            
    except (ValueError, TypeError, Exception):
        return -1


def TimestampFromSeconds(nSeconds: int, sPostfix: str = "") -> str:
    """
    Converte secondi dall'epoch in formato timestamp.
    
    Args:
        nSeconds: Secondi dall'epoch (1 gennaio 1970)
        sPostfix: Suffisso opzionale
        
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore
        
    Example:
        >>> TimestampFromSeconds(1706195455)
        '20240125:143055'
    """
    sProc = "TimestampFromSeconds"
    try:
        # Crea datetime dall'epoch + secondi
        dt = datetime(1970, 1, 1) + timedelta(seconds=nSeconds)
        
        # Formatta nel formato richiesto
        sTimestamp = dt.strftime("%Y%m%d:%H%M%S")
        
        # Aggiungi postfix se fornito
        if sPostfix:
            return f"{sTimestamp}:{sPostfix.lower()}"
            
        return sTimestamp
        
    except Exception:
        return ""


def TimestampFromDays(nDays: float, sPostfix: str = "") -> str:
    """
    Converte giorni dall'epoch in formato timestamp.
    
    Args:
        nDays: Giorni dall'epoch (1 gennaio 1970)
        sPostfix: Suffisso opzionale
        
    Returns:
        str: Timestamp formattato, stringa vuota in caso di errore
        
    Example:
        >>> TimestampFromDays(19745.5)
        '20240125:120000'
    """
    sProc = "TimestampFromDays"
    try:
        # Converti giorni in secondi
        seconds = int(nDays * 86400.0)
        
        # Usa TimestampFromSeconds
        return TimestampFromSeconds(seconds, sPostfix)
        
    except Exception:
        return ""


def TimestampValidate(sTimestamp: str) -> bool:
    """
    Valida se una stringa è nel formato timestamp valido.
    
    Args:
        sTimestamp: Stringa da validare
        
    Returns:
        bool: True se valido, False altrimenti
        
    Example:
        >>> TimestampValidate("20240125:143055")
        True
        >>> TimestampValidate("20240125:143055:test")
        True
        >>> TimestampValidate("20241325:143055")
        False
    """
    sProc = "TimestampValidate"
    try:
        if not sTimestamp:
            return False
            
        # Verifica formato base
        if ':' in sTimestamp:
            parts = sTimestamp.split(':')
            if len(parts) < 2:
                return False
                
            date_part = parts[0]
            time_part = parts[1]
        else:
            return False
            
        # Verifica lunghezza
        if len(date_part) != 8 or len(time_part) != 6:
            return False
            
        # Estrai componenti
        year = int(date_part[0:4])
        month = int(date_part[4:6])
        day = int(date_part[6:8])
        
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        
        # Valida mese
        if not (1 <= month <= 12):
            return False
            
        # Valida giorno (controllo iniziale)
        if not (1 <= day <= 31):
            return False
            
        # Valida ore
        if not (0 <= hour <= 23):
            return False
            
        # Valida minuti
        if not (0 <= minute <= 59):
            return False
            
        # Valida secondi
        if not (0 <= second <= 59):
            return False
            
        # Valida giorno del mese considerando anni bisestili
        days_in_month = [
            31,  # Gennaio
            29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28,  # Febbraio
            31,  # Marzo
            30,  # Aprile
            31,  # Maggio
            30,  # Giugno
            31,  # Luglio
            31,  # Agosto
            30,  # Settembre
            31,  # Ottobre
            30,  # Novembre
            31   # Dicembre
        ]
        
        if day > days_in_month[month - 1]:
            return False
            
        return True
        
    except (ValueError, TypeError):
        return False


def TimestampDiff(sTimestamp1: str, sTimestamp2: str, sMode: str = "s") -> Union[int, float]:
    """
    Calcola la differenza tra due timestamp.
    
    Args:
        sTimestamp1: Primo timestamp
        sTimestamp2: Secondo timestamp
        sMode: "d" per giorni, "s" per secondi
        
    Returns:
        Union[int, float]: Differenza in giorni o secondi, -1 in caso di errore
        
    Example:
        >>> TimestampDiff("20240125:120000", "20240125:130000", "s")
        3600
    """
    sProc = "TimestampDiff"
    try:
        # Valida entrambi i timestamp
        if not TimestampValidate(sTimestamp1) or not TimestampValidate(sTimestamp2):
            return -1
            
        # Converti in secondi
        sec1 = TimestampConvert(sTimestamp1, "s")
        sec2 = TimestampConvert(sTimestamp2, "s")
        
        if sec1 == -1 or sec2 == -1:
            return -1
            
        # Calcola differenza assoluta
        diff_seconds = abs(sec1 - sec2)
        
        # Ritorna in base alla modalità
        if sMode.lower() == "d":
            return diff_seconds / 86400.0
        elif sMode.lower() == "s":
            return diff_seconds
        else:
            return -1
            
    except Exception:
        return -1


def TimestampAdd(sTimestamp: str, nValue: Union[int, float], sUnit: str = "s") -> str:
    """
    Aggiunge tempo a un timestamp.
    
    Args:
        sTimestamp: Timestamp di partenza
        nValue: Valore da aggiungere
        sUnit: "s" per secondi, "m" per minuti, "h" per ore, "d" per giorni
        
    Returns:
        str: Nuovo timestamp, stringa vuota in caso di errore
        
    Example:
        >>> TimestampAdd("20240125:120000", 3600, "s")
        '20240125:130000'
    """
    sProc = "TimestampAdd"
    try:
        # Valida il timestamp
        if not TimestampValidate(sTimestamp):
            return ""
            
        # Converti in secondi
        seconds = TimestampConvert(sTimestamp, "s")
        if seconds == -1:
            return ""
            
        # Calcola secondi da aggiungere in base all'unità
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
            
        # Calcola nuovi secondi
        new_seconds = seconds + int(seconds_to_add)
        
        # Converti in timestamp
        return TimestampFromSeconds(new_seconds)
        
    except Exception:
        return ""


# Test delle funzioni se eseguito direttamente
if __name__ == "__main__":
    print("Test aiSysTimestamp.py")
    print("=" * 50)
    
    # Test Timestamp
    print("1. Test Timestamp:")
    ts1 = Timestamp()
    print(f"   Timestamp() = '{ts1}'")
    ts2 = Timestamp("Test")
    print(f"   Timestamp('Test') = '{ts2}'")
    
    # Test TimestampValidate
    print("\n2. Test TimestampValidate:")
    print(f"   '{ts1}' = {TimestampValidate(ts1)}")
    print(f"   '{ts2}' = {TimestampValidate(ts2)}")
    print(f"   'invalid' = {TimestampValidate('invalid')}")
    
    # Test TimestampConvert
    print("\n3. Test TimestampConvert:")
    seconds = TimestampConvert(ts1, "s")
    days = TimestampConvert(ts1, "d")
    print(f"   '{ts1}' -> secondi = {seconds}")
    print(f"   '{ts1}' -> giorni = {days:.6f}")
    
    # Test TimestampFromSeconds e TimestampFromDays
    print("\n4. Test TimestampFromSeconds/TimestampFromDays:")
    ts_from_sec = TimestampFromSeconds(seconds)
    ts_from_days = TimestampFromDays(days)
    print(f"   {seconds} sec -> '{ts_from_sec}'")
    print(f"   {days:.6f} giorni -> '{ts_from_days}'")
    
    # Test TimestampDiff
    print("\n5. Test TimestampDiff:")
    ts_start = "20240125:120000"
    ts_end = "20240125:130000"
    diff_sec = TimestampDiff(ts_start, ts_end, "s")
    diff_days = TimestampDiff(ts_start, ts_end, "d")
    print(f"   Diff('{ts_start}', '{ts_end}') -> {diff_sec} sec = {diff_days:.6f} giorni")
    
    # Test TimestampAdd
    print("\n6. Test TimestampAdd:")
    ts_original = "20240125:120000"
    ts_plus_1h = TimestampAdd(ts_original, 1, "h")
    ts_plus_30m = TimestampAdd(ts_original, 30, "m")
    print(f"   '{ts_original}' + 1h = '{ts_plus_1h}'")
    print(f"   '{ts_original}' + 30m = '{ts_plus_30m}'")
    
    print("\nTest completati!")