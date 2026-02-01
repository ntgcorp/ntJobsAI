"""
aiSysTest.py - Test completo di tutte le funzioni del modulo aiSys
"""

import sys
import os
import json
import tempfile
import shutil
from typing import Dict, List, Any, Tuple
from datetime import datetime

# =============================================================================
# IMPORT DEL MODULO DA TESTARE
# =============================================================================

try:
    import aiSys
except ImportError as e:
    print(f"ERRORE: Impossibile importare aiSys - {str(e)}")
    print("Assicurati che tutti i moduli aiSys*.py siano nella stessa directory.")
    sys.exit(1)


# =============================================================================
# CLASSE PER GESTIONE TEST
# =============================================================================

class TestManager:
    """Gestisce l'esecuzione e il reporting dei test."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_details = []
        self.failed_asserts = []
        self.current_test_num = 0
        self.current_assert_num = 0
        
    def start_test(self, test_num: int, module_name: str, test_name: str):
        """Inizia un nuovo test."""
        self.current_test_num = test_num
        self.current_assert_num = 0
        print(f"\n{'='*60}")
        print(f"Test: {test_num:03d} | File: {module_name} | NomeTest: {test_name}")
        print(f"{'='*60}")
        
    def assert_test(self, condition: bool, description: str, expected: Any = None, actual: Any = None):
        """Esegue un assert e registra il risultato."""
        self.current_assert_num += 1
        assert_id = f"Test{self.current_test_num:03d}_Assert{self.current_assert_num:03d}"
        
        if condition:
            print(f"  ✓ {assert_id}: {description}")
            return True
        else:
            print(f"  ✗ {assert_id}: {description}")
            if expected is not None and actual is not None:
                print(f"     Expected: {expected}")
                print(f"     Actual: {actual}")
            
            # Registra l'assert fallito
            self.failed_asserts.append({
                'test_num': self.current_test_num,
                'assert_num': self.current_assert_num,
                'assert_id': assert_id,
                'description': description,
                'expected': expected,
                'actual': actual
            })
            return False
            
    def end_test(self, test_passed: bool):
        """Termina un test e aggiorna le statistiche."""
        self.total_tests += 1
        if test_passed:
            self.passed_tests += 1
            print(f"  → Test {self.current_test_num:03d}: PASSATO")
        else:
            self.failed_tests += 1
            print(f"  → Test {self.current_test_num:03d}: FALLITO")
            
    def print_summary(self):
        """Stampa il riepilogo dei test."""
        print(f"\n{'='*60}")
        print("RIEPILOGO TEST")
        print(f"{'='*60}")
        print(f"Test totali:    {self.total_tests}")
        print(f"Test passati:   {self.passed_tests}")
        print(f"Test falliti:   {self.failed_tests}")
        print(f"Assert falliti: {len(self.failed_asserts)}")
        
        if self.failed_tests > 0:
            print(f"\n{'='*60}")
            print("DETTAGLIO TEST FALLITI:")
            print(f"{'='*60}")
            
            # Raggruppa gli assert falliti per test
            failed_tests_dict = {}
            for failed_assert in self.failed_asserts:
                test_num = failed_assert['test_num']
                if test_num not in failed_tests_dict:
                    failed_tests_dict[test_num] = []
                failed_tests_dict[test_num].append(failed_assert)
            
            # Stampa i dettagli per ogni test fallito
            for test_num in sorted(failed_tests_dict.keys()):
                print(f"\nTest {test_num:03d}:")
                for failed_assert in failed_tests_dict[test_num]:
                    print(f"  {failed_assert['assert_id']}: {failed_assert['description']}")
                    if failed_assert['expected'] is not None:
                        print(f"    Expected: {failed_assert['expected']}")
                    if failed_assert['actual'] is not None:
                        print(f"    Actual:   {failed_assert['actual']}")


# =============================================================================
# FUNZIONI DI SUPPORTO PER TEST
# =============================================================================

def create_temp_file(content: str = "", extension: str = ".txt") -> str:
    """Crea un file temporaneo con il contenuto specificato."""
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, f"test{extension}")
    if content:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
    return temp_file, temp_dir


def cleanup_temp_files(file_path: str, dir_path: str = None):
    """Pulisce i file temporanei."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        if dir_path and os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    except:
        pass


