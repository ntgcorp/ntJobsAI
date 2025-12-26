# ntJobsPy Framework
# CORE LIBRARY - DataTypes - OS - Basic Files - Process - Date
# Altre su nlExt dove vengono spostate le meno usate
# --------------------------------------------------------------------
# Lib per gestione path e files
from pathlib import Path
# For NF_File*
import os
# For NF_FileDelete (rmdir)
import shutil
# For NF_PathFind + NF_FileCopy
import glob
# For Exec & Kill
import subprocess
import signal
#import platform
# Lib per CheckEmail ed Altri Check
import re
# Per Ambiente
from sys import platform as sys_platform
# Lib per gestione Replace
from string import Template
# Per Wait e Date
import time
from datetime import datetime
# Per File Temporanei
import tempfile
# Per Argomenti (NF_Args)
import sys, argparse
# Per 
import configparser

# Setup: TEST o NO
NT_ENV_TEST_SYS=True
# ENCODING
NT_ENV_ENCODING="utf-8"
# YYYYMMDD.HHMMSS.MSEC
NT_ENV_DATE_DIV="."

# ----------------------- DA ARG A DICT ---------------------------
# Ritorna Dictionary. N:Valore
# Optional Arguments. Array "-argLight", "-arg", "help", required_true, default
# Result lResult. 0=sResult, 1=dictArgs o vuoto dict
def NF_Args(axArgs=None):
    if axArgs is None: axArgs = []
    sProc="NF_Args"
    bParse=False
    sResult=""
    dictArgs={}

# Facolativi
    NF_DebugFase(True,"Parametri per parsing Argomnenti:"  + str(axArgs), sProc)
    parser = argparse.ArgumentParser()
    parser.parse_args() 
    for xArg in axArgs:
        print("Argument " + xArg[0] + ": " + len(xArg))
        if len(xArg)==3:
# Caso 1: Nome parametro, help, required, default
            parser.add_argument(xArg[0],help=xArg[1],required=xArg[2],default=xArg[3])
            bParse=True
        elif len(xArg)==5:
        # Caso 2: light, No-à-me parametro, help, required, default
            parser.add_argument(xArg[0],xArg[1],help=xArg[2],required=xArg[3],default=xArg[4])
            bParse=True
        else:
            pass

# Converte in Dictionary con 2 modalità
    NF_DebugFase(True,"Parsing Argomenti (" + str(bParse) + "), Argomenti: " + str(sys.argv), sProc)
    if bParse==True:
        parser=argparse.ArgumentParser()
        dictArgs=vars(parser.parse_args())
# Converte in Dictionary 0:Arg1, 1:Arg2
    else:
        #   lResult[0]: Diagnostica di ritorno. ""=NoError,
        #   lResult[1]: Dict,
        lResult=NF_DictFromArr([],sys.argv[1:])
        sResult=lResult[0]
        if sResult=="":
            dictArgs=lResult[1]
# Ritorno
#    NF_DebugFase(True,"End",sProc)
    lResult=[sResult, dictArgs]
    return lResult

# ----------------------- FUNZIONI DI BASE ---------------------------

# IIF che in python non c'è
def iif (bExpr, trueResult, falseResult):
    if bExpr: return trueResult
    else: return falseResult

def NF_Kill(**kwargs):
    sProc="NF_Kill"
    sResult=""
    PID=0

# Parameters
# Iterating over the Python kwargs dictionary
    for key, value in kwargs.items():
        if key=="pid":
            PID=value
        else:
            sResult="key invalid " + key
# Try Kill
    try:
        if sys_platform != 'win32':
            os.kill(PID, signal.SIGKILL)
        else:
            os.kill(PID, signal.SIGTERM)
    except Exception as e:
        sResult=getattr(e, 'message', repr(e)) + "kill process " + str(PID)

# Ritorno
    return NF_ErrorProc(sResult, sProc)

# Execute External program
# action: tipo di exec
# cmd=Path da eseguire
# args=argomenti
# Ritorno: lResult
# 0=sResult, 1=paction(="" no), 2=command esecuzione, 3=arg,
def NF_Exec(**kwargs):
    sProc="NF_Exec"
    sResult=""
    sExec_cmd=""
    sExec_action=""
    vExec_pid=None
    sExec_args=""

# Iterating over the Python kwargs dictionary
    for key, value in kwargs.items():
        if key=="cmd":
            sExec_cmd=value
        elif key=="args":
            sExec_args=value
        elif key=="action":
            sExec_action=value
        else:
            sResult="key invalid " + key

# Test CMD
    if sExec_cmd=="":
        sResult="command line empty"

# Esecuzione - Caso Base
    if sResult=="":
        if sExec_action=="":
            try:
                vExec_pid=subprocess.call(sExec_cmd + " " + str(sExec_args))
                if vExec_pid<0: sResult="Errore in esecuzione: " + str(vExec_pid)
            except OSError as e:
                sResult="Errore Esecuzione " + str(e)
    else:
        sResult=f"Action not found {sExec_action}"

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    lResult=[sResult, vExec_pid, sExec_action, sExec_cmd, sExec_args]
    return lResult

# Return String on Condition
def NF_Assert(bCondition=False,sResultTrue="",sResultFalse="",sProc=""):
    sPrefix=iif(sProc!="", sProc+": ", "")
    if bCondition:
        return sPrefix + sResultTrue
    else:
        return sPrefix + sResultFalse

# Return String on Condition
def NF_AssertPrint(bCondition=False,sResultTrue="",sResultFalse="",sProc=""):
    sAssert=NF_Assert(bCondition,sResultTrue,sResultFalse,sProc)
    if sAssert != "": print(sAssert)
    return sAssert

# Attesa
def NF_Wait(nSecondi):
    time.sleep(nSecondi)

# ---------------------- FILES & PATH  -----------------------

# Copia File con vari attributi di copia. Prima su file temporaneo poi su dest con eventuale tenuta old
# Source=File, Dest=FileDest/PathDest
# Opzionali:
# - replace: No Errore se esiste e sovrascrive
# - pathdest: Dest è un path non un file
# - oldtake: NotKill Old if Replace
# - spath=Source è un wildargs - NON IMPLEMENTATO
# - bMove(move). Spostamento

# DA VERIFICARE
def NF_FileCopy(sSource: str, sDest: str, **kwargs):
    sProc="File.Copy"
    sResult=""
    bPathDest=False
    bMove=False
    sFileDest=""
    sPath=sFile=sExt=""
    bOld=False
    sFileTemp=""

# Parametri e Verifica
    dictVerify={"bool": ("replace","pathdest","oldtake")}
    sResult=NF_ParamVerify(dictVerify)
    if sResult=="":
        bReplace=NF_DictGet(kwargs, "replace",False)
        bPathDest=NF_DictGet(kwargs,"pathdest",False)
        bMove=NF_DictGet(kwargs,"move",False)
        bSpath=NF_DictGet(kwargs,"spath",False)
        bOld=NF_DictGet(kwargs,"oldtake",False)

# Sistemazioni
    if bPathDest:
        sPath,sFile,sExt=NF_PathScompose(sSource)
        sFileDest=NF_PathMake(sDest,sFile,sExt)
        # File Temp - Prima copia su file temp poi rename in base a gestione duplicati
        sFileTemp=NF_PathMake(sDest,sFile,"temp")
    else:
        sFileDest=sDest

# Copia
    if sResult=="":
        try:
            shutil.copy(sSource, sDest)
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + "fle copy " + sSource + ", in " + sDest
# disabilitato 10/5/25 per problemi da rivedere
# Gestione in caso ci sia già. Se Tenere Old già rinomina
#    if sResult=="":
#        if NF_FileExist(sDest):
#            if bOld:
#                sFileOld=NF_PathMake(sDest, str(sFile) + "_old", sExt)
#                sResult=NF_FileRename(sFileDest,sFileOld)
#            else:
#                sResult=NF_FileDelete(sFileDest)

# Rinomina Temp in Dest
#    if sResult=="":
#         sResult=NF_FileRename(sFileTemp,sFileDest)

# Toglie sorgente, tenendo conto old anche qui
    if sResult=="" and bMove:
        if bOld:
            sFileOld=NF_PathMake(sSource + "_old",sExt)
            sResult=NF_FileRename(sSource, sFileOld)
        else:
            sResult=NF_FileDelete(sSource)

# Uscita
    return NF_ErrorProc(sResult,sProc)

# Move: - copy wrapped
def NF_FileMove(sSource: str,sDest: str):
    sResult=""
    sProc="File.Move"

# Default MOVE e DEST=PATH
    sResult=NF_FileCopy(sSource,sDest,pathdest=True, move=True)

# Uscita
    return NF_ErrorProc(sResult,sProc)

# Ritorna Errore Standard NF_FileExist o "" come stringa.
def NF_FileExistErr(sFilename):
    sResult=iif(NF_FileExist(sFilename),"","Non Esistenza file " + sFilename)
    return sResult

# Alias File Exist
def NF_FileExist(sFilename):
    return os.path.exists(sFilename)

