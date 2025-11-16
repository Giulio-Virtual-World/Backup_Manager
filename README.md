## 📦 Backup Manager
Un programma in Python robusto e completo per gestire backup di file, directory e dischi interi su Windows.

<br>

## ✨ Caratteristiche Principali
<ol>
  <li><b>Backup Flessibile:</b> Supporta il backup di dischi interi, directory specifiche o singoli file</li>
  <li><b>Quattro modalità per gestire file già esistenti:</b></li>
  <ul>
    <li>Sovrascrivi sempre</li>
    <li>Salta file esistenti</li>
    <li>Sovrascrivi solo se più recente</li>
    <li>Chiedi conferma per ogni file</li>
  </ul> 
  
  <br>
  
  <li><b>Controllo Spazio:</b> Verifica automaticamente lo spazio disponibile prima di iniziare il backup</li>
  <li><b>Logging Completo:</b> Genera log dettagliati di tutte le operazioni con timestamp</li>
  <li><b>Gestione Errori:</b> Gestione robusta degli errori con statistiche dettagliate</li>
  <li><b>Protezione File di Sistema:</b> Salta automaticamente file di sistema Windows critici</li>
  <li><b>Preservazione Metadati:</b> Mantiene timestamp e attributi originali dei file</li>
</ol>

<br>

## 🚀 Utilizzo
Il programma guiderà l'utente attraverso un processo interattivo:

<ol>
  <li>Selezione della sorgente (disco/directory/file)</li>
  <li>Selezione della destinazione</li>
  <li>Scelta della modalità di gestione conflitti</li>
  <li>Conferma e avvio backup</li>
  <li>Attendi il termine del backup</li>
</ol>

<br>

## 📊 Funzionalità Avanzate
<ul>
  <li><b>Validazione Percorsi</b>: Verifica che tutti i percorsi siano accessibili prima di iniziare</li>
  <li><b>Calcolo Dimensioni</b>: Mostra lo spazio richiesto in GB prima del backup</li>
  <li><b>Statistiche Finali</b>: Riepilogo completo con file copiati, saltati ed errori</li>
  <li><b>Copia Ricorsiva</b>: Gestisce strutture di directory complesse mantenendo la gerarchia</li>
  <li><b>Gestione Permessi</b>: Identifica e registra problemi di accesso</li>
</ul>

<br>

## 📋 Requisiti
<ul>
  <li>Python 3.6+</li>
  <li>Sistema operativo Windows</li>
  <li>Moduli standard Python (os, shutil, logging, datetime, pathlib)</li>
</ul>

<br>

## ⚠️ Note
Progettato specificamente per Windows (gestione lettere di unità)<br>
Richiede permessi appropriati per accedere ai percorsi sorgente e destinazione<br>
I file di sistema Windows vengono automaticamente esclusi dal backup

<br>

## 🛡️ Sicurezza
Il programma include protezioni per:

File di sistema (pagefile.sys, hiberfil.sys, etc.)
Directory protette ($Recycle.Bin, System Volume Information)
Gestione errori di permessi e accesso negato

> ⚠️ Disclaimer: Sebbene abbia testato personalmente il programma su vari dispositivi e lo abbia trovato affidabile, non mi assumo alcuna responsabilità per eventuali danni causati da esso. Si consiglia di testare su dati non critici prima dell'uso.