# =============================================================================
# FUNZIONI DI TEST
# =============================================================================

def test_aiSysBase(test_mgr: TestManager) -> bool:
    """Test delle funzioni di aiSysBase.py"""
    test_passed = True
    
    # Test 001: aiErrorProc
    test_mgr.start_test(1, "aiSysBase.py", "aiErrorProc")
    
    # Assert 001_001
    result = aiSys.aiErrorProc("", "test_func")
    condition = test_mgr.assert_test(
        result == "",
        "aiErrorProc con sResult vuoto deve ritornare stringa vuota",
        "", result
    )
    test_passed = test_passed and condition
    
    # Assert 001_002
    result = aiSys.aiErrorProc("errore_123", "test_func")
    expected = "test_func: Errore errore_123"
    condition = test_mgr.assert_test(
        result == expected,
        "aiErrorProc con sResult non vuoto deve aggiungere prefisso",
        expected, result
    )
    test_passed = test_passed and condition
    
    test_mgr.end_test(test_passed)
    
    # Test 002: DictMerge
    test_mgr.start_test(2, "aiSysBase.py", "DictMerge")
    test_passed_2 = True
    
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    
    # Assert 002_001
    result = aiSys.DictMerge(dict1, dict2)
    expected = {"a": 1, "b": 3, "c": 4}
    condition = test_mgr.assert_test(
        result == expected,
        "DictMerge deve unire dizionari con priorità a dictAdd",
        expected, result
    )
    test_passed_2 = test_passed_2 and condition
    
    # Assert 002_002
    result = aiSys.DictMerge(None, dict2)
    condition = test_mgr.assert_test(
        result == dict2,
        "DictMerge con dictSource=None deve ritornare dictAdd",
        dict2, result
    )
    test_passed_2 = test_passed_2 and condition
    
    test_mgr.end_test(test_passed_2)
    test_passed = test_passed and test_passed_2
    
    # Test 003: DictExist
    test_mgr.start_test(3, "aiSysBase.py", "DictExist")
    test_passed_3 = True
    
    test_dict = {"chiave1": "valore1", "chiave2": 42}
    
    # Assert 003_001
    result = aiSys.DictExist(test_dict, "chiave1", "default")
    condition = test_mgr.assert_test(
        result == "valore1",
        "DictExist deve ritornare valore esistente",
        "valore1", result
    )
    test_passed_3 = test_passed_3 and condition
    
    # Assert 003_002
    result = aiSys.DictExist(test_dict, "chiave_inesistente", "valore_default")
    condition = test_mgr.assert_test(
        result == "valore_default",
        "DictExist deve ritornare valore default per chiavi inesistenti",
        "valore_default", result
    )
    test_passed_3 = test_passed_3 and condition
    
    # Assert 003_003
    result = aiSys.DictExist("non_un_dict", "chiave", "default")
    condition = test_mgr.assert_test(
        result is None,
        "DictExist con parametro non dizionario deve ritornare None",
        None, result
    )
    test_passed_3 = test_passed_3 and condition
    
    test_mgr.end_test(test_passed_3)
    test_passed = test_passed and test_passed_3
    
    return test_passed


