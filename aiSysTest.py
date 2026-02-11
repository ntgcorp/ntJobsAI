
"""Test per tutte le funzioni aiSys"""
import os
import sys
import tempfile
import shutil
from typing import Dict, Any, List, Tuple

# Importa il modulo aiSys
import aiSys


def run_tests() -> None:
    """Esegue tutti i test"""
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    print("=" * 60)
    print("INIZIO TEST MODULO aiSys")
    print("=" * 60)
    
    # Test 1: aiSysBase
    total_tests += 1
    if test_aiSysBase():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysBase.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysBase.py")
    
    # Test 2: aiSysTimestamp
    total_tests += 1
    if test_aiSysTimestamp():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysTimestamp.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysTimestamp.py")
    
    # Test 3: aiSysConfig (Expand e ExpandDict)
    total_tests += 1
    if test_aiSysConfig():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysConfig.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysConfig.py")
    
    # Test 4: aiSysFileio
    total_tests += 1
    if test_aiSysFileio():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysFileio.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysFileio.py")
    
    # Test 5: aiSysStrings
    total_tests += 1
    if test_aiSysStrings():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysStrings.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysStrings.py")
    
    # Test 6: aiSysDictToString
    total_tests += 1
    if test_aiSysDictToString():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysDictToString.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysDictToString.py")
    
    # Test 7: aiSysLog (acLog)
    total_tests += 1
    if test_aiSysLog():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: aiSysLog.py")
    else:
        failed_tests.append(f"Test {total_tests}: aiSysLog.py")
    
    # Test 8: Integrazione
    total_tests += 1
    if test_integration():
        passed_tests += 1
        print(f"✓ Test {total_tests} passato: Integrazione")
    else:
        failed_tests.append(f"Test {total_tests}: Integrazione")
    
    # Riepilogo
    print("\n" + "=" * 60)
    print("RIEPILOGO TEST")
    print("=" * 60)
    print(f"Test totali: {total_tests}")
    print(f"Test passati: {passed_tests}")
    print(f"Test falliti: {total_tests - passed_tests}")
    
    if failed_tests:
        print("\nTest falliti in dettaglio:")
        for failed in failed_tests:
            print(f"  - {failed}")
    
    print("=" * 60)


def test_aiSysBase() -> bool:
    """Test per aiSysBase.py"""
    print("\n" + "=" * 60)
    print("Test 1: File aiSysBase.py, NomeTest: Funzioni base")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    try:
        # Test 1.1: ErrorProc
        print(f"\nTest {test_num}.1: ErrorProc")
        print(f"  Input: sResult='Errore test', sProc='TestFunction'")
        result = aiSys.ErrorProc("Errore test", "TestFunction")
        print(f"  Output: {result}")
        assert ": Errore Errore test" in result, "Formato errore errato"
        test_num += 1
        
        # Test 1.2: ErrorProc con stringa vuota
        print(f"\nTest {test_num}.1: ErrorProc con stringa vuota")
        print(f"  Input: sResult='', sProc='TestFunction'")
        result = aiSys.ErrorProc("", "TestFunction")
        print(f"  Output: {result}")
        assert result == "", "Dovrebbe ritornare stringa vuota"
        test_num += 1
        
        # Test 1.3: DictMerge
        print(f"\nTest {test_num}.1: DictMerge")
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        print(f"  Input: dictSource={dict1}, dictAdd={dict2}")
        aiSys.DictMerge(dict1, dict2)
        print(f"  Output: {dict1}")
        assert dict1 == {"a": 1, "b": 3, "c": 4}, "Merge non corretto"
        test_num += 1
        
        # Test 1.4: DictExist
        print(f"\nTest {test_num}.1: DictExist")
        test_dict = {"key1": "value1", "key2": 123}
        print(f"  Input: dictParam={test_dict}, sKey='key1', xDefault='default'")
        result = aiSys.DictExist(test_dict, "key1", "default")
        print(f"  Output: {result}")
        assert result == "value1", "Valore chiave errato"
        
        print(f"\nTest {test_num}.2: DictExist chiave inesistente")
        print(f"  Input: dictParam={test_dict}, sKey='key3', xDefault='default'")
        result = aiSys.DictExist(test_dict, "key3", "default")
        print(f"  Output: {result}")
        assert result == "default", "Default non restituito"
        test_num += 1
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    
    return test_passed


