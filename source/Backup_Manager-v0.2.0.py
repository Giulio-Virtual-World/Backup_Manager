'''

    2025
    Author: Giulio Segre
    www.giulio-virtual-world.com

'''




import os
import shutil
import logging
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class BackupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Manager Pro")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variabili per il backup
        self.files_copied = 0
        self.files_skipped = 0
        self.errors = 0
        self.total_size = 0
        self.is_running = False
        self.should_stop = False
        
        # Setup logging
        self.setup_logging()
        
        # Crea l'interfaccia
        self.create_widgets()
        
    def setup_logging(self):
        """Configura il sistema di logging"""
        log_filename = f'backup_gui_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        
    def create_widgets(self):
        """Crea tutti i widget dell'interfaccia"""
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione griglia
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Titolo
        title_label = ttk.Label(main_frame, text="Backup Manager Pro", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sezione Sorgente
        ttk.Label(main_frame, text="SORGENTE", font=('Arial', 12, 'bold')).grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Tipo sorgente
        ttk.Label(main_frame, text="Tipo sorgente:").grid(row=2, column=0, sticky=tk.W, padx=(20, 10))
        
        self.source_type = tk.StringVar(value="directory")
        source_frame = ttk.Frame(main_frame)
        source_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Radiobutton(source_frame, text="Disco intero", variable=self.source_type, 
                       value="disk").grid(row=0, column=0, padx=(0, 15))
        ttk.Radiobutton(source_frame, text="Directory", variable=self.source_type, 
                       value="directory").grid(row=0, column=1, padx=(0, 15))
        ttk.Radiobutton(source_frame, text="File singolo", variable=self.source_type, 
                       value="file").grid(row=0, column=2)
        
        # Percorso sorgente
        ttk.Label(main_frame, text="Percorso sorgente:").grid(row=3, column=0, sticky=tk.W, padx=(20, 10), pady=(10, 0))
        
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(main_frame, textvariable=self.source_path, width=50)
        source_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        ttk.Button(main_frame, text="Sfoglia...", 
                  command=self.browse_source).grid(row=3, column=2, pady=(10, 0))
        
        # Sezione Destinazione
        ttk.Label(main_frame, text="DESTINAZIONE", font=('Arial', 12, 'bold')).grid(
            row=4, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        ttk.Label(main_frame, text="Percorso destinazione:").grid(row=5, column=0, sticky=tk.W, padx=(20, 10))
        
        self.dest_path = tk.StringVar()
        dest_entry = ttk.Entry(main_frame, textvariable=self.dest_path, width=50)
        dest_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(main_frame, text="Sfoglia...", 
                  command=self.browse_destination).grid(row=5, column=2)
        
        # Sezione Opzioni
        ttk.Label(main_frame, text="OPZIONI", font=('Arial', 12, 'bold')).grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))
        
        # Modalità gestione conflitti
        ttk.Label(main_frame, text="File esistenti:").grid(row=7, column=0, sticky=tk.W, padx=(20, 10))
        
        self.overwrite_mode = tk.StringVar(value="skip")
        overwrite_frame = ttk.Frame(main_frame)
        overwrite_frame.grid(row=7, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Radiobutton(overwrite_frame, text="Sovrascrivi", variable=self.overwrite_mode, 
                       value="overwrite").grid(row=0, column=0, padx=(0, 15))
        ttk.Radiobutton(overwrite_frame, text="Salta", variable=self.overwrite_mode, 
                       value="skip").grid(row=0, column=1, padx=(0, 15))
        ttk.Radiobutton(overwrite_frame, text="Solo più recenti", variable=self.overwrite_mode, 
                       value="newer").grid(row=0, column=2)
        
        # Opzioni aggiuntive
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.skip_system_files = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Salta file di sistema", 
                       variable=self.skip_system_files).grid(row=0, column=0, padx=(20, 20))
        
        self.preserve_timestamps = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Preserva timestamp", 
                       variable=self.preserve_timestamps).grid(row=0, column=1)
        
        # Pulsanti di controllo
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=(20, 0))
        
        self.start_button = ttk.Button(button_frame, text="Avvia Backup", 
                                      command=self.start_backup, style='Accent.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Ferma", 
                                     command=self.stop_backup, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="Cancella Log", 
                  command=self.clear_log).grid(row=0, column=2)
        
        # Barra di progresso
        ttk.Label(main_frame, text="Progresso:", font=('Arial', 10, 'bold')).grid(
            row=10, column=0, sticky=tk.W, pady=(20, 5))
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Statistiche
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiche", padding="10")
        stats_frame.grid(row=12, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        ttk.Label(stats_frame, text="File copiati:").grid(row=0, column=0, sticky=tk.W)
        self.copied_label = ttk.Label(stats_frame, text="0", foreground="green")
        self.copied_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="File saltati:").grid(row=0, column=2, sticky=tk.W)
        self.skipped_label = ttk.Label(stats_frame, text="0", foreground="orange")
        self.skipped_label.grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Errori:").grid(row=1, column=0, sticky=tk.W)
        self.errors_label = ttk.Label(stats_frame, text="0", foreground="red")
        self.errors_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(stats_frame, text="Dimensione:").grid(row=1, column=2, sticky=tk.W)
        self.size_label = ttk.Label(stats_frame, text="0 MB")
        self.size_label.grid(row=1, column=3, sticky=tk.W)
        
        # Area log
        ttk.Label(main_frame, text="Log:", font=('Arial', 10, 'bold')).grid(
            row=13, column=0, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.log_text.grid(row=14, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configurazione ridimensionamento
        main_frame.rowconfigure(14, weight=1)
        
    def browse_source(self):
        """Apre il dialog per selezionare la sorgente"""
        source_type = self.source_type.get()
        
        if source_type == "file":
            filename = filedialog.askopenfilename(
                title="Seleziona file da copiare",
                filetypes=[("Tutti i file", "*.*")]
            )
            if filename:
                self.source_path.set(filename)
        else:
            directory = filedialog.askdirectory(
                title="Seleziona directory sorgente"
            )
            if directory:
                self.source_path.set(directory)
    
    def browse_destination(self):
        """Apre il dialog per selezionare la destinazione"""
        directory = filedialog.askdirectory(
            title="Seleziona directory di destinazione"
        )
        if directory:
            self.dest_path.set(directory)
    
    def log_message(self, message, level="INFO"):
        """Aggiunge un messaggio al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Log su file
        if level == "ERROR":
            logging.error(message)
        elif level == "WARNING":
            logging.warning(message)
        else:
            logging.info(message)
    
    def clear_log(self):
        """Cancella il contenuto del log"""
        self.log_text.delete(1.0, tk.END)
    
    def update_stats(self):
        """Aggiorna le statistiche nell'interfaccia"""
        self.copied_label.config(text=str(self.files_copied))
        self.skipped_label.config(text=str(self.files_skipped))
        self.errors_label.config(text=str(self.errors))
        
        size_mb = self.total_size / (1024 * 1024)
        if size_mb < 1024:
            self.size_label.config(text=f"{size_mb:.1f} MB")
        else:
            size_gb = size_mb / 1024
            self.size_label.config(text=f"{size_gb:.2f} GB")
    
    def validate_inputs(self):
        """Valida gli input dell'utente"""
        if not self.source_path.get().strip():
            raise ValueError("Seleziona il percorso sorgente")
        
        if not self.dest_path.get().strip():
            raise ValueError("Seleziona il percorso di destinazione")
        
        source = self.source_path.get().strip()
        if not os.path.exists(source):
            raise ValueError(f"Il percorso sorgente non esiste: {source}")
        
        # Verifica permessi
        if not os.access(source, os.R_OK):
            raise ValueError(f"Permessi di lettura insufficienti: {source}")
    
    def should_skip_file(self, file_path):
        """Determina se un file deve essere saltato"""
        if not self.skip_system_files.get():
            return False
            
        system_files = {
            'pagefile.sys', 'hiberfil.sys', 'swapfile.sys',
            '$recycle.bin', 'system volume information'
        }
        
        file_name = os.path.basename(file_path).lower()
        return file_name in system_files
    
    def copy_file_safe(self, src, dst):
        """Copia un file con gestione degli errori"""
        try:
            if self.should_stop:
                return False
                
            # Controlla se il file esiste
            if os.path.exists(dst):
                mode = self.overwrite_mode.get()
                if mode == 'skip':
                    self.log_message(f"File saltato (già esiste): {os.path.basename(src)}")
                    self.files_skipped += 1
                    return True
                elif mode == 'newer':
                    if os.path.getmtime(src) <= os.path.getmtime(dst):
                        self.log_message(f"File saltato (più vecchio): {os.path.basename(src)}")
                        self.files_skipped += 1
                        return True
            
            # Crea directory di destinazione se necessaria
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            
            # Copia il file
            if self.preserve_timestamps.get():
                shutil.copy2(src, dst)
            else:
                shutil.copy(src, dst)
            
            file_size = os.path.getsize(src)
            self.total_size += file_size
            self.files_copied += 1
            
            self.log_message(f"Copiato: {os.path.basename(src)}")
            return True
            
        except PermissionError:
            self.log_message(f"Permesso negato: {os.path.basename(src)}", "ERROR")
            self.errors += 1
        except Exception as e:
            self.log_message(f"Errore copiando {os.path.basename(src)}: {str(e)}", "ERROR")
            self.errors += 1
        
        return False
    
    def backup_worker(self):
        """Thread worker per il backup"""
        try:
            source = self.source_path.get().strip()
            dest = self.dest_path.get().strip()
            
            self.log_message(f"Avvio backup da: {source}")
            self.log_message(f"Destinazione: {dest}")
            
            if os.path.isfile(source):
                # Backup singolo file
                dest_file = os.path.join(dest, os.path.basename(source))
                self.copy_file_safe(source, dest_file)
            else:
                # Backup directory
                for root, dirs, files in os.walk(source):
                    if self.should_stop:
                        break
                        
                    for file in files:
                        if self.should_stop:
                            break
                            
                        src_file = os.path.join(root, file)
                        
                        # Salta file di sistema se richiesto
                        if self.should_skip_file(src_file):
                            self.files_skipped += 1
                            continue
                        
                        # Calcola percorso destinazione
                        rel_path = os.path.relpath(src_file, source)
                        dest_file = os.path.join(dest, rel_path)
                        
                        self.copy_file_safe(src_file, dest_file)
                        
                        # Aggiorna GUI periodicamente
                        if (self.files_copied + self.files_skipped) % 10 == 0:
                            self.root.after(0, self.update_stats)
            
            # Aggiornamento finale
            self.root.after(0, self.backup_completed)
            
        except Exception as e:
            self.root.after(0, lambda: self.backup_error(str(e)))
    
    def backup_completed(self):
        """Chiamata quando il backup è completato"""
        self.is_running = False
        self.should_stop = False
        
        self.progress.stop()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.update_stats()
        
        if self.should_stop:
            self.log_message("Backup interrotto dall'utente", "WARNING")
        else:
            self.log_message("Backup completato!")
            
        # Mostra riepilogo
        messagebox.showinfo(
            "Backup Completato",
            f"Backup terminato!\n\n"
            f"File copiati: {self.files_copied}\n"
            f"File saltati: {self.files_skipped}\n"
            f"Errori: {self.errors}\n"
            f"Dimensione totale: {self.total_size / (1024*1024):.1f} MB"
        )
    
    def backup_error(self, error_msg):
        """Gestisce gli errori del backup"""
        self.is_running = False
        self.should_stop = False
        
        self.progress.stop()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.log_message(f"Errore durante il backup: {error_msg}", "ERROR")
        messagebox.showerror("Errore", f"Errore durante il backup:\n{error_msg}")
    
    def start_backup(self):
        """Avvia il processo di backup"""
        try:
            self.validate_inputs()
            
            # Reset statistiche
            self.files_copied = 0
            self.files_skipped = 0
            self.errors = 0
            self.total_size = 0
            self.should_stop = False
            
            self.update_stats()
            
            # Aggiorna interfaccia
            self.is_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress.start()
            
            # Avvia thread di backup
            backup_thread = threading.Thread(target=self.backup_worker)
            backup_thread.daemon = True
            backup_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Errore di Input", str(e))
    
    def stop_backup(self):
        """Ferma il backup in corso"""
        self.should_stop = True
        self.log_message("Richiesta di interruzione backup...", "WARNING")

def main():
    root = tk.Tk()
    
    # Configura lo stile
    style = ttk.Style()
    style.theme_use('clam')  # Tema moderno
    
    # Stile personalizzato per il pulsante principale
    style.configure('Accent.TButton', foreground='white', background='#0078d4')
    style.map('Accent.TButton', background=[('active', '#106ebe')])
    
    app = BackupGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
