# Documentação: Cálculo de Promoção de Classe



## Guia de Uso

Para executar este projeto, é **necessário** instalar as dependências listadas no arquivo `requirements.txt` e executar o arquivo `main.py` dentro da pasta `project`. Siga o passo a passo abaixo:

1.  **Acessar a pasta `project`**
    ```bash
    cd calculo_promocao_classe_windows
    ```

2.  **Criar e ativar um ambiente virtual**
    ```bash
    python -m venv env
    # No Windows:
    .\env\Scripts\activate
    # No Linux/macOS:
    source env/bin/activate
    ```

3.  **Instalar as dependências do projeto**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Executar o arquivo `main.py`**
    ```bash
    python main.py
    ```

## Estrutura do Projeto

```text
.gitignore                          # Define arquivos e diretórios a serem ignorados pelo Git.
README.md                           # Documentação do projeto, contendo informações sobre instalação e uso.
documentacao/                       # Pasta para documentação principal do projeto.
project/                            # Diretório raiz principal contendo todo o código-fonte e recursos.
├── app/                            # Contém a lógica de interface gráfica.
|   ├── __init__.py                 # Indica que 'app' é um pacote Python.
|   ├── app_controller.py           # Gerencia a lógica de negócios e as interações entre a view e os serviços (MVC Controller).
|   └── app_view.py                 # Define a interface gráfica do usuário usando `ttkbootstrap` (MVC View).
├── data/                           # Contém arquivos de dados estáticos e recursos necessários para os cálculos.
|   ├── mapa/                       # Contém o arquivo GeoJSON/Shapefile do mapa de setores censitários.
|   |   └── BR_setores_CD2022.shp   # Arquivo Shapefile com os setores censitários do IBGE.
|   ├── ipca.json                   # Arquivo JSON estático de fallback com dados históricos do IPCA.
|   └── uf_code.json                # Arquivo JSON que mapeia siglas de UFs para seus nomes completos (ou vice-versa).
├── services/                       # Contém a lógica de negócios e as funções de cálculo e geração de documentos.
|   ├── __init__.py                 # Indica que 'services' é um pacote Python.
|   ├── calculation_service.py      # Implementa toda a lógica de geoprocessamento e os cálculos de promoção de classe.
|   ├── creat_pdf_oficio.py         # Função para gerar o ofício de cobrança no formato Word (.docx).
|   ├── create_pdf.py               # Função para gerar o relatório final em formato PDF.
|   ├── ipca.py                     # Módulo para buscar e calcular a correção monetária pelo IPCA.
|   └── utils.py                    # Funções utilitárias diversas.
├── config.py                       # Centraliza variáveis de configuração e caminhos de arquivos do projeto.
├── main.py                         # Ponto de entrada da aplicação, inicializando a View e o Controller.
├── main.spec                       # Arquivo de especificação PyInstaller para gerar o executável.
├── requirements.txt                # Lista todas as dependências do projeto para instalação via `pip`.
└── runtime_hook.py                 # Script PyInstaller executado no início do executável para configurar caminhos de dependências geoespaciais.
```

## Documentação do Código-Fonte do Projeto

### Documentação do Código: `main.py`

O arquivo `main.py` serve como o **ponto de entrada** (entry point) da aplicação. Sua função principal é configurar o ambiente e orquestrar a inicialização do programa, instanciando os componentes de Interface (View) e Lógica de Controle (Controller) no padrão **MVC (Model-View-Controller)**.

#### Fluxo de Execução

O script é executado quando chamado diretamente (dentro do bloco `if \_\_name\_\_ == "\_\_main\_\_":`).

1.  **Importação**: Importa o módulo `config` (para acesso às constantes de configuração) e as classes `AppView` e `AppController` do pacote `app`.
    
2.  **Configuração de Variáveis**: Carrega as constantes necessárias do `config.py`:
    
    *   `default\_path`: O caminho padrão para salvar os arquivos (pasta de Downloads).
        
    *   `ufs\_list`, `classes\_list`: Listas de UFs e Classes de rádio FM para preenchimento dos campos da GUI.
        
    *   `lat`, `lon`: Valores _placeholder_ (exemplo) para os campos de entrada de coordenadas.
        
3.  **Inicialização da View**: Cria uma instância da classe `AppView` (`view`), configurando a aparência e passando as listas de dados e caminhos padrão.
    
    *   `themename="litera"`: Define o tema visual da interface.
        
    *   `title="Promoção de Classe"`: Define o título da janela.
        
4.  **Inicialização do Controller**: Cria uma instância da classe `AppController` (`controller`), passando a `view` como argumento para que o Controller possa interagir com a interface.
    
5.  **Conexão MVC**: Chama `view.set\_controller(controller)` para injetar a instância do Controller na View, completando a ligação entre os dois componentes.
    
6.  **Loop Principal**: Inicia o `view.mainloop()`, que é o loop de eventos do Tkinter, mantendo a janela da aplicação aberta e responsiva às interações do usuário.
    

