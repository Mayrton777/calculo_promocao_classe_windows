import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog

class AppView(ttk.Window):
    def __init__(self, ufs, classes, default_path, placeholder_lat, placeholder_lon, **kwargs):
        super().__init__(**kwargs)
        
        self.geometry("650x720")
        self.minsize(650, 620)
        
        self.controller = None
        self.loading_window = None

        self.ufs = ufs
        self.classes = classes
        self.default_output_path = default_path
        self.placeholder_lat = placeholder_lat
        self.placeholder_lon = placeholder_lon

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

        self.create_processo_section(form_container)
        self.create_estacao_atual_section(form_container)
        self.create_situacao_proposta_section(form_container)
        self.create_output_section(form_container)

        # --- BOTÕES DE AÇÃO ---
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=1)
        
        self.submit_button = ttk.Button(
            button_frame, 
            text="Gerar PDF", 
            
            command=lambda: self.controller.handle_generate_pdf(),
            bootstyle="primary"
        )
        self.submit_button.pack(side=LEFT, padx=10)

        self.clear_button = ttk.Button(
            button_frame,
            text="Limpar Campos",
            
            command=lambda: self.controller.handle_clear_form(),
            bootstyle="secondary"
        )
        self.clear_button.pack(side=LEFT, padx=10, pady=5)


    def set_controller(self, controller):
        """Define o controlador para esta view."""
        self.controller = controller


    def create_processo_section(self, parent):
        """Cria a seção 'Dados do Processo'."""
        lf = ttk.Labelframe(parent, text=" Dados do Processo ", padding=5)
        lf.pack(fill=X, pady=10)
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


    def create_output_section(self, parent):
        lf = ttk.Labelframe(parent, text=" Opções de Saída ", padding=5)
        lf.pack(fill=X, pady=1)
        lf.columnconfigure((1, 3), weight=1)

        ttk.Label(lf, text="Salvar PDF em:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.output_dir_var = ttk.StringVar(value=self.default_output_path)
        
        self.output_dir_entry = ttk.Entry(
            lf, textvariable=self.output_dir_var, state="readonly"
        )
        self.output_dir_entry.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        
        self.browse_button = ttk.Button(
            lf,
            text="Selecionar Pasta...",
            command=lambda: self.controller.handle_select_folder(),
            bootstyle="info-outline"
        )
        self.browse_button.grid(row=0, column=2, sticky=E, padx=5, pady=5)


    def get_form_data(self) -> dict:
        """Coleta todos os dados do formulário e retorna um dicionário."""
        return {
            "numero_processo": self.numero_processo.get(),
            "servico": self.servico.get(),
            "entidade": self.entidade.get(),
            "finalidade": self.finalidade.get(),
            "consulta_publica": self.consulta_publica.get(),
            "uf_atual": self.uf_atual.get(),
            "municipio_atual": self.municipio_atual.get(),
            "classe_atual": self.classe_atual.get(),
            "canal_atual": self.canal_atual.get(),
            "latitude_atual": self.latitude_atual.get(),
            "longitude_atual": self.longitude_atual.get(),
            "uf_proposta": self.uf_proposta.get(),
            "municipio_proposto": self.municipio_proposto.get(),
            "classe_proposta": self.classe_proposta.get(),
            "canal_proposto": self.canal_proposto.get(),
            "latitude_proposta": self.latitude_proposta.get(),
            "longitude_proposta": self.longitude_proposta.get(),
            "output_directory": self.output_dir_var.get()
        }


    def clear_all_fields(self):
        """Limpa todos os campos (sem pedir confirmação)."""
        self.numero_processo.delete(0, END)
        self.servico.delete(0, END)
        self.entidade.delete(0, END)
        self.finalidade.delete(0, END)
        self.consulta_publica.delete(0, END)
        
        self.uf_atual.set("")
        self.municipio_atual.delete(0, END)
        self.classe_atual.set("")
        self.canal_atual.delete(0, END)
        
        self.latitude_atual.delete(0, END)
        self.latitude_atual.insert(0, self.placeholder_lat)
        self.longitude_atual.delete(0, END)
        self.longitude_atual.insert(0, self.placeholder_lon)
        
        self.uf_proposta.set("")
        self.municipio_proposto.delete(0, END)
        self.classe_proposta.set("")
        self.canal_proposto.delete(0, END)
        
        self.latitude_proposta.delete(0, END)
        self.latitude_proposta.insert(0, self.placeholder_lat)
        self.longitude_proposta.delete(0, END)
        self.longitude_proposta.insert(0, self.placeholder_lon)

        self.output_dir_var.set(self.default_output_path)


    def set_output_path(self, path: str):
        """Define o caminho no campo de texto de saída."""
        if path:
            self.output_dir_var.set(path)


    def get_output_path(self) -> str:
        """Retorna o caminho de saída atual."""
        return self.output_dir_var.get()


    def toggle_buttons(self, enabled: bool):
        """Ativa ou desativa os botões principais."""
        state = "normal" if enabled else "disabled"
        self.submit_button.config(state=state)
        self.clear_button.config(state=state)


    def show_loading(self):
        """Mostra a janela de progresso."""
        self.loading_window = ttk.Toplevel(master=self, title="Gerando PDF...")
        self.loading_window.geometry("300x100")
        self.loading_window.transient(self)
        self.loading_window.grab_set()
        self.loading_window.resizable(False, False)
        
        x = self.winfo_x() + (self.winfo_width() / 2) - (300 / 2)
        y = self.winfo_y() + (self.winfo_height() / 2) - (100 / 2)
        self.loading_window.geometry(f"+{int(x)}+{int(y)}")

        ttk.Label(self.loading_window, text="Processando, por favor aguarde...", font=("Helvetica", 10)).pack(pady=10)
        progress = ttk.Progressbar(self.loading_window, mode="indeterminate", bootstyle="info-striped")
        progress.pack(pady=10, padx=20, fill=X, expand=True)
        progress.start(10)


    def hide_loading(self):
        """Fecha a janela de progresso."""
        if self.loading_window:
            self.loading_window.destroy()
            self.loading_window = None


    def show_info(self, title, message):
        messagebox.showinfo(title, message, parent=self)


    def show_warning(self, title, message):
        messagebox.showwarning(title, message, parent=self)


    def show_error(self, title, message):
        messagebox.showerror(title, message, parent=self)


    def ask_yes_no(self, title, message) -> bool:
        return messagebox.askyesno(title, message, parent=self)


    def ask_directory(self, initialdir) -> str | None:
        return filedialog.askdirectory(
            title="Selecione a pasta para salvar o PDF",
            initialdir=initialdir
        )