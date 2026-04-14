
#!/usr/bin/env python3
# Nomefile: aiJobsOS.py
# -*- coding: utf-8 -*-

"""
aiJobsOS - Applicazione principale
Orchestratore di batch processing basato su file system.
"""

import os
import sys
import time

# Assicura che il path di aiJobsOS sia nel sys.path
if 'K:\\aiJobsOS' not in sys.path:
    sys.path.append('K:\\aiJobsOS')

from acJobsOS import acJobsOS
import aiSys


def Start() -> None:
    """
    Funzione principale di avvio.
    Istanzia jData, esegue JobsStart e il ciclo principale.
    """
    sProc = "Start"
    
    # Istanzia jData
    jData = acJobsOS()
    
    # Esegue JobsStart
    sResult = jData.JobsStart()
    
    if sResult == "":
        jData.bExitOS = False
        
        # Ciclo principale
        while not jData.bExitOS:
            sResult = jData.Run()
            
            if sResult != "":
                jData.Log("Errore", f"Errore in Esecuzione Run: {sResult}")
            
            jData.CycleEnd()
    
    print("Uscita dall'applicativo")
    sys.exit(0)


if __name__ == "__main__":
    Start()