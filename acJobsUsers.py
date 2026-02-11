
#!/usr/bin/env python3
# Nomefile: acJobsUsers.py
# -*- coding: utf-8 -*-

"""
acJobsUsers - Classe mixin per la gestione login/logoff utenti
"""

from typing import Dict, Any, Optional, Union, List
from copy import deepcopy
import aiSys


class acJobsUsers:
    """
    Mixin per la gestione dell'autenticazione utenti.
    """
    
    def JobsUserLogin(self) -> str:
        """
        Si occupa dell'autenticazione utente.
        """
        sProc = "JobsUserLogin"
        sResult = ""
        
        dictTemp = deepcopy(self.dictJobs["CONFIG"])
        sUserVerify = dictTemp.get("USER", "")
        
        if not sUserVerify:
            sResult = "USER non specificato in CONFIG"
        elif sUserVerify not in self.JOBS_TAB_USERS:
            sResult = f"Utente non trovato {sUserVerify}"
        
        if sResult == "":
            dictUserTemp = deepcopy(self.JOBS_TAB_USERS[sUserVerify])
            sUser = dictUserTemp.get("USER", "")
            
            if sUser:
                dictUserTemp["USER_GROUPS"] = aiSys.StringToArray(dictUserTemp.get("USER_GROUPS", ""), ",")
                self.sUser = sUser
                self.dictUser = deepcopy(dictUserTemp)
                print(f"Logon utente {sUser}")
            else:
                sResult = f"Credenziali non valide per utente {sUser}"
        
        self.Log0(sResult, f"Login utente {self.sUser if hasattr(self, 'sUser') else ''}, Risultato: {sResult}")
        return aiSys.ErrorProc(sResult, sProc)
    
    def JobsUserLogoff(self) -> str:
        """
        Logoff utente corrente e reset variabili.
        """
        sProc = "JobsUserLogoff"
        sResult = ""
        
        if hasattr(self, 'sUser') and self.sUser:
            self.Log(f"Logoff", f"Logoff utente {self.sUser}")
        
        self.dictUser = None
        self.sUser = ""
        
        return sResult