#### Estrutura do Código

```python
import config
from app import AppView, AppController

if __name__ == "__main__":
    default_path = config.get_default_download_path()
    ufs_list = config.UFS
    classes_list = config.CLASSES
    lat = config.PLACEHOLDER_LAT
    lon = config.PLACEHOLDER_LON

    view = AppView(
        themename="litera",
        title="Promoção de Classe",
        ufs=ufs_list,
        classes=classes_list,
        default_path=default_path,
        placeholder_lat=lat,
        placeholder_lon=lon
    )

    controller = AppController(view)
    view.set_controller(controller)
    view.mainloop()
```

Este arquivo garante que todas as peças da aplicação (configurações, interface e lógica) sejam carregadas na ordem correta, permitindo que o programa inicie e funcione.

### Documentação do Código: `config.py`

O arquivo `config.py` atua como o **repositório central de configurações** e constantes globais do projeto. Sua função principal é definir caminhos de diretório dinâmicos (para garantir que a aplicação funcione tanto em modo de desenvolvimento quanto como executável PyInstaller) e fornecer listas de dados e valores *placeholder* padrão para a interface gráfica.

#### Seções e Constantes

O código é dividido em três seções principais para organização:

1.  **Lógica de Caminho (PROJECT\_ROOT)**:

      * Determina o caminho base do projeto (`PROJECT_ROOT`).
      * **Modo PyInstaller**: Se a aplicação estiver rodando como um executável congelado, ele usa `sys._MEIPASS` para encontrar a pasta temporária de recursos.
      * **Modo Desenvolvimento**: Caso contrário, ele usa a localização do próprio arquivo `config.py` para definir o caminho raiz.

2.  **Caminhos de Dados**:

      * Define os caminhos absolutos para os arquivos de dados estáticos, utilizando o `PROJECT_ROOT` como base para garantir que os arquivos sejam encontrados independentemente do modo de execução.
      * `PATH_SHP`: Caminho para o Shapefile (`BR_setores_CD2022.shp`) com os dados geoespaciais dos setores censitários.
      * `PATH_UF_JSON`: Caminho para o arquivo JSON que mapeia códigos de UF para nomes de estado.
      * `PATH_IPCA_JSON`: Caminho para o arquivo JSON de *fallback* com dados históricos do IPCA.

3.  **Dados do Formulário**:

      * Fornece as listas de valores fixos necessários para preencher *comboboxes* na GUI.
      * `UFS`: Lista de siglas das Unidades Federativas (Estados) brasileiras.
      * `CLASSES`: Lista de classes de radiodifusão FM (`E1` até `C`).
      * `PLACEHOLDER_LAT` / `PLACEHOLDER_LON`: Strings de exemplo para formatar as entradas de coordenadas (Latitude e Longitude) no formato Graus, Minutos, Segundos (GMS).

#### Função `get_default_download_path()`

Esta função utilitária tenta **encontrar o diretório padrão de "Downloads"** do usuário.

1.  Acessa o diretório *home* do usuário (`Path.home()`).
2.  Tenta construir o caminho para a pasta "Downloads".
3.  Se a pasta "Downloads" não for encontrada ou não for um diretório válido, retorna o diretório *home* como alternativa.
4.  Em caso de falha completa (ex: erro de permissão), retorna o diretório de trabalho atual (`Path.cwd()`).

#### Estrutura do Código

```python
import os
import sys
from pathlib import Path

# --- LÓGICA DE CAMINHO ---
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
```

Este arquivo é fundamental para a **portabilidade** do projeto, centralizando todos os parâmetros que precisam ser ajustados para diferentes ambientes ou para a implantação.

### Documentação do Código: `app_view.py`

O arquivo `app_view.py` define a **Interface Gráfica do Usuário (GUI)** do projeto, utilizando a biblioteca **`ttkbootstrap`** para um visual moderno baseado em Tkinter. Ele atua como o componente **View** no padrão MVC.

#### Classe `AppView(ttk.Window)`

Esta classe herda de `ttk.Window` e representa a janela principal da aplicação. É responsável por construir e gerenciar todos os elementos visuais do formulário.

| Método/Propriedade | Descrição |
| :--- | :--- |
| **`__init__`** | Inicializa a janela (tamanho, título), armazena as listas de dados (`ufs`, `classes`) e *placeholders*. Cria todas as seções do formulário (`lf_processo`, `lf_enderecamento`, etc.) e os botões de ação. |
| **`set_controller(controller)`** | Método essencial do MVC que define o objeto `AppController` dentro da View, permitindo que os botões acionem a lógica de controle. |
| **`create_*_section(parent)`** | Família de métodos para construir as seções do formulário (`lf_processo`, `lf_estacao_atual`, etc.), usando `ttk.Labelframe` para agrupar visualmente os campos. |
| **`_create_form_entry` / `_create_form_combobox`** | Métodos privados utilitários para padronizar a criação de `Entry` e `Combobox` (campo de texto e lista suspensa) na grade (Grid) da GUI. |
| **`toggle_enderecamento()`** | É chamada por um *checkbox*. **Mostra** ou **oculta** dinamicamente a seção de endereçamento (`lf_enderecamento`) usando `pack()` ou `pack_forget()`. |

