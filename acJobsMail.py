
#!/usr/bin/env python3
# Nomefile: acJobsMail.py
# -*- coding: utf-8 -*-

"""
acJobsMail - Classe mixin per l'invio di mail
"""

import json
import subprocess
from typing import Dict, Any, Optional, Union, List
from copy import deepcopy
import aiSys


class acJobsMail:
    """
    Mixin per l'invio di mail ad amministratore o utente corrente.
    """
    
    def JobsMail(self, sTo: str, sSubject: str, sText: str, asFiles: List[str] = []) -> str:
        """
        Invia una mail tramite SMTP o OLK.
        """
        sProc = "JobsMail"
        sResult = ""
        
        # Verifica file allegati
        for sFile in asFiles:
            if not aiSys.FileExists(sFile):
                sResult = "File allegati non tutti esistenti"
                return aiSys.ErrorProc(sResult, sProc)
        
        if self.sMailEngine == "SMTP":
            if not hasattr(self, 'jMail') or self.jMail is None:
                sResult = "Mail engine non inizializzato"
            else:
                sResult = self.jMail.Send([sTo], sSubject, sText, asFiles, "TXT")
        
        elif self.sMailEngine == "OLK":
            # Crea file JSON per il processo esterno
            sJsonFile = aiSys.PathMake(self.sSys_PathOlk, "ntjobs_mail", "json")
            
            dictJson = {
                "config": {
                    "nWaitStart": 3,
                    "nWaitMail": 20,
                    "bOlkStart": True,
                    "bOlkEnd": False
                },
                "mail_1": {
                    "id": "mail_001",
                    "to": [sTo],
                    "cc": [""],
                    "ccn": [],
                    "subject": sSubject,
                    "format": "txt",
                    "body": sText,
                    "attach": asFiles
                }
            }
            
            try:
                with open(sJsonFile, 'w', encoding='utf-8') as f:
                    json.dump(dictJson, f, indent=2, ensure_ascii=False)
                
                sCmd = f"{self.sSys_PathOlk} {sJsonFile}"
                subprocess.Popen(sCmd, shell=True)
                
            except Exception as e:
                sResult = f"Errore invio mail OLK: {str(e)}"
        
        else:
            sResult = "Mail Engine non inizializzato"
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsMailAdmin(self, sSubject: str, sText: str) -> str:
        """
        Invia mail all'amministratore.
        """
        sProc = "JobsMailAdmin"
        sResult = ""
        
        sMail = self.Config("ADMIN.EMAIL")
        if sMail:
            sResult = self.JobsMail(sMail, sSubject, sText, [])
        
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsMailUser(self, sSubject: str, sText: str) -> str:
        """
        Manda una mail all'utente corrente.
        """
        sProc = "JobsMailUser"
        sResult = ""
        
        if hasattr(self, 'dictUser') and self.dictUser:
            sUserMail = self.dictUser.get("USER_MAIL", "")
            if sUserMail:
                sResult = self.JobsMail(sUserMail, sSubject, sText, [])
            else:
                sResult = "USER_MAIL non definito per l'utente corrente"
        else:
            sResult = "Nessun utente corrente"
        
        return aiSys.ErrorProc(sResult, sProc)


