# Documentação: Cálculo de Promoção de Classe



## Guia de Uso

Para executar este projeto, é **necessário** instalar as dependências listadas no arquivo `requirements.txt` e executar o arquivo `main.py` dentro da pasta `project`. Siga o passo a passo abaixo:

1.  **Acessar a pasta `project`**
    ```bash
    cd project
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