---

### Coleta e Limpeza de Dados

| Método | Função |
| :--- | :--- |
| **`get_form_data() -> dict`** | **Coleta** o valor atual de **todos** os campos da View (Entradas, Comboboxes e Variáveis) e retorna um dicionário com os dados. Inclui condicionalmente os campos de endereçamento (`cnpj`, `fistel`, etc.) se o *checkbox* correspondente estiver ativo. |
| **`clear_all_fields()`** | **Limpa** o conteúdo de todos os campos de entrada, redefine os Comboboxes e insere novamente os valores *placeholder* nas entradas de coordenadas. |
| **`set_output_path(path)` / `get_output_path()`** | Métodos para gerenciar o caminho de saída (diretório onde os arquivos serão salvos), que é exibido em um campo `readonly`. |

---

### Gerenciamento de Estado e Diálogos

| Método | Função |
| :--- | :--- |
| **`toggle_buttons(enabled)`** | Ativa ou desativa os botões principais (`Gerar PDF`, `Limpar Campos`) para evitar interações enquanto a lógica de cálculo está em execução. |
| **`show_loading()` / `hide_loading()`** | Cria e gerencia uma janela `Toplevel` modal com uma barra de progresso indeterminada, exibida durante o processamento de longa duração na thread de trabalho. |
| **`show_info` / `show_warning` / `show_error`** | Métodos *wrapper* para exibir caixas de mensagens informativas, de aviso ou de erro. |
| **`ask_yes_no` / `ask_directory`** | Métodos para solicitar confirmação do usuário ou abrir a caixa de diálogo nativa para seleção de diretório. |

---

O `app_view.py` é responsável pela apresentação e pela coleta das informações do usuário, delegando a validação e o processamento de dados ao `AppController`.

### Documentação do Código: `app_controller.py`

O arquivo `app_controller.py` implementa o **Controller** do padrão MVC. Ele é o mediador entre a `AppView` (interface) e os módulos de serviço (lógica de negócio), orquestrando o fluxo de trabalho principal: validação, processamento de dados em *thread* separada, cálculo e geração de documentos.

#### Classe `AppController`

| Método/Propriedade | Descrição |
| :--- | :--- |
| **`__init__(self, view: AppView)`** | Inicializa o Controller, recebendo a instância da `AppView`. Configura variáveis de controle de thread (`worker_thread`, `thread_result`, `thread_error`) e carrega os *placeholders* de coordenadas de `config`. |
| **`handle_clear_form()`** | Executa a ação de limpar o formulário. Solicita confirmação do usuário via `view.ask_yes_no()` antes de chamar `view.clear_all_fields()`. |
| **`handle_select_folder()`** | Abre a caixa de diálogo para seleção de diretório (`view.ask_directory()`) e atualiza o campo de saída na View com o novo caminho. |
| **`_validate_form(data) -> list[str]`** | **Valida** se todos os campos obrigatórios (incluindo os campos condicionais de endereçamento, se ativados pelo *checkbox*) foram preenchidos e não contêm valores vazios ou *placeholders*. Retorna uma lista com os nomes dos campos inválidos. |

---

#### Orquestração e Processamento de Thread

O fluxo de cálculo e geração de arquivos é executado em uma **thread separada** (`worker_thread`) para manter a interface gráfica responsiva, uma prática essencial para operações demoradas como geoprocessamento e geração de PDF.

| Método | Função |
| :--- | :--- |
| **`handle_generate_pdf()`** | Executado ao clicar no botão "Gerar PDF". |
| | 1. Coleta os dados do formulário (`view.get_form_data()`). |
| | 2. Verifica a validade dos campos com `_validate_form()`. |
| | 3. Desativa os botões (`view.toggle_buttons(False)`) e exibe o *loading* (`view.show_loading()`). |
| | 4. Inicia a thread (`_pdf_task`) com os dados do formulário. |
| | 5. Chama `view.after(100, self._check_thread)` para iniciar a checagem do estado da thread. |
| **`_pdf_task(data: dict)`** | O núcleo da lógica de negócio, executado em background. |
| | 1. **Prepara Dados**: Normaliza (capitaliza e converte para maiúsculas) os campos de texto importantes. |
| | 2. **Cálculo Base**: Instancia `CalculationService` e chama `get_results()` para obter todos os dados de geoprocessamento e cálculo do $V_{pc}$ (Valor de Promoção de Classe). |
| | 3. **Correção IPCA**: Chama `ipca_calculation()` para aplicar a correção monetária no valor $V_{pc}$ e armazena o resultado (`ipca_value`) e a data da correção. |
| | 4. **Geração de PDF**: Chama `create_relatorio()` para gerar o relatório final. |
| | 5. **Geração de DOCX**: Se o *checkbox* `incluir_enderecamento` estiver ativo, chama `create_word_doc()` para gerar o ofício editável. |
| **`_check_thread()`** | Verifica periodicamente (`self.view.after(100)`) se `worker_thread.is_alive()` é falso (ou seja, se a thread terminou). |
| | Ao terminar, oculta o *loading* e exibe mensagens de sucesso (`thread_result`) ou erro (`thread_error`) para o usuário. |