# Ritorna doppio risultato.
# - sResult. "" o Errore
# - sFilename originale o rimappato con currentdirscript se esiste
def NF_FileExistMap(sFilename: str):
    sProc="File.Exist.Map"
    sResult=""

    if NF_FileExist(sFilename):
        sFileNew=os.path.abspath(sFilename)
    else:
        sFileNew=NF_PathAddSlash(os.getcwd()) + sFilename
        sResult=NF_FileExistErr(sFileNew)
        if sResult=="":
            print("File Rimappato in " + sFileNew)

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult,sFileNew

# String o Binary to File o viceversa
# sResult=Tipo di errore
def NF_FileWrite(sFilename: str, sText:str, sAttr: str):
    sResult=""
    sProc="File.Write"
    bOpen=False

# Verifica parametri
    if NF_ArrayFind(("w","a"), sAttr)<0: sResult="parametro: " + sAttr

# Apertura File
    if sResult=="":
        lResult=NF_FileOpen(sFilename,sAttr)
        sResult=lResult[0]

# Write string to file
    if sResult=="":
        hFile=lResult[1]
        bOpen=True
        try:
            hFile.write(sText)
        except (IOError, OSError) as e:
            sResult=getattr(e, 'message', repr(e)) + "scrittura su file aperto " + sAttr + ", " + sFilename

# Close file if Open
        if bOpen: hFile.close()

# Uscita
    return NF_ErrorProc(sResult,sProc)

# String o Binary to File o viceversa
# sResult=Tipo di errore
# Ritorna lResult. 0=sResult, 1=Text
def NF_FileRead(sText: str, sFilename: str, sAttr: str):
    sResult=""
    sProc="File.Read"
    bOpen=False

# Verifica parametri
    if NF_ArrayFind(("r", "rb"),sAttr)<0: sResult="parametro: " + sAttr

# Open Text File
    if (sResult==""):
        try:
            hFile = open(sFilename, mode=sAttr, encoding=NT_ENV_ENCODING)
        except:
            sResult="apertura file con attributo " + sAttr + ", " + sFilename
# Read string from file
        bOpen=True
        if sResult=="":
            try:
                hFile.read(sText)
            except:
                sResult=f"Lettura file con attributo {sAttr},{sFilename}"
# Close file
        if bOpen: hFile.close()
# Uscita
    return NF_Result(sResult,sProc,sText)

# Path.Rename
# F=File(Default), D=Directory, T=Directory e Contenuto
def	NF_FileDelete(sFile: str, sType="F"):
    sProc="NF_FileDelete"
    sResult=""

# Cancellazione
    try:
        if (sType=="F") :
            os.remove(sFile)
        elif (sType=="D"):
            os.rmdir(sFile)
        elif (sType=="T"):
            shutil.rmtree(sFile)
        else:
            sResult="Tipo non supportato in FileDelete " + sType
    except Exception as e:
        sResult=getattr(e, 'message', repr(e)) + "cancellazione file " + sFile

# Uscita
    return NF_ErrorProc(sResult,sProc)

def NF_FileWriteLine(file_handle, variable, sMode="l"):
    """
    Writes a variable to an already opened file with different modes.
    Returns empty string on success, error message on failure.
    
    Args:
        file_handle: An already opened file handle
        variable: The variable to write (any type)
        sMode: Write mode:
            "b" - binary mode (variable must be bytes)
            "s" - string mode (no newline added)
            "l" - string mode with newline added (default)
    
    Returns:
        str: Empty string if successful, error message if failed
    """
    try:
        if sMode == "b":
            if not isinstance(variable, bytes):
                return "Error: For binary mode, variable must be bytes"
            file_handle.write(variable)
        elif sMode in ("s", "l"):
            str_value = str(variable)
            if sMode == "l":
                str_value += "\n"
            file_handle.write(str_value)
        else:
            return f"Error: Invalid mode '{sMode}'. Use 'b', 's', or 'l'"
        
        return ""  # Empty string indicates success
        
    except (IOError, OSError) as e:
        return f"Error: File write failed - {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"
    
# Open File
# Attr: w=Write, a=Append, r=readonly, x=Create if not exist
# Return lResult. 0=sResult, 1=Handle/None
def NF_FileOpen(sFilename: str,sAttr: str,**kwargs):
    sResult=""
    sProc="File.Open"

# Scan kwargs
    vEncoding=NT_ENV_ENCODING
    for key, value in kwargs.items():
        if key=="encoding":
            vEncoding=value
# Apertura
    try:
        hFile = open(sFilename, mode=sAttr, encoding=vEncoding)
    except Exception as e:
        sResult=getattr(e, 'message', repr(e)) + "Apertura file modo " + sAttr + ", " + sFilename
# Uscita
    sResult=NF_ErrorProc(sResult,sProc)
    if sResult=="":
        lResult=[sResult,hFile]
    else:
        lResult=[sResult,None]
# Ritorno
    return lResult

# Path.Rename
def	NF_FileRename(sPathIn: str, sPathOut: str):
    sProc="NF_FileRename"
    sResult=""
# Rename
    try:
        os.rename(sPathIn, sPathOut)
    except Exception as e:
        sResult="Rinomina path " + sPathIn + " in " + sPathOut

# Uscita
    return NF_ErrorProc(sResult,sProc)

# INI: Ritorna Sezioni lette come dict di dict in lResult
# Parametro: Nomefile già normalizzato
# Ritorno lResult
# 0=sResult
# 1=Dizionario di Dizionari, dove Key=Sezione
# -----------------------------------------------------------------------------
def NF_INI_Read(sFileINI: str):
    sProc="NF_INI_Read"
    sResult=""
    dictINI=dict()

# Verifica esistenza
    sResult=NF_FileExistErr(sFileINI)

# Lettura INI Fase 1
    if sResult=="":
        try:
            config=configparser.ConfigParser(allow_no_value=True)
            config.read(sFileINI)
            asSections=config.sections()
        except:
            sResult="apertura file INI " + sFileINI

# Lettura INI Fase 2
    if (sResult==""):
    # Legge SEZIONE->KEYS, crea dict per ogni sections che aggiunge in dictINI
        for sSection in asSections:
            dictSection=dict()
            #Lettura KEYS
            for sKey in config[sSection]:
                vValue=config[sSection][sKey]
                # La chiave viene Trimmata+UCase
                sKey=NF_StrNorm(sKey)
                # Trim Value e Str per sicurezza
                vValue=(str(vValue)).lstrip().rstrip()
                # Assegnazione di ritorno
                dictSection[sKey]=vValue
            # Assegna KEYS a SEZIONE
            NF_DebugFase(NT_ENV_TEST_SYS, ", Tipo dictSection: " + str(type(dictSection)), sProc)
            dictINI[sSection]=dictSection.copy()

# Fine ciclo lettura INI
    sResult=NF_ErrorProc(sResult,sProc)
    return [sResult,dictINI]

# INI: Salva
# Nomefile già normalizzato. SEMPRE IN SCRITTURA. sE UPDATE USARE NF_INI_Update
# Passato in forma dict di dict
# Parametri:
#  sFileINI=File
#  dictINIs=INI doppio livello, sezione->dict
#  sAttr=Attributo scrittura, w/a (non r)
# Ritorna sResult
# -----------------------------------------------------------------------------
def NF_INI_Write(sFileINI:str, dictINIs: dict, sAttr="w"):
    sProc="NF_INI_WRITE"
    sResult=""
    sGroup=""

# Verifica
    if (sAttr != "w") and (sAttr != "a"): sResult="Attributo errato: " + sAttr

# Setup
    if sResult=="":
        config = configparser.ConfigParser()
# Per tutte le chiavi. Se inizia per #=Nome Sezione
        sResult,asGroup=NF_Return2(NF_DictKeys(dictINIs))

        for sGroup in asGroup:
# Aggiunge Sezione 
            sGroup=str(sGroup)
            if sGroup=="":sGroup="CONFIG"
            if not config.has_section(sGroup): config.add_section(sGroup)
# Prende Dizionario Sezione
            dictINI={}
            dictINI=NF_DictGet(dictINIs,sGroup,{})            
# Verifica che sia dizionario            
            if NF_IsDict(dictINI)==False:
                sResult="Formato errato, nodo INI non tipo dict. Key: " + sGroup
                break
            else:
                lResult2=NF_DictKeys(dictINI)
                asKeys=lResult2[1]
                for vKey in asKeys:                    
                    sValue=NF_DictGet(dictINI,vKey,"")
                    print(f"Proc: {sProc}, Group: {sGroup}, Key: {vKey} V: {sValue}")
                    config.set(sGroup,str(vKey),str(sValue))
# Salva File
    if sResult=="":
        sResult,hFile=NF_Return2(NF_FileOpen(sFileINI,sAttr))        
    if sResult=="":
        config.write(hFile)
    # Chiusura file
        hFile.close()

# Ritorno Scrittura
    return NF_ErrorProc(sResult,sProc)