def test_aiSysTimestamp() -> bool:
    """Test per aiSysTimestamp.py"""
    print("\n" + "=" * 60)
    print("Test 2: File aiSysTimestamp.py, NomeTest: Funzioni timestamp")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    try:
        # Test 2.1: Timestamp base
        print(f"\nTest {test_num}.1: Timestamp()")
        result = aiSys.Timestamp()
        print(f"  Output: {result}")
        assert len(result) == 15, "Lunghezza timestamp errata"
        assert ":" in result, "Formato timestamp errato"
        test_num += 1
        
        # Test 2.2: Timestamp con postfix
        print(f"\nTest {test_num}.1: Timestamp con postfix")
        result = aiSys.Timestamp("Test")
        print(f"  Output: {result}")
        assert result.endswith(":test"), "Postfix non aggiunto correttamente"
        test_num += 1
        
        # Test 2.3: TimestampValidate
        print(f"\nTest {test_num}.1: TimestampValidate valido")
        valid_ts = "20240125:143055"
        print(f"  Input: {valid_ts}")
        result = aiSys.TimestampValidate(valid_ts)
        print(f"  Output: {result}")
        assert result == True, "Timestamp valido non riconosciuto"
        
        print(f"\nTest {test_num}.2: TimestampValidate non valido")
        invalid_ts = "20240125:1430"
        print(f"  Input: {invalid_ts}")
        result = aiSys.TimestampValidate(invalid_ts)
        print(f"  Output: {result}")
        assert result == False, "Timestamp non valido riconosciuto come valido"
        test_num += 1
        
        # Test 2.4: TimestampConvert e TimestampFromSeconds (ciclo completo)
        print(f"\nTest {test_num}.1: Ciclo Timestamp ↔ Secondi")
        ts1 = aiSys.Timestamp()
        print(f"  Timestamp originale: {ts1}")
        seconds = aiSys.TimestampConvert(ts1, "s")
        print(f"  Convertito in secondi: {seconds}")
        ts2 = aiSys.TimestampFromSeconds(seconds)
        print(f"  Ricostruito: {ts2}")
        
        # Estrai parte timestamp (senza eventuale postfix)
        ts1_base = ts1.split(':')[0] + ':' + ts1.split(':')[1] if ':' in ts1 else ts1
        assert ts1_base == ts2, "Ciclo conversione non funziona"
        test_num += 1
        
        # Test 2.5: TimestampDiff
        print(f"\nTest {test_num}.1: TimestampDiff")
        ts1 = "20240125:120000"
        ts2 = "20240125:120100"
        print(f"  Input: {ts1}, {ts2}, sMode='s'")
        diff = aiSys.TimestampDiff(ts1, ts2, "s")
        print(f"  Output: {diff}")
        assert diff == 60, "Differenza in secondi errata"
        test_num += 1
        
        # Test 2.6: TimestampAdd
        print(f"\nTest {test_num}.1: TimestampAdd")
        ts = "20240125:120000"
        print(f"  Input: {ts}, nValue=60, sUnit='s'")
        result = aiSys.TimestampAdd(ts, 60, "s")
        print(f"  Output: {result}")
        assert result == "20240125:120100", "Aggiunta secondi errata"
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    
    return test_passed