---

O `AppController` garante que a interface do usuário permaneça responsiva durante os processos de cálculo intensivo, enquanto gerencia o fluxo lógico e o tratamento de erros.

### Documentação do Código: `calculation_service.py`

O arquivo `calculation_service.py` contém a classe `CalculationService`, que é o **coração da lógica de negócio** do projeto. Ela executa o geoprocessamento complexo (envolvendo `geopandas` e `shapely`), determina os valores de referência, calcula o contorno protegido da estação e, finalmente, realiza o cálculo do Valor de Promoção de Classe ($V_{pc}$).

#### Classe `CalculationService`

A classe possui várias constantes estáticas para os parâmetros regulatórios e logísticos.

| Constante Estática | Descrição |
| :--- | :--- |
| **`dmax_values`** | Dicionário que armazena os valores da **Distância Máxima ao Contorno Protegido ($D_{max}$)** em km, variando conforme a classe (`E1` a `C`) e a faixa de canal. |
| **`promotion_period`** | Dicionário que armazena o **Tempo para Atingir a Classe Proposta ($T_{cp}$)** em anos, com base na classe atual e na proposta. |
| **`referencias`** | Dicionário aninhado que armazena os códigos, nomes de município e valores de referência ($V_{AB}$ e $V_{BC}$) de preços mínimos de outorga, organizados por grupo de enquadramento (`B` ou `C`) e Unidade Federativa (UF). |

---

#### `__init__` e Propriedades de Inicialização

O construtor da classe recebe os caminhos para os arquivos geoespaciais e o dicionário de dados do formulário.

| Propriedade de Inicialização | Descrição |
| :--- | :--- |
| **Coordenadas** | Converte as coordenadas de GMS (Graus, Minutos, Segundos) para Decimal (`proposed_latitude_decimal`, `proposed_longitude_decimal`) utilizando `dms_for_decimal`. |
| **`dmax_contour`** | Calcula o valor de $D_{max}$ para a classe proposta. |
| **`gdf_protected_contour`** | Cria o **GeoDataFrame (GDF) do Contorno Protegido** (um círculo) usando a $D_{max}$ e as coordenadas propostas, chamando `create_circle_gdf()`. |
| **`gdf_census_municipalities`** | Carrega o GDF principal com os setores censitários do IBGE (incluindo população e geometria). |
| **Interseção Inicial** | Filtra o GDF de setores censitários para incluir apenas os estados que fazem **interseção** com o Contorno Protegido, otimizando o processamento subsequente. |

---

#### Métodos de Regulamentação e Validação

| Método | Função |
| :--- | :--- |
| **`_get_municipality_code(mun_name, state_name, mun_type)`** | Valida o nome do município e UF contra o GDF carregado e retorna o código municipal (`CD_MUN`) do IBGE. Levanta `ValueError` se o município não for encontrado. |
| **`_get_reference_value(state, classification, city_code)`** | Localiza e retorna a lista de valores de referência (`Código`, `Município`, `Valor`) com base na UF, na classificação do grupo (`B` ou `C`) e no código municipal (para exceções como São Paulo). |
| **`_class_group(classe)`** | Mapeia uma classe de estação (`A1`, `B2`, `E1`, etc.) ao seu respectivo Grupo de Enquadramento (`A`, `B` ou `C`). |
| **`_check_class_change` / `check_group_change`** | Determina se a alteração é uma "promoção de classe" ou "redução de classe/grupo". |
| **`_time_to_target_class(current_class, proposed_class)`** | Retorna o valor de $T_{cp}$ (Tempo para Atingir a Classe Proposta em anos) a partir da constante `promotion_period`. |
| **`dmax_cp(classe, canal)`** | Calcula o $D_{max}$ em km com base na classe e faixa de canal propostos. |
| **`get_municipality_with_code(code)`** | Recebe o código municipal e retorna uma string contendo o nome completo do estado, o nome do município e a **população total** (soma da coluna `v0001` de todos os setores censitários do município). |

---

#### Métodos de Geoprocessamento e Geração

