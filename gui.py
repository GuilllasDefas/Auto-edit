import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import timedelta
from main import extract_and_detect
import logging
import threading
from config import DETECTION_PARAMS, save_config

class MusicExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Extractor")
        self.root.geometry("800x600")
        
        self.video_path = ""
        self.segments = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seleção de arquivo
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Arquivo de Vídeo:").pack(side=tk.LEFT)
        self.file_entry = ttk.Entry(file_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(file_frame, text="Procurar", command=self.browse_file).pack(side=tk.LEFT)
        
        # Adicionar controles de configuração após a seleção de arquivo
        config_frame = ttk.LabelFrame(main_frame, text="Configurações")
        config_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Criar um notebook (abas) para configurações avançadas
        config_notebook = ttk.Notebook(config_frame)
        config_notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Aba de configurações básicas
        basic_tab = ttk.Frame(config_notebook)
        config_notebook.add(basic_tab, text="Básico")
        
        # Duração mínima do segmento
        min_duration_frame = ttk.Frame(basic_tab)
        min_duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(min_duration_frame, text="Duração mínima:").pack(side=tk.LEFT, padx=5)
        self.min_duration_var = tk.IntVar(value=DETECTION_PARAMS["min_segment_duration"] // 1000)
        min_duration_scale = ttk.Scale(
            min_duration_frame, 
            from_=10, 
            to=300, 
            variable=self.min_duration_var, 
            orient=tk.HORIZONTAL
        )
        min_duration_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Valor atual da duração mínima
        self.min_duration_label = ttk.Label(min_duration_frame, width=5)
        self.min_duration_label.pack(side=tk.LEFT, padx=5)
        
        # Atualizar o label quando o valor mudar
        def update_duration_label(*args):
            self.min_duration_label.config(text=f"{self.min_duration_var.get()}s")
        
        self.min_duration_var.trace_add("write", update_duration_label)
        update_duration_label()  # Inicializar o label
        
        # Aba de configurações avançadas
        advanced_tab = ttk.Frame(config_notebook)
        config_notebook.add(advanced_tab, text="Avançado")
        
        # Parâmetros de detecção avançados
        params_frame = ttk.LabelFrame(advanced_tab, text="Parâmetros de Detecção")
        params_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Threshold de silêncio
        threshold_frame = ttk.Frame(params_frame)
        threshold_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(threshold_frame, text="Limiar de silêncio (dB):").pack(side=tk.LEFT, padx=5)
        self.threshold_var = tk.IntVar(value=DETECTION_PARAMS["threshold"])
        threshold_scale = ttk.Scale(
            threshold_frame, 
            from_=-70, 
            to=-20, 
            variable=self.threshold_var, 
            orient=tk.HORIZONTAL
        )
        threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.threshold_label = ttk.Label(threshold_frame, width=5)
        self.threshold_label.pack(side=tk.LEFT, padx=5)
        
        def update_threshold_label(*args):
            self.threshold_label.config(text=f"{self.threshold_var.get()} dB")
        
        self.threshold_var.trace_add("write", update_threshold_label)
        update_threshold_label()
        
        # Duração mínima de silêncio
        silence_frame = ttk.Frame(params_frame)
        silence_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(silence_frame, text="Duração mín. silêncio (ms):").pack(side=tk.LEFT, padx=5)
        self.silence_len_var = tk.IntVar(value=DETECTION_PARAMS["min_silence_len"])
        silence_scale = ttk.Scale(
            silence_frame, 
            from_=500, 
            to=10000, 
            variable=self.silence_len_var, 
            orient=tk.HORIZONTAL
        )
        silence_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.silence_label = ttk.Label(silence_frame, width=7)
        self.silence_label.pack(side=tk.LEFT, padx=5)
        
        def update_silence_label(*args):
            self.silence_label.config(text=f"{self.silence_len_var.get()} ms")
        
        self.silence_len_var.trace_add("write", update_silence_label)
        update_silence_label()
        
        # Padding antes e depois
        padding_frame = ttk.Frame(params_frame)
        padding_frame.pack(fill=tk.X, pady=2)
        
        # Padding antes
        ttk.Label(padding_frame, text="Padding antes (ms):").pack(side=tk.LEFT, padx=5)
        self.padding_before_var = tk.IntVar(value=DETECTION_PARAMS["padding_before"])
        padding_before_scale = ttk.Scale(
            padding_frame, 
            from_=0, 
            to=10000, 
            variable=self.padding_before_var, 
            orient=tk.HORIZONTAL
        )
        padding_before_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.padding_before_label = ttk.Label(padding_frame, width=7)
        self.padding_before_label.pack(side=tk.LEFT, padx=5)
        
        def update_padding_before_label(*args):
            self.padding_before_label.config(text=f"{self.padding_before_var.get()} ms")
        
        self.padding_before_var.trace_add("write", update_padding_before_label)
        update_padding_before_label()
        
        # Padding depois
        padding_after_frame = ttk.Frame(params_frame)
        padding_after_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(padding_after_frame, text="Padding depois (ms):").pack(side=tk.LEFT, padx=5)
        self.padding_after_var = tk.IntVar(value=DETECTION_PARAMS["padding_after"])
        padding_after_scale = ttk.Scale(
            padding_after_frame, 
            from_=0, 
            to=10000, 
            variable=self.padding_after_var, 
            orient=tk.HORIZONTAL
        )
        padding_after_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.padding_after_label = ttk.Label(padding_after_frame, width=7)
        self.padding_after_label.pack(side=tk.LEFT, padx=5)
        
        def update_padding_after_label(*args):
            self.padding_after_label.config(text=f"{self.padding_after_var.get()} ms")
        
        self.padding_after_var.trace_add("write", update_padding_after_label)
        update_padding_after_label()
        
        # Botão de aplicar configurações
        ttk.Button(
            advanced_tab, 
            text="Aplicar Configurações", 
            command=self.apply_config
        ).pack(pady=10)
        
        # Botão de detecção (já existente)
        ttk.Button(main_frame, text="Detectar Músicas", command=self.detect_music).pack(pady=10)
        
        # Substituir a implementação da barra de progresso
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL,
            length=100, 
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X)
        
        # Adicionar um rótulo para mostrar a etapa atual do processamento
        self.progress_step_var = tk.StringVar(value="")
        self.progress_step_label = ttk.Label(
            progress_frame, 
            textvariable=self.progress_step_var,
            anchor=tk.CENTER
        )
        self.progress_step_label.pack(fill=tk.X)
        
        # Esconder inicialmente
        self.progress_bar.pack_forget()
        self.progress_step_label.pack_forget()
        
        # Tabela de segmentos
        ttk.Label(main_frame, text="Segmentos Detectados:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        columns = ("#1", "#2")
        self.segments_table = ttk.Treeview(
            main_frame, 
            columns=columns, 
            show="headings",
            height=10
        )
        self.segments_table.heading("#1", text="Início")
        self.segments_table.heading("#2", text="Fim")
        self.segments_table.column("#1", width=100, anchor=tk.CENTER)
        self.segments_table.column("#2", width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.segments_table.yview)
        self.segments_table.configure(yscroll=scrollbar.set)
        
        self.segments_table.pack(fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão de exportar
        self.export_btn = ttk.Button(
            main_frame, 
            text="Exportar Selecionados", 
            command=self.export_selected,
            state=tk.DISABLED
        )
        self.export_btn.pack(pady=20)
        
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_progress(self, value=0, step=None):
        """Atualiza a barra de progresso e o texto de status"""
        self.progress_var.set(value)
        if step:
            self.progress_step_var.set(step)
        self.root.update()
    
    def show_progress(self):
        """Exibe a barra de progresso e o rótulo de etapa"""
        self.progress_var.set(0)
        self.progress_bar.pack(fill=tk.X)
        self.progress_step_label.pack(fill=tk.X)
        self.root.update()
    
    def hide_progress(self):
        """Esconde a barra de progresso e o rótulo de etapa"""
        self.progress_bar.pack_forget()
        self.progress_step_label.pack_forget()
        self.root.update()
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecione um vídeo",
            filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.video_path = file_path
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
    
    def detect_music(self):
        if not self.video_path:
            messagebox.showerror("Erro", "Selecione um arquivo de vídeo!")
            return
        
        self.status_var.set("Processando...")
        self.export_btn.config(state=tk.DISABLED)
        self.segments_table.delete(*self.segments_table.get_children())
        self.show_progress()  # Mostra a barra de progresso
        
        # Executar em thread para não travar a interface
        threading.Thread(
            target=self.run_detection, 
            daemon=True
        ).start()
    
    def run_detection(self):
        try:
            # Etapa 1: Extração de áudio (33% do processo)
            self.update_progress(0, "Iniciando extração de áudio...")
            self.root.update()
            
            # Obter todos os parâmetros configurados pelo usuário
            detection_params = {
                "threshold": self.threshold_var.get(),
                "min_silence_len": self.silence_len_var.get(),
                "padding_before": self.padding_before_var.get(),
                "padding_after": self.padding_after_var.get(),
                "min_segment_duration": self.min_duration_var.get() * 1000
            }
            
            # Chama a função unificada com os parâmetros
            self.segments = extract_and_detect(
                self.video_path,
                progress_callback=self.detection_progress_callback,
                **detection_params
            )
            
            # Finalização
            self.update_progress(100, "Processamento concluído!")
            self.update_segments_table()
            self.export_btn.config(state=tk.NORMAL)
            self.status_var.set(f"{len(self.segments)} segmentos detectados")
        except Exception as e:
            self.status_var.set("Erro durante o processamento")
            messagebox.showerror("Erro", str(e))
            logging.exception("Erro na detecção")
        finally:
            self.hide_progress()  # Esconde a barra ao finalizar
    
    def detection_progress_callback(self, stage, progress):
        """Callback para atualizar o progresso durante a detecção"""
        stages = {
            "extract": ("Extraindo áudio", 0, 30),
            "detect": ("Analisando áudio para detectar músicas", 30, 90),
            "finalize": ("Finalizando processamento", 90, 100)
        }
        
        if stage in stages:
            name, start_pct, end_pct = stages[stage]
            current_pct = start_pct + (end_pct - start_pct) * (progress / 100)
            self.update_progress(current_pct, f"{name} ({int(progress)}%)")
    
    def update_segments_table(self):
        for item in self.segments_table.get_children():
            self.segments_table.delete(item)
        
        for i, seg in enumerate(self.segments):
            start_str = self.format_time(seg['start'])
            end_str = self.format_time(seg['end'])
            self.segments_table.insert("", "end", values=(start_str, end_str))
    
    def format_time(self, seconds):
        return str(timedelta(seconds=round(seconds)))
    
    def export_selected(self):
        if not self.segments:
            messagebox.showinfo("Exportar", "Nenhum segmento detectado")
            return
        
        selected_indices = [self.segments_table.index(item) for item in self.segments_table.selection()]
        if not selected_indices:
            messagebox.showinfo("Exportar", "Nenhum segmento selecionado. Exportando todos.")
            selected_segments = self.segments
        else:
            selected_segments = [self.segments[i] for i in selected_indices]
        
        output_dir = filedialog.askdirectory(title="Selecione a pasta de destino")
        if not output_dir:
            return
        
        self.status_var.set("Exportando segmentos...")
        self.show_progress()  # Mostra a barra de progresso
        
        threading.Thread(
            target=self.run_export, 
            args=(self.video_path, output_dir, selected_segments),
            daemon=True
        ).start()
    
    def run_export(self, video_path, output_dir, segments):
        try:
            from main import export_segments
            
            # Configurar acompanhamento de progresso
            total_segments = len(segments)
            
            def export_progress(current_segment, segment_progress):
                segment_pct = (current_segment / total_segments * 100)
                overall_progress = segment_pct
                status = f"Exportando segmento {current_segment+1} de {total_segments}"
                self.update_progress(overall_progress, status)
            
            # Chamar a exportação com callback de progresso
            export_segments(video_path, output_dir, segments, progress_callback=export_progress)
            
            self.update_progress(100, "Exportação concluída!")
            self.status_var.set(f"{len(segments)} segmentos exportados com sucesso!")
            messagebox.showinfo("Sucesso", f"{len(segments)} segmentos exportados para:\n{output_dir}")
        except Exception as e:
            self.status_var.set("Erro durante a exportação")
            messagebox.showerror("Erro", str(e))
        finally:
            self.hide_progress()  # Esconde a barra ao finalizar
    
    def apply_config(self):
        """Aplica as configurações atuais e salva"""
        updated_config = {
            "detection": {
                "threshold": self.threshold_var.get(),
                "min_silence_len": self.silence_len_var.get(),
                "padding_before": self.padding_before_var.get(),
                "padding_after": self.padding_after_var.get(),
                "min_segment_duration": self.min_duration_var.get() * 1000
            }
        }
        
        save_config(updated_config)
        messagebox.showinfo("Configurações", "Configurações aplicadas com sucesso!")