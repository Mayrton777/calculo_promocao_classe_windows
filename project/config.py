import os
import sys
from pathlib import Path

# --- LÓGICA DE CAMINHO (PROJECT_ROOT) ---
try:
    # Modo PyInstaller
    PROJECT_ROOT = Path(sys._MEIPASS)
except Exception:
    # Modo Desenvolvimento
    PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))

# --- CAMINHOS DE DADOS ---
PATH_SHP = PROJECT_ROOT / "data" / "mapa" / "BR_setores_CD2022.shp"
PATH_UF_JSON = PROJECT_ROOT / "data" / "uf_code.json"
PATH_IPCA_JSON = PROJECT_ROOT / "data" / "ipca.json"

# --- DADOS DO FORMULÁRIO ---
UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
    "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]
CLASSES = ["E1", "E2", "E3", "A1", "A2", "A3", "A4", "B1", "B2", "C"]
PLACEHOLDER_LAT = "10° 10' 10\" S"
PLACEHOLDER_LON = "10° 10' 10\" W"

def get_default_download_path() -> str:
    """Encontra a pasta de Downloads do usuário ou retorna o diretório atual."""
    try:
        home_dir = Path.home()
        downloads_folder = home_dir / "Downloads"
        
        if not downloads_folder.is_dir():
            downloads_folder = home_dir
    except Exception:
        downloads_folder = Path.cwd()
    
    return str(downloads_folder)