import datetime
import re

def Timestamp(sPrefix: str = None) -> str:
    """
    Ritorna timestamp nel formato AAAAMMGG.HHMMSS.
    Se sPrefix è fornito: sprefix_AAAAMMGG.HHMMSS
    """
    now = datetime.datetime.now()
    sTs = now.strftime("%Y%m%d.%H%M%S")
    if sPrefix:
        return f"{sPrefix.lower()}_{sTs}"
    return sTs

def Expand(sText: str, dictConfig: dict) -> str:
    """
    Converte variabili $KEY in valori da dictConfig.
    Gestisce \$ come escape, e pulisce \\, \", \n alla fine.
    """
    if not isinstance(sText, str):
        return sText

    # 1. Gestione Escaping del simbolo $ (\$ -> $)
    # Usiamo un segnaposto temporaneo per i \$
    sResult = sText.replace(r"\$", "___ESCAPED_DOLLAR___")

    # 2. Espansione variabili $KEY (A-Z, 0-9, ., _)
    # Regex: cerca $ seguito da caratteri alfanumerici, punti o underscore
    def replace_var(match):
        key = match.group(1)
        return dictConfig.get(key, "UNKNOWN")

    sResult = re.sub(r"\$([a-zA-Z0-9._]+)", replace_var, sResult)

    # Ripristiniamo i $ che erano preceduti da \
    sResult = sResult.replace("___ESCAPED_DOLLAR___", "$")

    # 3. Pulizia sequenze escape finali
    sResult = sResult.replace(r"\\", "\\")
    sResult = sResult.replace(r'\"', '"')
    sResult = sResult.replace(r"\n", "\n")

    return sResult

def ExpandDict(dictExpand: dict, dictParam: dict):
    """
    Espande ricorsivamente i valori di un dizionario.
    """
    for key, xValue in dictExpand.items():
        if isinstance(xValue, str):
            dictExpand[key] = Expand(xValue, dictParam)
        elif isinstance(xValue, dict):
            # Richiamo ricorsivo corretto
            ExpandDict(xValue, dictParam)
    return dictExpand

def StringBoolean(sText: str) -> bool:
    """
    Ritorna True solo se 'TRUE', altrimenti sempre False.
    """
    if not sText:
        return False
    sClean = str(sText).strip().upper()
    return sClean == "TRUE"