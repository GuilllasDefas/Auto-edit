import os
import ffmpeg
import logging
import tempfile
from config import AUDIO_EXTRACTION_PARAMS, EXPORT_PARAMS

def extract_audio(video_path, audio_output=None):
    """Extrai áudio do vídeo para processamento."""
    try:
        if audio_output is None:
            # Cria um arquivo temporário em um local com permissão garantida
            temp_dir = tempfile.gettempdir()
            audio_output = os.path.join(temp_dir, f"audio_{os.getpid()}.wav")
        
        (
            ffmpeg
            .input(video_path)
            .output(
                audio_output, 
                acodec=AUDIO_EXTRACTION_PARAMS["audio_codec"], 
                ac=AUDIO_EXTRACTION_PARAMS["audio_channels"], 
                ar=str(AUDIO_EXTRACTION_PARAMS["sample_rate"])
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True, quiet=True)
        )
        return audio_output
    except ffmpeg.Error as e:
        logging.error(f"Erro ao extrair áudio: {e.stderr.decode('utf-8')}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        raise

def cut_video_segment(video_path, output_path, start, end):
    """Corta um segmento de vídeo mantendo as características originais."""
    try:
        output_options = {}
        
        # Se estiver configurado para copiar codecs originais
        if EXPORT_PARAMS["copy_codec"]:
            output_options["c"] = "copy"
        
        (
            ffmpeg
            .input(video_path, ss=start, to=end)
            .output(output_path, **output_options)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True, quiet=True)
        )
        return True
    except ffmpeg.Error as e:
        logging.error(f"Erro ao cortar vídeo: {e.stderr.decode('utf-8')}")
        raise