# INI: Update
# Se esiste lo legge e update del dict passato come parametro
# Parametri: sFileINI, dictINIs (con sezione)
# Ritorno: sResult
# -----------------------------------------------------------------------------
def NF_INI_Update(sFileINI, dictINIs_update):
    sProc="NF_INI_Update"
    sResult=""

# Se non Esiste va a INI_Write ed ESCE
    if NF_FileExist(sFileINI):
# Legge INI
        sResult,dictINIs_read=NF_Return2(NF_INI_Read(sFileINI))
        if sResult=="":            
        # Merge (del tipo 2o livello)
            dictINIs_read=NF_DictMerge2(dictINIs_read, dictINIs_update)
        # Salva dictINI
            sResult=NF_INI_Write(sFileINI, dictINIs_read)
# Ritorno Scrittura
    return NF_ErrorProc(sResult,sProc)

# Create Path
def NF_PathCreateDir(sPath):
    sProc="NF_PathCreateDir"
    sResult=""
  
    try:
        os.makedirs(sPath)
    except OSError:
        sResult="Error creating {sPath}"
    if sResult=="":
        try:
            os.chdir(sPath)
        except OSError:
            sResult="Error creating/chdir {sPath}"
# Uscita
    return NF_ErrorProc(sResult,sProc)

# Path Temporaneo. Parametri: sPathBase, sPrefix, Type="FD"
# Ritorno: lResult 0=sResult, 1=PathCreato
def NF_PathTemp(sPathBase="", sPrefix="", sType="F"):
    sProc="NF_PathTemp"
    sResult=""
    sPath=""

# Creazione
    if sType=="D":
        try:
            sPath=tempfile.mkdtemp(prefix=sPrefix, dir=sPathBase)
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + f", Creazione Temp Path {sPathBase}"
    elif sType=="F":
        try:
            outfile=tempfile.NamedTemporaryFile(delete=False, dir='/tmp/myfolder')
            sPath=outfile.name
            outfile.close
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + f"Creazione Temp Path tipo {sType}"
    else:
        sResult=f"Type invalid {sType}"

# Uscita
    return [NF_ErrorProc(sResult,sProc),sPath]

# Path.Copy/XCopy
# F=Singolo File P=Path, (F=File), D=Dir
def NF_PathCopy(sPathIn, sPathOut, sType="F"):
    sProc="NF_PathCopy"
    sResult=""

# Flags
    bDir=NF_StrFind(0,sType,"D") != -1
    bPath=NF_StrFind(0,sType,"P") != -1
    bFile=(NF_StrFind(0,sType,"F") != -1) or (sType=="F")

# Rename
    try:
        if bDir: shutil.copytree(sPathIn, sPathOut)
        if bPath: shutil.copyfile(sPathIn, sPathOut)
        if bFile: shutil.copy(sPathIn, sPathOut)
    except:
        sResult="Copia " + sPathIn + " in " + sPathOut + ", Type: " + sType

# Uscita
    return NF_ErrorProc(sResult,sProc)

# Verifica esiste una caartella
# Ritorno: True=Ok
def NF_PathDirExists(sPath):
    return Path(sPath).is_dir()

# Cerca un Path, anche ricorsivo con jolly e crea un array di files
# R=Recursivo. 
# Ritorna lResult, 0=Risultato, 1=Lista
# Generata con DeepSeek Prompt PathFind
def NF_PathFind(sPath: str, sType=""):
    sResult = ""
    aResults = []
    
    # Validazione parametri
    if not sPath:
        sResult = "sProc=PathFind, Error: Path is empty"
        return sResult, aResults
    
    # Imposta il valore di default se sType è vuoto
    if not sType:
        sType = "F"
    
    # Controlla combinazioni non valide in sType
    if ('D' in sType and ('X' in sType or 'F' in sType)) or \
       ('F' in sType and 'X' in sType):
        sResult = "sProc=PathFind, Error: Invalid sType combination"
        return sResult, aResults
    
    # Determina se la ricerca è ricorsiva
    recursive = 'R' in sType
    
    # Determina cosa cercare
    find_files = 'F' in sType
    find_dirs = 'D' in sType
    find_both = 'X' in sType
    
    if find_both:
        find_files = True
        find_dirs = True
    
    # Se non è specificato nulla, cerca solo files (default)
    if not find_files and not find_dirs:
        find_files = True
    
    try:
        if recursive:
            # Ricerca ricorsiva
            for root, dirs, files in os.walk(sPath):
                if find_dirs:
                    for d in dirs:
                        full_path = os.path.join(root, d)
                        if glob.fnmatch.fnmatch(full_path, sPath) or glob.fnmatch.fnmatch(d, os.path.basename(sPath)):
                            aResults.append(full_path)
                
                if find_files:
                    for f in files:
                        full_path = os.path.join(root, f)
                        if glob.fnmatch.fnmatch(full_path, sPath) or glob.fnmatch.fnmatch(f, os.path.basename(sPath)):
                            aResults.append(full_path)
        else:
            # Ricerca non ricorsiva
            items = glob.glob(sPath)
            for item in items:
                if os.path.isdir(item) and find_dirs:
                    aResults.append(item)
                elif os.path.isfile(item) and find_files:
                    aResults.append(item)
        
        # Elimina eventuali duplicati
        aResults = list(set(aResults))
        aResults.sort()
        
    except Exception as e:
        sResult = f"sProc=PathFind, Error: {str(e)}"
    
    return sResult, aResults

# Path dello script corrente
# Type SCRIPT, ID.NE, PATH, NO.TYPE
def NF_PathScript(sType):
    sResult=""

    if sType=="SCRIPT":
        sResult=__file__
    elif sType=="ID.NE":
        sResult=os.path.splitext(os.path.basename(__file__))[0]
    elif sType=="PATH":
        sResult=NF_PathAddSlash(os.path.dirname(os.path.abspath(__file__)))
    else:
        sResult="NO.TYPE"
# Ritorno
    return sResult

# Remapping sFileIn, sFileOut
# Return 3 parameters. sResult, New FileIn, New FileOut
def NF_PathRemapInOut(sFileIn,sFileOut,sExtOut):
    sResult=""
    sProc="PathRemapInOut"

# Check FileIn Exist
    sResult,sFileIn=NF_FileExistMap(sFileIn)

# FileOut create
    if sResult=="":
        if sFileOut=="" or sFileOut=="#":
            sPath,sFile,sExt=NF_PathScompose(sFileIn)
            NF_DebugFase(True, "FileIn. Path: " + sPath + ", File: " + sFile + ", Ext: " + sExt, sProc)
            sFileOut=sPath + sFile + "." + sExtOut
            NF_DebugFase(True, "FileOut " + sFileOut, sProc)

# Fine
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult,sFileIn,sFileOut

# Path Rimappato con Dir Corrente
# Argomenti per ora non usato
def NF_PathCurDir(*args):
    sResult=""
    sCurDir=os.getcwd()
    sPath=""

# Path da Agganciare
    if len(args)>0: sPath=str(args[0])

# Ritorno
    sResult=NF_PathAddSlash(sCurDir) + sPath
    return sResult

# Add Slash a Path.
def NF_PathAddSlash(sPath: str):

# Slash per OS
    sSlash=iif(NF_IsWindows(),"\\","/")
# Check Add
    bAdd=NF_StrRight(sPath,1) != sSlash
# Ritorno
    sResult=sPath+iif(bAdd,sSlash,"")
    return sResult

# PathMake File e Cartella. Non aggiunge "\" alla fine
# Parametri: Path, File, Ext
def NF_PathMake(sPath: str, sFile: str, sExt=""):
    sResult=""
# Setup
    sResult=sPath
# Aggiunge File, prima eventuale slash
    if sFile != "": sResult = NF_PathAddSlash(sResult) + sFile
# Aggiunge Ext
    if sExt != "": sResult = sResult + "." + sExt
# Ritorno
    return sResult

# Split Path in Path,File,Ext
# Ritorna tre parametri path,name,ext
def NF_PathScompose(sFilePath: str):
    sPath = NF_PathAddSlash(os.path.dirname(sFilePath))
    sExt = os.path.splitext(sFilePath)[1][1:]
    sFileName=os.path.basename(sFilePath)
    sName= sFileName.rsplit('.', 1)[0]
    #print("Path: " + sPath + ", Name: " + sName + ", Ext: " + sExt)
# Ritorno
    return sPath,sName,sExt

# Normalizza Path con verifiche ed estraendo componenti
# Ritorno lResult
# 0=Ritorno, 1=Dir, 2=File, 3=Ext, 4=FileConExt, 5=FileNormalizzato
# Result=Eventuale errore
def NF_PathNormal(sFileIn: str):
    sProc="NF_PathNormal"
    sPath=""
    sExt=""
    sFile=""
    sFileExt=""
    aExt=[""]
    lResult=[]
    sResult=""

# Null
    if (sFileIn==""):
        sResult="No Input file"
        return NF_Result(sResult, sProc, [])

# Setup: CurDir, gestisce slash di default e su file passato come parametro
    sCurdir=os.getcwd()
    sFileIn=str(sFileIn)
    sSlash=iif(NF_IsWindows(), "\\","/")
    sFileIn=sFileIn.replace(iif(NF_IsWindows(),"/","\\"),sSlash)

