import json
import re
import xml.sax.saxutils

class acDictToString:
    def __init__(self, bInit=True):
        """Inizializza la classe. Il parametro bInit è disponibile ma non utilizzato dai metodi."""
        self.bInit = bInit

    # =========================================================================
    # METODO DictToXml
    # =========================================================================
    def DictToXml(self, dictParam=None, **xml_options):
        """
        Converte un dizionario in stringa XML.
        
        Parametri:
            dictParam (dict, optional): Dizionario da convertire. Default {}.
            **xml_options: Opzioni per personalizzare l'output XML.
        
        Opzioni XML:
            root_tag="root": Nome elemento radice
            attr_prefix="@": Prefisso per identificare attributi
            text_key="#text": Chiave per contenuto testuale
            cdata_key="#cdata": Chiave per contenuto CDATA
            item_name="item": Nome per elementi di array
            pretty=False: Indentazione output
            type_convert=True: Converte automaticamente tipi
        
        Ritorna:
            str: Stringa XML o stringa vuota in caso di errore
        """
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
        
        # Validazione input
        if dictParam is None or not isinstance(dictParam, dict):
            dictParam = {}
        
        try:
            # Funzione ricorsiva per convertire il dizionario in XML
            def dict_to_xml_str(tag, data, level=0):
                indent = '  ' * level if options['pretty'] else ''
                newline = '\n' if options['pretty'] else ''
                
                # Se data è una lista, processa ogni elemento
                if isinstance(data, list):
                    items = []
                    for item in data:
                        items.append(dict_to_xml_str(options['item_name'], item, level))
                    return f'{newline}'.join(items)
                
                # Se data non è un dizionario, convertilo in stringa
                if not isinstance(data, dict):
                    value = self._convert_value(data, options['type_convert'])
                    return f'{indent}<{tag}>{self._escape_xml(value)}</{tag}>{newline}'
                
                # Preparazione attributi, namespace e elementi
                attrs = {}
                ns_decls = {}
                elements = {}
                text_content = None
                cdata_content = None
                
                # Separazione chiavi in categorie
                for key, value in data.items():
                    # Gestione attributi
                    if key.startswith(options['attr_prefix']):
                        attr_name = key[len(options['attr_prefix']):]
                        attrs[attr_name] = self._convert_value(value, options['type_convert'])
                    
                    # Gestione namespace
                    elif key.startswith('xmlns:') or key in ['xmlns', 'xsi:', 'xml:']:
                        ns_decls[key] = self._convert_value(value, options['type_convert'])
                    
                    # Gestione testo
                    elif key == options['text_key']:
                        text_content = self._convert_value(value, options['type_convert'])
                    
                    # Gestione CDATA
                    elif key == options['cdata_key']:
                        cdata_content = self._convert_value(value, options['type_convert'])
                    
                    # Elementi normali
                    else:
                        elements[key] = value
                
                # Costruzione stringa attributi
                attr_str = ''
                all_attrs = {**ns_decls, **attrs}
                for a_key, a_value in all_attrs.items():
                    if a_value is not None:
                        attr_str += f' {a_key}="{self._escape_attr(str(a_value))}"'
                
                # Gestione elementi vuoti con attributi
                if not elements and text_content is None and cdata_content is None:
                    if all_attrs:
                        return f'{indent}<{tag}{attr_str}/>{newline}'
                    else:
                        return f'{indent}<{tag}/>{newline}'
                
                # Apertura tag
                result = f'{indent}<{tag}{attr_str}>'
                
                # Gestione contenuto testuale/CDATA
                if cdata_content is not None:
                    result += f'<![CDATA[{cdata_content}]]>'
                elif text_content is not None:
                    result += self._escape_xml(str(text_content))
                
                # Gestione elementi figli
                if elements:
                    if text_content is None and cdata_content is None:
                        result += newline
                    
                    for elem_key, elem_value in elements.items():
                        result += dict_to_xml_str(elem_key, elem_value, level + 1)
                    
                    if text_content is None and cdata_content is None:
                        result += indent
                
                # Chiusura tag
                result += f'</{tag}>{newline}'
                
                return result
            
            # Costruzione XML finale
            xml_content = dict_to_xml_str(options['root_tag'], dictParam)
            
            # Aggiunta dichiarazione XML
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
            if options['pretty']:
                return f'{xml_declaration}\n{xml_content}'
            else:
                return f'{xml_declaration}{xml_content}'
            
        except Exception:
            # In caso di qualsiasi errore, ritorna stringa vuota
            return ""

    def _convert_value(self, value, type_convert=True):
        """Converte valori in formato appropriato."""
        if value is None:
            return ""
        
        if not type_convert:
            return str(value)
        
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)

    def _escape_xml(self, text):
        """Escape caratteri speciali XML per contenuto testuale."""
        return xml.sax.saxutils.escape(text)

    def _escape_attr(self, text):
        """Escape caratteri speciali XML per attributi."""
        escaped = xml.sax.saxutils.escape(text)
        # Escape aggiuntivo per le virgolette
        escaped = escaped.replace('"', '&quot;')
        return escaped

    # =========================================================================
    # METODO DictToString
    # =========================================================================
    def DictToString(self, dictParam=None, sFormat="json"):
        """
        Converte un dizionario in stringa formattata.
        
        Parametri:
            dictParam (dict, optional): Dizionario da convertire. Default {}.
            sFormat (str): Formato di output. Valori: "json", "ini", "ini.sect"
        
        Ritorna:
            str: Stringa formattata o stringa vuota in caso di errore
        """
        # Validazione input
        if dictParam is None or not isinstance(dictParam, dict):
            dictParam = {}
        
        sResult = ""
        
        try:
            if sFormat == "json":
                # Conversione JSON
                sResult = json.dumps(dictParam, indent=2, ensure_ascii=True, default=str)
            
            elif sFormat == "ini":
                # Formato INI base (solo primo livello)
                lines = []
                for key, value in dictParam.items():
                    if isinstance(value, dict):
                        continue  # Ignora dizionari annidati
                    
                    str_key = self._safe_key(key)
                    str_value = self._format_ini_value(value)
                    
                    if str_value is not None:
                        lines.append(f"{str_key}={str_value}")
                
                sResult = "\n".join(lines)
            
            elif sFormat == "ini.sect":
                # Formato INI con sezioni (massimo 2 livelli)
                lines = []
                
                # Prima sezione vuota per elementi di primo livello non-dizionario
                top_level_items = []
                for key, value in dictParam.items():
                    if not isinstance(value, dict):
                        str_key = self._safe_key(key)
                        str_value = self._format_ini_value(value)
                        
                        if str_value is not None:
                            top_level_items.append(f"{str_key}={str_value}")
                
                if top_level_items:
                    lines.extend(top_level_items)
                
                # Sezioni per dizionari di secondo livello
                for key, value in dictParam.items():
                    if isinstance(value, dict):
                        section_name = self._safe_key(key)
                        lines.append(f"\n[{section_name}]")
                        
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, dict):
                                continue  # Ignora livelli più profondi
                            
                            str_key = self._safe_key(sub_key)
                            str_value = self._format_ini_value(sub_value)
                            
                            if str_value is not None:
                                lines.append(f"{str_key}={str_value}")
                
                sResult = "\n".join(lines).lstrip()
            
            else:
                # Formato non supportato
                sResult = ""
        
        except Exception:
            sResult = ""
        
        return sResult

    def _safe_key(self, key):
        """Rende una chiave sicura per formato INI."""
        # Converti in stringa
        str_key = str(key)
        
        # Sostituisci caratteri non ASCII con _
        str_key = re.sub(r'[^\x00-\x7F]+', '_', str_key)
        
        # Rimuovi caratteri speciali INI
        special_chars = r'\[\];#\n='
        str_key = re.sub(f'[{re.escape(special_chars)}]', '', str_key)
        
        return str_key

    def _format_ini_value(self, value):
        """Formatta un valore per formato INI."""
        if value is None:
            return ""
        
        # Gestione booleani
        if isinstance(value, bool):
            return "true" if value else "false"
        
        # Gestione numeri
        if isinstance(value, (int, float)):
            return str(value)
        
        # Gestione liste
        if isinstance(value, list):
            valid_items = []
            for item in value:
                if isinstance(item, (bool, str, int, float)):
                    valid_items.append(str(item))
            
            if valid_items:
                return ",".join(valid_items)
            else:
                return ""
        
        # Gestione stringhe
        if isinstance(value, str):
            # Sostituisci caratteri non ASCII con _
            safe_value = re.sub(r'[^\x00-\x7F]+', '_', value)
            # Rimuovi caratteri speciali INI (mantenendo il contenuto)
            safe_value = safe_value.replace('\n', ' ').replace('\r', ' ')
            return safe_value
        
        # Altri tipi: ignorati
        return None


