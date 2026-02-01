#!/usr/bin/env python3
"""
acJobsApp.py - Classe per gestire applicazioni batch ntJobApp
Versione basata sulla specifica coerente del documento.

Una ntJobApp è un'applicazione batch che:
1. Legge un file .ini di input o lo crea da parametri CLI
2. Esegue uno o più comandi (jobs) tramite callback
3. Restituisce un file .end con i risultati
4. Termina con codice: 0=OK, 1=Errore INI, 2=Errore job
"""

import sys
import os
import aiSys

class acJobsApp:
    """
    Classe principale per orchestrare micro applicazioni batch ntJobApp.
    """
    
    def __init__(self):
        """
        Inizializza gli attributi della classe.
        """
        # Inizializza sistema di log
        self.jLog = aiSys.acLog()
        
        # Inizializza dizionario job corrente
        self.dictJob = {}
        
        # Attributi della classe (come da specifica)
        self.sJobIni = ""           # File .ini di input
        self.bErrExit = True        # Esce in caso di errore di un job
        self.sName = ""             # Nome dell'applicazione
        self.tsStart = ""           # Timestamp inizio applicazione
        self.sType = ""             # Tipo e versione applicazione
        self.sLogFile = ""          # Nome facoltativo del file di Log
        self.dictPrint = None       # Istanza aiSysys (per stampa configurazione)
        self.sCommand = ""          # ID del comando corrente
        self.dictJobs = {}          # Dizionario contenente tutti i dizionari
        self.sJobEnd = ""           # Nome del file .end di output
        
        # Variabile per nome procedura corrente (per logging)
        self.sProc = ""
    
    # =========================================================================
    # METODO: Start
    # =========================================================================
    def Start(self):
        """
        Metodo principale di avvio.
        Legge o crea il file .ini, valida i parametri, inizializza il sistema.
        
        Returns:
            str: "" se successo, messaggio di errore altrimenti
        """
        self.sProc = "Start"
        sResult = ""
        
        # Inizializza timestamp di inizio
        self.tsStart = aiSys.Timestamp()
        
        # Verifica che ci siano parametri
        if len(sys.argv) < 2:
            sResult = "NTJOBSAPP: Eseguire con parametro file .ini o nella forma ntjobsapp.py command parametro valore ecc."
            print(sResult)
            return self._return_with_convention(sResult)
        
        # Gestione parametri: file .ini o creazione da parametri
        if not sys.argv[1].lower().endswith('.ini'):
            # Crea file .ini dai parametri
            sResult = self.MakeIni()
            if sResult != "":
                return self._return_with_convention(sResult)
        else:
            # Usa file .ini passato come parametro
            self.sJobIni = sys.argv[1]
        
        # Verifica esistenza file .ini
        if not os.path.exists(self.sJobIni):
            sResult = f"File .ini non esistente {self.sJobIni}"
            return self._return_with_convention(sResult)
        
        # Costruisce nome file .end
        base_name = os.path.splitext(self.sJobIni)[0]
        self.sJobEnd = base_name + ".end"
        
        # Legge file .ini
        sResult, self.dictJobs = aiSys.read_ini_to_dict(self.sJobIni)
        if sResult != "":
            return self._return_with_convention(sResult)
        
        print(f"Letto {self.sJobIni}")
        
        # Verifica chiavi riservate nelle sezioni (eccetto CONFIG)
        reserved_keys = ["TS.START", "TS.END", "RETURN.TYPE", "RETURN.VALUE"]
        reserved_prefix = "RETURN.FILE."
        
        for section in self.dictJobs:
            if section == "CONFIG":
                continue
                
            for key in self.dictJobs[section]:
                # Verifica chiavi riservate
                if key in reserved_keys or key.startswith(reserved_prefix):
                    sResult = f"Usate chiavi riservate {key} nella sezione {section}"
                    return self._return_with_convention(sResult)
        
        # Estrae lista sezioni
        sections = list(self.dictJobs.keys())
        sections_str = ", ".join(sections)
        print(f"Processato {self.sJobIni}, Sezioni {sections_str}")
        
        # Verifica esistenza sezione CONFIG
        if "CONFIG" not in self.dictJobs:
            sResult = f"Sezione CONFIG non trovata in file {self.sJobIni}"
            return self._return_with_convention(sResult)
        
        # Verifica sezioni JOB e file richiesti
        for section in self.dictJobs:
            if section == "CONFIG":
                continue
                
            dictTemp = self.dictJobs[section].copy()
            
            # Verifica presenza COMMAND
            if "COMMAND" not in dictTemp:
                sResult += f"Per questa sezione COMMAND non presente: {section}\n"
                continue
            
            # Verifica file richiesti (chiavi che iniziano con "FILE.")
            for key in list(dictTemp.keys()):
                if key.startswith("FILE."):
                    sFile = dictTemp[key]
                    
                    # Ripulisci sFile da eventuali path precedenti
                    sFile = os.path.basename(sFile)
                    dictTemp[key] = sFile  # Aggiorna con nome pulito
                    
                    # Verifica esistenza file
                    if not os.path.exists(sFile):
                        sResult += f"File richiesto non presente {sFile}\n"
        
        # Se ci sono errori nelle verifiche precedenti
        if sResult != "":
            return self._return_with_convention(sResult)
        
        # Stampa configurazione usando DictPrint
        try:
            # Nota: nella specifica è scritto self.dictJobs("CONFIG") 
            # ma probabilmente è un refuso, uso ["CONFIG"]
            aiSys.DictPrint(self.dictJobs["CONFIG"])
        except Exception as e:
            sResult = f"Errore in DictPrint: {str(e)}"
            return self._return_with_convention(sResult)
        
        # Estrae parametri di configurazione
        sTemp = self.Config("LOG")
        if sTemp != "":
            self.sLogFile = sTemp
        
        self.sType = self.Config("TYPE")
        self.sName = self.Config("NAME")
        self.bErrExit = aiSys.StringBool(self.Config("EXIT"))
        
        # Avvia sistema di log
        sResult = self.jLog.Start(self.sLogFile)
        if sResult != "":
            return self._return_with_convention(sResult)
        
        # Rimuove password dalla configurazione (se presente)
        if "PASSWORD" in self.dictJobs.get("CONFIG", {}):
            del self.dictJobs["CONFIG"]["PASSWORD"]
        
        # Espansione valori (sempre se nessun errore)
        if sResult == "":
            aiSys.ExpandDict(self.dictJobs, self.dictJobs["CONFIG"])
        
        # Verifiche finali sui parametri config
        if self.sName == "":
            sResult = "NAME APP non precisato"
        
        if self.sType is not None and not str(self.sType).startswith("NTJOBS.APP."):
            sResult = "Type INI non NTJOBSAPP"
        
        # Log finale e ritorno
        self.Log0(sResult)
        return self._return_with_convention(sResult)
    
    # =========================================================================
    # METODO: MakeIni
    # =========================================================================
    def MakeIni(self):
        """
        Crea un file .ini dai parametri passati da linea di comando.
        
        Formato: python acJobsApp.py command key1 value1 key2 value2 ...
        
        Returns:
            str: "" se successo, messaggio di errore altrimenti
        """
        self.sProc = "MakeIni"
        sResult = ""
        self.sJobIni = ""
        
        # Verifica numero parametri (deve essere 1 + multiplo di 2)
        # 1 per il comando, + coppie chiave-valore
        if (len(sys.argv) - 1) % 2 != 1:
            sResult = "Errore numero parametri comando chiave=valore ecc."
            return self._return_with_convention(sResult)
        
        # Estrae comando (primo parametro dopo nome script)
        sCommand = sys.argv[1]
        
        # Crea dizionario temporaneo con coppie chiave-valore
        dictTemp = {}
        i = 2  # Inizia dal terzo parametro (dopo script e comando)
        while i < len(sys.argv):
            key = sys.argv[i]
            # Verifica se c'è un valore successivo
            if i + 1 >= len(sys.argv):
                sResult = f"Valore mancante per chiave: {key}"
                return self._return_with_convention(sResult)
            
            value = sys.argv[i + 1]
            
            # Rimuove virgolette se presenti
            if key.startswith('"') and key.endswith('"'):
                key = key[1:-1]
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            dictTemp[key] = value
            i += 2
        
        # Crea file .ini
        sFileTemp = "ntjobsapp.ini"
        try:
            with open(sFileTemp, 'w', encoding='utf-8') as f:
                # Sezione CONFIG
                f.write("[CONFIG]\n")
                f.write("TYPE=NTJOBS.APP.1\n")
                f.write("\n")
                
                # Sezione JOB_01
                f.write("[JOB_01]\n")
                f.write(f"COMMAND={sCommand}\n")
                
                # Altre chiavi-valori
                for key, value in dictTemp.items():
                    f.write(f"{key}={value}\n")
            
            self.sJobIni = sFileTemp
            
        except Exception as e:
            sResult = f"Errore creazione file .ini: {str(e)}"
        
        return self._return_with_convention(sResult)
    
    # =========================================================================
    # METODO: Config
    # =========================================================================
    def Config(self, sKey):
        """
        Restituisce il valore di una chiave dalla sezione CONFIG.
        
        Args:
            sKey (str): Chiave da cercare
            
        Returns:
            str: Valore della chiave o stringa vuota se non trovata
        """
        # Usa get per evitare KeyError se CONFIG non esiste
        config_section = self.dictJobs.get("CONFIG", {})
        return aiSys.Config(config_section, sKey)
    
    # =========================================================================
    # METODO: AddTimestamp
    # =========================================================================
    def AddTimestamp(self, dictTemp):
        """
        Aggiunge o sostituisce timestamp TS.START e TS.END in un dizionario.
        
        Args:
            dictTemp (dict): Dizionario da aggiornare (per riferimento)
        """
        dictTemp["TS.START"] = self.tsStart
        dictTemp["TS.END"] = aiSys.Timestamp()
    
    # =========================================================================
    # METODO: Return
    # =========================================================================
    def Return(self, sResult, sValue="", dictFiles=None):
        """
        Aggiorna i risultati dell'elaborazione corrente.
        Chiamato dalla funzione callback cbCommands.
        
        Args:
            sResult (str): Risultato dell'elaborazione (""=successo)
            sValue (str): Valore facoltativo di ritorno
            dictFiles (dict): Dizionario file da restituire {id: nome_file}
            
        Returns:
            str: "" se successo, messaggio di errore altrimenti
        """
        self.sProc = "Return"
        
        # Determina tipo di ritorno
        if sResult != "":
            sReturnType = "E"  # Errore
        else:
            sReturnType = "S"  # Successo
        
        # Se sValue è vuoto e c'è errore, usa sResult come valore
        if sValue == "" and sReturnType == "E":
            sValue = sResult
        
        # Gestione file di ritorno
        if dictFiles is not None:
            file_counter = 1
            for file_id, file_name in dictFiles.items():
                # Prende solo nome file senza path
                clean_name = os.path.basename(file_name)
                
                # Verifica esistenza file nella cartella corrente
                if not os.path.exists(clean_name):
                    sResult = f"Errore file non presente: {clean_name}"
                    return self._return_with_convention(sResult)
                
                # Aggiunge prefisso RETURN.FILE. con formato a 2 cifre
                return_key = f"RETURN.FILE.{file_counter:02d}"
                self.dictJob[return_key] = clean_name
                file_counter += 1
        
        # Se sReturnType è vuoto, imposta a "S" (Successo)
        # (anche se normalmente non dovrebbe essere vuoto)
        if sReturnType == "":
            sReturnType = "S"
        
        # Aggiorna dizionario job corrente
        self.dictJob["RETURN.TYPE"] = sReturnType
        self.dictJob["RETURN.VALUE"] = sValue
        
        # Aggiunge timestamp
        self.AddTimestamp(self.dictJob)
        
        return self._return_with_convention(sResult)
    
    # =========================================================================
    # METODO: Run
    # =========================================================================
    def Run(self, cbCommands):
        """
        Esegue tutti i jobs definiti nel file .ini.
        
        Args:
            cbCommands (function): Funzione callback da chiamare per ogni job
            
        Returns:
            str: "" se tutti i job hanno successo, altrimenti messaggio errore
        """
        self.sProc = "Run"
        sResult = ""
        
        # Itera su tutte le sezioni (eccetto CONFIG)
        for sKey in self.dictJobs:
            if sKey == "CONFIG":
                continue
            
            print(f"Esecuzione Command {sKey}")
            
            # Copia il dizionario del job corrente
            self.dictJob = self.dictJobs[sKey].copy()
            
            # Estrae comando
            self.sCommand = aiSys.DictExist(self.dictJob, "COMMAND", "")
            
            if self.sCommand == "":
                sResult = f"COMMAND non trovato in {sKey}"
                self.Log(sResult)
                # Continua con il prossimo job
                continue
            
            # Esegue il comando tramite callback
            self.Log1(f"Eseguo il comando: {self.sCommand}, Sezione: {sKey}, TS: {aiSys.Timestamp()}, Risultato: {sResult}")
            
            sResult = cbCommands(self.dictJob)
            
            # Aggiorna il dizionario originale con i risultati
            self.dictJobs[sKey] = self.dictJob.copy()
            
            self.Log1(f"Eseguito il comando: {self.sCommand}, Sezione: {sKey}, TS: {aiSys.Timestamp()}, Risultato: {sResult}")
            
            # Se bErrExit=True e c'è errore, esce dal ciclo
            if self.bErrExit and sResult != "":
                break
        
        return self._return_with_convention(sResult)
    
    # =========================================================================
    # METODO: End
    # =========================================================================
    def End(self, sResult):
        """
        Metodo finale: salva risultati, log e termina applicazione.
        
        Args:
            sResult (str): Risultato finale dell'esecuzione
            
        Returns:
            int: Codice di uscita (0=OK, 1=Errore INI, 2=Errore job)
        """
        self.sProc = "End"
        bIsFatalError = False
        nResult = 0
        
        # Fase 1: Determina codice di uscita
        if not self.dictJobs:
            # Errore di Start: dictJobs vuoto
            nResult = 1
            self.dictJobs = {"CONFIG": {}}
            bIsFatalError = True
        elif sResult != "":
            # Errore in uno o più job
            nResult = 2
            bIsFatalError = True
        
        # Crea dizionario temporaneo
        dictTemp = {
            "RETURN.TYPE": "",
            "RETURN.VALUE": ""
        }
        
        # Se errore fatale, aggiorna tipo e valore
        if bIsFatalError:
            dictTemp["RETURN.TYPE"] = "E"
            dictTemp["RETURN.VALUE"] = sResult
        
        # Aggiunge timestamp in ogni caso
        self.AddTimestamp(dictTemp)
        
        # Propaga aggiornamenti alla sezione CONFIG
        if "CONFIG" not in self.dictJobs:
            self.dictJobs["CONFIG"] = {}
        
        # Unisci con priorità a dictTemp (sovrascrive se esiste già)
        self.dictJobs["CONFIG"].update(dictTemp)
        
        # Fase 3: Salva file .end
        sSaveResult = aiSys.save_dict_to_ini(self.dictJobs, self.sJobEnd)
        if sSaveResult == "":
            print(f"Creato file {self.sJobEnd}")
        
        # Log finale
        self.Log(sSaveResult, f"Fine applicazione {self.sName}")
        
        # Ritorna codice di uscita
        return nResult
    
    # =========================================================================
    # METODI DI LOG (remapping)
    # =========================================================================
    def Log(self, sMsg, sExtra=""):
        """
        Remapping di self.jLog.Log()
        """
        return self.jLog.Log(sMsg, sExtra)
    
    def Log0(self, sMsg):
        """
        Remapping di self.jLog.Log0()
        """
        return self.jLog.Log0(sMsg)
    
    def Log1(self, sMsg):
        """
        Remapping di self.jLog.Log1()
        """
        return self.jLog.Log1(sMsg)
    
    # =========================================================================
    # METODO PRIVATO: Gestione convenzione messaggi
    # =========================================================================
    def _return_with_convention(self, sResult):
        """
        Gestisce la convenzione di stampa dei messaggi.
        Stampa "Eseguita ntjobsapp.<sProc>: <sResult>" se sResult non è vuoto.
        
        Args:
            sResult (str): Risultato da ritornare
            
        Returns:
            str: Il risultato in input
        """
        # Se sResult non è vuoto, stampa secondo la convenzione
        if sResult != "":
            print(f"Eseguita ntjobsapp.{self.sProc}: {sResult}")
        
        # Ritorna sempre sResult (vuoto o meno)
        return sResult


