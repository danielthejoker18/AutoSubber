import sys
import os
import subprocess
import torch
import argparse
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import ffmpeg
import pysrt
from datetime import timedelta

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

transcriber = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-medium",
    device=device
)
translator_model_name = "facebook/m2m100_418M"
translator_tokenizer = AutoTokenizer.from_pretrained(translator_model_name)
translator = AutoModelForSeq2SeqLM.from_pretrained(translator_model_name).to(device)

LANG_MAPPINGS = {
    'pt-br': 'pt',
    'pt-pt': 'pt',
}

def extract_audio(video_path, audio_path):
    """Extract audio from video using FFmpeg."""
    try:
        subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("FFmpeg failed. Ensure it's installed.")

def transcribe_audio(audio_path, src_lang):
    """Transcribe full audio with timestamps."""
    result = transcriber(
        audio_path,
        return_timestamps=True,
        task="transcribe",
        language=src_lang
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
    src_lang = LANG_MAPPINGS.get(src_lang.lower(), src_lang)
    tgt_lang = LANG_MAPPINGS.get(tgt_lang.lower(), tgt_lang)
    
    translator_tokenizer.src_lang = src_lang
    translated = []
    for seg in segments:
        inputs = translator_tokenizer(seg['text'], return_tensors="pt").to(device)
        generated_tokens = translator.generate(**inputs, forced_bos_token_id=translator_tokenizer.get_lang_id(tgt_lang))
        trans_text = translator_tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
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
        subprocess.run([
            "ffmpeg", "-i", video_path, "-vf", f"subtitles={srt_path}", "-c:v", "libx264", "-crf", "23", "-c:a", "aac", output_path
        ], check=True)
    except subprocess.CalledProcessError:
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoSubber: Generate subtitles for videos or transcribe audio.")
    parser.add_argument("input_file", help="Path to input video or audio file")
    parser.add_argument("output", help="Path to output file (video or base for SRT/TXT)")
    parser.add_argument("src_lang", help="Source language code (e.g., en)")
    parser.add_argument("tgt_lang", help="Target language code (e.g., fr)")
    parser.add_argument("--srt-only", action="store_true", help="Generate SRT file only (no video embedding)")
    
    args = parser.parse_args()
    
    input_path = args.input_file
    output_base = os.path.splitext(args.output)[0]
    srt_path = f"{output_base}.srt"
    txt_path = f"{output_base}.txt"
    
    is_audio = is_audio_file(input_path)
    
    output_video = args.output if (not args.srt_only and not is_audio) else None
    src_lang = args.src_lang
    tgt_lang = args.tgt_lang
    
    audio_path = "temp_audio.wav"
    
    try:
        if is_audio:
            print(f"Input detected as audio file: {input_path}")
            print("Preparing audio...")
            subprocess.run(["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", audio_path, "-y"], check=True)
        else:
            print("Extracting audio from video...")
            extract_audio(input_path, audio_path)
        
        print("Transcribing...")
        segments = transcribe_audio(audio_path, src_lang)
        
        print("Translating...")
        translated_segments = translate_segments(segments, src_lang, tgt_lang)
        
        print("Generating SRT...")
        generate_srt(translated_segments, srt_path)
        
        print("Generating TXT...")
        save_transcription_txt(translated_segments, txt_path)
        
        if output_video:
            print("Embedding subtitles...")
            embed_subtitles(input_path, srt_path, output_video)
            print(f"Done! Output video at {output_video}")
        else:
            print(f"Done! SRT file at {srt_path}")
            print(f"Done! TXT file at {txt_path}")
            
    finally:
        if os.path.exists(audio_path): os.remove(audio_path)
        
        if output_video and os.path.exists(output_video):
            if os.path.exists(srt_path): os.remove(srt_path)