| Método | Função |
| :--- | :--- |
| **`create_circle_gdf(latitude, longitude, radius)`** | Cria o GDF de um círculo de raio `radius` (em km) centrado nas coordenadas da estação. A geometria é projetada para o sistema **UTM (EPSG:5880)** para que o *buffer* de distância seja calculado corretamente em metros, e depois reprojetada de volta para o sistema geográfico (EPSG:4674). |
| **`geo_process()`** | Executa a lógica de interseção espacial: Identifica os setores censitários com `SITUACAO == 'Urbana'` cuja geometria intersecta o `gdf_protected_contour`. O resultado são os `covered_municipalities_codes` (códigos dos municípios cujas áreas urbanas são alcançadas). |
| **`creat_map()`** | Gera um **mapa visual** do geoprocessamento usando `matplotlib`. O mapa mostra: o contorno protegido (`gdf_protected_contour`), as áreas urbanas atingidas (`gdf_urban_sectors_cp_intersection`) e a localização da estação. O mapa é salvo temporariamente como PNG e seu caminho é retornado. |
| **`calculo_promocao_classe(population)`** | Implementa a fórmula da Portaria MCom: $$V_{pc} = (\frac{P_{tot}}{P_{ref}}) \cdot (V_{AB} + V_{BC}) \cdot (1 + \frac{T_{cp}}{10})$$ O método determina os valores de $V_{AB}$ e $V_{BC}$ com base na mudança de grupo (`A`, `B` ou `C`) e calcula o $V_{pc}$ final. |

---

#### Método Final

| Método | Função |
| :--- | :--- |
| **`get_results()`** | Orquestra todo o fluxo: |
| | 1. Valida os códigos municipais. |
| | 2. Chama `data_process()` (define $T_{cp}$ e referências). |
| | 3. Chama `geo_process()` (determina municípios cobertos). |
| | 4. Chama `calculo_promocao_classe()` (calcula $V_{pc}$). |
| | 5. Chama `creat_map()` (gera o mapa). |
| | 6. Retorna o dicionário completo de resultados, incluindo todos os valores de entrada e os valores calculados ($V_{pc}, P_{tot}, T_{cp}, D_{max}$, etc.). |

### Documentação do Código: `create_pdf.py`

O arquivo `create_pdf.py` é responsável pela **geração do Relatório Técnico** do cálculo de promoção de classe, no formato **PDF**, utilizando a biblioteca `reportlab`. Este módulo foca na apresentação visual dos resultados, fórmulas e dados de geoprocessamento.

#### Configuração de Ambiente

Antes da função principal, o script tenta configurar o *locale* para o formato brasileiro (`pt_BR`).

  * **`locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')`**: Tenta definir a formatação regional para números e moeda no padrão brasileiro. Isso garante que valores como `R$ 1.000,00` e números grandes (`1.000.000`) sejam formatados corretamente dentro do PDF.

#### Função Principal: `create_relatorio()`

Esta é a única função pública do módulo e orquestra a criação de todo o documento.

| Parâmetro | Descrição |
| :--- | :--- |
| **`path_uf`** | Caminho para o arquivo JSON de estados/UFs (usado para converter nomes completos de estados em siglas, se necessário). |
| **`file_path`** | Caminho completo onde o arquivo PDF final será salvo. |
| **`data`** | Dicionário contendo todos os resultados do cálculo (`vpc`, `ipca`, `dmax`, `ptot`, `municípios_afetados`, `caminho_mapa_temp`, etc.). |

#### Fluxo de Execução

1.  **Formatação de Variáveis**: O script extrai os dados numéricos do dicionário (`vpc`, `ipca`, `dmax`, `pref`, etc.) e usa `locale.format_string()` para formatá-los no padrão brasileiro (separadores de milhar e decimal).
2.  **Configuração de Documento**: Cria o objeto `SimpleDocTemplate` e inicializa o *story* (lista de elementos do PDF).
3.  **Definição de Estilos**: Cria e configura diversos `ParagraphStyle`s (Títulos, Textos Normais, Subtítulos, etc.), definindo tamanho de fonte, alinhamento e espaçamento.
4.  **Seções do PDF (Página 1)**:
      * **Título**: Insere o título principal do documento.
      * **Tabela de Processo**: Tabela com os dados básicos do processo (Número, Serviço, Entidade).
      * **Tabela de Modificação**: Compara a **Situação Atual** e a **Situação Proposta** da estação (Município, Canal, Classe, Latitude, Longitude).
      * **Seção 2 (Municípios)**: Introdução e texto explicativo sobre o Contorno Protegido e a Portaria GM/MCom nº 1/2023.
5.  **Seções do PDF (Página 2)**:
      * **Mapa (Figura 1)**: Insere a imagem do mapa (PNG) gerada pelo `CalculationService`.
      * **Tabela de Municípios (Tabela 1)**: Lista todos os municípios cujas áreas urbanas foram atingidas pelo Contorno Protegido, juntamente com suas populações.
      * **Seção 3 (Cálculo)**: Tabela com os **dados intermediários** para o cálculo ($T_{cp}$, $D_{max}$, $P_{ref}$, $V_{AB}$, $V_{BC}$).
      * **Fórmulas**: Apresenta a **fórmula de $V_{pc}$** e a substituição dos valores.
      * **IPCA**: Apresenta o parágrafo final sobre a correção monetária pelo IPCA, mencionando a data de correção e o **valor final a ser cobrado**.
