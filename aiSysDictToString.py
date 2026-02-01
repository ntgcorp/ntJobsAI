"""
aiSysDictToString.py - Funzioni per convertire dizionari in stringhe
"""

import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, Any, Tuple
import html

def loc_aiErrorProc(sResult: str, sProc: str) -> str:
    """
    Funzione locale per la gestione errori.
    
    Args:
        sResult: Stringa errore
        sProc: Nome della procedura
    
    Returns:
        str: Stringa formattata o vuota
    """
    if sResult != "":
        return f"{sProc}: Errore {sResult}"
    return ""


def DictPrint(dictParam: Dict[str, Any], sFile: str = "") -> str:
    """
    Visualizza un dizionario su schermo o su file in accodamento.
    
    Args:
        dictParam: Dizionario da visualizzare
        sFile: File dove accodare (opzionale)
    
    Returns:
        str: Stringa vuota se successo, errore formattato altrimenti
    """
    sProc = "DictPrint"
    
    try:
        if not isinstance(dictParam, dict):
            dictParam = {}
        
        sResult, sText = DictToString(dictParam, "json")
        
        if sResult:
            error_msg = sResult + " " + sFile if sFile else sResult
            return loc_aiErrorProc(error_msg, sProc)
        
        print(sText)
        
        if sFile:
            try:
                with open(sFile, 'a', encoding='utf-8') as f:
                    f.write(sText + '\n')
            except Exception as e:
                sResult = str(e) + " " + sFile
                return loc_aiErrorProc(sResult, sProc)
        
        return ""
        
    except Exception as e:
        sResult = str(e) + " " + sFile if sFile else str(e)
        return loc_aiErrorProc(sResult, sProc)


def DictToXml(dictParam: Dict[str, Any], **xml_options) -> str:
    """
    Converte un dizionario in stringa XML.
    
    Args:
        dictParam: Dizionario da convertire
        **xml_options: Opzioni XML
    
    Returns:
        str: Stringa XML o stringa vuota in caso di errore
    """
    sProc = "DictToXml"
    
    try:
        if not isinstance(dictParam, dict):
            dictParam = {}
        
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
        
        def dict_to_xml_element(tag: str, data: Any) -> ET.Element:
            element = ET.Element(tag)
            
            if isinstance(data, dict):
                attrs = {}
                child_data = {}
                
                for key, value in data.items():
                    if key.startswith(options['attr_prefix']):
                        attr_name = key[len(options['attr_prefix']):]
                        attrs[attr_name] = str(value)
                    elif key == options['text_key']:
                        element.text = str(value)
                    elif key == options['cdata_key']:
                        element.text = str(value)
                    else:
                        child_data[key] = value
                
                for attr_name, attr_value in attrs.items():
                    element.set(attr_name, attr_value)
                
                for key, value in child_data.items():
                    if isinstance(value, list):
                        for item in value:
                            element.append(dict_to_xml_element(key, item))
                    else:
                        element.append(dict_to_xml_element(key, value))
                        
            elif isinstance(data, list):
                for item in data:
                    element.append(dict_to_xml_element(options['item_name'], item))
            else:
                element.text = str(data)
            
            return element
        
        root = dict_to_xml_element(options['root_tag'], dictParam)
        
        if options['pretty']:
            from xml.dom import minidom
            rough_string = ET.tostring(root, encoding='unicode')
            parsed = minidom.parseString(rough_string)
            sXML = parsed.toprettyxml(indent="  ")
        else:
            sXML = ET.tostring(root, encoding='unicode')
        
        return sXML
        
    except Exception:
        return ""


def DictToString(dictParam: Dict[str, Any], sFormat: str = "json") -> Tuple[str, str]:
    """
    Converte un dizionario in stringa (JSON, INI, INI con sezioni).
    
    Args:
        dictParam: Dizionario da convertire
        sFormat: Formato di output ("json", "ini", "ini.sect")
    
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
                sOutput = json.dumps(dictParam, indent=2, ensure_ascii=True, default=str)
            except Exception as e:
                sResult = str(e)
                sOutput = ""
        
        elif sFormat == "ini":
            try:
                lines = []
                for key, value in dictParam.items():
                    if isinstance(value, dict):
                        continue
                    
                    str_value = ""
                    if value is None:
                        str_value = ""
                    elif isinstance(value, bool):
                        str_value = "true" if value else "false"
                    elif isinstance(value, (int, float)):
                        str_value = str(value)
                    elif isinstance(value, str):
                        str_value = value
                    elif isinstance(value, list):
                        str_items = []
                        for item in value:
                            if isinstance(item, (str, int, float, bool)):
                                str_items.append(str(item))
                        str_value = ",".join(str_items)
                    else:
                        continue
                    
                    safe_key = re.sub(r'[\[\];#=\n]', '_', key)
                    safe_value = re.sub(r'[\[\];#=\n]', '_', str_value)
                    
                    safe_key = re.sub(r'[^\x00-\x7F]', '_', safe_key)
                    safe_value = re.sub(r'[^\x00-\x7F]', '_', safe_value)
                    
                    lines.append(f"{safe_key}={safe_value}")
                
                sOutput = "\n".join(lines)
            except Exception as e:
                sResult = str(e)
                sOutput = ""
        
        elif sFormat == "ini.sect":
            try:
                lines = []
                for key, value in dictParam.items():
                    if isinstance(value, dict):
                        lines.append(f"[{key}]")
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, dict):
                                continue
                            
                            str_value = ""
                            if subvalue is None:
                                str_value = ""
                            elif isinstance(subvalue, bool):
                                str_value = "true" if subvalue else "false"
                            elif isinstance(subvalue, (int, float)):
                                str_value = str(subvalue)
                            elif isinstance(subvalue, str):
                                str_value = subvalue
                            elif isinstance(subvalue, list):
                                str_items = []
                                for item in subvalue:
                                    if isinstance(item, (str, int, float, bool)):
                                        str_items.append(str(item))
                                str_value = ",".join(str_items)
                            else:
                                continue
                            
                            safe_key = re.sub(r'[\[\];#=\n]', '_', subkey)
                            safe_value = re.sub(r'[\[\];#=\n]', '_', str_value)
                            
                            safe_key = re.sub(r'[^\x00-\x7F]', '_', safe_key)
                            safe_value = re.sub(r'[^\x00-\x7F]', '_', safe_value)
                            
                            lines.append(f"{safe_key}={safe_value}")
                        lines.append("")
                    else:
                        lines.append(f"{key}={value}")
                
                sOutput = "\n".join(lines).strip()
            except Exception as e:
                sResult = str(e)
                sOutput = ""
        
        else:
            sResult = f"Formato non supportato: {sFormat}"
            sOutput = ""
        
        return (loc_aiErrorProc(sResult, sProc), sOutput)
        
    except Exception as e:
        return (loc_aiErrorProc(str(e), sProc), "")


