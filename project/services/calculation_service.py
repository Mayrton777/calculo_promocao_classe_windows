import geopandas as gpd
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import pandas as pd
import re
import shapely.geometry
import tempfile

matplotlib.use('Agg')

class CalculationService:
    def __init__(self, path_census_sectors: Path, path_uf: Path, data: dict):
        # Caminho do mapa
        self.path_census_sectors = path_census_sectors
        # Caminho do arquivo de UFs
        with open(path_uf, 'r', encoding='utf-8') as file:
            self.uf_names = json.load(file)

        # Dados do processo
        self.process_number = data['numero_processo']
        self.service = data['servico']
        self.entity = data['entidade']
        self.finality = data['finalidade']
        self.public_consultation = data['consulta_publica']

        # Dados da estação atual
        self.current_municipality = data['municipio_atual']
        self.current_state = data['uf_atual']
        self.current_class = data['classe_atual']
        self.current_channel = data['canal_atual']
        self.current_latitude = data['latitude_atual']
        self.current_longitude = data['longitude_atual']

        # Dados da situação proposta
        self.proposed_municipality = data['municipio_proposto']
        self.proposed_state = data['uf_proposta']
        self.proposed_class = data['classe_proposta']
        self.proposed_channel = data['canal_proposto']
        self.proposed_latitude = data['latitude_proposta']
        self.proposed_longitude = data['longitude_proposta']

        # Mapeia as siglas para os nomes completos
        self.current_name_state = self.uf_names.get(self.current_state)
        self.proposed_name_state = self.uf_names.get(self.proposed_state)

        self.dmax_values = {
            'e': [(range(0, 14), 65.6), (range(14, 47), 58.0), (range(47, 100), 58.0)],
            'especial': [(range(0, 14), 65.6), (range(14, 47), 58.0), (range(47, 100), 58.0)],
            'a': [(range(0, 14), 47.9), (range(14, 100), 42.5)],
            'b': [(range(0, 14), 32.3), (range(14, 100), 29.1)],
            'c': [(range(0, 14), 20.2), (range(14, 52), 18.1), (range(52, 100), 7.5)],
            'e1': 78.5, 'e2': 67.5, 'e3': 54.5, 'a1': 38.5, 'a2': 35.0, 'a3': 30.0,
            'a4': 24.0, 'b1': 16.5, 'b2': 12.5
        }

        self.proposed_latitude_decimal = self.dms_for_decimal(self.proposed_latitude)
        self.proposed_longitude_decimal = self.dms_for_decimal(self.proposed_longitude)
        self.dmax_contour = str(self.dmax_cp(self.proposed_class, self.proposed_channel))

        # Geodataframe do contorno protegido circular da classe proposta do canal
        self.gdf_protected_contour = self.create_circle_gdf(
            self.proposed_latitude_decimal, self.proposed_longitude_decimal, float(self.dmax_contour))
        
        # Geodaframe dos polígonos dos municípios
        self.gdf_census_municipalities = gpd.read_file(self.path_census_sectors)

        # O 'op='intersects'' garante que apenas as geometrias que se sobrepõem serão incluídas
        self.intersected_municipalities = gpd.sjoin(self.gdf_census_municipalities, self.gdf_protected_contour, predicate='intersects')

        # Pega os nomes dos estados únicos da coluna 'NM_UF' do geodataframe resultante
        unique_states = self.intersected_municipalities['NM_UF'].unique()

        # Trabalha com uma fatia menor do geodataframe
        self.gdf_census_municipalities = self.gdf_census_municipalities[self.gdf_census_municipalities['NM_UF'].isin(unique_states)]

        # DataFrame
        self.df = pd.DataFrame(self.gdf_census_municipalities)

        # Filtra o DataFrame para encontrar o município desejado com base no estado e nome
        matched_municipality = self.df[
            (self.df['NM_MUN'] == self.proposed_municipality) & 
            (self.df['NM_UF'] == self.proposed_name_state)
        ]

        # Captura o código do município ('CD_MUN') do primeiro resultado
        if not matched_municipality.empty:
            self.proposed_municipality_code = matched_municipality['CD_MUN'].iloc[0]
        else:
            self.proposed_municipality_code = None
            print(f"Município '{self.proposed_municipality}' em '{self.proposed_name_state}' não encontrado no DataFrame.")

        self.promotion_period = {
            'C': {'B2': 0, 'B1': 0, 'A4': 2, 'A3': 2, 'A2': 6, 'A1': 6, 'E3': 8, 'E2': 10, 'E1': 12},
            'B2': {'B1': 0, 'A4': 0, 'A3': 2, 'A2': 4, 'A1': 4, 'E3': 6, 'E2': 8, 'E1': 10},
            'B1': {'A4': 0, 'A3': 0, 'A2': 2, 'A1': 2, 'E3': 4, 'E2': 6, 'E1': 8},
            'A4': {'A3': 0, 'A2': 0, 'A1': 2, 'E3': 4, 'E2': 6, 'E1': 8},
            'A3': {'A2': 0, 'A1': 0, 'E3': 2, 'E2': 4, 'E1': 6},
            'A2': {'A1': 0, 'E3': 2, 'E2': 4, 'E1': 6},
            'A1': {'E3': 0, 'E2': 2, 'E1': 4},
            'E3': {'E2': 0, 'E1': 2},
            'E2': {'E1': 0}
        }

        self.referencias = {
            'B': {
                'SC': ['4209102', 'Joinville', 363499.72],
                'AC': ['1200401', 'Rio Branco', 32586.82],
                'AL': ['2704302', 'Maceió', 144040.28],
                'AP': ['1600303', 'Macapá', 60014.83],
                'BA': ['2927408', 'Salvador', 169291.50],
                'AM': ['1302603', 'Manaus', 78099.69],
                'MA': ['2111300', 'São Luís', 144005.30],
                'PA': ['1501402', 'Belém', 85097.28],
                'SP': {
                    'padrao': ['3509502', 'Campinas', 249622.55],
                    'especifico': ['3503901', '3505708', '3506607', '3509007', '3509205', '3510609', 
                                '3513009', '3513801', '3515004', '3515103', '3515707', '3516309',
                                '3516408', '3518305', '3518800', '3522208', '3522505', '3523107',
                                '3525003', '3526209', '3528502', '3529401', '3530607', '3534401',
                                '3539103', '3539806', '3543303', '3544103', '3545001', '3546801',
                                '3547304', '3547809', '3548708', '3548807', '3549953', '3550308',
                                '3552502', '3552809', '3556453']
                },
                'CE': ['2304400', 'Fortaleza', 166419.21],
                'GO': ['5208707', 'Goiânia', 235323.01],
                'SE': ['2800308', 'Aracajú', 141640.89],
                'MG': ['3106200', 'Belo Horizonte', 53718.66],
                'PB': ['2507507', 'João Pessoa', 144582.39],
                'MT': ['5103403', 'Cuiabá', 164843.20],
                'MS': ['5002704', 'Campo Grande', 215788.29],
                'DF': ['5300108', 'Brasília', 307127.24],
                'RO': ['1100205', 'Porto Velho', 45590.69],
                'RJ': ['3304557', 'Rio de Janeiro', 701663.27],
                'PE': ['2611606', 'Recife', 157833.60],
                'PR': ['4106902', 'Curitiba', 469494.06],
                'PI': ['2211001', 'Teresina', 144681.50],
                'RN': ['2408102', 'Natal', 145172.62],
                'RR': ['1400100', 'Boa Vista', 27459.32],
                'RS': ['4314902', 'Porto Alegre', 425475.87],
                'ES': ['3205200', 'Vila Velha', 69587.43],
                'TO': ['1721000', 'Palmas', 15473.83]
            },
            'C': {
                'SC': ['4209102', 'Joinville', 852817.55],
                'AC': ['1200401', 'Rio Branco', 77202.31],
                'AL': ['2704302', 'Maceió', 337505.73],
                'AP': ['1600303', 'Macapá', 111663.65],
                'BA': ['2927408', 'Salvador', 397584.59],
                'AM': ['1302603', 'Manaus', 183187.51],
                'MA': ['2111300', 'São Luís', 338625.89],
                'PA': ['1501402', 'Belém', 199600.76],
                'SP': {
                    'padrao': ['3509502', 'Campinas', 585504.63],
                    'especifico': ['3503901', '3505708', '3506607', '3509007', '3509205', '3510609', 
                                '3513009', '3513801', '3515004', '3515103', '3515707', '3516309',
                                '3516408', '3518305', '3518800', '3522208', '3522505', '3523107',
                                '3525003', '3526209', '3528502', '3529401', '3530607', '3534401',
                                '3539103', '3539806', '3543303', '3544103', '3545001', '3546801',
                                '3547304', '3547809', '3548708', '3548807', '3549953', '3550308',
                                '3552502', '3552809', '3556453']
                },
                'CE': ['2304400', 'Fortaleza', 391262.94],
                'GO': ['5208707', 'Goiânia', 551639.11],
                'SE': ['2800308', 'Aracajú', 332431.61],
                'MG': ['3106200', 'Belo Horizonte', 125672.29],
                'PB': ['2507507', 'João Pessoa', 338855.67],
                'MT': ['5103403', 'Cuiabá', 387763.39],
                'MS': ['5002704', 'Campo Grande', 505001.04],
                'DF': ['5300108', 'Brasília', 720385.32],
                'RO': ['1100205', 'Porto Velho', 105637.44],
                'RJ': ['3304557', 'Rio de Janeiro', 1629200.59],
                'PE': ['2611606', 'Recife', 369776.49],
                'PR': ['4106902', 'Curitiba', 1098420.32],
                'PI': ['2211001', 'Teresina', 339511.65],
                'RN': ['2408102', 'Natal', 340511.07],
                'RR': ['1400100', 'Boa Vista', 64624.06],
                'RS': ['4314902', 'Porto Alegre', 995714.32],
                'ES': ['3205200', 'Vila Velha', 79940.86],
                'TO': ['1721000', 'Palmas', 36039.46]
            }
        }
    
    def municipality_state(self, number_municipality, state):
        return f'{number_municipality} - {state}'
    
    def dms_for_decimal(self, dms):
        dms = dms.upper().strip().replace(' ', '').replace("’", "'").replace('”', '"').replace("''", '"').replace(',', '.')
        direction = re.findall(r'[A-Z]', dms)
        dms = re.sub(r'[A-Z]', '', dms)
        degree = float(dms.split('°')[0])
        minute = float(dms.split('°')[1].split("'")[0])
        second = float(dms.split('°')[1].split("'")[1].split('"')[0])
        decimal = degree + minute/60 + second/3600

        if 'S' in direction or 'W' in direction:
            decimal = -decimal

        return decimal

    def get_reference_value(self, state, classification, city_code):
        if classification in self.referencias and state in self.referencias[classification]:
            if state == 'SP':
                if city_code in self.referencias[classification][state]['especifico']:
                    return ['NA', 'Região Metropolitana de São Paulo', 2376643.72 if classification == 'B' else 5574558.80]
                return self.referencias[classification][state]['padrao']
            return self.referencias[classification][state]
        return 'Referência não encontrada'
    
    def class_group(self, classe):
        grupos = {
            'A': ['B1', 'B2', 'C'],
            'B': ['A', 'A1', 'A2', 'A3', 'A4', 'B'],
            'C': ['E1', 'E2', 'E3', 'E']
        }
        for grupo, classes in grupos.items():
            if classe in classes:
                return grupo
        return 'classe inexistente'
    
    def check_class_change(self, current_class, proposed_class):
        classes = ['C', 'B2', 'B1', 'A4', 'A3', 'A2', 'A1', 'E3', 'E2', 'E1']
        if current_class in classes and proposed_class in classes:
            if classes.index(current_class) == classes.index(proposed_class):
                return "sem mudança de classe"
            elif classes.index(current_class) < classes.index(proposed_class):
                return "promoção de classe"
            else:
                return "redução de classe"
        
        if current_class not in classes and proposed_class not in classes:
            return 'classe atual e proposta inexistente'
        else:
            return 'classe inexistente'

    def tcp(self, current_class, proposed_class):
        if self.check_class_change(current_class, proposed_class) != "promoção de classe":
            return "não se aplica"

        return self.promotion_period.get(current_class, {}).get(proposed_class, "não se aplica")
    
    def check_change_type(self, current_class, proposed_class):
        if self.check_class_change(current_class, proposed_class) == "promoção de classe":
            return "gradual" if self.tcp(current_class, proposed_class) == 0 else "não gradual"
        return "não se aplica"
    
    def check_group_change(self, current_class, proposed_class):
        classes = ['C', 'B2', 'B1', 'A4', 'A3', 'A2', 'A1', 'E3', 'E2', 'E1']
        grupos = ['A', 'B', 'C']

        if current_class in classes and proposed_class in classes:
            current_group = self.class_group(current_class)
            proposed_group = self.class_group(proposed_class)
            if current_group == proposed_group:
                return f"sem mudança de grupo - {current_group}"
            elif grupos.index(current_group) < grupos.index(proposed_group):
                return f"promoção de grupo - {current_group} para {proposed_group}"
            else:
                return f"redução de grupo - {current_group} para {proposed_group}"
        return 'classe atual e proposta inexistente' if current_class not in classes and proposed_class not in classes else 'classe inexistente'
    
    def check_payment(self, current_class, proposed_class):
        change = self.check_group_change(current_class, proposed_class)
        if "redução de grupo" in change:
            return "sem cobrança"
        elif "promoção de grupo" in change:
            return "com cobrança"
        elif "sem mudança de grupo" in change:
            return "sem cobrança" if self.tcp(current_class, proposed_class) in [0, "não se aplica"] else "com cobrança"
        else:
            return "não se aplica"

    def dmax_cp(self, classe, canal=None):
        classe_lower = classe.lower()
        if classe_lower in self.dmax_values:
            val = self.dmax_values[classe_lower]
            if isinstance(val, list):
                for r, dmax in val:
                    if canal in r:
                        return dmax
                return 7.5  # padrão se não encontrar faixa
            return val
        return 7.5
    
    def get_municipality_with_code(self, code):
        """
        Retorna a população total de um município a partir de seu código.
        """
        # Filtra o GeoDataFrame para incluir apenas os setores censitários do município com o código fornecido.
        municipality_sectors = self.gdf_municipalities[self.gdf_municipalities.CD_MUN == code]

        # Soma a população de todos os setores do município.
        total_municipality_population = municipality_sectors['v0001'].sum()

        # Retorna o nome do município, a UF e a população total.
        municipality_name = municipality_sectors['NM_MUN'].iloc[0]
        uf_name = municipality_sectors['NM_UF'].iloc[0]

        return f"{uf_name}/{municipality_name}/{int(total_municipality_population)}"


    def create_circle_gdf(self, latitude, longitude, radius):
        # Gera um GeoDataFrame de um círculo com centro em (latitude, longitude) e raio em metros.
        # Latitude e longitude em graus, raio em km.

        circle_center = shapely.geometry.Point(longitude, latitude)
        gdf_circle_center = gpd.GeoDataFrame(geometry=[circle_center], crs='EPSG:4674')
        circle_center_utm = gdf_circle_center.to_crs(epsg=5880)
        circle_utm = circle_center_utm.buffer(radius * 1000)  # raio convertido para metros
        circle = circle_utm.to_crs('EPSG:4674')

        return gpd.GeoDataFrame(geometry=circle)

    # Cálculo de dados intermediários
    def data_process(self, current_class, proposed_class, current_latitude, current_longitude, proposed_sit_state, proposed_sit_city_code):
        
        self.current_group = self.class_group(current_class)
        self.proposed_group = self.class_group(proposed_class)
        
        self.current_latitude_decimal = self.dms_for_decimal(current_latitude)
        self.current_longitude_decimal = self.dms_for_decimal(current_longitude)
        self.tcp_value = self.tcp(current_class, proposed_class)
        self.reference_city_code = self.get_reference_value(
            proposed_sit_state, self.proposed_group, proposed_sit_city_code
        )[0]
        self.reference_city = self.get_reference_value(
            proposed_sit_state, self.proposed_group, proposed_sit_city_code
        )[1]
        self.change_type = self.check_change_type(current_class, proposed_class)

    def geo_process(self):
        # Geodataframe da estação na situação proposta
        station_coordinates = shapely.geometry.Point(self.proposed_longitude_decimal, self.proposed_latitude_decimal)
        self.gdf_station = gpd.GeoDataFrame(geometry=[station_coordinates], crs='EPSG:4674')

        self.teste = self.gdf_census_municipalities.dissolve(by='CD_MUN', aggfunc={'NM_MUN': 'first', 'v0001': 'sum'})
        self.teste_mun = gpd.sjoin(self.teste, self.gdf_protected_contour, predicate='intersects')
        # Municípios que fazem interseção com o contorno protegido da classe do canal
        self.gdf_municipalities = gpd.sjoin(self.gdf_census_municipalities, self.gdf_protected_contour, predicate='intersects')
        self.gdf_municipalities = self.gdf_municipalities.drop('index_right', axis=1)
        self.gdf_municipalities = self.gdf_municipalities.reset_index(drop=True)

        # União das geometrias dos municípios para criar uma máscara
        gdf_united_municipalities = self.gdf_municipalities.copy()
        gdf_united_municipalities['Unir'] = 1
        gdf_united_municipalities = gdf_united_municipalities.dissolve(by='Unir')

        # Setores censitários dos municípios que fazem interseção com o contorno protegido
        gdf_census_sectors = gpd.read_file(self.path_census_sectors, mask=gdf_united_municipalities)

        # Setores censitários urbanos
        urban_census_sectors_filter = gdf_census_sectors.SITUACAO == 'Urbana'
        self.gdf_urban_census_sectors = gdf_census_sectors[urban_census_sectors_filter].reset_index(drop=True)

        # Geodataframe da interseção entre os setores censitários urbanos e o contorno protegido
        self.gdf_urban_sectors_cp_intersection = self.gdf_urban_census_sectors[self.gdf_urban_census_sectors.intersects(self.gdf_protected_contour.geometry[0])]
        self.gdf_urban_sectors_cp_intersection = self.gdf_urban_sectors_cp_intersection.reset_index(drop=True)

        # Geodataframe dos municípios cujas áreas urbanas são intersectadas pelo contorno protegido
        self.covered_municipalities_codes = list(self.gdf_urban_sectors_cp_intersection.CD_MUN.unique())
        self.gdf_municipalities_with_urban_area_reached = self.gdf_municipalities[self.gdf_municipalities.CD_MUN.isin(self.covered_municipalities_codes)]
        self.gdf_municipalities_with_urban_area_reached = self.gdf_municipalities_with_urban_area_reached.reset_index(drop=True)

        self.gdf_municipalities_with_urban_area_reached['MUNICIPIO-UF'] = np.vectorize(self.municipality_state)(
            self.gdf_municipalities_with_urban_area_reached['NM_MUN'], self.gdf_municipalities_with_urban_area_reached['NM_UF'])
        
        covered_municipalities = []
        for code in self.covered_municipalities_codes:
            covered_municipalities.append(self.get_municipality_with_code(code))
    
    def creat_map(self):
        fig, ax = plt.subplots(1,1,figsize=(12,10))
        #ax.grid(color='grey', linestyle='--', linewidth=0.5)

        # Municípios atingidos pelo contorno protegido
        self.teste_mun.plot(ax=ax, color='None', edgecolor='black', linewidth=3)
        self.gdf_municipalities.plot(ax=ax, color='None', edgecolor='black', linewidth=0.5)
        
        # Municípios com áreas urbanas atingidas pelo contorno protegido
        self.gdf_municipalities_with_urban_area_reached.plot(ax=ax, column='MUNICIPIO-UF', categorical=True, edgecolor='black', cmap='turbo', linewidth=0.1, alpha = 0.7, legend=False)

        # Setores urbanos dos municípios atingidos pelo contorno protegido
        #self.gdf_urban_census_sectors.plot(ax=ax, color='None', edgecolor='orange', linewidth=0.5)

        # Áreas urbanas atingidas pelo contorno protegido
        self.gdf_urban_sectors_cp_intersection.plot(ax=ax, color='None', edgecolor='red', linewidth=0.5)

        # Estação na situação proposta
        self.gdf_station.plot(ax=ax, color='yellow', edgecolor='black', linewidth=1.5)
        #ax.annotate("ESTAÇÃO", xy=(gdf_estacao.geometry.x, gdf_estacao.geometry.y), xytext=(3, 3), textcoords="offset points", fontsize=6, color='black')

        # Circunferência do contorno protegido teórico
        self.gdf_protected_contour.plot(ax = ax, color='none', edgecolor='red', linewidth=1.5, linestyle='dashed')

        # Mapa
        plt.title('Municípios com áreas urbanas atingidas pelo contorno protegido da classe proposta', fontsize=13, y=1.01)

        # --- INÍCIO DA ALTERAÇÃO ---
        
        # 1. Pega o diretório temporário do sistema
        temp_dir = tempfile.gettempdir()

        # 2. Cria um nome de arquivo único
        imagem_name = self.process_number.replace('/', '-').replace('.', '_')
        mapa_filename = f'img_{imagem_name}.png'
        
        # 3. Cria o caminho completo no diretório temporário
        caminho_salvar_mapa_temp = os.path.join(temp_dir, mapa_filename)

        # 4. Salva o mapa nesse caminho
        plt.savefig(caminho_salvar_mapa_temp)
        plt.close(fig) # Fecha a figura para liberar a memória

        # 5. Retorna o caminho onde o mapa foi salvo
        return caminho_salvar_mapa_temp

    def calculo_promocao_classe(self, population):
        # Carregamento dos dados populacionais
        df_populacao = self.gdf_census_municipalities
        df_populacao['CD_MUN'] = df_populacao['CD_MUN'].astype(str)

        # População dos municípios cobertos
        df_populacao_municipios_cobertos = df_populacao[df_populacao.CD_MUN.isin(self.covered_municipalities_codes)]
        df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.reset_index(drop=True)
        filtro_mun_ref = df_populacao["CD_MUN"] == self.reference_city_code

        num_population = []
        for item in population:
            match = re.search(r'\d+$', item)
            if match:
                num_population.append(int(match.group()))

        # # População dos municípios cobertos
        self.Ptot = sum(num_population)

        # if self.proposed_state == 'SP': # população do município de referência
        #     if self.reference_city_code == '3509502':
        #         self.Pref = int(1139047)
        #     else:
        #         self.Pref = int(20743587) 
        # else:
        
        # Soma todos os v0001 do município de referência
        self.Pref = int(df_populacao[filtro_mun_ref]['v0001'].sum())

        print(self.current_group)
        if self.current_group == 'A':
            if self.proposed_group == 'A':
                self.Vab, self.Vbc = 0, 0
            elif self.proposed_group == 'B':
                self.Vab = self.get_reference_value(self.proposed_state, self.proposed_group, self.reference_city_code)[2]
                self.Vbc = 0
            elif self.proposed_group == 'C':
                self.Vab = self.get_reference_value(self.proposed_state, 'B', self.reference_city_code)[2]
                self.Vbc = self.get_reference_value(self.proposed_state, self.proposed_group, self.reference_city_code)[2]
        elif self.current_group == 'B':
            if self.proposed_group == 'A':
                self.Vab, self.Vbc = 0, 0
            elif self.proposed_group == 'B':
                if self.tcp_value == 0:
                    self.Vab, self.Vbc = 0, 0
                else:
                    self.Vab = self.get_reference_value(self.proposed_state, 'B', self.reference_city_code)[2]
                    self.Vbc = 0
            elif self.proposed_group == 'C':
                self.Vab = 0
                self.Vbc = self.get_reference_value(self.proposed_state, self.proposed_group, self.reference_city_code)[2]
        elif self.current_group == 'C':
            if self.proposed_group == 'A':
                self.Vab, self.Vbc = 0, 0
            elif self.proposed_group == 'B':
                self.Vab, self.Vbc = 0, 0
            elif self.proposed_group == 'C':
                if self.tcp_value == 0:
                    self.Vab, self.Vbc = 0, 0
                else:
                    self.Vab = 0
                    self.Vbc = self.get_reference_value(self.proposed_state, 'C', self.reference_city_code)[2] 
                    
        if self.tcp_value != 'não se aplica':
            self.Vpc = (self.Ptot/self.Pref) * (self.Vab + self.Vbc) * (1+int(self.tcp_value)/10)
            self.Vpc = round(self.Vpc,2)
            self.tcp_value = str(self.tcp_value)
        else:
            self.Vpc = 'não se aplica'
    
    def get_results(self):
        
        # Chame os métodos de processamento de dados e geoprocessamento
        self.data_process(self.current_class, self.proposed_class, self.current_latitude, self.current_longitude, self.proposed_state, self.proposed_municipality_code)
        
        self.geo_process()
        
        # Obtenha os dados calculados para impressão
        proposed_class = self.proposed_class
        dmax_contorno = self.dmax_contour
        municipio_proposto = self.proposed_municipality
        uf_proposta = self.proposed_state
        grupo_proposto = self.proposed_group
        
        covered_municipalities = []
        for code in self.covered_municipalities_codes:
            covered_municipalities.append(self.get_municipality_with_code(code))
        
        self.calculo_promocao_classe(covered_municipalities)
        
        # --- INÍCIO DA ALTERAÇÃO ---
        # Capture o caminho do mapa retornado por creat_map()
        caminho_mapa_temporario = self.creat_map()
        # --- FIM DA ALTERAÇÃO ---
        
        Tcp = self.tcp_value
        Ptot = self.Ptot
        municipio_referencia = self.reference_city
        Vab = self.Vab
        Vbc = self.Vbc
        Pref = self.Pref
        Vpc = self.Vpc
        
        
        
        # # Imprima os resultados
        # print(f"Classe proposta: {proposed_class}\n")
        # print(f"Distância máxima ao contorno protegido: dmax = {dmax_contorno} km\n")
        # print(f"Município e UF da estação: {municipio_proposto}/{uf_proposta}\n")
        # print(f"Grupo de enquadramento proposto: {grupo_proposto}\n")

        # print(f'{len(covered_municipalities)} municípios com área urbana atingida pelo CP da classe: \n')

        # for municipio in covered_municipalities:
        #     print(municipio)
        
        # print(f'\nPopulação total dos municípios cobertos: Ptot = {Ptot:,.0f}\n'.replace(',','.'))
        # print(f"Município de referência: {municipio_referencia}/{uf_proposta}\n")
        # print(f"Valores de referência: Vab = R$ {Vab} e Vbc = R$ {Vbc}\n")
        # print(f'População do município de referência: Pref = {Pref:,}\n'.replace(',','.'))
        # print(f'Valor da promoção de classe: Vpc = R$ {Vpc}\n')

        result_list = {
            'numero_processo': self.process_number,
            'servico': self.service,
            'entidade': self.entity,
            'finalidade': self.finality,
            'consulta_publica': self.public_consultation,
            'municipio_atual': self.current_municipality,
            'uf_atual': self.current_state, 
            'classe_atual': self.current_class, 
            'canal_atual': self.current_channel, 
            'latitude_atual': self.current_latitude, 
            'longitude_atual': self.current_longitude, 
            'municipio_proposto': self.proposed_municipality, 
            'uf_proposta': self.proposed_state, 
            'classe_proposta': self.proposed_class, 
            'canal_proposto': self.proposed_channel, 
            'latitude_proposta': self.proposed_latitude, 
            'longitude_proposta': self.proposed_longitude, 
            'grupo_atual': self.current_group,
            'grupo_proposto': self.proposed_group,
            'municipios_afetados': covered_municipalities,
            'tcp': Tcp,
            'dmax': dmax_contorno,
            'municipio_referencia': municipio_referencia,
            'pref': Pref,
            'valor_ab': Vab,
            'valor_bc': Vbc,
            'ptot': Ptot,
            'vpc': Vpc,
            'caminho_mapa_temp': caminho_mapa_temporario
        }

        return result_list