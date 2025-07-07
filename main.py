import os
from music_detection import detect_music_segments
from video_operations import extract_audio, cut_video_segment
import logging
from config import DETECTION_PARAMS

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def extract_and_detect(video_path, progress_callback=None, **detection_params):
    """Função unificada para extração e detecção com tratamento de temp files e callback de progresso"""
    audio_path = None
    try:
        # Reportar início da extração
        if progress_callback:
            progress_callback("extract", 0)
            
        audio_path = extract_audio(video_path)
        
        # Reportar conclusão da extração e início da detecção
        if progress_callback:
            progress_callback("extract", 100)
            progress_callback("detect", 0)
        
        # Permite sobrescrever parâmetros específicos, mantendo os padrões para o resto
        segments = detect_music_segments(audio_path, **detection_params)
        
        # Reportar finalização
        if progress_callback:
            progress_callback("detect", 100)
            progress_callback("finalize", 0)
            progress_callback("finalize", 100)
            
        return segments
    finally:
        # Remove o arquivo de áudio temporário após o uso
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception as e:
                logging.warning(f"Erro ao remover temp file: {str(e)}")

def export_segments(video_path, output_dir, segments, progress_callback=None):
    """Exporta segmentos de vídeo com suporte a acompanhamento de progresso"""
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    for i, seg in enumerate(segments):
        # Reportar progresso
        if progress_callback:
            progress_callback(i, 0)
            
        output_path = os.path.join(
            output_dir, 
            f"{base_name}_part{i+1}.mp4"
        )
        
        cut_video_segment(
            video_path,
            output_path,
            seg['start'],
            seg['end']
        )
        
        # Reportar conclusão deste segmento
        if progress_callback:
            progress_callback(i, 100)

if __name__ == '__main__':
    import tkinter as tk
    from gui import MusicExtractorApp
    root = tk.Tk()
    app = MusicExtractorApp(root)
    root.mainloop()