6.  **Geração e Limpeza**:
      * Chama `doc.build(story)` para gerar o PDF.
      * No bloco `finally`, tenta **remover o arquivo de mapa temporário** (`map_path`) criado pelo `CalculationService` para evitar o acúmulo de arquivos.

### Documentação do Código: `creat_pdf_oficio.py`

O arquivo `creat_pdf_oficio.py` contém a função responsável por gerar um **ofício de cobrança em formato Microsoft Word (`.docx`)** utilizando a biblioteca `python-docx`. Este documento é destinado à entidade para formalizar a cobrança do valor de promoção de classe, incluindo instruções de pagamento e referências regulatórias.

#### Configuração de Ambiente

  * **`locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')`**: Tenta configurar o *locale* para o formato brasileiro, garantindo que o valor final do IPCA seja formatado corretamente (`R$ X.XXX,XX`).

#### Função Principal: `create_word_doc()`

Esta função recebe o caminho de saída e os dados processados para gerar o ofício.

| Parâmetro | Descrição |
| :--- | :--- |
| **`file_path_docx`** | Caminho completo onde o arquivo `.docx` final será salvo. |
| **`data`** | Dicionário contendo os dados do processo, endereçamento, e o valor final corrigido pelo IPCA. |

#### Fluxo de Execução

1.  **Extração e Formatação de Dados**:
      * O script extrai as variáveis de interesse (`entidade`, `cnpj`, `endereco`, `ipca`, `fistel`, etc.) do dicionário `data`.
      * O valor do IPCA (`ipca`) é formatado no padrão monetário brasileiro e armazenado em `ipca_normalized`.
2.  **Criação e Estilos**:
      * Inicializa o objeto `Document()`.
      * Define a fonte padrão do documento como **Arial, tamanho 10pt**.
3.  **Bloco de Destinatário**:
      * Cria o bloco de destinatário formatado com **negrito** no nome da entidade e no CNPJ.
      * Inclui o endereço completo (`endereco`, `cep`, `municipio/uf`).
4.  **Assunto e Referência**:
      * Insere o assunto ("Alteração de Plano Básico com mudança de grupo...") e o número do processo (Referência) em **negrito**.
5.  **Corpo do Ofício (Parágrafos Numerados)**:
      * **Ponto 1**: Informa que a **GRU (Guia de Recolhimento da União)** está disponível no sistema **SIGEC** da Anatel, referente à **promoção de classe**.
      * **Ponto 2**: Explica que o valor foi calculado pela **Portaria de Consolidação GM/MCom nº 1/2023** e foi **atualizado pelo IPCA** desde agosto de 2013.
6.  **Tabela de Cobrança**:
      * Insere uma tabela formatada (`Table Grid`) com 2 linhas e 5 colunas.
      * **Cabeçalho**: Define as colunas como `UF/MUNICÍPIO`, `CNPJ`, `FISTEL`, `CANAL`, e **`VALOR (R$)`**.
      * **Dados**: Preenche a linha de dados com as informações do processo e o `ipca_normalized`.
7.  **Instruções de Pagamento (Ponto 3)**:
      * Fornece um **passo a passo detalhado** (itens a a g) para que a entidade acesse o *site* da Anatel e consiga imprimir a Guia de Recolhimento (GRU).
8.  **Bloco Final (Ponto 4)**:
      * Menciona o **art. 31, §1º da Portaria GM/MCom nº 1/2023**, que condiciona a alteração no Plano Básico à confirmação do pagamento.
      * Finaliza com o vocativo "Atenciosamente".
9.  **Salvamento**: Chama `doc.save(file_path_docx)` para finalizar e salvar o documento.

### Documentação do Código: `ipca.py`

O arquivo `ipca.py` contém a lógica para buscar os índices do **IPCA (Índice Nacional de Preços ao Consumidor Amplo)** e aplicar a correção monetária em um valor base.

#### Função Principal: `ipca_calculation()`

Esta função recebe um valor monetário original e aplica a correção acumulada do IPCA, a partir de uma data de referência fixa até o índice mais recente disponível.

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| **`valor_original`** | `float` | O valor monetário a ser corrigido. |
| **`static_ipca_path`** | `str` | Caminho para o arquivo JSON estático de *fallback* (usado se a API falhar). |
| **Retorno** | `tuple` | Retorna uma tupla contendo o valor corrigido (`float`) e a data final da correção (`str`). |

#### Fluxo de Execução

1.  **Configuração da Data Inicial**: A correção é sempre calculada a partir de **`01/08/2013`**, conforme a regulamentação do projeto.
2.  **Busca de Dados (API vs. *Fallback*)**:
      * **Prioridade (API)**: Tenta buscar os dados do índice IPCA na API pública do Banco Central do Brasil (BCB).
      * **Mecanismo de Falha (*Fallback*)**: Se a requisição HTTP falhar (ex: erro de rede, *timeout*, ou erro do servidor), o código tenta carregar os dados do arquivo JSON estático fornecido em `static_ipca_path`.
      * **Tratamento de Erros**: Se a API falhar E o arquivo estático não for encontrado ou estiver mal formatado, a função levanta um `ValueError` fatal.