def test_aiSysConfig() -> bool:
    """Test per aiSysConfig.py (con focus su Expand e ExpandDict)"""
    print("\n" + "=" * 60)
    print("Test 3: File aiSysConfig.py, NomeTest: Expand e ExpandDict")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    try:
        # Test 3.1: Expand - sequenze di escape
        print(f"\nTest {test_num}.1: Expand sequenze di escape")
        dictConfig = {"USER": "Mario"}
        test_str = "Ciao %% USER %n Test%#citazione%# %$dollaro %\\backslash"
        print(f"  Input: sText='{test_str}', dictConfig={dictConfig}")
        result = aiSys.Expand(test_str, dictConfig)
        print(f"  Output: {repr(result)}")
        assert "%" not in result or "%%" not in result, "Escape % non gestito"
        assert "\n" in result, "Escape %n non gestito"
        test_num += 1
        
        # Test 3.2: Expand - variabili
        print(f"\nTest {test_num}.1: Expand variabili")
        dictConfig = {"USER": "Mario", "LIVELLO": "admin"}
        test_str = "Ciao $USER, livello: $LIVELLO"
        print(f"  Input: sText='{test_str}', dictConfig={dictConfig}")
        result = aiSys.Expand(test_str, dictConfig)
        print(f"  Output: {result}")
        assert "Mario" in result, "Variabile USER non espansa"
        assert "admin" in result, "Variabile LIVELLO non espansa"
        
        print(f"\nTest {test_num}.2: Expand variabile inesistente")
        test_str = "Ciao $UTENTE_SCONOSCIUTO"
        print(f"  Input: sText='{test_str}', dictConfig={dictConfig}")
        result = aiSys.Expand(test_str, dictConfig)
        print(f"  Output: {result}")
        assert "UNKNOWN" in result, "Variabile inesistente non gestita"
        test_num += 1
        
        # Test 3.3: ExpandConvert (inversa)
        print(f"\nTest {test_num}.1: ExpandConvert")
        test_str = 'Test "citazione"\nNuova riga $variabile\\escape'
        print(f"  Input: '{test_str}'")
        converted = aiSys.ExpandConvert(test_str)
        print(f"  Convertito: {repr(converted)}")
        # Test ciclo completo
        dictConfig = {"variabile": "valore"}
        expanded = aiSys.Expand(converted, dictConfig)
        print(f"  Riconvertito: {repr(expanded)}")
        assert 'citazione' in expanded, "Ciclo conversione non funziona"
        test_num += 1
        
        # Test 3.4: ExpandDict
        print(f"\nTest {test_num}.1: ExpandDict")
        dictExpand = {
            "msg1": "Ciao $USER",
            "msg2": "Test%n nuova riga",
            "nested": {
                "msg3": "Variabile $LEVEL"
            }
        }
        dictParam = {"USER": "Mario", "LEVEL": "alto"}
        print(f"  Input: dictExpand={dictExpand}, dictParam={dictParam}")
        result = aiSys.ExpandDict(dictExpand, dictParam)
        print(f"  Output: {result}")
        assert "Mario" in result["msg1"], "Variabile non espansa nel dizionario"
        assert "\n" in result["msg2"], "Escape non espanso nel dizionario"
        assert "alto" in result["nested"]["msg3"], "Nested dict non espanso"
        test_num += 1
        
        # Test 3.5: Config e ConfigDefault
        print(f"\nTest {test_num}.1: Config e ConfigDefault")
        config_dict = {"key1": "value1", "key2": ""}
        print(f"  Dict iniziale: {config_dict}")
        
        # ConfigDefault con chiave vuota
        aiSys.ConfigDefault("key2", "default2", config_dict)
        print(f"  Dopo ConfigDefault key2: {config_dict}")
        assert config_dict["key2"] == "default2", "ConfigDefault non ha impostato valore vuoto"
        
        # ConfigDefault con chiave inesistente
        aiSys.ConfigDefault("key3", "value3", config_dict)
        print(f"  Dopo ConfigDefault key3: {config_dict}")
        assert config_dict["key3"] == "value3", "ConfigDefault non ha aggiunto chiave"
        
        # Config lettura
        value = aiSys.Config(config_dict, "key1")
        print(f"  Config read key1: {value}")
        assert value == "value1", "Config non legge correttamente"
        test_num += 1
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    
    return test_passed


