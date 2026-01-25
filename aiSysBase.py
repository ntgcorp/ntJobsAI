"""
aiSysBase.py - Funzioni di base del sistema aiSys
Contiene funzioni per gestire errori, dizionari e visualizzazione
"""

from typing import Dict, Any, Optional, Union
import sys

try:
    from acDictToString import acDictToString
except ImportError:
    # Fallback per quando acDictToString non è disponibile
    acDictToString = None


def aiErrorProc(sResult: str, sProc: str) -> str:
    """
    Ritorna stringa di errore formattata con nome della procedura.
    
    Args:
        sResult: Stringa del risultato/errore
        sProc: Nome della funzione/procedura
        
    Returns:
        str: Stringa formattata se sResult non è vuoto, altrimenti sResult
        
    Example:
        >>> aiErrorProc("File non trovato", "read_file")
        'read_file: Errore File non trovato'
        >>> aiErrorProc("", "read_file")
        ''
    """
    sProc = "aiErrorProc"
    try:
        if sResult != "":
            return f"{sProc}: Errore {str(sResult)}"
        else:
            return sResult
    except Exception:
        return ""


def DictMerge(dictSource: Dict, dictAdd: Dict) -> Dict:
    """
    Unisce due dizionari con priorità su dictAdd.
    
    Args:
        dictSource: Dizionario sorgente
        dictAdd: Dizionario da aggiungere (ha priorità)
        
    Returns:
        Dict: Dizionario unito
        
    Example:
        >>> DictMerge({"a": 1, "b": 2}, {"b": 3, "c": 4})
        {'a': 1, 'b': 3, 'c': 4}
    """
    sProc = "DictMerge"
    try:
        # Se dictAdd è None o vuoto, non fare nulla
        if dictAdd is None or len(dictAdd) == 0:
            return dictSource
            
        # Se dictSource non esiste o è vuoto, ritorna copia di dictAdd
        if dictSource is None or len(dictSource) == 0:
            return dictAdd.copy()
            
        # Crea copia del sorgente e aggiorna con dictAdd
        result = dictSource.copy()
        result.update(dictAdd)
        return result
        
    except Exception as e:
        # In caso di errore, ritorna dictSource se esiste
        if dictSource is not None:
            return dictSource
        return {}


def DictPrint(jDS: acDictToString, dictData: Dict, sFile: Optional[str] = None) -> str:
    """
    Visualizza un dizionario su schermo o su file in accodamento.
    
    Args:
        jDS: Istanza della classe acDictToString
        dictData: Dizionario da visualizzare
        sFile: File opzionale dove accodare l'output
        
    Returns:
        str: Stringa vuota in caso di successo, stringa di errore altrimenti
        
    Example:
        >>> converter = acDictToString()
        >>> DictPrint(converter, {"nome": "Mario"}, "output.txt")
        ''
    """
    sProc = "DictPrint"
    try:
        # Verifica che jDS sia valido
        if jDS is None or not isinstance(jDS, acDictToString):
            return f"{sProc}: Errore Istanza acDictToString non valida"
            
        # Verifica che dictData sia valido
        if dictData is None or not isinstance(dictData, dict):
            return f"{sProc}: Errore Dizionario non valido"
            
        # Converti il dizionario in stringa JSON
        sText = jDS.DictToString(dictData, "json")
        
        # Se sFile è fornito, scrive su file
        if sFile:
            try:
                with open(sFile, 'a', encoding='utf-8') as f:
                    f.write(sText + '\n')
            except Exception as e:
                return f"{sProc}: ErroreRiscontrato {e} {sFile}"
        
        # Mostra sempre su schermo
        print(sText)
        return ""  # Successo -> stringa vuota
        
    except Exception as e:
        sResult = f"ErroreRiscontrato {e}"
        if sFile:
            sResult += f" {sFile}"
        return sResult


# Test delle funzioni se eseguito direttamente
if __name__ == "__main__":
    print("Test aiSysBase.py")
    print("=" * 50)
    
    # Test aiErrorProc
    print("1. Test aiErrorProc:")
    print(f"   Successo: '{aiErrorProc('', 'test_func')}'")
    print(f"   Errore: '{aiErrorProc('File non trovato', 'test_func')}'")
    
    # Test DictMerge
    print("\n2. Test DictMerge:")
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    result = DictMerge(dict1, dict2)
    print(f"   DictMerge({{'a':1, 'b':2}}, {{'b':3, 'c':4}}) = {result}")
    
    # Test DictMerge con dictAdd vuoto
    result2 = DictMerge(dict1, {})
    print(f"   DictMerge({{'a':1, 'b':2}}, {{}}) = {result2}")
    
    # Test DictMerge con dictSource vuoto
    result3 = DictMerge({}, dict2)
    print(f"   DictMerge({{}}, {{'b':3, 'c':4}}) = {result3}")
    
    # Test DictPrint (richiede acDictToString)
    print("\n3. Test DictPrint:")
    try:
        from acDictToString import acDictToString
        converter = acDictToString()
        print(f"   DictPrint con dizionario semplice:")
        dict_simple = {"nome": "Test", "valore": 123}
        error = DictPrint(converter, dict_simple)
        if error:
            print(f"   ERRORE: {error}")
        else:
            print(f"   SUCCESSO: Dizionario stampato")
    except ImportError:
        print("   SKIPPATO: acDictToString non disponibile")
    
    print("\nTest completati!")