def test_aiSysTimestamp(test_mgr: TestManager) -> bool:
    """Test delle funzioni di timestamp."""
    test_passed = True
    
    # Test 004: Timestamp
    test_mgr.start_test(4, "aiSysTimestamp.py", "Timestamp")
    test_passed_4 = True
    
    # Assert 004_001
    result = aiSys.Timestamp()
    condition = test_mgr.assert_test(
        len(result) >= 15,
        "Timestamp() deve generare stringa di almeno 15 caratteri",
        "len >= 15", f"len={len(result)}"
    )
    test_passed_4 = test_passed_4 and condition
    
    # Assert 004_002
    result = aiSys.Timestamp("test")
    condition = test_mgr.assert_test(
        ":" in result and result.count(":") >= 2,
        "Timestamp con postfix deve contenere due ':'",
        True, ":" in result and result.count(":") >= 2
    )
    test_passed_4 = test_passed_4 and condition
    
    test_mgr.end_test(test_passed_4)
    test_passed = test_passed and test_passed_4
    
    # Test 005: TimestampValidate
    test_mgr.start_test(5, "aiSysTimestamp.py", "TimestampValidate")
    test_passed_5 = True
    
    valid_ts = datetime.now().strftime("%Y%m%d:%H%M%S")
    
    # Assert 005_001
    result = aiSys.TimestampValidate(valid_ts)
    condition = test_mgr.assert_test(
        result == True,
        "TimestampValidate con timestamp valido deve ritornare True",
        True, result
    )
    test_passed_5 = test_passed_5 and condition
    
    # Assert 005_002
    result = aiSys.TimestampValidate("20241301:120000")  # Mese 13
    condition = test_mgr.assert_test(
        result == False,
        "TimestampValidate con mese non valido deve ritornare False",
        False, result
    )
    test_passed_5 = test_passed_5 and condition
    
    test_mgr.end_test(test_passed_5)
    test_passed = test_passed and test_passed_5
    
    return test_passed


def test_aiSysConfig(test_mgr: TestManager) -> bool:
    """Test delle funzioni di configurazione."""
    test_passed = True
    
    # Test 006: Expand
    test_mgr.start_test(6, "aiSysConfig.py", "Expand")
    test_passed_6 = True
    
    dict_config = {"USER": "Mario", "VAR": "valore"}
    
    # Assert 006_001
    result = aiSys.Expand("Ciao $USER", dict_config)
    condition = test_mgr.assert_test(
        result == "Ciao Mario",
        "Expand deve sostituire variabile $USER",
        "Ciao Mario", result
    )
    test_passed_6 = test_passed_6 and condition
    
    # Assert 006_002 - Test sequenze di escape
    result = aiSys.Expand("Testo%nnuova riga", dict_config)
    condition = test_mgr.assert_test(
        "\n" in result,
        "Expand deve convertire %n in newline",
        True, "\n" in result
    )
    test_passed_6 = test_passed_6 and condition
    
    # Assert 006_003 - Test variabile inesistente
    result = aiSys.Expand("Variabile $INESISTENTE", dict_config)
    condition = test_mgr.assert_test(
        result == "Variabile UNKNOWN",
        "Expand deve sostituire variabili inesistenti con UNKNOWN",
        "Variabile UNKNOWN", result
    )
    test_passed_6 = test_passed_6 and condition
    
    # Assert 006_004 - Test escape speciale
    result = aiSys.Expand("%$VAR", dict_config)
    condition = test_mgr.assert_test(
        result == "valore",
        "Expand deve gestire %$ come escape per $",
        "valore", result
    )
    test_passed_6 = test_passed_6 and condition
    
    test_mgr.end_test(test_passed_6)
    test_passed = test_passed and test_passed_6
    
    # Test 007: ExpandDict
    test_mgr.start_test(7, "aiSysConfig.py", "ExpandDict")
    test_passed_7 = True
    
    dict_to_expand = {
        "msg1": "Ciao $USER",
        "msg2": "Test %n nuova riga",
        "nested": {
            "sub": "Valore: $VAR"
        }
    }
    
    # Assert 007_001
    result = aiSys.ExpandDict(dict_to_expand, dict_config)
    condition = test_mgr.assert_test(
        isinstance(result, dict),
        "ExpandDict deve ritornare un dizionario",
        True, isinstance(result, dict)
    )
    test_passed_7 = test_passed_7 and condition
    
    # Assert 007_002
    condition = test_mgr.assert_test(
        result.get("msg1") == "Ciao Mario",
        "ExpandDict deve espandere valori nel dizionario",
        "Ciao Mario", result.get("msg1")
    )
    test_passed_7 = test_passed_7 and condition
    
    test_mgr.end_test(test_passed_7)
    test_passed = test_passed and test_passed_7
    
    # Test 008: Config e ConfigDefault
    test_mgr.start_test(8, "aiSysConfig.py", "Config e ConfigDefault")
    test_passed_8 = True
    
    config_dict = {"chiave1": "valore1", "chiave2": ""}
    
    # Assert 008_001 - Config lettura esistente
    result = aiSys.Config(config_dict, "chiave1")
    condition = test_mgr.assert_test(
        result == "valore1",
        "Config deve leggere valore esistente",
        "valore1", result
    )
    test_passed_8 = test_passed_8 and condition
    
    # Assert 008_002 - Config lettura inesistente
    result = aiSys.Config(config_dict, "chiave_inesistente")
    condition = test_mgr.assert_test(
        result == "",
        "Config per chiave inesistente deve ritornare stringa vuota",
        "", result
    )
    test_passed_8 = test_passed_8 and condition
    
    # Assert 008_003 - ConfigDefault
    result_dict = config_dict.copy()
    aiSys.ConfigDefault("chiave2", "nuovo_valore", result_dict)
    condition = test_mgr.assert_test(
        result_dict["chiave2"] == "nuovo_valore",
        "ConfigDefault deve impostare valore se vuoto",
        "nuovo_valore", result_dict["chiave2"]
    )
    test_passed_8 = test_passed_8 and condition
    
    # Assert 008_004 - ConfigDefault non sovrascrive
    aiSys.ConfigDefault("chiave1", "non_dovrebbe", result_dict)
    condition = test_mgr.assert_test(
        result_dict["chiave1"] == "valore1",
        "ConfigDefault non deve sovrascrivere valori esistenti non vuoti",
        "valore1", result_dict["chiave1"]
    )
    test_passed_8 = test_passed_8 and condition
    
    test_mgr.end_test(test_passed_8)
    test_passed = test_passed and test_passed_8
    
    return test_passed


