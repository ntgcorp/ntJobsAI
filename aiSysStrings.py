"""
aiSysStrings.py - Funzioni per la manipolazione e validazione di stringhe
Contiene funzioni per validare password, email, convertire tipi, etc.
"""

from typing import List, Union, Optional
import re


def isBool(sText: str) -> bool:
    """
    Verifica se una stringa rappresenta un valore booleano.
    
    Args:
        sText: Stringa da verificare
        
    Returns:
        bool: True se la stringa è "True", "TRUE", "False" o "FALSE"
        
    Example:
        >>> isBool("True")
        True
        >>> isBool("FALSE")
        True
        >>> isBool("yes")
        False
    """
    sProc = "isBool"
    
    try:
        if sText is None:
            return False
            
        # Rimuovi spazi e converti in stringa
        sText = str(sText).strip()
        
        # Verifica valori booleani
        return sText in ["True", "TRUE", "False", "FALSE"]
        
    except Exception:
        return False


def isValidPassword(sText: str) -> bool:
    """
    Verifica se una stringa è una password valida.
    Caratteri permessi: Lettere, Numeri, "_", ".", "!"
    
    Args:
        sText: Stringa da verificare
        
    Returns:
        bool: True se contiene solo caratteri permessi, False altrimenti
        
    Example:
        >>> isValidPassword("Password123!")
        True
        >>> isValidPassword("Pass@word")
        False  # @ non permesso
    """
    sProc = "isValidPassword"
    
    try:
        if sText is None:
            return False
            
        # Espressione regolare: solo lettere, numeri, _, ., !
        pattern = r'^[A-Za-z0-9_\.!]+$'
        
        return bool(re.match(pattern, sText))
        
    except Exception:
        return False


def isLettersOnly(sText: str) -> bool:
    """
    Verifica se una stringa contiene solo lettere e spazi.
    
    Args:
        sText: Stringa da verificare
        
    Returns:
        bool: True se contiene solo lettere (maiuscole/minuscole) e spazi
        
    Example:
        >>> isLettersOnly("Solo Lettere")
        True
        >>> isLettersOnly("Con123 Numeri")
        False
    """
    sProc = "isLettersOnly"
    
    try:
        if sText is None:
            return False
            
        # Espressione regolare: solo lettere e spazi
        pattern = r'^[A-Za-z\s]+$'
        
        return bool(re.match(pattern, sText))
        
    except Exception:
        return False


def isEmail(sMail: str) -> bool:
    """
    Verifica se una stringa è un formato email valido.
    
    Args:
        sMail: Stringa da verificare
        
    Returns:
        bool: True se il formato è valido, False altrimenti
        
    Example:
        >>> isEmail("nome.cognome@gmail.com")
        True
        >>> isEmail("nome@gmail")
        False
    """
    sProc = "isEmail"
    
    try:
        if not sMail or not isinstance(sMail, str):
            return False
            
        # Espressione regolare base per email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        return bool(re.match(pattern, sMail))
        
    except Exception:
        return False


def StringToArray(sText: str, delimiter: str = ',') -> List[str]:
    """
    Converte una stringa in un array (lista) di stringhe.
    
    Args:
        sText: Stringa da convertire
        delimiter: Carattere delimitatore (default: ',')
        
    Returns:
        List[str]: Lista di stringhe pulite
        
    Example:
        >>> StringToArray("a,b,c")
        ['a', 'b', 'c']
        >>> StringToArray(" item1, item2 ,, item3 ")
        ['item1', 'item2', 'item3']
    """
    sProc = "StringToArray"
    
    try:
        if not sText:
            return []
            
        # Splitta la stringa
        parts = sText.split(delimiter)
        
        # Pulisci ogni elemento
        result = []
        for part in parts:
            cleaned = part.strip()
            if cleaned:  # Aggiungi solo se non vuoto dopo strip
                result.append(cleaned)
                
        return result
        
    except Exception:
        return []


