import os
import cv2
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
import base64
import subprocess
import asyncio
from prompts import prompt_video

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
temp_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)))

async def transcribe_audio(video_path):
    """Extrai e transcreve o áudio do vídeo de forma assíncrona"""
    # Usa temp_directory se definido, senão tempfile escolhe o padrão
    audio_temp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False, dir=temp_directory).name

    # Comando para extrair áudio usando subprocess
    command = [
        'ffmpeg', '-i', video_path,
        '-q:a', '0', '-map', 'a', audio_temp,
        '-y', '-loglevel', 'error'
    ]
    # Roda ffmpeg em um thread separado
    process = await asyncio.to_thread(
        subprocess.run, command, check=True, capture_output=True
    )
    print("Áudio extraído com sucesso.")

    # Transcreve o áudio usando a API Whisper em um thread separado
    def sync_transcribe():
        with open(audio_temp, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
            )
        return transcription.text

    transcription_text = await asyncio.to_thread(sync_transcribe)
    print("Áudio transcrito com sucesso.")

    # Remove o arquivo temporário sempre
    if os.path.exists(audio_temp):
        try:
            os.remove(audio_temp)
        except OSError as e:
             print(f"Erro ao remover arquivo de áudio temporário {audio_temp}: {e}")

    return transcription_text

# --- Nova função extract_frames ---
async def extract_frames(video_path, interval_seconds=1, scale=1.0):
    """
    Extrai frames de um vídeo em intervalos especificados de forma assíncrona.

    Args:
        video_path (str): Caminho para o arquivo de vídeo.
        interval_seconds (int): Intervalo em segundos entre frames extraídos.
        scale (float): Fator de escala para redimensionar os frames.

    Returns:
        list: Uma lista de frames (arrays numpy no formato RGB).
    """
    
    extracted_frames = []

    def sync_extract():
        video = cv2.VideoCapture(video_path)
        if not video.isOpened():
            raise IOError(f"Não foi possível abrir o vídeo: {video_path}")
        
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = total_frames / fps if fps > 0 else 0
        
        print(f"Vídeo Info: FPS={fps:.2f}, Total Frames={total_frames}, Duração={duration_seconds:.2f}s")

        frames_to_extract = []
        if interval_seconds <= 0:
             # Se intervalo for inválido, extrai apenas o primeiro frame
             frames_to_extract.append(0)
        else:
            current_second = 0
            while current_second < duration_seconds:
                frame_index = int(current_second * fps)
                if frame_index < total_frames:
                    frames_to_extract.append(frame_index)
                current_second += interval_seconds
            # Garante que o último frame seja incluído se o intervalo não coincidir exatamente
            if total_frames > 0 and (not frames_to_extract or frames_to_extract[-1] < total_frames - 1):
                 # Adiciona o penúltimo frame para evitar potencial problema com o último exato
                 # Ou podemos adicionar o último frame: total_frames - 1
                 last_frame_index = total_frames - 1
                 if last_frame_index not in frames_to_extract:
                     frames_to_extract.append(last_frame_index)
        
        print(f"Extraindo {len(frames_to_extract)} frames em intervalos de {interval_seconds}s...")

        local_frames_list = []
        last_extracted_index = -1
        for frame_index in sorted(list(set(frames_to_extract))): # Ordena e remove duplicados
             if frame_index >= total_frames:
                  continue # Evita buscar frames além do limite
             
             # Otimização: Se o próximo frame a extrair é o seguinte ao último lido, apenas leia.
             # Caso contrário, reposicione (seek).
             if frame_index != last_extracted_index + 1:
                  video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
             
             ret, frame = video.read()
             if ret:
                # Converte BGR para RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Redimensiona se necessário
                if scale != 1.0:
                    height, width = frame_rgb.shape[:2]
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
                
                local_frames_list.append(frame_rgb)
                last_extracted_index = frame_index
             else:
                 print(f"Aviso: Falha ao ler o frame no índice {frame_index}")

        video.release()
        print(f"Frames extraídos com sucesso: {len(local_frames_list)}")
        return local_frames_list

    try:
        extracted_frames = await asyncio.to_thread(sync_extract)
        return extracted_frames
    except IOError as e:
         print(f"Erro de I/O ao processar o vídeo: {e}")
         raise
    except Exception as e:
         print(f"Erro inesperado durante a extração de frames: {e}")
         raise

