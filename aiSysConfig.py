"""
aiSysConfig.py - Funzioni per la gestione della configurazione
Contiene funzioni per espandere variabili, gestire dizionari e validare booleani
"""

from typing import Dict, List, Any, Optional, Union
import re


def Expand(sText: str, dictConfig: Dict) -> str:
    """
    Converte una stringa espandendo sequenze di escape e variabili.
    
    Fase 1: Gestione sequenze di escape:
        %% -> %
        %" -> "
        %n -> \n (newline)
        %$ -> $
        \\ -> \ (backslash singolo)
    
    Fase 2: Espansione variabili $NOME_VARIABILE:
        Sostituisce con dictConfig[NOME_VARIABILE] o "UNKNOWN"
    
    Args:
        sText: Stringa da convertire
        dictConfig: Dizionario di configurazione per l'espansione
        
    Returns:
        str: Stringa convertita
        
    Example:
        >>> Expand("Ciao $USER", {"USER": "Mario"})
        'Ciao Mario'
        >>> Expand("Testo%nNuovaLinea", {})
        'Testo\\nNuovaLinea'
    """
    sProc = "Expand"
    try:
        if not sText:
            return ""
            
        # Fase 1: Gestione sequenze di escape
        result = sText
        
        # Sostituzioni in ordine specifico per evitare conflitti
        result = result.replace('\\\\', '\\')    # \\ -> \
        result = result.replace('%%', '%')       # %% -> %
        result = result.replace('%"', '"')       # %" -> "
        result = result.replace('%n', '\n')      # %n -> newline
        result = result.replace('%$', '$')       # %$ -> $
        
        # Fase 2: Espansione variabili $NOME_VARIABILE
        # Trova tutte le variabili nel formato $NOME_VARIABILE
        # Usiamo una regex per trovare variabili senza spazi
        pattern = r'\$([A-Za-z_][A-Za-z0-9_]*)'
        
        def replace_var(match):
            var_name = match.group(1)
            if var_name in dictConfig:
                value = dictConfig[var_name]
                # Converti in stringa se non lo è già
                return str(value) if value is not None else "UNKNOWN"
            else:
                return "UNKNOWN"
        
        # Applica la sostituzione
        result = re.sub(pattern, replace_var, result)
        
        return result
        
    except Exception:
        # In caso di errore, ritorna la stringa originale
        return sText if sText else ""


def ExpandDict(dictExpand: Dict, dictParams: Dict) -> Dict:
    """
    Applica la funzione Expand() a tutti i valori di un dizionario.
    
    Args:
        dictExpand: Dizionario da espandere (può contenere dizionari annidati)
        dictParams: Dizionario di parametri per l'espansione
        
    Returns:
        Dict: Dizionario espanso
        
    Example:
        >>> ExpandDict({"msg": "Ciao $USER", "config": {"path": "$HOME"}}, 
        ...            {"USER": "Mario", "HOME": "/home/mario"})
        {'msg': 'Ciao Mario', 'config': {'path': '/home/mario'}}
    """
    sProc = "ExpandDict"
    try:
        if not dictExpand:
            return {}
            
        result = {}
        
        for key, value in dictExpand.items():
            if isinstance(value, dict):
                # Ricorsione per dizionari annidati
                result[key] = ExpandDict(value, dictParams)
            elif isinstance(value, str):
                # Espandi stringhe
                result[key] = Expand(value, dictParams)
            else:
                # Mantieni altri tipi così come sono
                result[key] = value
                
        return result
        
    except Exception:
        # In caso di errore, ritorna dizionario vuoto
        return {}


def isGroups(asGroups1: List[str], asGroups2: List[str]) -> bool:
    """
    Verifica se almeno un elemento di asGroups1 è contenuto in asGroups2.
    
    Args:
        asGroups1: Prima lista di stringhe
        asGroups2: Seconda lista di stringhe
        
    Returns:
        bool: True se almeno un elemento di asGroups1 è in asGroups2
        
    Example:
        >>> isGroups(["admin", "user"], ["user", "guest"])
        True
        >>> isGroups(["admin"], ["guest"])
        False
    """
    sProc = "isGroups"
    try:
        # Verifica input validi
        if not asGroups1 or not asGroups2:
            return False
            
        # Confronto case-sensitive
        for group1 in asGroups1:
            if group1 in asGroups2:
                return True
                
        return False
        
    except Exception:
        return False


def Config(dictConfig: Dict, sKey: str) -> str:
    """
    Legge un valore da un dizionario di configurazione.
    
    Args:
        dictConfig: Dizionario di configurazione
        sKey: Chiave da leggere
        
    Returns:
        str: Valore della chiave, stringa vuota se non trovato
        
    Example:
        >>> Config({"nome": "Mario", "età": 30}, "nome")
        'Mario'
        >>> Config({"nome": "Mario"}, "inesistente")
        ''
    """
    sProc = "Config"
    try:
        # Verifica input validi
        if dictConfig is None or sKey is None:
            return ""
            
        # Cerca la chiave nel dizionario
        if sKey in dictConfig:
            value = dictConfig[sKey]
            # Converti in stringa se non None
            return str(value) if value is not None else ""
        else:
            return ""
            
    except Exception:
        return ""


