import numpy as np
from pydub import AudioSegment, silence
import logging
import os
from config import DETECTION_PARAMS

def detect_music_segments(audio_path, threshold=None, min_silence_len=None, 
                          padding_before=None, padding_after=None, min_segment_duration=None):
    """Detecta segmentos de música no áudio com silêncio como separador.
    
    Args:
        audio_path: Caminho para o arquivo de áudio
        threshold: Limiar de detecção de silêncio em dB
        min_silence_len: Duração mínima de silêncio em ms
        padding_before: Padding antes do segmento em ms
        padding_after: Padding depois do segmento em ms
        min_segment_duration: Duração mínima do segmento em ms (padrão: 60000 = 1 minuto)
    """
    try:
        # Usar valores padrão do config.py se não especificados
        threshold = threshold if threshold is not None else DETECTION_PARAMS["threshold"]
        min_silence_len = min_silence_len if min_silence_len is not None else DETECTION_PARAMS["min_silence_len"]
        padding_before = padding_before if padding_before is not None else DETECTION_PARAMS["padding_before"]
        padding_after = padding_after if padding_after is not None else DETECTION_PARAMS["padding_after"]
        min_segment_duration = min_segment_duration if min_segment_duration is not None else DETECTION_PARAMS["min_segment_duration"]
        
        # Verifica se o arquivo existe e tem tamanho adequado
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1024:
            raise ValueError(f"Arquivo de áudio inválido: {audio_path}")
        
        audio = AudioSegment.from_file(audio_path)
        
        # Ajusta o limiar de silêncio baseado no volume médio se não for especificado
        if threshold is None:
            threshold = audio.dBFS - 14
        
        silence_ranges = silence.detect_silence(
            audio, 
            min_silence_len=min_silence_len, 
            silence_thresh=threshold
        )
        
        segments = []
        prev_end = 0
        
        for start, end in silence_ranges:
            segment_duration = start - prev_end
            if segment_duration > 5000:  # Filtro inicial para segmentos muito curtos
                segments.append((
                    max(0, prev_end - padding_before),
                    min(len(audio), start + padding_after)
                ))
            prev_end = end
        
        # Adiciona último segmento
        if len(audio) - prev_end > 5000:
            segments.append((
                max(0, prev_end - padding_before),
                len(audio)
            ))
        
        # Filtra segmentos com base na duração mínima
        filtered_segments = []
        for start, end in segments:
            duration = end - start
            if duration >= min_segment_duration:
                filtered_segments.append((start, end))
                logging.info(f"Segmento detectado: {start/1000:.2f}s - {end/1000:.2f}s (duração: {duration/1000:.2f}s)")
            else:
                logging.info(f"Segmento ignorado por ser muito curto: {start/1000:.2f}s - {end/1000:.2f}s (duração: {duration/1000:.2f}s)")
        
        return [{'start': s[0]/1000, 'end': s[1]/1000} for s in filtered_segments]
    
    except Exception as e:
        logging.error(f"Erro na detecção de músicas: {str(e)}")
        raise