def test_aiSysFileio() -> bool:
    """Test per aiSysFileio.py"""
    print("\n" + "=" * 60)
    print("Test 4: File aiSysFileio.py, NomeTest: Operazioni file")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    # Crea file temporanei
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test 4.1: save_array_file e read_array_file
        print(f"\nTest {test_num}.1: save_array_file e read_array_file")
        test_file = os.path.join(temp_dir, "test_array.txt")
        test_lines = ["Linea 1", "Linea 2", "Linea 3"]
        print(f"  Input: sFile='{test_file}', asLines={test_lines}")
        
        # Salva
        result_save = aiSys.save_array_file(test_file, test_lines)
        print(f"  save_array_file risultato: {result_save}")
        assert result_save == "", f"Errore salvataggio: {result_save}"
        
        # Leggi
        result_read, lines_read = aiSys.read_array_file(test_file)
        print(f"  read_array_file risultato: {result_read}, lines: {lines_read}")
        assert result_read == "", f"Errore lettura: {result_read}"
        assert lines_read == test_lines, "Linee lette non corrispondono"
        test_num += 1
        
        # Test 4.2: save_dict_to_ini e read_ini_to_dict
        print(f"\nTest {test_num}.1: save_dict_to_ini e read_ini_to_dict")
        ini_file = os.path.join(temp_dir, "test.ini")
        test_dict = {
            "sezione1": {"chiave1": "valore1", "chiave2": "valore2"},
            "sezione2": {"chiaveA": "valoreA"}
        }
        print(f"  Input: data_dict={test_dict}, ini_file_path='{ini_file}'")
        
        # Salva INI
        result_save = aiSys.save_dict_to_ini(test_dict, ini_file)
        print(f"  save_dict_to_ini risultato: {result_save}")
        assert result_save == "", f"Errore salvataggio INI: {result_save}"
        
        # Leggi INI
        result_read, dict_read = aiSys.read_ini_to_dict(ini_file)
        print(f"  read_ini_to_dict risultato: {result_read}")
        print(f"  Dict letto: {dict_read}")
        assert result_read == "", f"Errore lettura INI: {result_read}"
        assert dict_read == test_dict, "Dizionario letto non corrisponde"
        test_num += 1
        
        # Test 4.3: isValidPath e isFilename
        print(f"\nTest {test_num}.1: isValidPath")
        print(f"  Input: sPath='{temp_dir}'")
        result = aiSys.isValidPath(temp_dir)
        print(f"  Output: {result}")
        assert result == True, "Percorso valido non riconosciuto"
        
        print(f"\nTest {test_num}.2: isFilename valido")
        print(f"  Input: sFilename='test_file.txt'")
        result = aiSys.isFilename("test_file.txt")
        print(f"  Output: {result}")
        assert result == True, "Filename valido non riconosciuto"
        
        print(f"\nTest {test_num}.3: isFilename non valido")
        print(f"  Input: sFilename='file\\con\\path.txt'")
        result = aiSys.isFilename("file\\con\\path.txt")
        print(f"  Output: {result}")
        assert result == False, "Filename non valido riconosciuto"
        test_num += 1
        
        # Test 4.4: PathMake
        print(f"\nTest {test_num}.1: PathMake")
        print(f"  Input: sPath='{temp_dir}', sFile='test', sExt='txt'")
        result = aiSys.PathMake(temp_dir, "test", "txt")
        print(f"  Output: {result}")
        expected = os.path.join(temp_dir, "test.txt")
        assert result == expected, f"PathMake errato: atteso {expected}, ottenuto {result}"
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    finally:
        # Pulizia
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return test_passed


def test_aiSysStrings() -> bool:
    """Test per aiSysStrings.py"""
    print("\n" + "=" * 60)
    print("Test 5: File aiSysStrings.py, NomeTest: Operazioni stringhe")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    try:
        # Test 5.1: StringAppend
        print(f"\nTest {test_num}.1: StringAppend")
        print(f"  Input: sSource='prima', sAppend='seconda', sDelimiter=','")
        result = aiSys.StringAppend("prima", "seconda", ",")
        print(f"  Output: {result}")
        assert result == "prima,seconda", "StringAppend errato"
        test_num += 1
        
        # Test 5.2: StringBool
        print(f"\nTest {test_num}.1: StringBool true")
        print(f"  Input: sText='true'")
        result = aiSys.StringBool("true")
        print(f"  Output: {result}")
        assert result == True, "'true' non riconosciuto"
        
        print(f"\nTest {test_num}.2: StringBool false")
        print(f"  Input: sText='false'")
        result = aiSys.StringBool("false")
        print(f"  Output: {result}")
        assert result == False, "'false' non riconosciuto come false"
        test_num += 1
        
        # Test 5.3: isValidPassword
        print(f"\nTest {test_num}.1: isValidPassword valida")
        print(f"  Input: sText='Pass123_.!'")
        result = aiSys.isValidPassword("Pass123_.!")
        print(f"  Output: {result}")
        assert result == True, "Password valida non riconosciuta"
        
        print(f"\nTest {test_num}.2: isValidPassword non valida")
        print(f"  Input: sText='Pass@123'")
        result = aiSys.isValidPassword("Pass@123")
        print(f"  Output: {result}")
        assert result == False, "Password non valida riconosciuta"
        test_num += 1
        
        # Test 5.4: isEmail
        print(f"\nTest {test_num}.1: isEmail valida")
        print(f"  Input: sMail='nome.cognome@gmail.com'")
        result = aiSys.isEmail("nome.cognome@gmail.com")
        print(f"  Output: {result}")
        assert result == True, "Email valida non riconosciuta"
        
        print(f"\nTest {test_num}.2: isEmail non valida")
        print(f"  Input: sMail='nome@'")
        result = aiSys.isEmail("nome@")
        print(f"  Output: {result}")
        assert result == False, "Email non valida riconosciuta"
        test_num += 1
        
        # Test 5.5: StringToArray
        print(f"\nTest {test_num}.1: StringToArray")
        print(f"  Input: sText='a,b,c', delimiter=','")
        result = aiSys.StringToArray("a,b,c", ",")
        print(f"  Output: {result}")
        assert result == ["a", "b", "c"], "StringToArray errato"
        
        print(f"\nTest {test_num}.2: StringToArray con spazi")
        print(f"  Input: sText=' item1, item2 ,, item3 '")
        result = aiSys.StringToArray(" item1, item2 ,, item3 ")
        print(f"  Output: {result}")
        assert result == ["item1", "item2", "item3"], "StringToArray con spazi errato"
        test_num += 1
        
        # Test 5.6: StringToNum
        print(f"\nTest {test_num}.1: StringToNum intero")
        print(f"  Input: sNumber='123'")
        result = aiSys.StringToNum("123")
        print(f"  Output: {result} (tipo: {type(result).__name__})")
        assert result == 123 and isinstance(result, int), "Conversione intero errata"
        
        print(f"\nTest {test_num}.2: StringToNum float con virgola")
        print(f"  Input: sNumber='123,45'")
        result = aiSys.StringToNum("123,45")
        print(f"  Output: {result} (tipo: {type(result).__name__})")
        assert result == 123.45 and isinstance(result, float), "Conversione float errata"
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    
    return test_passed


