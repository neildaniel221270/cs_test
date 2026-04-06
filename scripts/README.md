## Extract audio (and subtitles where needed) from a folder:**
```
python scripts/extract_audio.py --input Data/raw_videos --manifest Data/processed/manifest.jsonl
```
## Run on 5-10 videos
```
python scripts/transcribe_batch.py --manifest Data/processed/manifest.jsonl --limit 10 --model medium --device cpu --compute_type int8
```

## Create a reference text file by manually correcting:
**(./Data/references/LMOS_Intro.ref.txt)**
```
python scripts/eval_wer.py --ref_txt "Data/references/LMOS Introduction to the process.ref.txt" --hyp_raw_json "Data/transcripts_raw/LMOS Introduction to the process.raw.json"
```

## Clean the trasncript based on ASML Glossary.csv
```
python clean_transcript.py --in_raw_json "..\Data\transcripts_raw\LMOS Introduction to the process.raw.json" --out_clean_json "..\Data\transcripts_clean\LMOS Introduction to the process.clean.json" --glossary_csv "..\Data\ASML Glossary.csv" --structure --lmstudio_model "mistralai/mistral-7b-instruct-v0.3" --lmstudio_timeout 900 --structure_max_chars 6000
```

**clean_transcript.py(for longer videos)**
```
--structure_max_chars 12000
--lmstudio_timeout 1200
```
**clean_transcript.py (for shorter videos)**
```
--structure_max_chars 6000
--lmstudio_timeout 600
```

## Structure batch
```
(.venv) C:\Users\nedaniel\Documents\CS\.venv\Scripts>set LM_API_TOKEN=......

(.venv) C:\Users\nedaniel\Documents\CS\.venv\Scripts>curl http://10.46.199.194:1234/v1/models -H "Authorization: Bearer %LM_API_TOKEN%"

(.venv) C:\Users\nedaniel\Documents\CS\.venv\Scripts>curl -i http://10.46.199.194:1234/v1/chat/completions -H "Authorization: Bearer %LM_API_TOKEN%" -H "Content-Type: application/json" -d "{\"model\":\"mistralai/mistral-7b-instruct-v0.3\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello\"}],\"temperature\":0.1,\"stream\":false}"

python scripts/structure_batch.py --in_dir Data/transcripts_clean --out_dir Data/transcripts_structured --model "mistralai/mistral-7b-instruct-v0.3" --base_url "http://10.46.199.194:1234/v1" --api_key "%LM_API_TOKEN%" --force --no_few_shot --max_chars 1000 --timeout 600
```