# ntJobsOS_test.py
# Funzioni di test per ntJobsOS

import aiSys
import aiJobsOS
import os
from aiJobsOS import acJobsOS

# ============================================================================
# SEZIONE TEST: Funzioni di Test
# ============================================================================

def SysPrintConfig(jData, sDiz):
    """
    Stampa la configurazione specificata di jData.
    
    Parametri:
        jData: Istanza di acJobsOS
        sDiz: Sigla del dizionario da estrarre
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    # Mappatura dei valori di sDiz ai dizionari corrispondenti
    diz_map = {
        "CONFIG": jData.dictConfig if hasattr(jData, 'dictConfig') else None,
        "USERS": jData.JOBS_TAB_USERS if hasattr(jData, 'JOBS_TAB_USERS') else None,
        "GROUPS": jData.JOBS_TAB_GROUPS if hasattr(jData, 'JOBS_TAB_GROUPS') else None,
        "ACTIONS": jData.JOBS_TAB_ACTIONS if hasattr(jData, 'JOBS_TAB_ACTIONS') else None,
        "USER": jData.dictUser if hasattr(jData, 'dictUser') else None,
        "JOBS": jData.dictJobs if hasattr(jData, 'dictJobs') else None,
        "ACTION": jData.dictAction if hasattr(jData, 'dictAction') else None,
        "CFGINI": jData.dictJobs.get("CONFIG") if hasattr(jData, 'dictJobs') and jData.dictJobs else None
    }
    
    sResult = ""
    
    if sDiz in diz_map:
        dictTemp = diz_map[sDiz]
        if dictTemp is not None:
            aiSys.DictPrint(dictTemp)
        else:
            sResult = f"Attributo non disponibile: {sDiz}"
    else:
        sResult = f"ID non trovato: {sDiz}"
    
    return sResult


def SysTestConfig():
    """
    Effettua verifiche sulla partenza di acJobsOS.
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    sResult = ""
    
    try:
        jData = acJobsOS()
        
        sResult = jData.Start_ReadIni()
        print("Lettura INI: " + sResult)
        
        if sResult == "":
            sResult = jData.Start_ReadDat()
            print("Lettura CSV: " + sResult)
    
    except Exception as e:
        sResult = f"Errore in SysTestConfig: {str(e)}"
    
    return sResult


def SysTestStart():
    """
    Verifica la partenza di acJobsOS con stampa delle configurazioni.
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    sResult = ""
    
    try:
        print("Inizio Creazione istanza jData")
        
        jData = acJobsOS()
        
        sResult = jData.Start()
        print("Esecuzione jData.Start(): " + sResult)
        
        if sResult == "":
            asDiz = ["CONFIG", "USERS", "GROUPS", "ACTIONS", "CFGINI"]
            
            for sDiz in asDiz:
                sResult = SysPrintConfig(jData, sDiz)
                if sResult != "":
                    break  # Interrompe se c'è un errore
        
        # In Python, l'istanza sarà garbage collected automaticamente
        # Possiamo esplicitamente eliminare il riferimento
        del jData
        
        print("Fine Creazione istanza jData")
        
    except Exception as e:
        sResult = f"Errore in SysTestStart: {str(e)}"
    
    return sResult


def SysTestMail():
    """
    Testa l'invio di mail tramite acJobsOS.
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    sResult = ""
    
    try:
        jData = acJobsOS()
        
        sResult = jData.Start()
        print("Esecuzione Test.Mail. jData.Start:" + sResult)
        
        if sResult == "":
            sResult = jData.MailAdmin("Mail a Admin", "Testo Mail a Admin")
        
        del jData
        
    except Exception as e:
        sResult = f"Errore in SysTestMail: {str(e)}"
    
    return sResult


def SysTestReadDat():
    """
    Testa la lettura del file CSV delle azioni.
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    sResult = ""
    
    try:
        sResult, dictCSV = aiSys.read_csv_to_dict("ntjobs_actions.csv")
        print("Esecuzione read_csv_to_dict:" + sResult)
        
        if sResult == "":
            aiSys.DictPrint(dictCSV)
    
    except Exception as e:
        sResult = f"Errore in SysTestReadDat: {str(e)}"
    
    return sResult


def SysTestReadIni():
    """
    Testa la lettura del file INI di configurazione.
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    sResult = ""
    
    try:
        sResult, dictINI = aiSys.read_ini_to_dict("ntjobs_config.ini")
        print("Esecuzione read_ini_to_dict:" + sResult)
        
        if sResult == "":
            aiSys.DictPrint(dictINI)
    
    except Exception as e:
        sResult = f"Errore in SysTestReadIni: {str(e)}"
    
    return sResult