def test_aiSysDictToString() -> bool:
    """Test per aiSysDictToString.py"""
    print("\n" + "=" * 60)
    print("Test 6: File aiSysDictToString.py, NomeTest: Conversione dizionari")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    try:
        # Test 6.1: DictToString JSON
        print(f"\nTest {test_num}.1: DictToString JSON")
        test_dict = {"nome": "Mario", "età": 30, "attivo": True}
        print(f"  Input: dictParam={test_dict}, sFormat='json'")
        result_err, result_str = aiSys.DictToString(test_dict, "json")
        print(f"  Output errore: {result_err}")
        print(f"  Output stringa: {result_str[:50]}...")
        assert result_err == "", f"Errore conversione JSON: {result_err}"
        assert '"nome": "Mario"' in result_str, "JSON non contiene dati attesi"
        test_num += 1
        
        # Test 6.2: DictToString INI
        print(f"\nTest {test_num}.1: DictToString INI")
        print(f"  Input: dictParam={test_dict}, sFormat='ini'")
        result_err, result_str = aiSys.DictToString(test_dict, "ini")
        print(f"  Output errore: {result_err}")
        print(f"  Output stringa: {result_str}")
        assert result_err == "", f"Errore conversione INI: {result_err}"
        assert "nome=Mario" in result_str, "INI non contiene dati attesi"
        test_num += 1
        
        # Test 6.3: DictToString INI.SECT
        print(f"\nTest {test_num}.1: DictToString INI.SECT")
        test_dict_sect = {
            "sezione1": {"chiave1": "valore1", "chiave2": "valore2"},
            "sezione2": {"chiaveA": "valoreA"}
        }
        print(f"  Input: dictParam={test_dict_sect}, sFormat='ini.sect'")
        result_err, result_str = aiSys.DictToString(test_dict_sect, "ini.sect")
        print(f"  Output errore: {result_err}")
        print(f"  Output stringa:\n{result_str}")
        assert result_err == "", f"Errore conversione INI.SECT: {result_err}"
        assert "[sezione1]" in result_str, "Sezioni non presenti in output"
        test_num += 1
        
        # Test 6.4: DictToXml
        print(f"\nTest {test_num}.1: DictToXml base")
        test_dict_xml = {"user": {"@id": "1", "name": "Mario"}}
        print(f"  Input: dictParam={test_dict_xml}")
        result = aiSys.DictToXml(test_dict_xml, root_tag="root")
        print(f"  Output: {result}")
        assert "<root>" in result, "Tag root mancante"
        assert "id=\"1\"" in result, "Attributo mancante"
        assert "<name>Mario</name>" in result, "Elemento mancante"
        test_num += 1
        
        # Test 6.5: DictPrint (test visivo)
        print(f"\nTest {test_num}.1: DictPrint (test visivo)")
        print("  Output atteso su schermo:")
        aiSys.DictPrint(test_dict)
        # Non c'è assert, è solo un test visivo
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    
    return test_passed


