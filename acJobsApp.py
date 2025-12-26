import sys
import os
import configparser
from typing import Callable, Optional, Dict
import aiSys

jData: Optional['acJobsApp'] = None 

class acJobsApp:
    def __init__(self):
        self.sName = os.path.basename(sys.argv[0])
        self.sFileIni = ""
        self.sJobEnd = ""
        self.bErrExit = False
        self.bExpand = False
        self.sLog = ""
        self.dictJob = {}             
        self.dictJobs = {} 
        self.dictConfig = {}          
        self.asKeyReserved = ["RETURN.TYPE", "TS.START", "TS.END", "RETURN.VALUE"]

    def AddTimestamp(self, target_dict: Dict[str, str], sKey: str = "TS.END"):
        # Nuovo formato tramite aiSys
        target_dict[sKey] = aiSys.Timestamp()

    def Log(self, sType: str, sValue: str):
        ts = aiSys.Timestamp()
        log_line = f"{ts}.{sType}: {sValue}"
        print(log_line)
        if self.sLog:
            try:
                with open(self.sLog, 'a', encoding='utf-8') as f:
                    f.write(log_line + "\n")
            except: pass 

    def Log0(self, sResult: str, sValue: str = ""):
        sVal = sValue if sValue else ""
        if sResult:
            self.Log("ERR", f"{sResult}: {sVal}" if sVal else sResult)
        else:
            self.Log("INFO", sVal)

    def Config(self, sKey: str) -> str:
        return self.dictConfig.get(sKey.upper().replace(" ", ""), "")

    def Start_Expand(self):
        print("Esecuzione Start_Expand")
        # Utilizzo della nuova funzione aiSys.ExpandDict
        aiSys.ExpandDict(self.dictJobs, self.dictConfig)

    def Start(self) -> str:
        sProc = "Start"
        print(f"Esecuzione {sProc}")
        args = sys.argv[1:]
        if not args or not args[0].lower().endswith(".ini"):
            sRes = self.MakeIni()
            if sRes: return sRes
        else:
            self.sFileIni = os.path.abspath(args[0])

        if not os.path.exists(self.sFileIni):
            return f"File non trovato: {self.sFileIni}"

        self.sJobEnd = os.path.splitext(self.sFileIni)[0] + ".end"
        parser = configparser.ConfigParser(interpolation=None)
        parser.optionxform = str 
        try:
            parser.read(self.sFileIni, encoding='utf-8')
        except Exception as e:
            return str(e)

        for section in parser.sections():
            sec = section.upper().replace(" ", "")
            self.dictJobs[sec] = dict(parser.items(section))

        if "CONFIG" not in self.dictJobs: return "Sezione [CONFIG] mancante."
        
        self.dictConfig = self.dictJobs["CONFIG"].copy()
        self.AddTimestamp(self.dictConfig, "TS.START")
        
        self.bExpand = aiSys.StringBoolean(self.Config("EXPAND"))
        if self.bExpand:
            self.Start_Expand()
        
        self.dictJobs["CONFIG"] = self.dictConfig.copy()
        self.sLog = self.Config("LOG")
        self.bErrExit = aiSys.StringBoolean(self.Config("EXIT"))
        
        self.Log0("", f"Start {self.sName} {self.sFileIni}")
        return ""

    def Run(self, cbCommands: Callable[[], str]) -> str:
        print("Esecuzione Run")
        sResult = ""
        for sKey in list(self.dictJobs.keys()):
            if sKey == "CONFIG": continue
            self.dictJob = self.dictJobs[sKey]
            self.sCommand = self.dictJob.get("COMMAND", "")
            sResult = cbCommands()
            self.dictJobs[sKey] = self.dictJob
            self.Log0(sResult, f"Esecuzione {self.sCommand}.Run conclusa")
            if self.bErrExit and sResult: return sResult 
        return sResult 

    def End(self, sResult_main: str):
        print("Esecuzione End")
        nResult = 0
        if not self.dictJobs: nResult = 1
        elif sResult_main: nResult = 2

        if nResult > 0:
            dicErr = {"RETURN.TYPE": "E", "RETURN.VALUE": sResult_main}
            self.AddTimestamp(dicErr, "TS.END")
            self.dictConfig.update(dicErr)
            self.dictJobs["CONFIG"] = self.dictConfig.copy()

        if self.sJobEnd:
            parser = configparser.ConfigParser(interpolation=None)
            parser.optionxform = str
            for section, params in self.dictJobs.items():
                if section == "CONFIG" and "TS.END" not in params:
                    self.AddTimestamp(params, "TS.END")
                parser.add_section(section)
                for k, v in params.items(): parser.set(section, k, str(v))
            with open(self.sJobEnd, 'w', encoding='utf-8') as f: parser.write(f)

        self.Log0(sResult_main, f"Fine {self.sName}")
        if nResult != 0: sys.exit(nResult)