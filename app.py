
import os
import threading
import uuid
import logging
import queue
import time
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from werkzeug.utils import secure_filename
import autosubber

app = Flask(__name__)

# Config
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global logging queue for SSE
log_queue = queue.Queue()

# Custom logger to push to queue
class QueueHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put(log_entry)

# Setup logging
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
queue_handler = QueueHandler()
queue_handler.setFormatter(formatter)
logging.getLogger().addHandler(queue_handler)

# Configure autosubber logger as well
autosubber_logger = logging.getLogger('autosubber')
autosubber_logger.addHandler(queue_handler)
autosubber_logger.setLevel(logging.INFO)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # Uniqueify filename to prevent collisions
        unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)
        return jsonify({'filename': unique_name, 'filepath': save_path})

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    filename = data.get('filename')
    src_lang = data.get('src_lang', 'en')
    tgt_lang = data.get('tgt_lang', 'pt')
    model = data.get('model', 'openai/whisper-small')
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404

    # Output naming
    base_name = os.path.splitext(filename)[0]
    output_video_name = f"{base_name}_subbed.mp4"
    output_video_path = os.path.join(app.config['OUTPUT_FOLDER'], output_video_name)
    
    srt_name = f"{base_name}.srt"
    srt_path = os.path.join(app.config['OUTPUT_FOLDER'], srt_name)
    
    txt_name = f"{base_name}.txt"
    txt_path = os.path.join(app.config['OUTPUT_FOLDER'], txt_name)

    # Start processing in a separate thread so we don't block
    thread = threading.Thread(target=run_processing, args=(input_path, output_video_path, srt_path, txt_path, src_lang, tgt_lang, model))
    thread.start()
    
    return jsonify({'status': 'Processing started', 'output_video': output_video_name})

def run_processing(input_path, output_video_path, srt_path, txt_path, src_lang, tgt_lang, model_name):
    try:
        logging.info(f"Processing started for {os.path.basename(input_path)}")
        logging.info(f"Configuration: src={src_lang}, tgt={tgt_lang}, model={model_name}")
        
        audio_path = input_path + ".wav"
        is_audio = autosubber.is_audio_file(input_path)


        if is_audio:
            logging.info("Converting audio...")
            subprocess.run(["ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", audio_path, "-y"], check=True)
        else:
            logging.info("Extracting audio...")
            autosubber.extract_audio(input_path, audio_path)
            
        logging.info("Transcribing (this may take a while)...")
        segments = autosubber.transcribe_audio(audio_path, src_lang, model_name)
        
        logging.info("Translating...")
        translated_segments = autosubber.translate_segments(segments, src_lang, tgt_lang)
        
        logging.info("Saving SRT...")
        autosubber.generate_srt(translated_segments, srt_path)
        
        logging.info("Saving TXT...")
        autosubber.save_transcription_txt(translated_segments, txt_path)
        
        if not is_audio:
            logging.info("Burning subtitles into video...")
            autosubber.embed_subtitles(input_path, srt_path, output_video_path)
            logging.info("Done! Video created.")
        else:
             logging.info("Done! Audio input processed (SRT/TXT only).")

        # Cleanup temp audio
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        logging.info("PROCESS_COMPLETE") # Signal frontend
        
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())

@app.route('/stream_logs')
def stream_logs():
    def generate():
        while True:
            try:
                # Use a small timeout to allow checking for client disconnect triggers or app shutdown
                message = log_queue.get(timeout=1.0)
                yield f"data: {message}\n\n"
            except queue.Empty:
                # Send a keep-alive comment so the connection doesn't drop
                yield ": keep-alive\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
