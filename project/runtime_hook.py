import os
import sys

# Verifica se esta rodando como um executável
if getattr(sys, 'frozen', False):
    
    # sys._MEIPASS é o caminho para a pasta temporária do PyInstaller
    base_path = sys._MEIPASS

    # Adiciona a pasta das DLLs do pyogrio ao PATH
    pyogrio_libs_path = os.path.join(base_path, 'pyogrio.libs')
    os.environ['PATH'] = pyogrio_libs_path + os.pathsep + os.environ.get('PATH', '')
    
    # Adiciona a pasta das DLLs do shapely (geopandas também precisa dele)
    shapely_libs_path = os.path.join(base_path, 'shapely.libs')
    os.environ['PATH'] = shapely_libs_path + os.pathsep + os.environ.get('PATH', '')