3.  **Processamento com Pandas**: Os dados carregados (seja da API ou do arquivo) são convertidos para um `pandas.DataFrame` para facilitar o cálculo.
      * **Limpeza/Conversão**: As colunas 'data' e 'valor' são convertidas para tipos adequados (`datetime` e `numeric`).
      * **Filtro**: O *DataFrame* é filtrado para garantir que os dados comecem na `data_inicial_str` (`01/08/2013`).
4.  **Cálculo da Correção**:
      * **Fator Mensal**: Cria uma nova coluna `fator_mensal` onde cada índice é transformado de percentual para fator (ex: $2\% \rightarrow 1.02$): $$Fator\ Mensal = 1 + (\frac{Valor\ do\ IPCA}{100})$$
      * **Fator Acumulado**: O `fator_acumulado` é calculado como o **produto** de todos os `fator_mensal` (multiplicação acumulada).
      * **Valor Corrigido**: O `valor_original` é multiplicado pelo `fator_acumulado` para obter o resultado final.
5.  **Retorno**: Retorna o `valor_corrigido` e a `data_final_str` (a data mais recente do índice utilizado).

#### Estrutura do Código (Resumo da Função `ipca_calculation`)

```python
def ipca_calculation(valor_original: float, static_ipca_path: str) -> tuple | None:
    data_inicial_str = '01/08/2013'
    # 1. Tenta buscar dados da API do BCB
    try:
        # ... requisição HTTP ...
        dados = response.json()
    # 2. Em caso de falha da API, tenta carregar do arquivo JSON estático
    except requests.exceptions.RequestException:
        # ... carrega do arquivo estático ...
    
    # 3. Processa dados com Pandas
    df = pd.DataFrame(dados)
    # 4. Filtra a partir de 01/08/2013
    df = df[df['data'] >= data_inicial].copy()
    
    # 5. Calcula o Fator Acumulado (produto da série de fatores mensais)
    df['fator_mensal'] = 1 + (df['valor'] / 100)
    fator_acumulado = df['fator_mensal'].prod()
    
    # 6. Calcula o Valor Corrigido
    valor_corrigido = valor_original * fator_acumulado
    
    return valor_corrigido, data_final_str
```

### Documentação do Código: `utils.py`

O arquivo `utils.py` contém um conjunto de funções utilitárias projetadas para realizar o tratamento e a conversão de dados específicos do formulário, como coordenadas geográficas e formatação de texto.

#### Função: `dms_for_decimal()`

Esta função é crucial para o geoprocessamento, pois converte as coordenadas geográficas do formato **Graus, Minutos, Segundos (GMS)** inseridas pelo usuário para o formato **Decimal**.

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| **`dms`** | `str` | A string de coordenadas no formato GMS (ex: `"10° 10' 10\" S"`). |
| **Retorno** | `float` | O valor da coordenada no formato decimal, pronto para uso em cálculos geoespaciais. |

##### Fluxo de Conversão:

1.  **Pré-processamento**: A string de entrada é padronizada (convertida para maiúsculas, espaços removidos e caracteres como `'` e `"` corrigidos).
2.  **Extração de Direção**: A função identifica a direção (N, S, E, W) usando uma expressão regular (`re.findall`).
3.  **Cálculo Decimal**: Os componentes (grau, minuto, segundo) são separados e o valor decimal é calculado pela fórmula: $\text{Decimal} = \text{Grau} + \frac{\text{Minuto}}{60} + \frac{\text{Segundo}}{3600}$.
4.  **Sinalização**: Se a direção contiver **Sul (`S`)** ou **Oeste (`W`)**, o valor decimal é negado (adiciona um sinal de menos), o que é o padrão para coordenadas no formato decimal.

#### Função: `capitalizar_string()`

Esta função é utilizada para garantir que as entradas de texto do formulário (como nomes de entidades, serviços e finalidades) estejam formatadas de maneira padronizada e legível, seguindo regras de capitalização específicas.

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| **`texto`** | `str` | A string de texto a ser formatada. |
| **Retorno** | `str` | A string formatada. |

##### Regras de Capitalização:

1.  **Palavras Minúsculas**: Palavras comuns como preposições e artigos (`de`, `em`, `do`, `da`, `e`, `o`, `a`, etc.) são mantidas em **minúsculas**.
2.  **Siglas/Acrônimos**: Siglas importantes (`FM`, `AM`, `LTDA`, `TV`) são mantidas em **MAIÚSCULAS**.
3.  **Outras Palavras**: Todas as outras palavras são capitalizadas (apenas a primeira letra em maiúscula).

#### Estrutura do Código

