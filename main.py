import sys
import os
import subprocess
import torch
import argparse
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import ffmpeg
import pysrt
from datetime import timedelta

# Check for GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load models (downloads on first run)
transcriber = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-medium",  # Bumped to medium for better accuracy; use 'large' if your GPU can handle it
    device=device
)
translator_model_name = "facebook/m2m100_418M"  # Multilingual, supports 100+ langs
translator_tokenizer = AutoTokenizer.from_pretrained(translator_model_name)
translator = AutoModelForSeq2SeqLM.from_pretrained(translator_model_name).to(device)

# Language code mappings for variants
LANG_MAPPINGS = {
    'pt-br': 'pt',  # Brazilian Portuguese -> standard pt
    'pt-pt': 'pt',  # European Portuguese -> standard pt
    # Add more if needed, e.g., 'en-us': 'en'
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
        task="transcribe",  # Explicitly set to transcribe (not translate)
        language=src_lang  # Use the source lang from args (e.g., 'en'); improves detection accuracy
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
    # Apply mappings if needed
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoSubber: Generate subtitles for videos.")
    parser.add_argument("input_video", help="Path to input video file")
    parser.add_argument("output", help="Path to output file (video or base for SRT)")
    parser.add_argument("src_lang", help="Source language code (e.g., en)")
    parser.add_argument("tgt_lang", help="Target language code (e.g., fr)")
    parser.add_argument("--srt-only", action="store_true", help="Generate SRT file only (no video embedding)")
    
    args = parser.parse_args()
    
    video_path = args.input_video
    output_base = os.path.splitext(args.output)[0]  # e.g., 'video2' from 'video2.mp4'
    srt_path = f"{output_base}.srt"
    output_video = args.output if not args.srt_only else None  # No video if SRT only
    src_lang = args.src_lang
    tgt_lang = args.tgt_lang
    
    audio_path = "temp_audio.wav"
    
    try:
        print("Extracting audio...")
        extract_audio(video_path, audio_path)
        
        print("Transcribing...")
        segments = transcribe_audio(audio_path, src_lang)
        
        print("Translating...")
        translated_segments = translate_segments(segments, src_lang, tgt_lang)
        
        print("Generating SRT...")
        generate_srt(translated_segments, srt_path)
        
        if not args.srt_only:
            print("Embedding subtitles...")
            embed_subtitles(video_path, srt_path, output_video)
            print(f"Done! Output video at {output_video}")
        else:
            print(f"Done! SRT file at {srt_path}")
    finally:
        # Cleanup
        if os.path.exists(audio_path): os.remove(audio_path)
        if args.srt_only or not os.path.exists(output_video):  # Keep SRT if SRT-only or embedding failed
            pass
        else:
            if os.path.exists(srt_path): os.remove(srt_path)