def test_aiSysLog() -> bool:
    """Test per aiSysLog.py (classe acLog)"""
    print("\n" + "=" * 60)
    print("Test 7: File aiSysLog.py, NomeTest: Classe acLog")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    # Crea directory temporanea per il log
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "aiSysTest_acLog.log")
    
    try:
        # Test 7.1: Creazione e inizializzazione
        print(f"\nTest {test_num}.1: Creazione acLog e Start")
        log = aiSys.acLog()
        print(f"  Oggetto acLog creato")
        
        result = log.Start(sLogfile="aiSysTest_acLog", sLogFolder=temp_dir)
        print(f"  Start risultato: {result}")
        print(f"  Percorso log: {log.sLog}")
        assert result == "", f"Errore Start: {result}"
        assert log.sLog == log_file, f"Percorso log errato: {log.sLog}"
        test_num += 1
        
        # Test 7.2: Scrittura log
        print(f"\nTest {test_num}.1: Scrittura log")
        print("  Output atteso su schermo e file:")
        log.Log("TEST", "Messaggio di test 1")
        log.Log1("Messaggio INFO")
        log.Log0("", "Messaggio senza errore")
        log.Log0("Errore123", "Messaggio con errore")
        
        # Verifica che il file sia stato creato
        assert os.path.exists(log_file), "File log non creato"
        
        # Leggi file per verificare contenuto
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"  Linee scritte nel file: {len(lines)}")
            assert len(lines) >= 4, "Numero linee log insufficiente"
        test_num += 1
        
        # Test 7.3: Log con file vuoto (test gestione errori)
        print(f"\nTest {test_num}.1: Log con sLog vuoto")
        log2 = aiSys.acLog()
        log2.Log("TEST", "Questo non dovrebbe scrivere")
        print("  OK: Nessun errore con sLog vuoto")
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    finally:
        # Pulizia
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    return test_passed


def test_integration() -> bool:
    """Test di integrazione tra moduli"""
    print("\n" + "=" * 60)
    print("Test 8: Integrazione moduli aiSys")
    print("=" * 60)
    
    test_passed = True
    test_num = 1
    
    try:
        # Test 8.1: Uso combinato di più moduli
        print(f"\nTest {test_num}.1: Integrazione base")
        
        # Crea dizionario con Timestamp
        config_dict = {
            "timestamp": aiSys.Timestamp(),
            "user": "TestUser",
            "level": "debug"
        }
        
        # Usa Expand con il dizionario
        message = "Log $timestamp - Utente: $user - Livello: $level"
        expanded = aiSys.Expand(message, config_dict)
        print(f"  Messaggio espanso: {expanded}")
        assert "TestUser" in expanded, "Expand non funziona con dizionario"
        
        # Usa StringAppend
        log_line = aiSys.StringAppend("", expanded, " | ")
        print(f"  Linea log: {log_line}")
        
        # Valida email
        email_valid = aiSys.isEmail("test@example.com")
        print(f"  Email valida: {email_valid}")
        assert email_valid == True, "Validazione email non funziona"
        
        # Converte stringa in array
        tags = aiSys.StringToArray("python,test,integration")
        print(f"  Tags: {tags}")
        assert len(tags) == 3, "Conversione array non funziona"
        
        test_num += 1
        
        # Test 8.2: File operations con configurazione
        print(f"\nTest {test_num}.1: Operazioni file con configurazione")
        
        # Crea file INI con dati complessi
        temp_dir = tempfile.mkdtemp()
        ini_file = os.path.join(temp_dir, "config.ini")
        
        config_data = {
            "database": {
                "host": "$DB_HOST",
                "port": "$DB_PORT"
            },
            "app": {
                "name": "$APP_NAME",
                "version": "1.0"
            }
        }
        
        # Salva
        aiSys.save_dict_to_ini(config_data, ini_file)
        
        # Espandi variabili
        env_config = {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "APP_NAME": "aiSysTest"
        }
        
        # Leggi ed espandi
        result, loaded = aiSys.read_ini_to_dict(ini_file)
        expanded_config = aiSys.ExpandDict(loaded, env_config)
        
        print(f"  Config espanso: {expanded_config}")
        assert expanded_config["database"]["host"] == "localhost", "ExpandDict non funziona con INI"
        
        # Test PathMake
        full_path = aiSys.PathMake(temp_dir, "log", "txt")
        print(f"  Path creato: {full_path}")
        assert full_path.endswith(".txt"), "PathMake non funziona"
        
        # Pulizia
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except AssertionError as e:
        print(f"  ❌ Assert fallito: {e}")
        test_passed = False
    except Exception as e:
        print(f"  ❌ Errore durante il test: {e}")
        test_passed = False
    
    return test_passed


# Esegui i test quando il file viene eseguito direttamente
if __name__ == "__main__":
    run_tests()