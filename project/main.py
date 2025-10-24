import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from tkinter import messagebox
from pathlib import Path
import time
import os
import sys
import threading

# Bliblotecas internas
from services import CalculationService, capitalizar_string, create_pdf, ipca_calculation

try:
    # Modo PyInstaller
    PROJECT_ROOT = Path(sys._MEIPASS)
except Exception:
    # Modo Desenvolvimento
    PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))


class FormularioApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera", title="Promoção de Classe")
        self.geometry("650x720")
        self.minsize(650, 620)

        try:
            home_dir = Path.home()
            downloads_folder = home_dir / "Downloads"
            
            if not downloads_folder.is_dir():
                downloads_folder = home_dir
        except Exception:
            downloads_folder = Path.cwd()

        
        # Define o caminho padrão como uma string
        self.default_output_path = str(downloads_folder)
        
        # Listas de opções para os Comboboxes
        self.ufs = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        self.classes = ["E1", "E2", "E3", "A1", "A2", "A3", "A4", "B1", "B2", "C"]

        # --- ADICIONE ESTAS DUAS LINHAS ---
        self.placeholder_lat = "10° 10' 10\" S"
        self.placeholder_lon = "10° 10' 10\" W"
        # ---------------------------------

        # --- CABEÇALHO ---
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=(10, 1))
        ttk.Label(
            header_frame, 
            text="Cálculo de Promoção de Classe de Estações",
            font=("Helvetica", 14, "bold")
        ).pack()

        # --- CONTAINER PRINCIPAL DO FORMULÁRIO ---
        form_container = ttk.Frame(self)
        form_container.pack(padx=10, pady=1, fill=BOTH, expand=True)

        # 2. Criação das seções (Fieldsets)
        self.create_processo_section(form_container)
        self.create_estacao_atual_section(form_container)
        self.create_situacao_proposta_section(form_container)
        self.create_output_section(form_container)

        # 3. Botões de Ação (Substitua sua seção "3. Botão de Envio" por esta)
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=1)
        
        # Botão Gerar PDF
        self.submit_button = ttk.Button(
            button_frame, 
            text="Gerar PDF", 
            command=self.iniciar_geracao_pdf,
            bootstyle="primary"
        )
        self.submit_button.pack(side=LEFT, padx=10)

        self.clear_button = ttk.Button(
            button_frame,
            text="Limpar Campos",
            command=self.limpar_formulario,
            bootstyle="secondary"
        )
        self.clear_button.pack(side=LEFT, padx=10, pady=5)

    def create_processo_section(self, parent):
        """Cria a seção 'Dados do Processo'."""
        lf = ttk.Labelframe(parent, text=" Dados do Processo ", padding=5)
        lf.pack(fill=X, pady=10)

        # Configura o grid para expandir as colunas de entrada
        lf.columnconfigure((1, 3), weight=1)

        self.numero_processo = self._create_form_entry(lf, "Número do processo:", 0)
        self.servico = self._create_form_entry(lf, "Serviço:", 0, col_offset=2)
        
        self.entidade = self._create_form_entry(lf, "Entidade:", 1)
        self.finalidade = self._create_form_entry(lf, "Finalidade:", 1, col_offset=2)

        self.consulta_publica = self._create_form_entry(lf, "Consulta Pública:", 2)

    def create_estacao_atual_section(self, parent):
        lf = ttk.Labelframe(parent, text=" Dados da Estação Atual ", padding=5)
        lf.pack(fill=X, pady=10)
        lf.columnconfigure((1, 3), weight=1)

        self.uf_atual = self._create_form_combobox(lf, "UF:", 0, self.ufs)
        self.municipio_atual = self._create_form_entry(lf, "Município:", 0, col_offset=2)
        
        self.classe_atual = self._create_form_combobox(lf, "Classe:", 1, self.classes)
        self.canal_atual = self._create_form_entry(lf, "Canal:", 1, col_offset=2)
        
        self.latitude_atual = self._create_form_entry(lf, "Latitude (GMS):", 2, placeholder=self.placeholder_lat)
        self.longitude_atual = self._create_form_entry(lf, "Longitude (GMS):", 2, col_offset=2, placeholder=self.placeholder_lon)

    def create_situacao_proposta_section(self, parent):
        lf = ttk.Labelframe(parent, text=" Dados da Estação Proposta ", padding=5)
        lf.pack(fill=X, pady=10)
        lf.columnconfigure((1, 3), weight=1)

        self.uf_proposta = self._create_form_combobox(lf, "UF:", 0, self.ufs)
        self.municipio_proposto = self._create_form_entry(lf, "Município:", 0, col_offset=2)
        
        self.classe_proposta = self._create_form_combobox(lf, "Classe:", 1, self.classes)
        self.canal_proposto = self._create_form_entry(lf, "Canal:", 1, col_offset=2)

        self.latitude_proposta = self._create_form_entry(lf, "Latitude (GMS):", 2, placeholder=self.placeholder_lat)
        self.longitude_proposta = self._create_form_entry(lf, "Longitude (GMS):", 2, col_offset=2, placeholder=self.placeholder_lon)

    # --- 2. ADICIONE ESTA NOVA FUNÇÃO ---
    def create_output_section(self, parent):
        """Cria a seção 'Salvar PDF'."""
        lf = ttk.Labelframe(parent, text=" Opções de Saída ", padding=5)
        lf.pack(fill=X, pady=1)

        # Configura o grid
        lf.columnconfigure((1, 3), weight=1) # Coluna do campo de texto expande

        ttk.Label(lf, text="Salvar PDF em:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        
        # Variável para armazenar o caminho (facilita ler e definir)
        self.output_dir_var = ttk.StringVar(value=self.default_output_path)
        
        # Campo de texto (Entry) - readonly para forçar o uso do botão
        self.output_dir_entry = ttk.Entry(
            lf, 
            textvariable=self.output_dir_var, 
            state="readonly"
        )
        self.output_dir_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        
        # Botão "Selecionar..."
        browse_button = ttk.Button(
            lf,
            text="Selecionar Pasta...",
            command=self.selecionar_pasta_saida, # Chama a nova função
            bootstyle="info-outline"
        )
        browse_button.grid(row=0, column=2, sticky=E, padx=5, pady=5)
    
    # --- 3. ADICIONE ESTA NOVA FUNÇÃO ---
    def selecionar_pasta_saida(self):
        """Abre uma caixa de diálogo para o usuário selecionar uma pasta."""
        # Pega o diretório atual como ponto de partida
        initial_dir = self.output_dir_var.get()
        
        # Abre o diálogo pedindo um diretório
        directory = filedialog.askdirectory(
            title="Selecione a pasta para salvar o PDF",
            initialdir=initial_dir
        )
        
        # Se o usuário selecionou uma pasta (e não clicou em "Cancelar")
        if directory:
            self.output_dir_var.set(directory) # Atualiza a variável (e o campo de texto)
            print(f"Pasta de saída definida como: {directory}")
    

    # Funções auxiliares para criar widgets e evitar repetição de código
    def _create_form_entry(self, parent, label_text, row, col_offset=0, placeholder=""):
        ttk.Label(parent, text=label_text).grid(row=row, column=col_offset, sticky=W, padx=5, pady=5)
        entry = ttk.Entry(parent)
        entry.insert(0, placeholder)
        entry.grid(row=row, column=col_offset + 1, sticky=EW, padx=5, pady=5)
        return entry

    def _create_form_combobox(self, parent, label_text, row, values, default_text=None):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky=W, padx=5, pady=5)
        combo = ttk.Combobox(parent, values=values)
        if default_text:
            combo.set(default_text)
        combo.grid(row=row, column=1, sticky=EW, padx=5, pady=5)
        return combo
    
    def limpar_formulario(self):
        """Limpa todos os campos de entrada e comboboxes do formulário."""
        
        # Pede confirmação ao usuário antes de apagar
        if not messagebox.askyesno("Confirmar", "Você tem certeza que deseja limpar todos os campos?"):
            return # Se o usuário clicar em "Não", a função para aqui

        # --- Limpa Campos de Processo (Entry) ---
        self.numero_processo.delete(0, END)
        self.servico.delete(0, END)
        self.entidade.delete(0, END)
        self.finalidade.delete(0, END)
        self.consulta_publica.delete(0, END)
        
        # --- Limpa Campos da Estação Atual ---
        self.uf_atual.set("") # Comboboxes usam .set("")
        self.municipio_atual.delete(0, END)
        self.classe_atual.set("")
        self.canal_atual.delete(0, END)
        
        # Limpa e re-insere os placeholders de Lat/Long
        self.latitude_atual.delete(0, END)
        self.latitude_atual.insert(0, self.placeholder_lat)
        self.longitude_atual.delete(0, END)
        self.longitude_atual.insert(0, self.placeholder_lon)
        
        # --- Limpa Campos da Situação Proposta ---
        self.uf_proposta.set("")
        self.municipio_proposto.delete(0, END)
        self.classe_proposta.set("")
        self.canal_proposto.delete(0, END)
        
        # Limpa e re-insere os placeholders de Lat/Long
        self.latitude_proposta.delete(0, END)
        self.latitude_proposta.insert(0, self.placeholder_lat)
        self.longitude_proposta.delete(0, END)
        self.longitude_proposta.insert(0, self.placeholder_lon)

        self.output_dir_var.set(self.default_output_path)


    def _validar_formulario(self):
        """
        Verifica se todos os campos obrigatórios foram preenchidos.
        Retorna True se válido, False se inválido.
        """
        
        # Lista de tuplas: (widget, "Nome do Campo", [lista_de_valores_invalidos])
        campos_a_validar = [
            (self.numero_processo, "Número do processo", [""]),
            (self.servico, "Serviço", [""]),
            (self.entidade, "Entidade", [""]),
            (self.finalidade, "Finalidade", [""]),
            (self.consulta_publica, "Consulta Pública", [""]),
            
            (self.uf_atual, "UF Atual", [""]),
            (self.municipio_atual, "Município Atual", [""]),
            (self.classe_atual, "Classe Atual", [""]),
            (self.canal_atual, "Canal Atual", [""]),
            (self.latitude_atual, "Latitude Atual", ["", self.placeholder_lat]),
            (self.longitude_atual, "Longitude Atual", ["", self.placeholder_lon]),
            
            (self.uf_proposta, "UF Proposta", [""]),
            (self.municipio_proposto, "Município Proposto", [""]),
            (self.classe_proposta, "Classe Proposta", [""]),
            (self.canal_proposto, "Canal Proposto", [""]),
            (self.latitude_proposta, "Latitude Proposta", ["", self.placeholder_lat]),
            (self.longitude_proposta, "Longitude Proposta", ["", self.placeholder_lon]),
        ]
        
        campos_invalidos = []
        for widget, nome_campo, valores_invalidos in campos_a_validar:
            # Pega o valor e remove espaços em branco extras
            valor = widget.get().strip() 
            
            # Verifica se o valor está na lista de inválidos (ex: "" ou o placeholder)
            if valor in valores_invalidos:
                campos_invalidos.append(nome_campo)
        
        # Se a lista de inválidos não estiver vazia, mostra o erro
        if campos_invalidos:
            mensagem = "Os seguintes campos são obrigatórios e não foram preenchidos (ou ainda contêm o valor padrão):\n\n"
            # Cria uma lista com marcadores
            mensagem += "\n".join(f"- {nome}" for nome in campos_invalidos)
            
            messagebox.showwarning("Campos Incompletos", mensagem)
            return False # Falha na validação
            
        return True # Sucesso na validação


    def iniciar_geracao_pdf(self):
        """Função chamada pelo botão (roda na thread principal)."""
        
        # --- ETAPA DE VALIDAÇÃO ---
        if not self._validar_formulario():
            return  # Para a execução se o formulário for inválido
        # --- FIM DA VALIDAÇÃO ---
        
        # 1. Desabilitar botões para evitar cliques duplos
        self.submit_button.config(state="disabled")
        self.clear_button.config(state="disabled")

        # 2. Criar e exibir a janela de loading
        self.loading_window = ttk.Toplevel(master=self, title="Gerando PDF...")
        self.loading_window.geometry("300x100")
        self.loading_window.transient(self) # Mantém no topo
        self.loading_window.grab_set() # Bloqueia interação com a janela principal
        self.loading_window.resizable(False, False)
        
        # Centralizar a janela de loading
        x = self.winfo_x() + (self.winfo_width() / 2) - (300 / 2)
        y = self.winfo_y() + (self.winfo_height() / 2) - (100 / 2)
        self.loading_window.geometry(f"+{int(x)}+{int(y)}")

        ttk.Label(self.loading_window, text="Processando, por favor aguarde...", font=("Helvetica", 10)).pack(pady=10)
        progress = ttk.Progressbar(self.loading_window, mode="indeterminate", bootstyle="info-striped")
        progress.pack(pady=10, padx=20, fill=X, expand=True)
        progress.start(10) # Inicia a animação da barra

        # 3. Iniciar a thread de trabalho
        self.worker_thread = threading.Thread(target=self.tarefa_gerar_pdf)
        self.worker_thread.start()

        # 4. Iniciar o monitoramento da thread
        self.verificar_thread()

    def tarefa_gerar_pdf(self):
        """Coleta dados e executa o trabalho pesado em uma thread separada."""
        self.thread_result = None
        self.thread_error = None
        
        try:
            # --- Início da lógica original de 'gerar_pdf' ---
            PATH_SHP = PROJECT_ROOT / "data" / "mapa" / "BR_setores_CD2022.shp"
            PATH_UF_JSON = PROJECT_ROOT / "data" / "uf_code.json"
            start_time = time.time()
            print('Dados enviados para o servidor')

            # Coleta de todos os dados dos campos de entrada
            dados = {
                "numero_processo": self.numero_processo.get(),
                "servico": capitalizar_string(self.servico.get()),
                "entidade": capitalizar_string(self.entidade.get()),
                "finalidade": capitalizar_string(self.finalidade.get()),
                "consulta_publica": self.consulta_publica.get(),
                "uf_atual": str(self.uf_atual.get()).upper(),
                "municipio_atual": capitalizar_string(self.municipio_atual.get()),
                "classe_atual": str(self.classe_atual.get()).upper(),
                "canal_atual": self.canal_atual.get(),
                "latitude_atual": self.latitude_atual.get(),
                "longitude_atual": self.longitude_atual.get(),
                "uf_proposta": str(self.uf_proposta.get()).upper(),
                "municipio_proposto": capitalizar_string(self.municipio_proposto.get()),
                "classe_proposta": str(self.classe_proposta.get()).upper(),
                "canal_proposto": self.canal_proposto.get(),
                "latitude_proposta": self.latitude_proposta.get(),
                "longitude_proposta": self.longitude_proposta.get()
            }
            
            # Validação do diretório (movida para cá)
            output_directory = self.output_dir_var.get()
            if not output_directory:
                # Lança um erro que será pego pelo 'except'
                raise ValueError("Nenhuma pasta de saída foi selecionada.")

            # Processamento pesado
            calculo = CalculationService(PATH_SHP, PATH_UF_JSON, dados)
            resultado_calculo_promocao = calculo.get_results()
            print('Calculo de promoção de classe realizado')

            ipca_value, ipca_date = ipca_calculation(resultado_calculo_promocao['vpc'])
            resultado_calculo_promocao['ipca'] = ipca_value
            resultado_calculo_promocao['data_ipca'] = ipca_date

            numero_processo_tratado = self.numero_processo.get().replace('/', '-').replace('.', '_')
            
            caminho_arquivo_pdf = os.path.join(output_directory, f"relatorio_{numero_processo_tratado}.pdf")
            
            # (Assumindo que sua create_pdf foi corrigida para não precisar mais do PATH_UF_JSON)
            # Se ainda precisar, carregue o JSON aqui ou passe o PATH_UF_JSON para create_pdf
            # Vamos assumir que a create_pdf precisa do PATH_UF_JSON
            create_pdf(PATH_UF_JSON, caminho_arquivo_pdf, resultado_calculo_promocao)
            print('PDF criado')

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Tempo de execução: {execution_time:.2f} segundos")
            print("--- DADOS COLETADOS ---")
            for chave, valor in dados.items():
                print(f"{chave}: {valor}")
            print("------------------------")

            # Salva a mensagem de sucesso
            self.thread_result = "Relatório gerado com sucesso!"
            # --- Fim da lógica original ---

        except Exception as e:
            # Salva a mensagem de erro
            print(f"Erro na thread: {e}")
            self.thread_error = e

    def verificar_thread(self):
        """Verifica se a thread de trabalho terminou (roda na thread principal)."""
        if self.worker_thread.is_alive():
            # A thread ainda está rodando, checa de novo em 100ms
            self.after(100, self.verificar_thread)
        else:
            # A thread terminou, hora de atualizar a UI
            
            # 1. Fechar a janela de loading
            if self.loading_window:
                self.loading_window.destroy()
                self.loading_window = None

            # 2. Reabilitar os botões
            self.submit_button.config(state="normal")
            self.clear_button.config(state="normal")

            # 3. Mostrar o resultado (sucesso ou erro)
            if self.thread_error:
                # Mostra o erro que capturamos
                messagebox.showerror(
                    "Erro ao Gerar PDF",
                    f"Ocorreu uma falha:\n\n{self.thread_error}"
                )
            elif self.thread_result:
                # Mostra a mensagem de sucesso
                messagebox.showinfo(
                    title="Sucesso!", 
                    message=self.thread_result
                )

if __name__ == "__main__":
    app = FormularioApp()
    app.mainloop()