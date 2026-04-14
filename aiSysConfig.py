"""Modulo per la gestione della configurazione e espansione variabili"""
from typing import Dict, Any, Optional, Union, List
import re
from aiSysBase import ErrorProc

# Crea alias locale
loc_ErrorProc = ErrorProc


def Expand(sText: str, dictConfig: dict) -> str:
    """
    Espande una stringa con sequenze di escape e variabili.
    
    Fase 1: Gestione sequenze di escape (in QUESTO ORDINE):
    1. %## → #      
    2. %# → "  (ASCII 34, virgolette diritte)
    3. %% → %
    4. %n → (carattere newline)
    5. %$ → $
    
    Fase 2: Espansione variabili:
    $NOME_VARIABILE viene sostituita con dictConfig[NOME_VARIABILE]
    Se non viene trovata la variabile in dictConfig, lascia $NOME_VARIABILE come testo.
    
    Args:
        sText: Stringa da espandere
        dictConfig: Dizionario con le variabili per l'espansione
        
    Returns:
        Stringa espansa
    """
    if not sText:
        return sText
    
    # FASE 1: Gestione sequenze di escape
    result = []
    i = 0
    length = len(sText)
    
    while i < length:
        char = sText[i]
        
        if char == '%' and i + 1 < length:
            # Gestione sequenze di escape che iniziano con %
            next_char = sText[i + 1]
            
            # 1. %## → #
            if next_char == '#' and i + 2 < length and sText[i + 2] == '#':
                result.append('#')
                i += 3
                continue
            
            # 2. %# → "
            elif next_char == '#':
                result.append('"')
                i += 2
                continue
            
            # 3. %% → %
            elif next_char == '%':
                result.append('%')
                i += 2
                continue
            
            # 4. %n → newline
            elif next_char == 'n':
                result.append('\n')
                i += 2
                continue
            
            # 5. %$ → $
            elif next_char == '$':
                result.append('$')
                i += 2
                continue
            
            # % seguito da carattere non nella lista → mantieni %+carattere
            else:
                result.append('%')
                result.append(next_char)
                i += 2
                continue
        
        # % finale della stringa → mantieni %
        elif char == '%' and i + 1 == length:
            result.append('%')
            i += 1
            continue
        
        # Aggiungi carattere normale
        result.append(char)
        i += 1
    
    # Converti la lista in stringa dopo Fase 1
    phase1_result = ''.join(result)
    
    # FASE 2: Espansione variabili
    result = []
    i = 0
    length = len(phase1_result)
    
    while i < length:
        char = phase1_result[i]
        
        if char == '$' and i + 1 < length:
            # Cerca il nome della variabile (case-sensitive)
            # I nomi possono contenere lettere, numeri e underscore
            j = i + 1
            var_name = []
            
            # Raccogli i caratteri validi per il nome della variabile
            while j < length:
                c = phase1_result[j]
                if c.isalnum() or c == '_':
                    var_name.append(c)
                    j += 1
                else:
                    break
            
            if var_name:
                # Abbiamo trovato un nome di variabile
                var_name_str = ''.join(var_name)
                
                # Cerca nel dizionario
                if var_name_str in dictConfig:
                    # Sostituisci con il valore
                    result.append(str(dictConfig[var_name_str]))
                else:
                    # Non trovato → mantieni $NOME_VARIABILE
                    result.append('$' + var_name_str)
                
                i = j  # Salta alla posizione dopo il nome
                continue
        
        # $ senza nome dopo → mantieni $
        # Oppure carattere normale
        result.append(char)
        i += 1
    
    return ''.join(result)

def ExpandConvert(sString: str) -> str:
    """
    Conversione inversa di Expand.
    
    Converte caratteri speciali in sequenze di escape.
    
    Args:
        sString: Stringa da convertire
        
    Returns:
        str: Stringa convertita
    """
    sProc = "ExpandConvert"
    
    try:
        if not sString:
            return ""
            
        result = sString
        
        # Ordine importante per evitare sostituzioni multiple
        conversions = [
            ("%", "%%"),
            ("\\", "%\\"),
            ("$", "%$"),
            ("\n", "%n"),
            ('"', "%#"),
            ("#", "%##")
        ]
        
        # Applica conversioni in ordine inverso rispetto a Expand
        for char, escape in reversed(conversions):
            result = result.replace(char, escape)
            
        return result
        
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)