# Aggiunge directory corrente se path relativo o nullo
    sPath=os.path.dirname(sFileIn)
    if os.path.isabs(sPath) == False:
        sPath=sCurdir + sSlash + sPath
        sFileIn=sCurdir + sSlash + sFileIn

# Split in array 2 (almeno uno ci sarà anche se vuoto)
    sFileExt=os.path.basename(sFileIn)
    aExt=sFileExt.split(".")
    sFile=aExt[0]
    if len(aExt)>1: sExt=aExt[1]

# Test code
#   if NT_ENV_TEST_SYS == True:
#        print ("TEST TYPES P: " + type(sPath).__name__ + ", F: " + type(sFile).__name__ + ", E: " + type(sExt).__name__)
#        print(sProc + ": " + "File.IN: " + sFileIn)
#        print(sProc + ": " + "Path,File,Ext. P:" + sPath + ", F:" + sFile + ", E:" + sExt)

# LResult
# 0=Ritorno, 1=Dir, 2=File, 3=Ext 4=FileConExt, 5=FileNormalizzato
    lResult=["",sPath,sFile,sExt,sFileExt,sFileIn]
    #if NT_ENV_TEST_SYS == True: print (sProc + ": " + str(lResult))
    return lResult

# Tipo di PATH. N=Non Esiste, F=File, D=Dir
def NF_PathType(sFile: str):
    sResult=""

# Calcolo
    path=Path(sFile)
    if os.path.exists(sFile)==False: sResult="N"
    if path.is_file(): sResult="F"
    if path.is_dir(): sResult="D"

# Ritorno
    return sResult

# ----------------------------- PARAMETRI ------------------------------

# Parametri:
# dictParams=dictionary parametri
# exist(array): Quali devono esistere obbligatoriamente
# num(arrray): Quali devono essere nuemerico
# fexist(array): File che devono esistere
# dexist(array): Path che devono esistere (vuoti o no)
# alnum(array): alphanumeric
# dict(dictionary): deve essere un dizionario
# list(array): deve essere una lista
def NF_ParamVerify(dictParams, **kwargs):
    sProc="PARAN.VERIFY"
    sResult=""

# dictionary parametri
    if NF_DictLen(dictParams)<1:
        sResult="No params"
        return sResult

# Parametri check, Crea sResult aggiungendo sTemp ad ogni verifica
    for key,value in kwargs.items():
        sTemp=""
        if key=="exist":
            for vItem in value:
                vValue=NF_DictGet(dictParams,vItem)
                if len(str(vValue))==0: sResult=sResult + "not exist" + vItem
        elif key=="num":
            for vItem in value:
                vValue=str(NF_DictGet(dictParams,vItem))
                if (vValue.isnumeric()) == False: sTemp="not numeric" + vItem
        elif key=="fexist":
            for vItem in value:
                sFilename=str(NF_DictGet(dictParams,vItem))
                if (NF_FileExist(sFilename)==False): sTemp="file not exist " + vItem
        elif key=="dexist":
            for vItem in value:
                vValue=str(NF_DictGet(dictParams,vItem))
                if NF_PathDirExists(vValue)==False: sTemp="dir not exist " + vItem
        elif key=="alnum":
            for vItem in value:
                vValue=str(NF_DictGet(dictParams,vItem))
                if vValue.isalnum==False: sTemp="not alphanum " + vItem
        elif key=="dict":
            if NF_IsDict(value)==False: sTemp="not dict" + vItem
        elif key=="list":
            if NF_IsArray(value)==False: sTemp="not dict" + vItem
        else:
            sResult="check type errato: " + str(key)
        if len(sTemp)>0: sResult = sResult + ": " + sTemp
# Ritorno
    return NF_ErrorProc(sResult, sProc)

# ------------------------------- TEMPO E DATE -------------------------

# Differenza tra due timestamp

# Da Dict a TS
# Input:
#   dtDateTime, output (S o D)
# Ritorna sResult,sTS (sResult!="" errore)
# sOutput. S=TS.String, D=Date
def NF_TS_FromDict(dtDate, sOutput="S"):
    dictID={0:"Y", 1:"M", 2:"D", 3:"HH", 4:"MM", 5:"SS", 6:"DW", 7:"DY", 8:"DY", 9:"IY", 10:"YW", 11:"YD"}
    sProc="TS_FromDict"
    sResult=""
    dtTS=None
    vDateResult=""

# Verifica
    if NF_DictLen(dtDate) != 12:
        sResult="Error dict param"
    for sKey in dtDate.Keys():
        if NF_DictExistKey(dictID,sKey)==-1:
            sResult="Error key not found " + sKey
            break

# Composizione
    if sResult=="":
        dtTS=datetime.datetime(dtDate["Y"],
            dtDate["M"],
            dtDate["D"],
            dtDate["HH"],
            dtDate["MM"],
            dtDate["SS"])

# Composizione
    if sOutput=="S":
        VDateResult=NF_TS_ToStr()
    elif sOutput=="D":
        vDateResult=dtTS
    else:
        sResult="Output reslt not correct " + sOutput

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult, vDateResult

# Da formato Data a Stringa
# Input:
#    dtDate: Data Input
# Opzionali
#    sType=(sType, default="B"): Aggiunge IsoCalendar o No, Type=B=Base(def), N=Normal, X=Esteso
# Ritorno
#    sTS(TimeStamp)

def NF_TS_ToDict(dtDate, sType="B"):
# Setup
    tt=dtDate.timetuple
    dictTime=dict()
    nID=0
    dictID={0:"Y", 1:"M", 2:"D", 3:"HH", 4:"MM", 5:"SS", 6:"DW", 7:"DY", 8:"DY", 9:"IY", 10:"YW", 11:"YD"}
    sProc="TS.ToDict"
    sResult=""
# Scomposizione
# Assegna e incrementa Indice
    for nValue in tt:
    # Conversione nID->sID
        sID=dictID[nValue]
        dictTime[sID]=nValue
        nID=nID+1
    # Aggiunge IC (Tipo N/X)
    if (sType!="B") :
        ic=dtDate.isocalendar()
        for nValue in ic:
            sID=dictID[nValue]
            dictTime[sID]=nValue
            nID=nID+1
# Ritorno
    return dictTime

# TIMESTIME: ToStr Quello attuale
# Parametri:
#  sType: L(default)=YYYYMMDD.HHMMSS, X=YYYYMMDD.HHMMSS.MILLISEC
# Parametri opzionali
#  sOld(old): TimeStampstr Vecchia data a cui non deve coincidere
#  from_dict=FromDict da convertire
# Ritorno:
#  lResult=[sResult, sTimeStamp]
def NF_TS_ToStr(sType="L", **kwargs):
    sResult=""
    sProc="TS_ToStr"
    sTS=""
    sOld=""
# NOW DATETIME
    now=datetime.today()
    vDateTime=now
    if sType=="": sType="L"
# Parametri opzionali
    for key,value in kwargs.items():
        if key=="from_dict":
            sResult,vDateTime=NF_TS_FromDict(value,"D")
        elif key=="old":
            sOld=value
        else:
            sResult="key not correct " + key
# Conversione in base al tipo
    if sResult=="":
        if sType=="X":
            sTS=NF_DateStrYYYYMMDD(vDateTime) + "." + NF_TimeStrHHMMSS(vDateTime) + "." + str(vDateTime.microsecond)
        elif sType=="L":
            sTS=NF_DateStrYYYYMMDD(vDateTime) + "." + NF_TimeStrHHMMSS(vDateTime)
        else:
            sResult="Type not corrent: " + sType
# Loop deve essere diverso dal vecchio se specificato
    if (sResult=="") and (sOld != ""):
        while sTS==sOld:
            lResult=NF_TS_ToStr(sType, old=sOld)
            sTS=lResult[1]
# Uscita
    #print(sProc, sResult, sOld, sType, sTS)
    return [NF_ErrorProc(sResult,sProc), sTS]

# Fast TIMESTAMP con ritorno solo stringa
def NF_TS_ToStr2():
    lResult=NF_TS_ToStr()
    return lResult[1]

# TIMESTAMP: ToStr. Ritorna lresult, 0=sResult, 1=Date, 2=Time, 3=Msec
# sDateTime: DATE.TIME[.MSEC]
def NF_TS_FromStr(sDateTime: str):
    sResult=""
    sProc="TS_FromStr"
    nMsec=0
    dtDate=""
    tmTime=""

# Split
    if (sDateTime==""):
        sResult="NoDateTime"
    if (sResult==""):
        asDate=sDateTime.split(NT_ENV_DATE_DIV)
        asDate=NF_ArrayStrNorm(asDate,"SLR")
        nLen=len(asDate)
        if nLen<2: sResult="NoValid sep"
    if (sResult==""):
        # Estrae
        sDate=asDate[0]
        sTime=asDate[1]
        if nLen==3: nMsec=int(asDate[3])
        # Converte da Str a dt/tm
        dtDate=NF_DateYYYYMMDD_fStr(sDate)
        tmTime=NF_TimeHHMMSS_fStr(sTime)

