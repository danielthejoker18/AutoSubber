
import sys
import os
import subprocess
import torch
import ffmpeg
import pysrt
from datetime import timedelta
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"

# Global model cache to avoid reloading on every request (if persistence is desired)
_transcriber = None
_translator = None
_translator_tokenizer = None
_current_whisper_model = None

LANG_MAPPINGS = {
    'pt-br': 'pt',
    'pt-pt': 'pt',
}

def get_transcriber(model_name="openai/whisper-medium"):
    global _transcriber, _current_whisper_model
    if _transcriber is None or _current_whisper_model != model_name:
        logger.info(f"Loading Whisper model: {model_name}...")
        _transcriber = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=device
        )
        _current_whisper_model = model_name
    return _transcriber

def get_translator():
    global _translator, _translator_tokenizer
    if _translator is None:
        logger.info("Loading M2M100 model...")
        model_name = "facebook/m2m100_418M"
        _translator_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _translator = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    return _translator, _translator_tokenizer

def extract_audio(video_path, audio_path):
    """Extract audio from video using FFmpeg."""
    try:
        subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"], check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg failed: {e.stderr.decode()}")
        raise RuntimeError("FFmpeg failed. Ensure it's installed.")

def transcribe_audio(audio_path, src_lang, model_name="openai/whisper-medium"):
    """Transcribe full audio with timestamps."""
    transcriber = get_transcriber(model_name)
    logger.info("Starting transcription...")
    
    # Whisper expects language code or None for auto-detect
    # Check if src_lang fits Whisper's expectations or let it auto-detect if unsure
    lang_arg = src_lang if src_lang and src_lang != "auto" else None
    
    result = transcriber(
        audio_path,
        return_timestamps=True,
        task="transcribe",
        language=lang_arg
    )
    segments = []
    for chunk in result['chunks']:
        start, end = chunk['timestamp']
        segments.append({
            'start': timedelta(seconds=start if start is not None else 0),
            'end': timedelta(seconds=end if end is not None else 0),
            'text': chunk['text'].strip()
        })
    return segments

def translate_segments(segments, src_lang, tgt_lang):
    """Translate text segments."""
    if src_lang == tgt_lang:
        return segments

    translator, tokenizer = get_translator()
    logger.info("Starting translation...")
    
    src_lang_code = LANG_MAPPINGS.get(src_lang.lower(), src_lang)
    tgt_lang_code = LANG_MAPPINGS.get(tgt_lang.lower(), tgt_lang)
    
    tokenizer.src_lang = src_lang_code
    translated = []
    
    # Simple batching could be implemented here for speed
    total = len(segments)
    for i, seg in enumerate(segments):
        if i % 10 == 0:
            logger.info(f"Translating segment {i}/{total}")
            
        inputs = tokenizer(seg['text'], return_tensors="pt").to(device)
        generated_tokens = translator.generate(**inputs, forced_bos_token_id=tokenizer.get_lang_id(tgt_lang_code))
        trans_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        translated.append({**seg, 'text': trans_text})
        
    return translated

def timedelta_to_srt_time(td):
    """Convert timedelta to SubRipTime."""
    total_ms = int(td.total_seconds() * 1000)
    hours = total_ms // (3600 * 1000)
    minutes = (total_ms // (60 * 1000)) % 60
    seconds = (total_ms // 1000) % 60
    milliseconds = total_ms % 1000
    return pysrt.SubRipTime(hours, minutes, seconds, milliseconds)

def generate_srt(segments, srt_path):
    """Create SRT file from segments."""
    subs = pysrt.SubRipFile()
    for i, seg in enumerate(segments, start=1):
        sub = pysrt.SubRipItem(
            index=i,
            start=timedelta_to_srt_time(seg['start']),
            end=timedelta_to_srt_time(seg['end']),
            text=seg['text']
        )
        subs.append(sub)
    subs.save(srt_path, encoding='utf-8')

def embed_subtitles(video_path, srt_path, output_path):
    """Burn subtitles into video."""
    try:
        # Use abs paths to avoid FFmpeg issues
        video_path = os.path.abspath(video_path)
        srt_path = os.path.abspath(srt_path)
        output_path = os.path.abspath(output_path)
        
        # Escape path for filter (windows/linux distinct, but keeping simple for now)
        # Note: In complex paths, escaping : and \ is needed for filter_complex
        # Simple workaround: -vf subtitles="filename"
        
        # On POSIX, typical path is fine. On Windows, needs escaping.
        # Python's subprocess handles arguments, but the internal filter string is parsed by ffmpeg.
        srt_arg = srt_path.replace("\\", "/").replace(":", "\\:")
        
        subprocess.run([
            "ffmpeg", "-i", video_path, 
            "-vf", f"subtitles='{srt_arg}'", 
            "-c:v", "libx264", "-crf", "23", "-c:a", "aac", 
            output_path, "-y"
        ], check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg embedding failed: {e.stderr.decode()}")
        raise RuntimeError("FFmpeg embedding failed.")

def save_transcription_txt(segments, txt_path):
    """Save transcription to a text file."""
    with open(txt_path, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"{seg['text']}\n")

def is_audio_file(filepath):
    """Check if file is audio based on extension."""
    audio_exts = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma'}
    return os.path.splitext(filepath)[1].lower() in audio_exts
