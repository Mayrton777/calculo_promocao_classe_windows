import threading
import os

from .app_view import AppView 
import config
from services import CalculationService, capitalizar_string, create_pdf, ipca_calculation

class AppController:
    def __init__(self, view: AppView):
        self.view = view
        self.worker_thread = None
        self.thread_result = None
        self.thread_error = None
        
        self.placeholder_lat = config.PLACEHOLDER_LAT
        self.placeholder_lon = config.PLACEHOLDER_LON


    def handle_clear_form(self):
        """Lida com o clique no botão 'Limpar'."""
        if self.view.ask_yes_no("Confirmar", "Você tem certeza que deseja limpar todos os campos?"):
            self.view.clear_all_fields()
            

    def handle_select_folder(self):
        """Lida com o clique no botão 'Selecionar Pasta'."""
        current_path = self.view.get_output_path()
        new_path = self.view.ask_directory(initialdir=current_path)
        if new_path:
            self.view.set_output_path(new_path)


    def _validate_form(self, data: dict) -> list[str]:
        """Valida os dados do formulário. Retorna uma lista de erros."""
        
        # Mapeia chaves do dicionário para "Nomes Amigáveis" e valores inválidos
        campos_a_validar = [
            ("numero_processo", "Número do processo", [""]),
            ("servico", "Serviço", [""]),
            ("entidade", "Entidade", [""]),
            ("finalidade", "Finalidade", [""]),
            ("consulta_publica", "Consulta Pública", [""]),
            ("uf_atual", "UF Atual", [""]),
            ("municipio_atual", "Município Atual", [""]),
            ("classe_atual", "Classe Atual", [""]),
            ("canal_atual", "Canal Atual", [""]),
            ("latitude_atual", "Latitude Atual", ["", self.placeholder_lat]),
            ("longitude_atual", "Longitude Atual", ["", self.placeholder_lon]),
            ("uf_proposta", "UF Proposta", [""]),
            ("municipio_proposto", "Município Proposto", [""]),
            ("classe_proposta", "Classe Proposta", [""]),
            ("canal_proposto", "Canal Proposto", [""]),
            ("latitude_proposta", "Latitude Proposta", ["", self.placeholder_lat]),
            ("longitude_proposta", "Longitude Proposta", ["", self.placeholder_lon]),
        ]
        
        campos_invalidos = []
        for key, nome_campo, valores_invalidos in campos_a_validar:
            valor = data.get(key, "").strip()     
            if valor in valores_invalidos:
                campos_invalidos.append(nome_campo)
        
        if not data.get("output_directory"):
            campos_invalidos.append("Pasta de Saída")
            
        return campos_invalidos


    def handle_generate_pdf(self):
        """Lida com o clique no botão 'Gerar PDF'. Valida e inicia a thread."""
        
        form_data = self.view.get_form_data()
        
        campos_invalidos = self._validate_form(form_data)
        if campos_invalidos:
            mensagem = "Os seguintes campos são obrigatórios e não foram preenchidos (ou ainda contêm o valor padrão):\n\n"
            mensagem += "\n".join(f"- {nome}" for nome in campos_invalidos)
            self.view.show_warning("Campos Incompletos", mensagem)
            return
        
        self.view.toggle_buttons(enabled=False)
        self.view.show_loading()

        self.worker_thread = threading.Thread(target=self._pdf_task, args=(form_data,))
        self.worker_thread.start()

        self.view.after(100, self._check_thread)


    def _pdf_task(self, data: dict):
        """O trabalho pesado (executado na thread)."""
        self.thread_result = None
        self.thread_error = None
        
        try:
            # Prepara os dados
            dados_processados = {
                "numero_processo": data["numero_processo"],
                "servico": capitalizar_string(data["servico"]),
                "entidade": capitalizar_string(data["entidade"]),
                "finalidade": capitalizar_string(data["finalidade"]),
                "consulta_publica": data["consulta_publica"],
                "uf_atual": str(data["uf_atual"]).upper(),
                "municipio_atual": capitalizar_string(data["municipio_atual"]),
                "classe_atual": str(data["classe_atual"]).upper(),
                "canal_atual": data["canal_atual"],
                "latitude_atual": data["latitude_atual"],
                "longitude_atual": data["longitude_atual"],
                "uf_proposta": str(data["uf_proposta"]).upper(),
                "municipio_proposto": capitalizar_string(data["municipio_proposto"]),
                "classe_proposta": str(data["classe_proposta"]).upper(),
                "canal_proposto": data["canal_proposto"],
                "latitude_proposta": data["latitude_proposta"],
                "longitude_proposta": data["longitude_proposta"]
            }
            
            output_directory = data["output_directory"]
            
            calculo = CalculationService(config.PATH_SHP, config.PATH_UF_JSON, dados_processados)
            resultado_calculo_promocao = calculo.get_results()
            ipca_value, ipca_date = ipca_calculation(resultado_calculo_promocao['vpc'])
            resultado_calculo_promocao['ipca'] = ipca_value
            resultado_calculo_promocao['data_ipca'] = ipca_date

            numero_processo_tratado = data["numero_processo"].replace('/', '-').replace('.', '_')
            caminho_arquivo_pdf = os.path.join(output_directory, f"relatorio_{numero_processo_tratado}.pdf")
            create_pdf(config.PATH_UF_JSON, caminho_arquivo_pdf, resultado_calculo_promocao)

            self.thread_result = "Relatório gerado com sucesso!"

        except Exception as e:
            print(f"Erro na thread: {e}")
            self.thread_error = e


    def _check_thread(self):
        """Verifica se a thread de trabalho terminou."""
        if self.worker_thread.is_alive():
            self.view.after(100, self._check_thread)
        else:
            self.view.hide_loading()
            self.view.toggle_buttons(enabled=True)

            if self.thread_error:
                self.view.show_error(
                    "Erro ao Gerar PDF",
                    f"Ocorreu uma falha:\n\n{self.thread_error}"
                )
            elif self.thread_result:
                self.view.show_info(
                    title="Sucesso!", 
                    message=self.thread_result
                )