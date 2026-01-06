# MailSimple Class
# Generata con DeepsSeek PromptMailSimple

import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional
import os
import time

class NC_MailSimple:
    def __init__(self):
        """Inizializza l'oggetto senza parametri"""
        self.sProc = "__init__"
        self.sResult = ""
        self.asTo = []
        self.sSubject = ""
        self.asAttach = []
        self.sFormat = "TXT"
        self.sBody = ""
        self.sSmtp_User = ""
        self.sSmtp_Password = ""
        self.sSmtp_Host = ""
        self.nSmtp_Port = 25
        self.nTimeout = 30  # Timeout di default di 30 secondi (valore comune)
        self.bSSL = False  # Default: usa STARTTLS invece di SSL
        self.bReconnect = True  # Default: tentativo di riconnessione automatica
        self.bLogin = False
        self.smtp = None
        self.asLogging = []  # Log delle operazioni

    def _add_log(self, sMessage: str):
        """Aggiunge un messaggio al log con timestamp"""
        self.asLogging.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {sMessage}")

    def LogReset(self):
        """Resetta il log delle operazioni"""
        self.asLogging = []
        self._add_log("Log resettato")

    def Start(self, sSmtp_User_par: str, sSmtp_Password_par: str, sSmtp_Host_par: str, 
              nSmtp_Port_par: int = 25, nTimeout_par: int = 30, bSSL_par: bool = False,
              bReconnect_par: bool = True) -> str:
        """Effettua il login al server SMTP"""
        self.sProc = "MailSingle.Start"
        self.sResult = ""
        self._add_log(f"Avvio connessione SMTP a {sSmtp_Host_par}:{nSmtp_Port_par}")
        
        # Assegnazione valori
        self.sSmtp_User = sSmtp_User_par
        self.sSmtp_Password = sSmtp_Password_par
        self.sSmtp_Host = sSmtp_Host_par
        self.nSmtp_Port = nSmtp_Port_par
        self.nTimeout = nTimeout_par
        self.bSSL = bSSL_par
        self.bReconnect = bReconnect_par
        
        # Validazione parametri obbligatori
        if not all([self.sSmtp_User, self.sSmtp_Password, self.sSmtp_Host]):
            self.sResult = f"{self.sProc}: Errore - Parametri SMTP obbligatori mancanti"
            self._add_log(self.sResult)
            return self.sResult
        
        # Tentativo di connessione e login
        try:
            self._add_log(f"Tentativo di connessione (SSL={self.bSSL}, Timeout={self.nTimeout}s)")
            
            if self.bSSL:
                self.smtp = smtplib.SMTP_SSL(self.sSmtp_Host, self.nSmtp_Port, timeout=self.nTimeout)
            else:
                self.smtp = smtplib.SMTP(self.sSmtp_Host, self.nSmtp_Port, timeout=self.nTimeout)
                self.smtp.starttls()  # Usa TLS per sicurezza
            
            self.smtp.login(self.sSmtp_User, self.sSmtp_Password)
            self.bLogin = True
            self._add_log("Connessione e login effettuati con successo")
            return self.sResult
            
        except smtplib.SMTPException as e:
            self.sResult = f"{self.sProc}: Errore SMTP - {str(e)}"
        except socket.timeout:
            self.sResult = f"{self.sProc}: Timeout della connessione ({self.nTimeout} secondi, Host:{self.sSmtp_Host})"
        except Exception as e:
            self.sResult = f"{self.sProc}: Errore generico - {str(e)}"
        
        self._add_log(f"Errore durante la connessione: {self.sResult}")
        
        # In caso di errore, chiudi la connessione se presente
        self._safe_quit()
        return self.sResult

    def VerifyConnect(self) -> bool:
        """Verifica se la connessione è ancora attiva"""
        self.sProc = "VerifyConnect"
        self.sResult = ""
        
        if not self.bLogin or not self.smtp:
            self._add_log("Connessione non attiva (non loggato o oggetto SMTP non presente)")
            return False
        
        try:
            status = self.smtp.noop()[0]
            if status == 250:
                self._add_log("Verifica connessione: attiva (NOOP successivo)")
                return True
            else:
                self._add_log(f"Verifica connessione: problema (codice {status})")
                return False
        except:
            self._add_log("Verifica connessione: fallita (errore durante NOOP)")
            return False

    def _safe_quit(self):
        """Chiude la connessione in modo sicuro"""
        if hasattr(self, 'smtp') and self.smtp:
            try:
                self.smtp.quit()
                self._add_log("Connessione chiusa")
            except:
                pass
        self.bLogin = False

    def _ensure_connection(self) -> bool:
        """Garantisce che la connessione sia attiva (con riconnessione se necessario)"""
        if self.VerifyConnect():
            return True
        
        if not self.bReconnect:
            self._add_log("Riconnessione automatica disabilitata")
            return False
            
        self._add_log("Tentativo di riconnessione...")
        result = self.Start(self.sSmtp_User, self.sSmtp_Password, 
                          self.sSmtp_Host, self.nSmtp_Port, 
                          self.nTimeout, self.bSSL)
        return not bool(result)

    def Send(self, asTo_par: List[str], sSubject_par: str = "", asAttach_par: List[str] = [], 
             sFormat_par: str = "TXT", sBody_par: str = "") -> str:
        """Invia l'email con i parametri specificati"""
        self.sProc = "Send"
        self.sResult = ""
        self._add_log(f"Preparazione invio email a {len(asTo_par)} destinatari")
        
        # Validazione parametri
        if not asTo_par:
            self.sResult = f"{self.sProc}: Errore - Destinatari obbligatori mancanti"
            self._add_log(self.sResult)
            return self.sResult
        
        sFormat_par = sFormat_par.upper()
        if sFormat_par not in ("HTML", "TXT"):
            self.sResult = f"{self.sProc}: Errore - Formato deve essere 'HTML' o 'TXT'"
            self._add_log(self.sResult)
            return self.sResult
        
        # Verifica/connessione
        if not self._ensure_connection():
            self.sResult = f"{self.sProc}: Errore - Connessione SMTP non attiva"
            self._add_log(self.sResult)
            return self.sResult
        
        # Assegnazione valori
        self.asTo = asTo_par
        self.sSubject = sSubject_par
        self.asAttach = asAttach_par
        self.sFormat = sFormat_par
        self.sBody = sBody_par
        
        try:
            # Creazione messaggio
            msg = MIMEMultipart()
            msg['From'] = self.sSmtp_User
            msg['To'] = ", ".join(self.asTo)
            msg['Subject'] = self.sSubject
            self._add_log(f"Creazione messaggio: Da={self.sSmtp_User}, Oggetto={self.sSubject}")
            
            # Aggiunta corpo messaggio
            msg.attach(MIMEText(self.sBody, 'html' if self.sFormat == "HTML" else 'plain'))
            self._add_log(f"Aggiunto corpo messaggio (formato: {self.sFormat})")
            
            # Aggiunta allegati
            for file_path in self.asAttach:
                try:
                    if not os.path.isfile(file_path):
                        self.sResult = f"{self.sProc}: Errore - File non trovato: {file_path}"
                        self._add_log(self.sResult)
                        return self.sResult
                    
                    with open(file_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    filename = os.path.basename(file_path)
                    part.add_header("Content-Disposition", f"attachment; filename={filename}")
                    msg.attach(part)
                    self._add_log(f"Aggiunto allegato: {filename}")
                except Exception as e:
                    self.sResult = f"{self.sProc}: Errore durante l'allegato {file_path} - {str(e)}"
                    self._add_log(self.sResult)
                    return self.sResult
            
            # Invio email
            self._add_log("Invio email in corso...")
            self.smtp.sendmail(self.sSmtp_User, self.asTo, msg.as_string())
            self._add_log("Email inviata con successo")
            return self.sResult
            
        except smtplib.SMTPException as e:
            self.sResult = f"{self.sProc}: Errore SMTP durante l'invio - {str(e)}"
        except socket.timeout:
            self.sResult = f"{self.sProc}: Timeout durante l'invio"
        except Exception as e:
            self.sResult = f"{self.sProc}: Errore generico durante l'invio - {str(e)}"
        
        self._add_log(f"Errore durante l'invio: {self.sResult}")
        return self.sResult

    def Logoff(self) -> str:
        """Effettua il logout dal server SMTP"""
        self.sProc = "Logoff"
        self.sResult = ""
        self._add_log("Richiesta disconnessione")
        
        if not self.bLogin or not self.smtp:
            self._add_log("Nessuna connessione attiva da chiudere")
            return self.sResult
            
        try:
            self.smtp.quit()
            self.bLogin = False
            self._add_log("Disconnessione effettuata con successo")
        except smtplib.SMTPException as e:
            self.sResult = f"{self.sProc}: Errore SMTP durante il logout - {str(e)}"
            self._add_log(self.sResult)
        except Exception as e:
            self.sResult = f"{self.sProc}: Errore generico durante il logout - {str(e)}"
            self._add_log(self.sResult)
        
        return self.sResult

    def __del__(self):
        """Distruttore - assicura che la connessione venga chiusa"""
        self._add_log("Distruttore chiamato")
        if hasattr(self, 'bLogin') and self.bLogin and hasattr(self, 'smtp') and self.smtp:
            self.Logoff()
            