# Uscita
    lResult=[NF_ErrorProc(sResult,sProc), dtDate, tmTime, nMsec]
    return lResult

# Ritorna microsecondi
def NF_DateMsec(dtDate):
    return int(dtDate.strftime("%f"))

# Da Data a AAAAAMMDD Str
def NF_DateStrYYYYMMDD(dtDate):
    sResult=str(dtDate)
    #print("D1:" + sResult)
    sResult=sResult.replace("-","")
    #print("D2:" + sResult)
    sResult=NF_StrLeft(sResult,8)
    #print("D3:" + sResult)
    return sResult

# Da YYYYMMDDStr a Data
def NF_DateYYYYMMDD_fStr(sDate: str):
    nYear=int(NF_StrLeft(sDate,4))
    nMonth=int(NF_StrMid(sDate,6,2))
    nDay=int(NF_StrMid(sDate,7,2))
    dtDate=datetime(nYear,nMonth,nDay)
    return dtDate

# Da HHMMSSStr a Time
def NF_TimeHHMMSS_fStr(sTime):
    tmTime=datetime.strptime(sTime, '%H%M%S')
    return tmTime

# Da Time a AAAAAMMDD Str
def NF_TimeStrHHMMSS(tmTime):
    sResult=str(tmTime)
    sResult=NF_StrMid(sResult,11,8)
    sResult=sResult.replace(":","")
    sResult=NF_StrLeft(sResult,6)
    return sResult

# DateTime to AAAAMMDD.HHMMSS
# Checl if DateTime
# Return status, string AAAAMMDD.HHMMSS
def NF_DateTime_DTHH(vDateTime):
    sResult=""
    sDateTime=""
    sProc="DateTim.AAAAMMDD.HHMMSS"

    try:
        sDateTime=datetime.strptime(vDateTime, "%d%b%Y.%H%M%S")
    except Exception as e:
        sResult=getattr(e, 'DateTime convert ', repr(e))

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult, sDateTime

#  ------------- DIAGNOTICA E GESTIONE ERRORI ---------------------

# NullTo0/nullToStr
def NF_NullTo0(vValue):
    if vValue==None:
        return 0
    else:
        return int(vValue)

def NF_NullToStr(vValue):
    if vValue==None:
        return ""
    else:
        return str(vValue)

# Range
def NF_Range(vValue, vMin, vMax):
    return (vValue>=vMin) and (vValue<=vMax)

# TypeCasting
def NF_TypeCast(vDato,sType=None):
# Selezione
    if sType=="T":
        vDato=str(vDato)
    elif sType=="B":
        vDato=bool(vDato)
    elif sType=="N":
        vDato=float(vDato)
    elif sType=="I":
        vDato=int(vDato)
    else:
        pass
# Uscita
    return vDato

# Crea lResult con Errore e Result per return diretto - NON DEVE ESISTERE LRESULT
def NF_Result(sResult: str, sProc: str, vResult):
    sResult=NF_ErrorProc(sResult, sProc)
    return [sResult,vResult]

# Ritorna 2 Variabili da un lResult di 2. Conversione
def NF_Return2(lResult: list):
    return lResult[0],lResult[1]

# Ritorno con Errore sProc aggiunto
def NF_ErrorProc(sResult: str, sProc: str) -> str:
    #print ("NF_ErrorProc: " + str(type(sResult)))
    if (sResult != ""):
        return sProc + ": Errore " + str(sResult)
    else:
        return sResult

# Ritorno stringa Test
def NF_DebugFase(bDebug, sText, sProc):
    if bDebug:
        if (sText == ""): sText="Start"
        print (sProc + ", Fase: " + sText)

# ------------------------------ STRINGHE -------------------------------

# String Test + ", " Append se non è la prima
def NF_StrAppendExt(sSource: str, sAppend: str, sDelimiter=","):

    if str(type(sSource)) != "<class 'str'>":
        return sSource
    if sSource == "":
        return sAppend
    else:
        return sSource + sDelimiter + str(sAppend)

# Template String Replace from Dict, using template library
# %Campo
def NF_StrReplaceDict(sTemplate: str, dictData: dict):
    if isinstance(sTemplate, str):
        template = Template(sTemplate)
        return template.safe_substitute(dictData)
    return sTemplate

# Conversione da STR a BOOL - La bool() non funziona bene
def NF_StrBool(sText: str):
    sText=str(sText).strip().upper()
    bResult=iif(sText=="TRUE",True,False)
    return bResult

# Cerca substr i String, -1=Left, 0=Internal, 1=Right
# Return. -1=Errore, 1=Trovata a Sinistra, maggiore zero=interno
def NF_StrFind(nPos: int, sString: str, sFind: str): 
    nResult=-1

# Verifiche
    if sString=="" or sFind=="": 
        return -1

# Casi
    nFind=len(sFind)
    if nPos==-1:
        sString2=NF_StrLeft(sString,nFind)
        if sString2==sFind: 
            nResult=1
    if nPos==1:
        sString2=NF_StrRight(sString,nFind)
        if sString2==sFind:
            nResult=len(sString)-nFind
    elif nPos==0:
        nResult=sString.find(sFind)
        if nResult != -1: 
            nResult=nResult+1
# Uscita
    return nResult

# convertoto in STr + Trim + UCase +
def NF_StrNorm(sText):
    sText=str(sText)
    return ((sText.lstrip()).rstrip()).upper()

# Strings per lettura
def NF_StrLeft(s, amount):
    return s[:amount]
def NF_StrRight(s, amount):
    return s[-amount:]
def NF_StrMid(s, offset, amount):
    return s[offset:offset+amount]

# Join text con parametri vari
# delim=Delimitoatore (o ","). prefix=Prefisso prima di ogni stringa, postfix=dopo ogni stringa, node=NoDelimitatorOnE. nofixe=no suffix/prefix on empty
# fast=True, usa la join python
def NF_StrJoin(**kwargs):
    sResult=""
    sPrefix=""
    sSuffix=""
    sDelim=","
    vResult=[]
    avResult=[]
    bNofixe=False
    bNode=False
    bFast=False

# Parametri
    for key,value in kwargs.items():
        if key=="delim":
            sDelim=value
        elif key=="start":
            sPrefix=value
        elif key=="end":
            sSuffix=value
        elif key=="node":
            bNode=bool(value)
        elif key=="nofixe":
            bNofixe=bool(value)
        elif key=="text":
            avResult=value
        elif key=="fast":
            bFast=bool(value)

# Ciclo Standard
    if bFast:
        if len(avResult)==0: avResult=[""]
        sResult = sDelim.join(str(x) for x in avResult)
    else:
        for vResult in avResult:
            vResult=str(vResult)
            vResult=iif(bNofixe,"",sPrefix) + vResult + iif(bNofixe,"",sSuffix)
            if sResult != "": sResult = sResult + iif(bNode, "", sDelim)
            sResult=sResult + str(vResult)
# Ritorno
    return sResult

# Da Oggetto a Stringa
def NF_StrObj(objX):
    sResult=""
    sProc="NF_ObjStr"
    nIndex=0
    sValue=""

# Verifica Tipo Dict
    if type(objX) != dict:
        sResult="Not dict"
    elif  NF_DictLen(objX)<1:
        sResult="Dict Empty"
    else:
# Inizio: Ciclo Key->Value
        asKeys=NF_DictKeys(objX)
        print("Keys: " + str(asKeys))
        for sKey in asKeys:
            sKeyType=type(sKey)
            if sKeyType != str:
                sResult="Key invalid " + str(nIndex) + ": " + str(sKeyType)
            else:
            # Key
                print(sProc + ": NF_DictExistKey.Key: " + str(nIndex) + ", " + sKey )
                sValue=""
                vValue=None
                if sKey != "": vValue=objX[sKey]
            # Value: Lista
                if type(vValue)==list:
                    sValue=NF_StrObj(vValue)
            # Value: Dictionary
                elif type(vValue)==dict:
                    sValue=NF_StrObj(vValue)
            # Value: Altri casi
                else:
                    sValue=sKey + "=" + str(vValue)
        # Append Key+Value
            sResult=NF_StrAppendExt(sResult, sValue)

# Uscita (così è giusto)
    return sResult

# Strip Evoluto. X=NoASC, S=NoSpazi interni, D=Left & Right Space, A=Left & Right Apici, K= doppi apici in uno solo
def NF_StrStrip(sText: str, sType: str):
    sText=str(sText)
    if sType.find("X") != -1:
        sText = ''.join(cChar for cChar in sText if ( ((ord(cChar)<128) and (ord(cChar)>31))) )
    if sType.find("S") != -1:
        sText = ''.join(cChar for cChar in sText if ( ord(cChar)!=32 )  )
    if sType.find("D") != -1:
            sText = sText.lstrip().rstrip()
    if sType.find("A") != -1:
        if sText.startswith('"') and sText.endswith('"'):
            sText = sText[1:-1]
    if sType.find("K") != -1:
        sText = sText.replace('""', '"')
    return sText