def StringToNum(sText: str) -> Union[int, float]:
    """
    Converte una stringa in un numero (int o float).
    
    Args:
        sText: Stringa da convertire
        
    Returns:
        Union[int, float]: Numero convertito, 0 in caso di errore
        
    Example:
        >>> StringToNum("123")
        123
        >>> StringToNum("123.45")
        123.45
        >>> StringToNum("invalid")
        0
    """
    sProc = "StringToNum"
    
    try:
        if not sText:
            return 0
            
        # Rimuovi spazi
        sText = sText.strip()
        
        if not sText:
            return 0
            
        # Conta le virgole per determinare se è un float
        comma_count = sText.count(',')
        
        if comma_count == 0:
            # Nessuna virgola, prova come intero
            try:
                return int(sText)
            except ValueError:
                # Potrebbe essere float senza virgola
                try:
                    return float(sText)
                except ValueError:
                    return 0
                    
        elif comma_count == 1:
            # Una virgola, prova come float
            # Sostituisci virgola con punto per la conversione
            sText_float = sText.replace(',', '.')
            try:
                return float(sText_float)
            except ValueError:
                return 0
                
        else:
            # Più di una virgola, non valido
            return 0
            
    except Exception:
        return 0


# Test delle funzioni se eseguito direttamente
if __name__ == "__main__":
    print("Test aiSysStrings.py")
    print("=" * 50)
    
    # Test isBool
    print("1. Test isBool:")
    test_cases = ["True", "TRUE", "False", "FALSE", "true", "false", "Yes", "No", ""]
    for test in test_cases:
        print(f"   isBool('{test}') = {isBool(test)}")
    
    # Test isValidPassword
    print("\n2. Test isValidPassword:")
    passwords = [
        "Password123!",  # Valido
        "user_123.",     # Valido
        "test!test",     # Valido
        "pass@word",     # Non valido (@)
        "pass word",     # Non valido (spazio)
        "pass#word",     # Non valido (#)
    ]
    for pwd in passwords:
        print(f"   isValidPassword('{pwd}') = {isValidPassword(pwd)}")
    
    # Test isLettersOnly
    print("\n3. Test isLettersOnly:")
    texts = [
        "SoloLettere",
        "Solo Lettere e Spazi",
        "Con123Numeri",
        "Con punteggiatura.",
        "",
    ]
    for text in texts:
        print(f"   isLettersOnly('{text}') = {isLettersOnly(text)}")
    
    # Test isEmail
    print("\n4. Test isEmail:")
    emails = [
        "nome.cognome@gmail.com",
        "nome@gmail.com",
        "nome_cognome@libero.it",
        "nome@azienda.co.uk",
        "nome@",
        "@dominio.com",
        "nome@.com",
        "nome@dominio",
    ]
    for email in emails:
        print(f"   isEmail('{email}') = {isEmail(email)}")
    
    # Test StringToArray
    print("\n5. Test StringToArray:")
    test_strings = [
        ("a,b,c", ','),
        (" item1, item2 ,, item3 ", ','),
        ("", ','),
        ("single", ','),
        ("1|2|3", '|'),
        ("  a  ;  b  ;  c  ", ';'),
    ]
    for sText, delim in test_strings:
        result = StringToArray(sText, delim)
        print(f"   StringToArray('{sText}', '{delim}') = {result}")
    
    # Test StringToNum
    print("\n6. Test StringToNum:")
    numbers = [
        "123",
        "123.45",
        "123,45",
        "-123",
        "-123.45",
        "123,45,67",  # Troppe virgole
        "abc",
        "",
        "  456  ",
        "789,0",
    ]
    for num in numbers:
        result = StringToNum(num)
        type_name = "int" if isinstance(result, int) else "float"
        print(f"   StringToNum('{num}') = {result} ({type_name})")
    
    print("\nTest completati!")