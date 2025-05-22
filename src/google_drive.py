import logging
import os
import ssl
import tempfile
import requests
import subprocess
from datetime import datetime
import pytz
from dotenv import load_dotenv

from src import database
from src.frigate_api import generate_video_url

load_dotenv()

UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'Frigate')
TIMEZONE = os.getenv('TIMEZONE', 'America/Sao_Paulo')
RCLONE_REMOTE = os.getenv('RCLONE_REMOTE', 'gdrive')


def generate_filename(camera_name, start_time, event_id):
    utc_time = datetime.fromtimestamp(start_time, pytz.utc)
    local_time = utc_time.astimezone(pytz.timezone(TIMEZONE))
    return f"{local_time.strftime('%Y-%m-%d-%H-%M-%S')}__{camera_name}__{event_id}.mp4"


def upload_to_google_drive(event, frigate_url):
    camera_name = event['camera']
    start_time = event['start_time']
    event_id = event['id']
    filename = generate_filename(camera_name, start_time, event_id)
    year, month, day = filename.split("__")[0].split("-")[:3]
    video_url = generate_video_url(frigate_url, event_id)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = os.path.join(tmpdir, filename)
            response = requests.get(video_url, stream=True, timeout=300)

            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Caminho remoto no Google Drive via rclone
                remote_path = f"{RCLONE_REMOTE}:{UPLOAD_DIR}/{camera_name}/{year}/{month}/{day}/{filename}"

                result = subprocess.run(["rclone", "copyto", local_path, remote_path], capture_output=True, text=True)

                if result.returncode == 0:
                    logging.info(f"Upload de {filename} feito com sucesso para {remote_path}")
                    return True
                else:
                    logging.error(f"Erro no upload com rclone: {result.stderr}")
                    return False

            elif response.status_code == 500 and response.json().get('message') == "Could not create clip from recordings":
                logging.warning(f"Clip não encontrado para o evento {event_id}.")
                if database.select_tries(event_id) >= 10:
                    database.update_event(event_id, 0, retry=0)
                    logging.error(f"Clip falhou permanentemente: {event_id}")
                return False
            else:
                logging.error(f"Erro ao baixar vídeo de {video_url} - Status: {response.status_code}")
                return False

    except (requests.RequestException, ssl.SSLError) as e:
        logging.error(f"Erro ao baixar vídeo de {video_url}: {e}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado: {e}", exc_info=True)
        return False

