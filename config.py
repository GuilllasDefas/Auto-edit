"""
Configurações centralizadas para o sistema de detecção e edição de música.
"""

# Parâmetros para detecção de música
DETECTION_PARAMS = {
    # Limiar de detecção de silêncio em dB (valores mais negativos = mais sensível)
    "threshold": -45,
    
    # Duração mínima de silêncio em ms para considerar como separador entre músicas
    "min_silence_len": 3000,
    
    # Padding antes do segmento em ms (para não cortar o início da música)
    "padding_before": 5000,
    
    # Padding depois do segmento em ms (para não cortar o final da música)
    "padding_after": 5000,
    
    # Duração mínima de um segmento para ser considerado música (ms)
    "min_segment_duration": 60000,  # 1 minuto por padrão
}

# Parâmetros para exportação de vídeo
EXPORT_PARAMS = {
    # Formato de arquivo de saída
    "format": "mp4",
    
    # Qualidade de exportação (manter original)
    "copy_codec": True,
}

# Parâmetros para extração de áudio
AUDIO_EXTRACTION_PARAMS = {
    # Codec de áudio para análise
    "audio_codec": "pcm_s16le",
    
    # Canais de áudio (1 = mono)
    "audio_channels": 1,
    
    # Taxa de amostragem para análise
    "sample_rate": 16000,
}

# Função para salvar configurações atualizadas
def save_config(updated_params):
    """
    Atualiza os parâmetros de configuração em tempo de execução.
    Esta é uma versão simplificada que apenas atualiza os dicionários em memória.
    """
    for category, params in updated_params.items():
        if category == "detection":
            DETECTION_PARAMS.update(params)
        elif category == "export":
            EXPORT_PARAMS.update(params)
        elif category == "audio":
            AUDIO_EXTRACTION_PARAMS.update(params)
    
    return {
        "detection": DETECTION_PARAMS,
        "export": EXPORT_PARAMS,
        "audio": AUDIO_EXTRACTION_PARAMS
    }
