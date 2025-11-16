'''

    2025
    Author: Giulio Segre
    www.giulio-virtual-world.com

'''




import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class BackupManager:
    def __init__(self):
        self.files_copied = 0
        self.files_skipped = 0
        self.errors = 0
        self.total_size = 0

    def validate_disk_letter(self, disk_letter):
        """Valida la lettera del disco e verifica che sia accessibile"""
        disk_letter = disk_letter.upper().strip()
        
        if len(disk_letter) != 1 or not disk_letter.isalpha():
            raise ValueError("Inserisci una singola lettera valida (A-Z)")
        
        disk_path = disk_letter + ":\\"
        
        if not os.path.exists(disk_path):
            raise ValueError(f"L'unità {disk_letter}: non esiste o non è accessibile")
        
        # Verifica se l'unità è pronta (importante per unità rimovibili)
        try:
            os.listdir(disk_path)
        except PermissionError:
            raise ValueError(f"Accesso negato all'unità {disk_letter}:")
        except OSError as e:
            raise ValueError(f"Errore nell'accesso all'unità {disk_letter}: {e}")
        
        return disk_path

    def validate_path(self, path):
        """Valida che il percorso esista ed sia accessibile"""
        if not os.path.exists(path):
            raise ValueError(f"Il percorso '{path}' non esiste")
        
        if not os.access(path, os.R_OK):
            raise ValueError(f"Permessi di lettura insufficienti per '{path}'")
        
        return True

    def get_directory_size(self, path):
        """Calcola la dimensione totale di una directory"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        continue
        except PermissionError:
            logging.warning(f"Impossibile accedere ad alcune directory in {path}")
        
        return total_size

    def check_available_space(self, dest_path, required_space):
        """Verifica se c'è spazio sufficiente nella destinazione"""
        try:
            free_space = shutil.disk_usage(dest_path)[2]  # bytes liberi
            if free_space < required_space:
                required_gb = required_space / (1024**3)
                free_gb = free_space / (1024**3)
                raise ValueError(
                    f"Spazio insufficiente. Richiesti: {required_gb:.2f} GB, "
                    f"Disponibili: {free_gb:.2f} GB"
                )
        except OSError as e:
            logging.warning(f"Impossibile verificare lo spazio disponibile: {e}")

    def should_skip_file(self, file_path):
        """Determina se un file deve essere saltato"""
        # File di sistema Windows da evitare
        system_files = {
            'pagefile.sys', 'hiberfil.sys', 'swapfile.sys',
            '$recycle.bin', 'system volume information'
        }
        
        file_name = os.path.basename(file_path).lower()
        return file_name in system_files

    def copy_file_with_progress(self, src, dst, overwrite_mode):
        """Copia un singolo file con gestione degli errori migliorata"""
        try:
            # Controlla se il file di destinazione esiste già
            if os.path.exists(dst):
                if overwrite_mode == 'skip':
                    logging.info(f"File già esistente, saltato: {dst}")
                    self.files_skipped += 1
                    return True
                elif overwrite_mode == 'newer':
                    src_mtime = os.path.getmtime(src)
                    dst_mtime = os.path.getmtime(dst)
                    if src_mtime <= dst_mtime:
                        logging.info(f"File di destinazione più recente, saltato: {dst}")
                        self.files_skipped += 1
                        return True
            
            # Copia il file preservando metadati
            shutil.copy2(src, dst)
            file_size = os.path.getsize(src)
            self.total_size += file_size
            self.files_copied += 1
            
            logging.info(f"Copiato: {src} -> {dst} ({file_size} bytes)")
            return True
            
        except PermissionError:
            logging.error(f"Permesso negato: {src}")
            self.errors += 1
            return False
        except FileNotFoundError:
            logging.error(f"File non trovato: {src}")
            self.errors += 1
            return False
        except OSError as e:
            logging.error(f"Errore OS durante la copia di {src}: {e}")
            self.errors += 1
            return False
        except Exception as e:
            logging.error(f"Errore imprevisto durante la copia di {src}: {e}")
            self.errors += 1
            return False

    def backup_files(self, source_path, dest_path, overwrite_mode='ask'):
        """Esegue il backup dei file con gestione avanzata"""
        logging.info(f"Inizio backup da '{source_path}' a '{dest_path}'")
        
        # Verifica percorsi
        self.validate_path(source_path)
        
        # Calcola dimensione totale e verifica spazio
        if os.path.isdir(source_path):
            required_space = self.get_directory_size(source_path)
            logging.info(f"Dimensione totale da copiare: {required_space / (1024**3):.2f} GB")
            self.check_available_space(dest_path, required_space)
        
        # Crea directory di destinazione se non esiste
        os.makedirs(dest_path, exist_ok=True)
        
        if os.path.isfile(source_path):
            # Copia singolo file
            dest_file = os.path.join(dest_path, os.path.basename(source_path))
            self.copy_file_with_progress(source_path, dest_file, overwrite_mode)
        else:
            # Copia directory ricorsivamente
            for root, dirs, files in os.walk(source_path):
                # Calcola percorso relativo
                relative_path = os.path.relpath(root, source_path)
                dest_dir = os.path.join(dest_path, relative_path) if relative_path != '.' else dest_path
                
                # Crea directory di destinazione
                os.makedirs(dest_dir, exist_ok=True)
                
                # Copia tutti i file nella directory corrente
                for file in files:
                    src_file = os.path.join(root, file)
                    
                    # Salta file di sistema
                    if self.should_skip_file(src_file):
                        logging.info(f"File di sistema saltato: {src_file}")
                        self.files_skipped += 1
                        continue
                    
                    dest_file = os.path.join(dest_dir, file)
                    self.copy_file_with_progress(src_file, dest_file, overwrite_mode)
        
        # Stampa statistiche finali
        self.print_summary()

    def print_summary(self):
        """Stampa il riepilogo dell'operazione di backup"""
        print("\n" + "="*50)
        print("RIEPILOGO BACKUP")
        print("="*50)
        print(f"File copiati: {self.files_copied}")
        print(f"File saltati: {self.files_skipped}")
        print(f"Errori: {self.errors}")
        print(f"Dimensione totale copiata: {self.total_size / (1024**3):.2f} GB")
        print("="*50)
        
        if self.errors > 0:
            print(f"Attenzione: {self.errors} errori rilevati. Controlla il file di log per dettagli.")