def test_aiSysFileio(test_mgr: TestManager) -> bool:
    """Test delle funzioni di file I/O."""
    test_passed = True
    
    # Test 009: read_csv_to_dict e save_array_file
    test_mgr.start_test(9, "aiSysFileio.py", "read_csv_to_dict e save_array_file")
    test_passed_9 = True
    
    # Crea file CSV temporaneo
    csv_content = """ID;Nome;Eta
1;Mario;30
2;Luigi;25
3;Peach;28"""
    
    csv_file, csv_dir = create_temp_file(csv_content, ".csv")
    
    try:
        # Assert 009_001 - Lettura CSV
        result = aiSys.read_csv_to_dict(csv_file, ["ID", "Nome", "Eta"], ";")
        condition = test_mgr.assert_test(
            isinstance(result, tuple) and len(result) == 2,
            "read_csv_to_dict deve ritornare tupla (sResult, dict)",
            "tuple len=2", f"{type(result)} len={len(result) if isinstance(result, tuple) else 'N/A'}"
        )
        test_passed_9 = test_passed_9 and condition
        
        if condition and len(result) == 2:
            sResult, data_dict = result
            condition = test_mgr.assert_test(
                sResult == "" and len(data_dict) == 3,
                "read_csv_to_dict deve leggere 3 record correttamente",
                "sResult='', len=3", f"sResult='{sResult}', len={len(data_dict)}"
            )
            test_passed_9 = test_passed_9 and condition
    
    finally:
        cleanup_temp_files(csv_file, csv_dir)
    
    test_mgr.end_test(test_passed_9)
    test_passed = test_passed and test_passed_9
    
    # Test 010: isValidPath e PathMake
    test_mgr.start_test(10, "aiSysFileio.py", "isValidPath e PathMake")
    test_passed_10 = True
    
    # Assert 010_001 - isValidPath per percorso corrente
    result = aiSys.isValidPath(".")
    condition = test_mgr.assert_test(
        result == True,
        "isValidPath deve ritornare True per percorso corrente",
        True, result
    )
    test_passed_10 = test_passed_10 and condition
    
    # Assert 010_002 - PathMake
    result = aiSys.PathMake("/tmp", "testfile", "txt")
    condition = test_mgr.assert_test(
        result.endswith("/tmp/testfile.txt") or result.endswith("\\tmp\\testfile.txt"),
        "PathMake deve creare percorso completo",
        True, result.endswith("/tmp/testfile.txt") or result.endswith("\\tmp\\testfile.txt")
    )
    test_passed_10 = test_passed_10 and condition
    
    test_mgr.end_test(test_passed_10)
    test_passed = test_passed and test_passed_10
    
    return test_passed


