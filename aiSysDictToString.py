"""Modulo per la conversione di dizionari in stringhe"""
from typing import Dict, Any, Optional, Union, List, Tuple
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from aiSysBase import ErrorProc

# Crea alias locale
loc_ErrorProc = ErrorProc


def DictPrint(dictParam: Dict, sFile: Optional[str] = None) -> str:
    """
    Visualizza un dizionario su schermo o su file.
    
    Args:
        dictParam: Dizionario da visualizzare
        sFile: File dove accodare (opzionale)
        
    Returns:
        str: sResult
    """
    sProc = "DictPrint"
    
    try:
        sResult = ""
        
        if not isinstance(dictParam, dict):
            dictParam = {}
        
        # Converte in stringa JSON
        sText = DictToString(dictParam, "json")
        
        # Stampa su schermo
        print(sText[1])  # sOutput è il secondo elemento della tupla
        
        # Scrivi su file se specificato
        if sFile:
            try:
                with open(sFile, 'a', encoding='utf-8') as f:
                    f.write(sText[1] + "\n")
            except Exception as e:
                sResult = f"Errore scrittura file {sFile}: {str(e)}"
                return loc_ErrorProc(sResult, sProc)
        
        return sResult
        
    except Exception as e:
        sResult = str(e) + f" {sFile if sFile else ''}"
        return loc_ErrorProc(sResult, sProc)


def DictToXml(dictParam: Dict, **xml_options) -> str:
    """
    Converte un dizionario in stringa XML.
    
    Args:
        dictParam: Dizionario da convertire
        **xml_options: Opzioni XML
        
    Returns:
        str: Stringa XML o vuota in caso di errore
    """
    sProc = "DictToXml"
    
    try:
        if not isinstance(dictParam, dict):
            dictParam = {}
        
        # Opzioni di default
        options = {
            'root_tag': 'root',
            'attr_prefix': '@',
            'text_key': '#text',
            'cdata_key': '#cdata',
            'item_name': 'item',
            'pretty': False,
            'type_convert': True
        }
        options.update(xml_options)
        
        # Funzione ricorsiva per convertire
        def dict_to_xml_element(tag, data):
            # Gestisci namespace
            if ':' in tag:
                ns, tag_name = tag.split(':', 1)
                element = ET.Element(f'{{{ns}}}{tag_name}')
            else:
                element = ET.Element(tag)
            
            # Se data è una stringa semplice
            if isinstance(data, (str, int, float, bool)):
                element.text = str(data)
                return element
            
            # Se data è un dizionario
            if isinstance(data, dict):
                # Separa attributi e elementi figli
                attrs = {}
                children = {}
                
                for key, value in data.items():
                    if key.startswith(options['attr_prefix']):
                        attr_name = key[len(options['attr_prefix']):]
                        element.set(attr_name, str(value))
                    elif key == options['text_key']:
                        element.text = str(value)
                    elif key == options['cdata_key']:
                        # CDATA section
                        cdata = minidom.CDATASection(str(value))
                        element.append(cdata)
                    elif key.startswith('xmlns:') or key == 'xmlns':
                        # Namespace
                        if ':' in key:
                            prefix = key.split(':', 1)[1]
                            ET.register_namespace(prefix, str(value))
                        element.set(key, str(value))
                    else:
                        children[key] = value
                
                # Processa elementi figli
                for key, value in children.items():
                    if isinstance(value, list):
                        # Array di elementi
                        for item in value:
                            child_element = dict_to_xml_element(key, item)
                            element.append(child_element)
                    else:
                        child_element = dict_to_xml_element(key, value)
                        element.append(child_element)
            
            # Se data è una lista
            elif isinstance(data, list):
                for item in data:
                    child_element = dict_to_xml_element(options['item_name'], item)
                    element.append(child_element)
            
            return element
        
        # Crea elemento radice
        root_element = dict_to_xml_element(options['root_tag'], dictParam)
        
        # Converti in stringa
        xml_string = ET.tostring(root_element, encoding='unicode')
        
        # Pretty print se richiesto
        if options['pretty']:
            parsed = minidom.parseString(xml_string)
            xml_string = parsed.toprettyxml(indent="  ")
        
        return xml_string
        
    except Exception as e:
        loc_ErrorProc(str(e), sProc)
        return ""


def DictToString(dictParam: Dict, sFormat: str = "json") -> Tuple[str, str]:
    """
    Converte un dizionario in stringa nei formati supportati.
    
    Args:
        dictParam: Dizionario da convertire
        sFormat: Formato ("json", "ini", "ini.sect")
        
    Returns:
        Tuple[str, str]: (sResult, sOutput)
    """
    sProc = "DictToString"
    
    try:
        sResult = ""
        sOutput = ""
        
        if not isinstance(dictParam, dict):
            dictParam = {}
        
        if sFormat == "json":
            try:
                # Converte in JSON con indentazione
                sOutput = json.dumps(dictParam, indent=2, ensure_ascii=True)
            except Exception as e:
                sResult = str(e)
                sOutput = ""
        
        elif sFormat == "ini":
            lines = []
            for key, value in dictParam.items():
                if isinstance(value, dict):
                    # Ignora dizionari annidati in formato "ini"
                    continue
                
                # Converte valore in stringa sicura
                str_value = _value_to_ini_string(value)
                
                # Rimuovi caratteri speciali dalla chiave
                safe_key = _make_ini_safe(key)
                
                lines.append(f"{safe_key}={str_value}")
            
            sOutput = "\n".join(lines)
        
        elif sFormat == "ini.sect":
            lines = []
            for key, value in dictParam.items():
                safe_key = _make_ini_safe(key)
                
                if isinstance(value, dict):
                    # Sezione
                    lines.append(f"[{safe_key}]")
                    for sub_key, sub_value in value.items():
                        safe_sub_key = _make_ini_safe(sub_key)
                        str_value = _value_to_ini_string(sub_value)
                        lines.append(f"{safe_sub_key}={str_value}")
                    lines.append("")  # Linea vuota tra sezioni
                else:
                    # Valore di primo livello
                    str_value = _value_to_ini_string(value)
                    lines.append(f"{safe_key}={str_value}")
            
            sOutput = "\n".join(lines).strip()
        
        else:
            sResult = f"Formato non supportato: {sFormat}"
        
        return (loc_ErrorProc(sResult, sProc), sOutput)
        
    except Exception as e:
        return (loc_ErrorProc(str(e), sProc), "")


def _make_ini_safe(s: str) -> str:
    """Rende una stringa sicura per formato INI."""
    if not s:
        return ""
    
    # Rimuovi caratteri speciali INI
    special_chars = ['[', ']', ';', '#', '\n', '=', '%']
    result = s
    for char in special_chars:
        result = result.replace(char, '_')
    
    # Converti caratteri non ASCII in underscore
    result = ''.join(c if ord(c) < 128 else '_' for c in result)
    
    return result


def _value_to_ini_string(value: Any) -> str:
    """Converte un valore in stringa sicura per INI."""
    if value is None:
        return ""
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        # Converte lista in stringa separata da virgole
        items = []
        for item in value:
            if isinstance(item, (str, int, float, bool)):
                items.append(str(item))
            else:
                items.append("")
        return ",".join(items)
    elif isinstance(value, str):
        # Rimuovi caratteri speciali e newline
        safe = value.replace('\n', ' ').replace('\r', ' ')
        special_chars = ['[', ']', ';', '#', '=', '%']
        for char in special_chars:
            safe = safe.replace(char, '_')
        # Converti caratteri non ASCII
        safe = ''.join(c if ord(c) < 128 else '_' for c in safe)
        return safe
    else:
        return ""