def NF_StrSplitKeys(sKeys: str, sDelimiter=","):
    asFieldsCSV=sKeys.split(sDelimiter)
    asFieldsCSV=NF_ArrayStrNorm(asFieldsCSV,"LRUS")
    return asFieldsCSV

def NF_StrSplitString(sText: str, sDelimiter=';', bNames=False):
    sResult = ""
    avFields = []
    sProc="NF_StrSplitString"
    
    # Verifica che il delimitatore sia un singolo carattere
    if len(sDelimiter) != 1:
        sResult = "Delimiter must be a single character"
        return sResult, avFields
    
    # Split della stringa
    parts = sText.split(sDelimiter)
    
    for part in parts:
        # Rimuove spazi all'inizio e alla fine
        stripped = part.lstrip().rstrip()
        
        # Rimuove le virgolette circostanti se presenti
        if len(stripped) >= 2 and stripped[0] == '"' and stripped[-1] == '"':
            stripped = stripped[1:-1]
        
        # Filtra i caratteri non consentiti
        if bNames==True:
            allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
            filtered = [c for c in stripped if c in allowed]
            avFields.append(''.join(filtered))
        # Non filtra
        else:
            avFields.append(stripped)
    
    return NF_ErrorProc(sResult,sProc), avFields

# Scrive una stringa su file con carriage return
# sAttr: "a"=Append, "w"=Write
def NF_StrFileWrite(sFile: str, sText: str, sAttr: str):
    sProc="StrFileWrite"
    sResult=""

# Verifica parametri
    if NF_ArrayFind(("w","a"), sAttr)<0: 
        sResult="parametro errato: " + sAttr + " file " + sFile
    if sFile=="": 
        sResult = "File name empty"

# Apertura + Scrittura
    if sResult=="":
        try:
            with open(sFile, sAttr, encoding=NT_ENV_ENCODING) as txt_file:
                txt_file.write(str(sText) + "\n")
        except Exception as e:
            sResult=getattr(e, 'message', repr(e)) + "scrittura su file " + sFile
# Uscita
    return NF_ErrorProc(sResult,sProc)

# Legge un Array dove ogni riga è una riga del file a differenza di NF_FileRead()
# Return lResult, 0=Result, 1=list con Linee Lette. Si presuppone sia file di texto
def NF_StrFileRead(sFile: str):
    sProc="StrFileRead"
    sResult=""
    lines=0

# Verifica
    sResult=NF_FileExist(sFile) 
# Apertura + Lettura
    if sResult=="":
        lResult=NF_FileOpen(sFile,"r", encoding=NT_ENV_ENCODING)
        sResult=lResult[0]
    if sResult=="":
        txt_file=lResult[1]
# Lettura Linee
        try:
            lines = txt_file.readlines()
        except:
            sResult="Lettura file " + sFile
# Chiusura
    if sResult=="":
        txt_file.close()
# Ritorno
    return NF_Result(sResult,sProc,lines)

# Ritorno stringa Test
def NF_StrTestResult(sResult: str, sProc: str):
    if (sResult != ""):
        return "Test " + sProc + ": " + str(sResult)
    else:
        return "Test " + sProc + ": OK"

# Se la conversione di sParam con NF_StrNorm="TRUE" (convertito in maiuscolo) allora bResult=True, se se="FALSE", bResult=False

# Test in serie con stringa di ritorno. Nulla tutto ok
# 0=Test, 1=StringaPerErrore, 2=FacoltativoIdTest
def NF_StrTests(avTests):
    sResult=""
# Ciclo
    for vTest in avTests:
        nLen=len(vTest)
        if nLen>1:
            bResult=vTest[0]
            sErrorText=vTest[1]
            sTestID=iif(nLen>2,vTest[2]+": ","")
            if bResult==True: sResult=NF_StrAppendExt(sResult, sTestID + sErrorText)
# Uscita
    return sResult

# --------------------------- ARRAY ---------------------------

# ArrayGet con valore di default per non andare in errore
def NF_ArrayGet(av, nPos: int, vDefault):
    vResult=vDefault
# Get Array Len 
    nLen=NF_ArrayLen(av)    
# Get Item if in Range
    if nLen>0:
        if nPos<=nLen:
            vResult=av[nPos]            
# Ritorno
    return  vResult

# Array Append (somma di due Array MONODIMENSIONALI. Ritorna av1+av2
def NF_ArrayAppend(av1: list, av2: list):
# Append
    for row in av2:        av1.append(row)
# Ritorno
    return av1

# Comparazione Array TUPLE
def NF_ArrayCompare(av1, av2):
    sProc="ARR_COMPARE"
    sResult=""

# Confronto Tipo
    if not (NF_IsArray(av1) and NF_IsArray(av2)): sResult="Var non di tipo array tutti e 2: " + str(type(av1)) + ", " + str(type(av2))

# Confronto Len
    if sResult=="":
        nLen1=len(av1)
        nLen2=len(av2)
        if nLen1!=nLen2: sResult="Array len diverse, av1: " + str(nLen1) + ", av2: " + str(nLen2)

# Confronto elementi
    if sResult=="":
        for nF1 in range(0,nLen1):
            if av1[nF1] != av2[nF1]:
                sResult=NF_StrAppendExt(sResult, "i: " + str(nF1))
        if sResult != "": sResult = "Elementi diversi: " + sResult

# Ritorno
    return NF_ErrorProc(sResult, sProc)

# ArrayCountValues
# Ritorna Array dove ci sono chiavi duplicate
# Ritorna lResult 0=Status, 1=Dict con VALORE=CONTATORE (senza doppi)
# DA VERIFICARE
def NF_ArrayCountValues(avArray):
    sProc="ArrayCountValues"
    sResult=""
    dictCount={}

    # Verifica Array
    if NF_IsArray(avArray)<0: sResult="Array Empty"

    # Ciclo di conteggio
    if sResult=="":

        # Ciclo per tutti i VALORI (DOPPI E NON DOPPI)
        for vValue in avArray:
        # Verifica se esiste gia' - Incrementa INDICE solo SE NON ESISTE
            if NF_DictExistKey(dictCount, vValue) == False:
        # Ricerca quanti valori ce ne sono e lo aggiunge a dictCount
                nCount=NF_ArrayCountValue(avArray, vValue)
                dictCount[vValue]=nCount
    # Uscita
    return NF_Result(sResult, sProc, dictCount)

# Conta Occorrenze di un Valore in Array
# DA VERIFICARE
# Parametri:
#   avArray=Da Controllare
#   vValue=Da cercare
#   sMode ""=Normale, C=StringWithoutCase, L.PathLike=Cerca con PathLike (DA IMPLEMENTARE ALLA PRIMA OCCASIONE)
# Ritorno:
#   nResult -1,0 o Numero Occorrenze
def NF_ArrayCountValue(avArray, vValue, sMode=""):
    nResult=0
# Verrà usata
    sMode=""
# Ciclo di Conteggio
    nLen=NF_ArrayLen(avArray)
# Solo se Len>0 altrimenti Count=Len
    if nLen>0:
        for nF1 in range(0, nLen):
            if vValue==avArray(nF1): nResult=nResult+1
    else:
        nResult=nLen
# Uscita
    return nResult

# ritorna l'array Riempie un Array Crea Array con Elementi, tutti uguali. Se specificata dimensione allarga a quella dimensione
def NF_ArrayFill(asArrInput, vFill, nLen=None):
    sResult = ""
    sProc="ArrayFill"
        
    # Verifica se asArrInput è una lista (in Python gli array sono liste)
    if not isinstance(asArrInput, list):
        sResult = "Errore not Array"
    
    # Se c'è un errore, ritorna immediatamente
    if sResult != "":
        return [sResult, None]
    
    # Se nLen è specificato, ridimensiona la lista
    if nLen is not None and isinstance(nLen, int):
        # Se nLen > lunghezza attuale, estendi la lista con vFill
        if nLen > len(asArrInput):
            asArrInput += [vFill] * (nLen - len(asArrInput))
        # Se nLen < lunghezza attuale, tronca la lista
        else:
            asArrInput = asArrInput[:nLen]
    
    # Riempie la lista con vFill
    for i in range(len(asArrInput)):
        asArrInput[i] = vFill
    
# Ritorno
    return NF_Result(sResult, sProc, asArrInput)

# Rimuove Duplicati da Array
def NF_ArrayRemoveDups(avArray):
    return list(dict.fromkeys(avArray))

# Rimuove Elementi da Array, Restituendo nuovo Array. avRemove contiene indici numerici nel range
# Ritorna lResult 0=Status, 1=Array
def NF_ArrayRemoveRows(avArray, avRemove):
    sProc="ArrayRemoveRows"
    avRemove=[]
    avArrayOut=[]
    sResult=""

# Verifica Array
    nLenInput=NF_ArrayLen(avArray)
    if (nLenInput<1):
        sResult="Array Error Input"
    else:
        nLenRemove=NF_ArrayLen(avRemove)
        if (nLenRemove<1): sResult="Array Error ToRemove"