# --- Função para codificar frames em base64 ---
async def encode_frames_to_base64(frames):
    """Codifica uma lista de frames (numpy arrays) para strings base64 JPEG."""
    encoded_frames = []
    
    def sync_encode(frame):
        # Codifica o frame como JPEG (mais eficiente para imagens naturais)
        success, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if not success:
            raise RuntimeError("Falha ao codificar frame para JPEG")
        # Converte para base64 string
        return base64.b64encode(buffer).decode('utf-8')

    # Cria tarefas para codificar cada frame em paralelo usando threads
    tasks = [asyncio.to_thread(sync_encode, frame) for frame in frames]
    encoded_frames = await asyncio.gather(*tasks)
    print(f"{len(encoded_frames)} frames codificados para base64.")
    return encoded_frames


async def analyze_video(video_path):
    """Envia frames amostrados e áudio do vídeo para análise pelo GPT-4o (versão assíncrona)"""
    
    print("Iniciando análise de vídeo (extração paralela de frames e áudio)...")
    # Executa a extração de frames e a transcrição de áudio em paralelo
    try:
        # Extrai 1 frame por segundo (padrão)
        frame_extraction_task = asyncio.create_task(extract_frames(video_path, interval_seconds=1))
        audio_transcription_task = asyncio.create_task(transcribe_audio(video_path))

        # Espera ambas as tarefas concluírem
        extracted_frames, audio_transcription = await asyncio.gather(
            frame_extraction_task,
            audio_transcription_task
        )
        print("Extração de frames e transcrição de áudio concluídas.")

        if not extracted_frames:
            raise ValueError("Nenhum frame foi extraído do vídeo.")

        # Codifica os frames extraídos para base64 em paralelo
        encoded_frames = await encode_frames_to_base64(extracted_frames)

    except Exception as e:
        print(f"Erro durante o pré-processamento (frames/áudio): {e}")
        raise # Re-lança a exceção para parar a execução

    # Monta a lista de conteúdo para a API
    content = [
        {
            "type": "text",
            "text": prompt_video, # Usando o prompt importado
        }
    ]
    # Adiciona cada frame codificado como uma imagem separada
    for encoded_frame in encoded_frames:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_frame}",
                # 'detail': 'low' pode ser usado para reduzir custo se alta resolução não for crucial
            }
        })
    # Adiciona a transcrição de áudio no final
    content.append({
        "type": "text",
        "text": f"Transcrição do Áudio:\n{audio_transcription}"
    })

    print(f"Enviando {len(extracted_frames)} frames e transcrição para análise do GPT-4o...")
    # Envolve a chamada síncrona da API OpenAI com asyncio.to_thread
    def sync_openai_call():
        response = client.chat.completions.create(
            model="gpt-4o-mini", # ou gpt-4o para mais capacidade
            messages=[
                {
                    "role": "user",
                    "content": content, # Passa a lista montada
                }
            ],
            max_tokens=1000 # Aumentar tokens pode ser necessário com mais frames/info
        )
        return response.choices[0].message.content

    analysis_result = await asyncio.to_thread(sync_openai_call)
    print("Análise do GPT-4o recebida.")
    return analysis_result

if __name__ == "__main__":
    video_path = "C:\\Users\\diham\\segurança-trabalho\\project\\video.mp4"
    
    print(f"Processando vídeo: {video_path}")
    # Executa a função principal assíncrona
    analysis = asyncio.run(analyze_video(video_path))
    print("\n--- Análise Completa ---")
    print(analysis)