def test_aiSysStrings(test_mgr: TestManager) -> bool:
    """Test delle funzioni di stringhe."""
    test_passed = True
    
    # Test 011: StringBool
    test_mgr.start_test(11, "aiSysStrings.py", "StringBool")
    test_passed_11 = True
    
    # Assert 011_001
    result = aiSys.StringBool("True")
    condition = test_mgr.assert_test(
        result == True,
        "StringBool('True') deve ritornare True",
        True, result
    )
    test_passed_11 = test_passed_11 and condition
    
    # Assert 011_002
    result = aiSys.StringBool("FALSE")
    condition = test_mgr.assert_test(
        result == True,
        "StringBool('FALSE') deve ritornare True (valida booleano)",
        True, result
    )
    test_passed_11 = test_passed_11 and condition
    
    # Assert 011_003
    result = aiSys.StringBool("notabool")
    condition = test_mgr.assert_test(
        result == False,
        "StringBool('notabool') deve ritornare False",
        False, result
    )
    test_passed_11 = test_passed_11 and condition
    
    test_mgr.end_test(test_passed_11)
    test_passed = test_passed and test_passed_11
    
    # Test 012: isEmail e isValidPassword
    test_mgr.start_test(12, "aiSysStrings.py", "isEmail e isValidPassword")
    test_passed_12 = True
    
    # Assert 012_001
    result = aiSys.isEmail("nome.cognome@gmail.com")
    condition = test_mgr.assert_test(
        result == True,
        "isEmail deve validare email corretta",
        True, result
    )
    test_passed_12 = test_passed_12 and condition
    
    # Assert 012_002
    result = aiSys.isEmail("non-email")
    condition = test_mgr.assert_test(
        result == False,
        "isEmail deve rifiutare stringa non email",
        False, result
    )
    test_passed_12 = test_passed_12 and condition
    
    # Assert 012_003
    result = aiSys.isValidPassword("Pass123!_.")
    condition = test_mgr.assert_test(
        result == True,
        "isValidPassword deve accettare password con caratteri permessi",
        True, result
    )
    test_passed_12 = test_passed_12 and condition
    
    test_mgr.end_test(test_passed_12)
    test_passed = test_passed and test_passed_12
    
    return test_passed