# =============================================================================
# FUNZIONE PRINCIPALE - ESEMPIO DI UTILIZZO
# =============================================================================
def main():
    """
    Esempio di utilizzo della classe acJobsApp.
    Segue la logica di funzionamento descritta nel documento.
    """
    # 1. Crea istanza di acJobsApp in variabile globale jData
    global jData
    jData = acJobsApp()
    
    # 2. Esegui sResult=jData.Start()
    sResult = jData.Start()
    
    # 3. Se sResult diverso da "":
    if sResult != "":
        # a. Esegui il metodo self.End(sResult)
        error_code = jData.End(sResult)
        # b. Esci dall'applicazione
        sys.exit(error_code)
    
    # 4. Definizione della funzione callback per eseguire comandi
    def cbCommands(dictJob):
        """
        Esempio di funzione callback per eseguire comandi.
        In un'applicazione reale, questa funzione conterrebbe la logica
        per eseguire il comando specificato in dictJob["COMMAND"].
        
        Args:
            dictJob (dict): Dizionario con parametri del job
            
        Returns:
            str: "" se successo, messaggio di errore altrimenti
        """
        command = dictJob.get("COMMAND", "")
        print(f"  [Callback] Esecuzione comando: {command}")
        
        # ESEMPIO: logica per diversi comandi
        if command == "NOME_AZIONE":
            # Simula elaborazione riuscita
            print(f"    Elaborazione per {command} completata")
            # Aggiorna risultati usando Return
            jData.Return("", "Elaborazione completata con successo")
            return ""
        elif command == "ERRORE_TEST":
            # Simula errore
            print(f"    Simulazione errore per {command}")
            jData.Return("Errore simulato", "Test di errore completato")
            return "Errore simulato"
        else:
            # Comando non riconosciuto
            error_msg = f"Comando non riconosciuto: {command}"
            print(f"    {error_msg}")
            jData.Return(error_msg, error_msg)
            return error_msg
    
    # 5. Esegui sResult=jData.Run(cbCommands)
    sResult = jData.Run(cbCommands)
    
    # 6. Esegui il metodo jData.End(sResult)
    error_code = jData.End(sResult)
    
    # 7. Esci dall'applicazione
    sys.exit(error_code)


# Punto di ingresso
if __name__ == "__main__":
    main()