def ConfigDefault(sKey: str, xValue: Any, dictConfig: Dict) -> None:
    """
    Imposta un valore di default in un dizionario solo se la chiave non esiste
    o ha valore None/stringa vuota.
    
    Args:
        sKey: Chiave da impostare
        xValue: Valore di default
        dictConfig: Dizionario da aggiornare (modificato in-place)
        
    Returns:
        None: La funzione modifica dictConfig direttamente
        
    Example:
        >>> d = {"nome": "Mario"}
        >>> ConfigDefault("nome", "Default", d)
        >>> d["nome"]
        'Mario'  # Non modificato perché già presente
        >>> ConfigDefault("età", 30, d)
        >>> d["età"]
        30  # Aggiunto perché non esisteva
    """
    sProc = "ConfigDefault"
    try:
        # Verifica input validi
        if dictConfig is None or sKey is None:
            return
            
        # Se la chiave non esiste, aggiungila
        if sKey not in dictConfig:
            dictConfig[sKey] = xValue
            return
            
        # Se la chiave esiste ma ha valore None o stringa vuota, sostituisci
        current_value = dictConfig[sKey]
        if current_value is None or current_value == "":
            dictConfig[sKey] = xValue
            
        # Altrimenti non fare nulla (mantieni il valore esistente)
        
    except Exception:
        pass  # In caso di errore, non fare nulla


def ConfigSet(dictConfig: Dict, sKey: str, xValue: Any = "") -> None:
    """
    Aggiunge o sostituisce una chiave in un dizionario.
    
    Args:
        dictConfig: Dizionario da aggiornare (modificato in-place)
        sKey: Chiave da aggiungere/sostituire
        xValue: Valore da impostare (default: stringa vuota)
        
    Returns:
        None: La funzione modifica dictConfig direttamente
        
    Example:
        >>> d = {"nome": "Mario"}
        >>> ConfigSet(d, "nome", "Luigi")
        >>> d["nome"]
        'Luigi'
        >>> ConfigSet(d, "nuova", "valore")
        >>> d["nuova"]
        'valore'
    """
    sProc = "ConfigSet"
    try:
        # Verifica input validi
        if dictConfig is None or sKey is None:
            return
            
        # Imposta sempre il valore (sovrascrive se esiste)
        dictConfig[sKey] = xValue
        
    except Exception:
        pass  # In caso di errore, non fare nulla


# Test delle funzioni se eseguito direttamente
if __name__ == "__main__":
    print("Test aiSysConfig.py")
    print("=" * 50)
    
    # Test Expand
    print("1. Test Expand:")
    config = {"USER": "Mario", "HOME": "/home/mario", "PATH": "/usr/bin"}
    
    test1 = "Ciao $USER, la tua home è $HOME"
    result1 = Expand(test1, config)
    print(f"   '{test1}' -> '{result1}'")
    
    test2 = "Testo%nNuova%nLinea%n"
    result2 = Expand(test2, {})
    print(f"   '{test2}' -> '{result2}' (mostra caratteri speciali)")
    
    test3 = "Variabile $INESISTENTE e escaped %$VAR"
    result3 = Expand(test3, {"VAR": "valore"})
    print(f"   '{test3}' -> '{result3}'")
    
    # Test ExpandDict
    print("\n2. Test ExpandDict:")
    dict_to_expand = {
        "messaggio": "Ciao $USER",
        "percorso": "$HOME/documenti",
        "config": {
            "file": "$PATH/programma",
            "test": "Test%nNuovaLinea"
        }
    }
    
    expanded = ExpandDict(dict_to_expand, config)
    print(f"   Dizionario originale: {dict_to_expand}")
    print(f"   Dizionario espanso: {expanded}")
    
    # Test isGroups
    print("\n3. Test isGroups:")
    groups1 = ["admin", "user"]
    groups2 = ["user", "guest"]
    groups3 = ["guest", "visitor"]
    
    print(f"   isGroups({groups1}, {groups2}) = {isGroups(groups1, groups2)}")
    print(f"   isGroups({groups1}, {groups3}) = {isGroups(groups1, groups3)}")
    
    # Test Config
    print("\n4. Test Config:")
    test_config = {"nome": "Mario", "età": 30, "città": "Roma"}
    
    print(f"   Config({{'nome': 'Mario'}}, 'nome') = '{Config(test_config, 'nome')}'")
    print(f"   Config({{'nome': 'Mario'}}, 'inesistente') = '{Config(test_config, 'inesistente')}'")
    
    # Test ConfigDefault
    print("\n5. Test ConfigDefault:")
    d1 = {"nome": "Mario", "età": None}
    d2 = {"nome": "Mario"}
    
    print(f"   Prima: d1 = {d1}")
    ConfigDefault("nome", "Default", d1)  # Non dovrebbe cambiare
    ConfigDefault("età", 30, d1)  # Dovrebbe impostare 30
    ConfigDefault("città", "Roma", d1)  # Dovrebbe aggiungere
    print(f"   Dopo: d1 = {d1}")
    
    print(f"   Prima: d2 = {d2}")
    ConfigDefault("età", 25, d2)  # Dovrebbe aggiungere
    print(f"   Dopo: d2 = {d2}")
    
    # Test ConfigSet
    print("\n6. Test ConfigSet:")
    d3 = {"nome": "Mario"}
    
    print(f"   Prima: d3 = {d3}")
    ConfigSet(d3, "nome", "Luigi")  # Sovrascrive
    ConfigSet(d3, "nuova", "valore")  # Aggiunge
    ConfigSet(d3, "vuota")  # Aggiunge con valore vuoto
    print(f"   Dopo: d3 = {d3}")
    
    print("\nTest completati!")