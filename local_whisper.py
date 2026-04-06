import os
import whisper
import torch

# Downloading locally
# # Define path
# path = os.path.join("models", "whisper")
# os.makedirs(path, exist_ok=True)

# # This will download the .pt file into your folder
# print("Downloading...")
# model_path = whisper._download(whisper._MODELS["medium.en"], path, False)
# print(f"Success! Model is at: {model_path}")

# Running Whisper
# Point directly to your local file
local_file = os.path.join("models", "whisper", "medium.en.pt")

# GPU check
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading model on: {device}")

# Load from your local path
model = whisper.load_model(local_file, device=device)

# Test run
# result = model.transcribe("your_audio_file.mp3")