def get_overwrite_mode():
    """Chiede all'utente come gestire i file esistenti"""
    while True:
        choice = input(
            "Come gestire i file già esistenti?\n"
            "1. Sovrascrivi sempre (overwrite)\n"
            "2. Salta file esistenti (skip)\n"
            "3. Sovrascrivi solo se più recente (newer)\n"
            "4. Chiedi per ogni file (ask)\n"
            "Scelta (1-4): "
        ).strip()
        
        mode_map = {
            '1': 'overwrite',
            '2': 'skip', 
            '3': 'newer',
            '4': 'ask'
        }
        
        if choice in mode_map:
            return mode_map[choice]
        print("Scelta non valida. Inserisci un numero da 1 a 4.")

def main():
    backup_manager = BackupManager()
    
    try:
        # Input percorso sorgente
        while True:
            source_choice = input(
                "Scegli il tipo di sorgente:\n"
                "1. Disco intero\n"
                "2. Directory specifica\n"
                "3. File specifico\n"
                "Scelta (1-3): "
            ).strip()
            
            if source_choice == '1':
                source_disk = backup_manager.validate_disk_letter(
                    input("Inserisci la lettera del disco di origine: ")
                )
                source_path = source_disk
                break
            elif source_choice == '2':
                source_disk = backup_manager.validate_disk_letter(
                    input("Inserisci la lettera del disco di origine: ")
                )
                source_dir = input("Inserisci la directory di origine (es. Users\\NomeUtente\\Documents): ").strip()
                source_path = os.path.join(source_disk, source_dir)
                break
            elif source_choice == '3':
                source_path = input("Inserisci il percorso completo del file: ").strip()
                break
            else:
                print("Scelta non valida. Inserisci 1, 2 o 3.")
        
        # Input percorso destinazione
        dest_disk = backup_manager.validate_disk_letter(
            input("Inserisci la lettera del disco di destinazione: ")
        )
        dest_dir = input("Inserisci la directory di destinazione: ").strip()
        dest_path = os.path.join(dest_disk, dest_dir)
        
        # Modalità gestione file esistenti
        overwrite_mode = get_overwrite_mode()
        
        # Conferma prima di iniziare
        print(f"\nConfigurazione backup:")
        print(f"Sorgente: {source_path}")
        print(f"Destinazione: {dest_path}")
        print(f"Modalità conflitti: {overwrite_mode}")
        
        confirm = input("\nVuoi procedere? (s/n): ").strip().lower()
        if confirm not in ['s', 'si', 'sì', 'y', 'yes']:
            print("Backup annullato.")
            return
        
        # Esegui backup
        backup_manager.backup_files(source_path, dest_path, overwrite_mode)
        
        print("\nBackup completato!")
        
    except KeyboardInterrupt:
        print("\n\nBackup interrotto dall'utente.")
    except ValueError as e:
        print(f"Errore di input: {e}")
        logging.error(f"Errore di input: {e}")
    except Exception as e:
        print(f"Errore imprevisto: {e}")
        logging.error(f"Errore imprevisto: {e}")

if __name__ == "__main__":
    main()