def test_aiSysDictToString(test_mgr: TestManager) -> bool:
    """Test delle funzioni di conversione dizionari."""
    test_passed = True
    
    # Test 013: DictToString
    test_mgr.start_test(13, "aiSysDictToString.py", "DictToString")
    test_passed_13 = True
    
    test_dict = {"nome": "Mario", "età": 30, "attivo": True}
    
    # Assert 013_001 - Formato JSON
    result = aiSys.DictToString(test_dict, "json")
    condition = test_mgr.assert_test(
        isinstance(result, tuple) and len(result) == 2,
        "DictToString deve ritornare tupla (sResult, sOutput)",
        "tuple len=2", f"{type(result)} len={len(result) if isinstance(result, tuple) else 'N/A'}"
    )
    test_passed_13 = test_passed_13 and condition
    
    if condition and len(result) == 2:
        sResult, sOutput = result
        condition = test_mgr.assert_test(
            sResult == "" and "Mario" in sOutput,
            "DictToString JSON deve contenere i dati",
            "sResult='', output contiene 'Mario'", f"sResult='{sResult}', output={sOutput[:50]}..."
        )
        test_passed_13 = test_passed_13 and condition
    
    # Assert 013_002 - Formato INI
    result = aiSys.DictToString(test_dict, "ini")
    if isinstance(result, tuple) and len(result) == 2:
        sResult, sOutput = result
        condition = test_mgr.assert_test(
            sResult == "" and "Mario" in sOutput,
            "DictToString INI deve contenere i dati",
            "sResult='', output contiene 'Mario'", f"sResult='{sResult}'"
        )
        test_passed_13 = test_passed_13 and condition
    
    test_mgr.end_test(test_passed_13)
    test_passed = test_passed and test_passed_13
    
    return test_passed


def test_aiSysLog(test_mgr: TestManager) -> bool:
    """Test della classe acLog."""
    test_passed = True
    
    # Test 014: acLog
    test_mgr.start_test(14, "aiSysLog.py", "acLog")
    test_passed_14 = True
    
    try:
        # Crea oggetto log
        log = aiSys.acLog()
        
        # Assert 014_001 - Inizializzazione
        result = log.Start("aiSysTest_acLog.log", ".")
        condition = test_mgr.assert_test(
            result == "",
            "acLog.Start deve ritornare stringa vuota se successo",
            "", result
        )
        test_passed_14 = test_passed_14 and condition
        
        # Assert 014_002 - Scrittura log
        log.Log1("Test log info")
        log.Log("ERR", "Test errore")
        
        # Verifica che il file sia stato creato
        log_file = "./aiSysTest_acLog.log"
        condition = test_mgr.assert_test(
            os.path.exists(log_file),
            "acLog deve creare file di log",
            True, os.path.exists(log_file)
        )
        test_passed_14 = test_passed_14 and condition
        
        # Pulizia
        if os.path.exists(log_file):
            os.remove(log_file)
            
    except Exception as e:
        condition = test_mgr.assert_test(
            False,
            f"Errore durante test acLog: {str(e)}",
            "Nessun errore", str(e)
        )
        test_passed_14 = False
    
    test_mgr.end_test(test_passed_14)
    test_passed = test_passed and test_passed_14
    
    return test_passed


# =============================================================================
# FUNZIONE PRINCIPALE
# =============================================================================

def main():
    """Funzione principale di test."""
    print("=" * 70)
    print("TEST COMPLETO DEL MODULO aiSys")
    print("=" * 70)
    
    # Inizializza gestore test
    test_mgr = TestManager()
    
    # Calcola numero totale di test
    test_functions = [
        test_aiSysBase,
        test_aiSysTimestamp,
        test_aiSysConfig,
        test_aiSysFileio,
        test_aiSysStrings,
        test_aiSysDictToString,
        test_aiSysLog
    ]
    
    total_tests = len(test_functions) + 7  # Test aggiuntivi per ogni modulo
    print(f"\nNumero totale di test da eseguire: {total_tests}")
    print("Inizio esecuzione test...")
    
    # Esegui tutti i test
    for test_func in test_functions:
        try:
            test_func(test_mgr)
        except Exception as e:
            print(f"\nERRORE durante l'esecuzione del test: {str(e)}")
    
    # Stampa riepilogo
    test_mgr.print_summary()
    
    # Ritorna codice di uscita
    if test_mgr.failed_tests == 0:
        print("\n✅ TUTTI I TEST SONO PASSATI CON SUCCESSO!")
        return 0
    else:
        print("\n❌ ALCUNI TEST SONO FALLITI")
        return 1


# =============================================================================
# PUNTO DI INGRESSO
# =============================================================================

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrotto dall'utente.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERRORE CRITICO: {str(e)}")
        sys.exit(2)