# =============================================================================
# ESEMPI D'USO
# =============================================================================
if __name__ == "__main__":
    # Creazione istanza della classe
    converter = acDictToString(bInit=True)
    
    print("=" * 60)
    print("ESEMPI DictToXml")
    print("=" * 60)
    
    # Esempio 1: XML base
    data1 = {"user": {"@id": "1", "name": "Mario", "age": 30}}
    xml1 = converter.DictToXml(data1, root_tag="root")
    print("Esempio 1 - XML base:")
    print(xml1)
    print()
    
    # Esempio 2: XML con array
    data2 = {"users": {"user": [{"name": "Mario"}, {"name": "Luigi"}]}}
    xml2 = converter.DictToXml(data2, pretty=True)
    print("Esempio 2 - XML con array (pretty):")
    print(xml2)
    print()
    
    # Esempio 3: XML con attributi e testo
    data3 = {"book": {"@id": "101", "#text": "Il contenuto del libro", "author": "Autore"}}
    xml3 = converter.DictToXml(data3)
    print("Esempio 3 - XML con attributi e testo:")
    print(xml3)
    print()
    
    # Esempio 4: XML con CDATA
    data4 = {"script": {"#cdata": "<script>alert('test')</script>"}}
    xml4 = converter.DictToXml(data4)
    print("Esempio 4 - XML con CDATA:")
    print(xml4)
    print()
    
    # Esempio 5: XML con namespace
    data5 = {"root": {"xmlns": "http://example.com", "item": "test"}}
    xml5 = converter.DictToXml(data5)
    print("Esempio 5 - XML con namespace:")
    print(xml5)
    print()
    
    print("=" * 60)
    print("ESEMPI DictToString")
    print("=" * 60)
    
    # Esempio 6: JSON
    json_data = {"nome": "Mario", "età": 30, "attivo": True, "figli": None}
    json_str = converter.DictToString(json_data, "json")
    print("Esempio 6 - JSON:")
    print(json_str)
    print()
    
    # Esempio 7: INI base
    ini_data = {"nome": "Mario", "età": 30, "città": "Roma", "config": {"debug": True}}
    ini_str = converter.DictToString(ini_data, "ini")
    print("Esempio 7 - INI base:")
    print(ini_str)
    print()
    
    # Esempio 8: INI con sezioni
    ini_sect_data = {
        "nome": "Mario",
        "database": {"host": "localhost", "port": 5432},
        "server": {"ip": "192.168.1.1", "enabled": True}
    }
    ini_sect_str = converter.DictToString(ini_sect_data, "ini.sect")
    print("Esempio 8 - INI con sezioni:")
    print(ini_sect_str)
    print()
    
    # Esempio 9: Gestione caratteri speciali
    special_data = {"nome": "Mario[Rossi]", "età": 30, "note": "test; #commento"}
    special_str = converter.DictToString(special_data, "ini")
    print("Esempio 9 - INI con caratteri speciali:")
    print(special_str)
    print()
    
    # Esempio 10: Gestione array
    array_data = {"tags": ["python", "xml", "json"], "numeri": [1, 2, 3]}
    array_str = converter.DictToString(array_data, "ini")
    print("Esempio 10 - INI con array:")
    print(array_str)
    print()
    
    print("=" * 60)
    print("TEST ERRORI")
    print("=" * 60)
    
    # Test con input non valido
    invalid_xml = converter.DictToXml("non un dizionario")
    print("XML da input non dizionario:", '"' + invalid_xml + '"')
    
    invalid_json = converter.DictToString([1, 2, 3], "json")
    print("JSON da input non dizionario:", '"' + invalid_json + '"')