# Ciclo costruzione nuovo Array
    if sResult=="":
        for nF1 in range(0, nLenRemove-1):
            if NF_ArrayFind(avRemove,nF1) == False:
                avArrayOut.append(avArray[nF1])

# Ritorno
    return NF_Result(sResult,sProc,avArrayOut)

# ArrayTrim  & CASE
# LR=Trim Space Left/Right, U=UCase, LCase, Capitalize, S=StripSpaces, X=StripNoAsc, F=ForzaStr
def NF_ArrayStrNorm(asArray: list[str], sActions: str) -> list[str]:

# Setup + Verify
    nIndex=0
# Ciclo
    for sArray in asArray:
    # Forza Str
        if sActions.find("F")!=-1: sArray=str(sArray)
        if str(type(sArray))=="<class 'str'>":
            #print (str(type(sArray)) + " " + sArray)
    # LTRIM, RTRIM, TRIM
            if sActions.find("L")!=-1: sArray=sArray.lstrip()
            if sActions.find("R")!=-1: sArray=sArray.rstrip()
            if sActions.find("S")!=-1: sArray=NF_StrStrip(sArray,"S")
    # UCASE
            if sActions.find("U")!=-1: sArray=sArray.upper()
            elif sActions.find("C")!=-1: sArray=sArray.lower()
            elif sActions.find("Z")!=-1: sArray=sArray.capitalize()
    # NOASC
            if sActions.find("X")!=-1: sArray=NF_StrStrip(sArray,"X")
    # END + NEXT
        asArray[nIndex]=sArray
        nIndex+=1
# Ritorno
    return asArray

# Replace Array of Str with Templates $ with a Dictionary of Keys
def NF_ArrayStrReplaceDict(asArray: list[str], dictConfig: dict)  -> list[str]:
    nIndex=0
    for sArray in  asArray:
        asArray[nIndex]=NF_StrReplaceDict(sArray, dictConfig)
        nIndex +=1
#  Ritorno
    return asArray

# Replace Items of Dictionary with Templates $ with a Dictionary of Keys calling NF_StrReplaceDict. 
def NF_DictStrReplaceDict(dictTemplate: dict, dictConfig: dict)  -> dict:
    for sKey in dictTemplate.keys():
        sText=NF_StrReplaceDict(dictTemplate[sKey], dictConfig)
        dictTemplate[sKey]=sText
#  Ritorno
    return dictTemplate

# Ritorna -1 se non esiste, 0=Empty, >0 c'è qualcosa, numero di elementi
def NF_ArrayLen(avArray):
    nResult=0
    #print("DictLen.0: " + str(nResult))
    if NF_IsArray(avArray)==False: 
        nResult=-1
    #print("DictLen.1: " + str(nResult))
    if nResult==0: 
        nResult=len(avArray)
    #print("DictLen.2: " + str(nResult))
    return nResult

# Ritorna <0 o posizione in ArrayList
def NF_ArrayFind(avKeys, vKey):
    nResult=0

# Caso Array problema
    if NF_ArrayLen(avKeys)==-1: return -1

# Caso No Elementi
    #NF_DebugFase(NT_ENV_TEST_SYS, "Type avKeys: " + str(type(avKeys)),sProc)
    if (avKeys==None):
        nResult=-2
    else:
        try:
            nResult=avKeys.index(vKey)
        except:
            nResult=-1
# Fine
    return nResult

# Conversione da lista a tupla per modificarlo
def NF_ArrayT2L(avTuple):
    avList=[]
    for x in avTuple:
        avList.append(x)
    return avList

# Array Sort with checks
# Parameters:
#	avArray (array_to_sort)
#   sMode=""/"A"= Ascendent, "D"=Discendent
# Return
# 	lResult. 0=Status= 1=New Array
def	NF_ArraySort(avArray, sMode="A"):
    sResult=""
    sProc="NF_ArraySort"
    avResult=[]
    bReverse=False

# Check
    if NF_IsArray(avArray)==False: sResult="Not Array"
    if sMode=="A" or sMode=="":
        sMode=""
        bReverse=False
    elif sMode=="D":
        bReverse=True
    else:
        sResult="Mode invalid " + str(sMode)
# Sort
    if sResult=="":
        avResult=sorted(avArray,reverse=bReverse)
# Return
    return NF_Result(sResult,sProc,avResult)

def NF_IsWindows():
    if  sys_platform=="win32":
        return True
    else:
        return False

def NF_IsLinux():
    if  sys_platform=="linux":
        return True
    else:
        return False

# Param is Array
def NF_IsArray(aParams):
    t=type(aParams)
    return (t==type(list())) or (t==type(tuple()))

# True=Dictionary
def NF_IsDict(dictParams):
    return (type(dictParams)==type(dict()))

def NF_IsString(vParam):
    return (type(vParam)==type("x"))

# ----------------------------------- DICTIONARY ----------------------------------

# Conversione di tipi in dict
# In: DictParams da verificare, dictConvert Key=Tipo B=Bool, I=Int, N=Float
def NF_DictConvert(dictParams: dict, dictConvert: dict):
    sType=""
    sProc="DictConvert"
# Verifiche
    if (NF_DictLen(dictParams)<1) or (NF_DictLen(dictConvert)<1): return dictParams
# Setup
    lResult=NF_DictKeys(dictParams)
    avKeys=iif(lResult[0],lResult[1],list())
    lResult=NF_DictKeys(dictConvert)
    avConvert=iif(lResult[0],lResult[1],list())
# Ciclo Conversione
    for vKey in avKeys:
        if NF_ArrayFind(avConvert,vKey)>=0:
            print(sProc + ": " + str(vKey))
            vValue=dictParams[vKey]
            vValue=str(vValue)
            sType=dictConvert[vKey]
            if (sType=="B"): vValue=NF_StrBool(vValue)
            if (sType=="I"): vValue=int(vValue)
            if (sType=="N"): vValue=float(vValue)
            dictParams[vKey]=vValue
# Ritorno
    return dictParams

# GET ESTESA, con Valore di defaultt
def NF_DictGet(dictParams: dict, sKey: str,vDefault=""):
    sKey=str(sKey)
    vResult=dictParams.get(sKey)
    if vResult==None: vResult=vDefault
    return vResult

# FROM KEYS PIU' SEMPLICE. Nuovo Dictionary solo delle key scelte "se esistono"
# VUOTO COMUNQUE SE NESSUNO
def NF_DictFromKeys(dictParams: dict, avKeys):
    dictResult=dict()
    for vKey in avKeys:
        dictResult[vKey]=dictParams[vKey]
    return dictResult

# Ritorna una lista VERA delle Keys di un dictionary perché .keys ritorna una cosa diversa. una view ref.
# Ritorna lResult 0=Status, 1=Array
def NF_DictKeys(dictData):
    avResult=[]
    sResult=""
    sProc="NF_DictKeys"

# Ciclo
    if (NF_IsDict(dictData)):
        for vKey in dictData.keys():
            avResult.append(vKey)
    else:
        sResult="No dict " + str(type(dictData))

# Debug
    #print("NF_DictKeys: " + str(asResult))
# Ritorno
    return NF_Result(sResult,sProc,avResult)

# Ritorna una lista VERA dei valori di un dictionary perché .values ritorna una cosa diversa. una view ref.
# Ritorna lResult 0=Status, 1=Array Valori
def NF_DictValues(dictData: dict):
    avResult=[]
    sProc="NF_DictValues"
    sResult=""
    
    if (NF_IsDict(dictData)):
        for vKey in dictData.keys():
            avResult.append(dictData[vKey])
    else:
        sResult="No dict " + str(type(dictData)) + ": " + sProc

# Debug
    #print("NF_DictValues: " + str(asResult))
    return NF_Result(sResult,sProc,avResult)

# Ritorno -1=NoDict, 0=Empty. Oppure>0
def NF_DictLen(dictParams):
    nResult=0
    #print("DictLen.0: " + str(nResult))
    if NF_IsDict(dictParams)==False: nResult=-1
    #print("DictLen.1: " + str(nResult))
    if nResult==0: nResult=len(dictParams)
    #print("DictLen.2: " + str(nResult))
    return nResult

# Dictionary. Esiste singola key
# Ritorno. True=Esiste, False=No
def NF_DictExistKey(dictData: dict,vKeyFind):
    lResult=NF_DictKeys(dictData)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
            #Debug
            #print("NF_DictExistKey.Key: " + str(vKey))
# Trovata Key in dictData
            if (vKey==vKeyFind): return True
    else:
# Diagnostica per probabile errore
        print("DictExistKey.dict: NONE")
# Non Trovata Key in dictData
    return False

# Dictionary. Esiste singolo Valore in Dictionary
def NF_DictExistValue(dictData: dict,vValueFind):
    lResult=NF_DictKeys(dictData)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
# Trovato Value in dictData
            if (dictData[vKey]==vValueFind): return True
    else:
# Diagnostica per probabile errore
        print("DictExistKey.dict: NONE")