```python
import re

def dms_for_decimal(dms):
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

def capitalizar_string(texto):
    texto = str(texto)
    texto = texto.lower()

    palavras_min = ['de', 'em', 'do', 'da', 'dos', 'das', 'e', 'o', 'a']    
    palavras_max = ['fm', 'am', 'ltda', 'tv']
    
    palavras = texto.split()
    
    resultado = []
    for palavra in palavras:
        if palavra in palavras_min:
            resultado.append(palavra)
        elif palavra in palavras_max:
            resultado.append(palavra.upper())
        else:
            resultado.append(palavra.capitalize())
            
    return ' '.join(resultado)
```

### Documentação do Código: `runtime_hook.py`

O arquivo `runtime_hook.py` é um **script auxiliar** destinado a ser executado durante o processo de *runtime* (tempo de execução) de um executável criado pelo **PyInstaller** (congelamento de pacotes Python). Sua principal função é garantir que as dependências geoespaciais críticas (`pyogrio` e `shapely`) sejam carregadas corretamente, mesmo quando estão empacotadas.

#### Fluxo de Execução

1.  **Verificação do Ambiente**:
      * O script inicia verificando se a aplicação está rodando como um executável congelado através da checagem de `getattr(sys, 'frozen', False)`. Se `frozen` for `True`, significa que está em um ambiente PyInstaller.
2.  **Definição do Caminho Base**:
      * Se for um executável, a variável `base_path` é definida como `sys._MEIPASS`. O `sys._MEIPASS` é o caminho para a pasta temporária onde o PyInstaller extrai todos os recursos e bibliotecas no momento da execução.
3.  **Configuração do PATH (Essencial para Geoespacial)**:
      * As bibliotecas geoespaciais, como `geopandas` (que usa `pyogrio` e `shapely`), dependem de DLLs e bibliotecas de baixo nível (como GDAL e GEOS).
      * O script adiciona os caminhos dessas bibliotecas dentro da pasta temporária do PyInstaller (`pyogrio.libs` e `shapely.libs`) à variável de ambiente **`PATH`** do sistema.
      * **Objetivo**: Ao modificar o `PATH`, o sistema operacional consegue encontrar as bibliotecas nativas necessárias para o funcionamento correto do `geopandas` e seus componentes, resolvendo problemas comuns de dependência em executáveis congelados.

#### Estrutura do Código

```python
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
```

Este gancho de *runtime* é um componente técnico que garante a **portabilidade** do projeto, permitindo que a aplicação funcione em computadores que não possuem as dependências geoespaciais instaladas globalmente.

### Documentação do Código: `main.spec`

O arquivo `main.spec` é o **arquivo de especificação** usado pela ferramenta **PyInstaller** para "congelar" a aplicação Python em um executável autônomo. Ele define todos os arquivos, bibliotecas e configurações necessárias para que o programa funcione sem a necessidade de um ambiente Python instalado no computador do usuário.

#### Configurações Principais

| Variável/Bloco | Descrição |
| :--- | :--- |
| **`SITE_PACKAGES_DIR`** | Define o caminho para o diretório `site-packages` dentro do ambiente virtual do projeto.É usado como base para localizar bibliotecas geoespaciais. |
| **`binaries`** |Adiciona as **DLLs e bibliotecas binárias** necessárias para as dependências geoespaciais, como `pyogrio.libs` e `shapely.libs`.Isso é fundamental para o funcionamento do `geopandas`. |
| **`datas`** |Lista os arquivos e diretórios de dados que devem ser incluídos no executável.Inclui: * O diretório **`data`** do projeto (contendo JSONs e Shapefiles). *O diretório **`pyogrio\gdal_data`** (contendo arquivos de configuração internos do GDAL). |
| **`hiddenimports`** |Lista módulos que o PyInstaller pode falhar em detectar automaticamente, garantindo que sejam explicitamente incluídos (ex: `pyogrio` e seus submódulos). |
| **`runtime_hooks`** |Define scripts Python a serem executados imediatamente antes do `main.py` ser iniciado no executável.O script **`runtime_hook.py`** é usado para configurar a variável de ambiente `PATH` para que as DLLs geoespaciais sejam encontradas. |
| **`Analysis`** |Bloco principal que analisa o script de entrada (`main.py`) e coleta as dependências. |
| **`EXE`** |Bloco que cria o arquivo executável final.Define o nome de saída como `promocao_classe` e usa `console=False` para criar uma aplicação **sem janela de console** (GUI). |
| **`COLLECT`** |Bloco que agrupa (`collect`) o executável, binários e dados em um único diretório de distribuição. |

#### Objetivo


O arquivo `main.spec` tem o objetivo de **empacotar** a aplicação (`main.py`) juntamente com todas as bibliotecas necessárias, prestando atenção especial às dependências complexas de geoprocessamento (`pyogrio` e `shapely`), que exigem inclusão manual de DLLs (`binaries`) e configurações (`datas`, `runtime_hooks`) para garantir que o executável funcione em qualquer ambiente Windows.
