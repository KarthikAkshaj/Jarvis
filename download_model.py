# download_model.py
import os
import requests
from tqdm import tqdm
import zipfile


def download_vosk_model():
    # Create model directory
    model_dir = "model/vosk"
    os.makedirs(model_dir, exist_ok=True)

    # URL for small English model
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    zip_path = "vosk-model-small-en-us-0.15.zip"

    # Download the model
    print("Downloading Vosk model...")
    response = requests.get(model_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    with open(zip_path, "wb") as file, tqdm(
        desc=zip_path,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

    # Extract the model
    print("\nExtracting model...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall("model/vosk")

    # Clean up
    os.remove(zip_path)

    # Rename the extracted folder
    extracted_dir = "model/vosk/vosk-model-small-en-us-0.15"
    if os.path.exists(extracted_dir):
        for item in os.listdir(extracted_dir):
            os.rename(
                os.path.join(extracted_dir, item), os.path.join("model/vosk", item)
            )
        os.rmdir(extracted_dir)

    print("Model setup complete!")


if __name__ == "__main__":
    download_vosk_model()