# Non Trovata Key in dictData
    return False

# Verifica esistenza Keys in Dictionary
def NF_DictExistKeys(dictData: dict, avKeys):
    sProc="NF_DictExistKeys"
    sResult=""

# Check Dic NotEmptyWithValues and avKeys not empty
    nResult=NF_DictLen(dictData)
    if (nResult<1):
        sResult="Dict.Test Exist+Values: " + str(nResult)
    if (NF_ArrayLen(avKeys)<1):
        sResult="Array Keys to find empty"
# Verifica Keys
    if (sResult==""):

        lResult=NF_DictKeys(dictData)
        sResult=lResult[0]
        if sResult=="":
            avDataKeys=lResult[1]
            for vKey in avKeys:
                if NF_ArrayFind(avDataKeys, vKey) < 0:
                    sResult=NF_StrAppendExt(sResult, str(vKey))
            if (sResult != ""): sResult="Dict.Test.Keys.Not.Found: " + sResult

# Ritorno
    return NF_ErrorProc(sResult, sProc)

# Return dictionary from Array Header/Data
def NF_DictFromArr(asHeader: list[str], avData):
# Input: asHeader(array keys), avData(array valori).
# Se asHeader=[], allora viene riempito di numeri pari a avData oppure i 2 array devono avere stessa lunghezza
# Ritorno:
#   lResult[0]: Diagnostica di ritorno. ""=NoError,
#   lResult[1]: Dict,
#   Altri: 2=LenHdr, 3=LenData, 4=TypeHDR(se non Array), 5=TypeData(se non Array)
    sProc="NF_DictFromArr"
    sResult=""
    dictResult={}

# Verifica Componenti
    lHType=len(asHeader)
    lHData=len(avData)

# Caso Header non passato, riempito di numeri 0..N
    if lHType==0:
        asHeader=list(range(0,lHData))
# Verifica
    bVerify=False
    if NF_IsArray(asHeader) and NF_IsArray(avData):
        if NF_ArrayLen(asHeader)>0 and NF_ArrayLen(avData)>0: bVerify=True
# Verifica lunghezza uguale (salvo zero allora lista 0..n
    if bVerify:
        bVerify = (lHType != lHData)
        sResult=iif(bVerify, "", "lunghezze diverse: Header=" + str(lHType) + ", Data=" + str(lHData))
# Esecuzione
    if sResult=="":
        nIndex=0
        for sID in asHeader:
            vDato=avData[nIndex]
            dictResult.update({sID: vDato})
            nIndex=nIndex+1
# Ritorno
    sResult=NF_ErrorProc(sResult,sProc)
    lResult=[sResult,dictResult,len(asHeader),lHType,lHData,str(type(asHeader)), str(type(avData))]
    return lResult

# Get Param
# Return: sResult, vValue (doppio)
# ---------------------------------------------------------------------
def NF_DictGetParam(dictParam: dict, sKey: str, sError="", sType=None):
    sProc="DICT.GET.PARAM"
    sResult=""
    vDato=None

# Debug
#   print(sProc + ".DICT: " + str(dictParam))

# Estrazione
    if NF_DictExistKey(dictParam,sKey)==False:
        sResult=sError
        vDato=None
    else:
        vDato=dictParam[sKey]

# Tipizzazione
    if sType != None: vDato=NF_TypeCast(vDato,sType)

# Ritorno
    sResult=NF_ErrorProc(sResult, sProc)
    return sResult,vDato

# Merge 2 Dict. Ritorno "copia" di Source+Add
# ---------------------------------------------------------------------
def NF_DictMerge(dictSource: dict, dictAdd: dict):

# Copia
    dictEnd=dictSource.copy()

# Per ogni elemento in dictAdd
    lResult=NF_DictKeys(dictAdd)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
        # Aggiunge elementi secondo array
            dictEnd[vKey]=dictAdd[vKey]

# Uscita
    return dictEnd

# Merge 2 Dict(2) dict di dict. Ritorno "copia" di Source+Add
# ---------------------------------------------------------------------
def NF_DictMerge2(dictSource: dict, dictAdd: dict):

# Copia
    dictEnd=dictSource.copy()

# Per ogni dict dentro dictAdd
    lResult=NF_DictKeys(dictAdd)
    sResult=lResult[0]
    if sResult=="":
        for vKey in lResult[1]:
            dictAdd2=dictAdd[vKey]
    # Cerca se esiste o attribuisce dictAdd
            if NF_DictExistKey(dictSource,vKey):
                dictSource2=dictSource[vKey]
            else:
                dictSource2=dictAdd
    # Merge
            dictMerge=NF_DictMerge(dictSource2, dictAdd2)
            dictEnd[vKey]=dictMerge

# Uscita
    return dictEnd

# DictReplace. sResult=Errore se dictParams non esiste
# --------------------------------------------------------------------------------------
def NF_DictReplace(dictParams, sKey: str, vValue):
    sProc="NF_DictReplace"
    sResult=""

    if NF_IsDict(dictParams):
        sResult="Not dict"
    else:
        dictParams[sKey]=vValue

# Ritorno
    return NF_ErrorProc(sResult, sProc), dictParams

# Sort Dictionary from Keys/Values
# lResult 0=Status, 1=DictResult
# Parametri:
# 	dictParams (Input), sMode (K o "": Keys, "V"=Values), "KR"=Key/Reverse, "VA"=Value/Reverse
# Result: lResult (0=Status, 1=NewDictionaryResultSorted)
# DA VERIFICARE
# -------------------------------------------------------------------------------------
def NF_DictSort(dictParams: dict, sMode=""):
    dictResult=dict()
    sProc="NF_DictSort"
    sResult=""
    sModeReverse=""
    avKeys=list()

# Check Dictionary
    if NF_IsDict(dictParams)==False:
        sResult="Not Dictionary"
        return sResult

# Array Keys per maggior uso
    lResult=NF_DictKeys(dictParams)
    if sResult=="": avKeys=lResult[1]

# Keys for Sort
    if (sMode=="") or (sMode=="K"):
        pass
    elif sMode=="VR":
        sModeReverse="D"
    elif sMode=="KR":
        sModeReverse="D"
    elif sMode=="V":
        lResult=NF_DictValues(dictParams)
        if sResult=="": avKeys=lResult[1]
    else:
        sResult="Mode invalid " + str(sMode)

# Sort
    if sResult=="":
        lResult=NF_ArraySort(avKeys,sModeReverse)
        sResult=lResult[0]

# New Dictionary
    if sResult=="":
        avKeys=lResult[1]
        for vKey in avKeys:
            dictResult[vKey]=dictParams[vKey]

# Uscita
    return NF_Result(sResult,sProc,dictResult)

def NF_DictStr(dictData: dict, livello=0):
    
    # Definisci lo spazio per l'indentazione (4 spazi per livello)
    spazi = "    " * (livello + 1)
    spazi_chiusura = "    " * livello
    
    linee = []
    
    for chiave, valore in dictData.items():
        # Se il valore è un altro dizionario, richiama la funzione stessa (ricorsione)
        if isinstance(valore, dict):
            valore_str = NF_DictStr(valore, livello + 1)
        else:
            # repr() mantiene le virgolette se è una stringa
            valore_str = repr(valore)
            
        linee.append(f"{spazi}{repr(chiave)}: {valore_str}")

    # Unisce le linee e racchiude tra parentesi graffe
    contenuto = ",\n".join(linee)
    return f"{{\n{contenuto}\n{spazi_chiusura}}}"    

# ------------------- TABLE (ARRAY BYDIM) FUNCTONS -------------
# Return Row,Cols of a bidimensional array
def NF_TableLen(avTable: list):

# Check Empty
    if not avTable:
        return -1, -1        
# Get rows
    rows = len(avTable)

# Get cols from first row
# If no rows or first row empty, cols is -1
    cols = len(avTable[0]) if rows > 0 and avTable[0] else -1
# Ritorno
    return rows, cols

# Replace a bidimensional array with a dictionary variables list
# Input: avTable - bidimensional array string
# Output: [sResult] and avTable Changed.
# Call this function with a copy of the original Table or the table to be change directly
def NF_TableReplaceDict(avTable: list[list[str]], dictVars: dict): 
    sProc = "NF_TableReplaceDict"
    sResult = ""

# Check table dimensions
    rows, cols = NF_TableLen(avTable)
    if rows == -1 or cols == -1:
        sResult = "Error not table rows x cols"
    else:
        for row in range(0,rows):
            for col in range(0, cols):
                 #print (f"Row {row}, Col {col} Value {avTable[row][col]}")
                sTemp1=avTable[row][col]
                sTemp2=NF_StrReplaceDict(sTemp1,dictVars)
                if sTemp1 != sTemp2:
                    avTable[row][col]=sTemp2
 # Ritorno   
    return NF_ErrorProc(sResult, sProc)
    
# True=Valida Email
def NF_StrIsEmail(email: str):
# Make a regular expression
# for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
# pass the regular expression and the string into the fullmatch() method
    return iif(re.fullmatch(regex, email),True,False)