def ExpandDict(dictExpand: Dict, dictParam: Dict) -> Dict:
    """
    Applica Expand() a tutti i valori di un dizionario.
    
    Args:
        dictExpand: Dizionario da espandere
        dictParam: Dizionario per espansione variabili
        
    Returns:
        Dict: Dizionario espanso
    """
    sProc = "ExpandDict"
    
    try:
        if not isinstance(dictExpand, dict):
            return {}
            
        result = {}
        
        for key, value in dictExpand.items():
            if isinstance(value, dict):
                # Ricorsione per dizionari annidati (massimo un livello)
                result[key] = ExpandDict(value, dictParam)
            elif isinstance(value, str):
                result[key] = Expand(value, dictParam)
            else:
                result[key] = value
                
        return result
        
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)


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
            
        for item1 in asGroups1:
            if item1 in asGroups2:
                return True
                
        return False
        
    except Exception as e:
        # In caso di errore, ritorna False
        loc_ErrorProc(str(e), sProc)
        return False


def Config(dictConfig: Dict, sKey: str) -> Any:
    """
    Legge un valore da un dizionario di configurazione.
    
    Args:
        dictConfig: Dizionario da leggere
        sKey: Chiave da estrarre
        
    Returns:
        Any: Valore della chiave o stringa vuota
    """
    sProc = "Config"
    
    try:
        if not dictConfig or not isinstance(dictConfig, dict):
            return ""
            
        if sKey not in dictConfig:
            return ""
            
        return dictConfig[sKey]
        
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)


def ConfigDefault(sKey: str, xValue: Any, dictConfig: Dict) -> None:
    """
    Imposta un valore di default se non presente o vuoto.
    
    Args:
        sKey: Chiave da impostare
        xValue: Valore di default
        dictConfig: Dizionario da aggiornare
    """
    sProc = "ConfigDefault"
    
    try:
        if not isinstance(dictConfig, dict):
            return
            
        if sKey not in dictConfig:
            dictConfig[sKey] = xValue
        elif dictConfig[sKey] is None or dictConfig[sKey] == "":
            dictConfig[sKey] = xValue
            
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)


def SplitSettings(sString: str, dictConfig: Optional[Dict] = None) -> Dict:
    """
    Separa una stringa in un dizionario di coppie chiave-valore.
    
    Args:
        sString: Stringa da analizzare
        dictConfig: Dizionario per espansione variabili (opzionale)
        
    Returns:
        Dict: Dizionario risultante
    """
    sProc = "SplitSettings"
    
    try:
        dictResult = {}
        
        if not sString:
            return dictResult
            
        # Normalizza i separatori: spazio, \n, %n
        normalized = sString.replace("%n", "\n")
        lines = normalized.split("\n")
        
        for line in lines:
            # Gestisci anche separatori spazio per righe multiple
            if " " in line and "=" in line:
                # Potrebbe contenere più chiavi separate da spazio
                parts = line.strip().split()
                for part in parts:
                    if "=" in part:
                        key_value = part.split("=", 1)
                        if len(key_value) == 2:
                            key = key_value[0].strip()
                            value = key_value[1].strip()
                            dictResult[key] = value
            elif "=" in line:
                key_value = line.split("=", 1)
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    dictResult[key] = value
        
        # Espandi se dictConfig è fornito
        if dictConfig:
            dictResult = ExpandDict(dictResult, dictConfig)
            
        return dictResult
        
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)


def ConfigSet(dictConfig: Dict, sKey: str, xValue: Any = "") -> None:
    """
    Aggiunge o sostituisce una chiave in un dizionario.
    
    Args:
        dictConfig: Dizionario da aggiornare
        sKey: Chiave da aggiungere/sostituire
        xValue: Valore da assegnare (default: "")
    """
    sProc = "ConfigSet"
    
    try:
        if not isinstance(dictConfig, dict):
            return
            
        dictConfig[sKey] = xValue
        
    except Exception as e:
        return loc_ErrorProc(str(e), sProc)