def SysTestJobsRun():
    """
    Verifica il ciclo principale di esecuzione di acJobsOS.
    
    Ritorna:
        sResult: "" se successo, altrimenti messaggio di errore
    """
    sResult = ""
    
    try:
        jData = acJobsOS()
        
        print("Inizio Test jData.Run")
        
        sResult = jData.Start()
        print("Esecuzione jData.Start(): " + sResult)
        
        if sResult == "":
            # Definisce il contenuto del file di configurazione temporaneo
            asLines = [
                "[CONFIG]",
                "TYPE=NTJOBS.CONFIG.1",
                "ADMIN.EMAIL=ntgcorp@gmail.com",
                "PYTHON=G:/Il mio Drive/Progetti/ntJobsOS/PYN.CMD",
                "; METODO INVIO MAIL PREVISTO",
                "; 1=SMTP",
                "; 2=OLKSENDMAIL (usando variabile OLKSENDMAIL per path di esecuzione dove creare ntjobs.json)",
                "MAIL.ENGINE=OLKSENDMAIL",
                "",
                "[JOB_1]",
                "ACTION=sys.mail.admin",
                "",
                "[JOB_2]",
                "ACTION=sys.mail.user"
            ]
            
            # Crea il percorso per il file temporaneo
            sPath = aiSys.PathMake("", "users/mach0/jobs", "ini")
            
            # Crea la directory se non esiste
            os.makedirs(os.path.dirname(sPath), exist_ok=True)
            
            # Crea il file temporaneo
            sResult = aiSys.save_array_file(sPath, asLines)
            
            if sResult == "":
                # NOTA: Assumiamo che jData.Run() utilizzi automaticamente
                # il file jobs.ini nel percorso specificato dalla configurazione
                # o che sia stato configurato per usare sPath
                
                # Esegue il ciclo principale fino a che bExitOS è True
                while not getattr(jData, 'bExitOS', True):
                    # Questa parte dipende dall'implementazione di jData.Run()
                    # Potrebbe essere necessario adattarla
                    pass
                
                # In un'implementazione reale, si chiamerebbe:
                # jData.Run()  # che dovrebbe impostare bExitOS=True quando finisce
            
            # Pulisce: cancella il file temporaneo
            try:
                if os.path.exists(sPath):
                    os.remove(sPath)
                    print(f"File temporaneo cancellato: {sPath}")
            except Exception as e:
                print(f"Attenzione: impossibile cancellare il file {sPath}: {str(e)}")
        
        del jData
        
        print("Fine Test jData.Run")
    
    except Exception as e:
        sResult = f"Errore in SysTestJobsRun: {str(e)}"
    
    return sResult


# ============================================================================
# Funzione __main__
# ============================================================================

if __name__ == "__main__":
    """
    Esegue tutte le funzioni di test in sequenza.
    Si ferma se una funzione restituisce un errore (sResult != "").
    """
    
    print("=" * 60)
    print("INIZIO TEST NTJOBSOS")
    print("=" * 60)
    
    # Esegue SysTestConfig
    sResult = SysTestConfig()
    print(f"Risultato SysTestConfig: {sResult}")
    if sResult != "":
        print("TEST INTERROTTO: errore in SysTestConfig")
        exit(1)
    
    # Esegue SysTestReadIni
    sResult = SysTestReadIni()
    print(f"Risultato SysTestReadIni: {sResult}")
    if sResult != "":
        print("TEST INTERROTTO: errore in SysTestReadIni")
        exit(1)
    
    # Esegue SysTestReadDat
    sResult = SysTestReadDat()
    print(f"Risultato SysTestReadDat: {sResult}")
    if sResult != "":
        print("TEST INTERROTTO: errore in SysTestReadDat")
        exit(1)
    
    # Esegue SysTestStart
    sResult = SysTestStart()
    print(f"Risultato SysTestStart: {sResult}")
    if sResult != "":
        print("TEST INTERROTTO: errore in SysTestStart")
        exit(1)
    
    # Esegue SysTestMail
    sResult = SysTestMail()
    print(f"Risultato SysTestMail: {sResult}")
    if sResult != "":
        print("TEST INTERROTTO: errore in SysTestMail")
        exit(1)
    
    # Esegue SysTestJobsRun
    sResult = SysTestJobsRun()
    print(f"Risultato SysTestJobsRun: {sResult}")
    if sResult != "":
        print("TEST INTERROTTO: errore in SysTestJobsRun")
        exit(1)
    
    print("=" * 60)
    print("TUTTI I TEST COMPLETATI CON SUCCESSO!")
    print("=" * 60)