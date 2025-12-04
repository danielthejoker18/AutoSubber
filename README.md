```markdown
# AutoSubber: Automatic Video Subtitle Generator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

AutoSubber is a local Python tool that automatically generates timed subtitles for any video by transcribing the audio, translating the text to a selected language, and embedding the subtitles back into the video (optional). It uses open-source AI models for transcription (OpenAI's Whisper) and translation (Facebook's M2M100), making it privacy-friendly and cost-free to run on your machine.

Perfect for making videos accessible across languages—great for movies, lectures, or personal projects. Runs entirely offline after model downloads, leveraging your GPU for speed.

### Features
- **Audio Transcription**: Extracts audio from video (or uses audio files directly) and transcribes it with accurate timestamps using Whisper.
- **Multi-Language Translation**: Translates transcripts to 100+ languages.
- **Subtitle & Text Generation**: Outputs standard SRT files and plain text (TXT) transcriptions.
- **Video Embedding**: Optionally burns subtitles into a new video file.
- **GPU Acceleration**: Optimized for NVIDIA GPUs for fast processing.
- **Simple CLI**: Easy command-line usage—no GUI needed.

## Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/danielthejoker18/AutoSubber.git
   cd auto-subber
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.8+ installed. Then, install the required packages:
   ```
   pip install -r requirements.txt
   ```

   Note: For GPU support, install PyTorch with CUDA:
   ```
   pip install torch --index-url https://download.pytorch.org/whl/cu121  # Adjust for your CUDA version
   ```

3. **Install FFmpeg**:
   FFmpeg is required for audio extraction and video processing. Download and install it:
   - **Windows**: Use [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
   - **macOS**: Use [Homebrew](https://brew.sh/): `brew install ffmpeg`
   - **Linux**: `sudo apt update && sudo apt install ffmpeg` (Ubuntu/Debian)

   Verify installation: `ffmpeg -version`

4. **Model Downloads**:
   The first run will automatically download the Whisper and M2M100 models from Hugging Face (~1-2GB total). Ensure you have an internet connection for this step.

## Usage

Run the script from the command line:

```
python main.py <input_file> <output> <src_lang> <tgt_lang> [--srt-only]
```

- `<input_file>`: Path to your input video or audio file (e.g., `movie.mp4`, `interview.mp3`).
- `<output>`: Path to the output file. If `--srt-only` is used or input is audio, this is the base name for the `.srt` and `.txt` files. Otherwise, it's the path to the output video with embedded subtitles.
- `<src_lang>`: Source language code (e.g., `en` for English).
- `<tgt_lang>`: Target language code (e.g., `fr` for French).
- `--srt-only` (optional): If specified, the script will only generate the SRT subtitle file and will not embed it into the video.

### Language Variants
The script can handle language variants like `pt-br` (Brazilian Portuguese) and `pt-pt` (European Portuguese) by mapping them to their base language code (e.g., `pt`).

### Examples

**Generate a subtitled video:**
```
python main.py video.mp4 video_subbed.mp4 en es
```
This transcribes English audio from `video.mp4`, translates it to Spanish, and creates a new video file `video_subbed.mp4` with the subtitles embedded.

**Generate an SRT file only:**
```
python main.py video.mp4 video_subbed en es --srt-only
```
This transcribes and translates the video, but only saves the Spanish subtitles to `video_subbed.srt` and transcription to `video_subbed.txt`. No video will be created.

**Transcribe an audio file:**
```
python main.py interview.mp3 interview_transcribed en en
```
This transcribes the English audio `interview.mp3` and saves the result to `interview_transcribed.srt` and `interview_transcribed.txt`.

## How It Works

AutoSubber supports multilingual transcription via Whisper (for source languages) and translation via M2M100 (for target languages). Use the 2-letter ISO 639-1 codes listed below when specifying `<src_lang>` and `<tgt_lang>`. For language variants (e.g., Brazilian Portuguese `pt-br`), map to the closest supported code (e.g., `pt` for Portuguese). Performance may vary based on audio quality and accents.

### Transcription Languages (Whisper)
Whisper supports transcription in ~99 languages. The model auto-detects the language if not specified, but providing `<src_lang>` improves accuracy.

| Code | Language          | Code | Language          | Code | Language          |
|------|-------------------|------|-------------------|------|-------------------|
| af   | Afrikaans        | am   | Amharic          | ar   | Arabic           |
| as   | Assamese         | az   | Azerbaijani      | ba   | Bashkir          |
| be   | Belarusian       | bg   | Bulgarian        | bn   | Bengali          |
| bo   | Tibetan          | br   | Breton           | bs   | Bosnian          |
| ca   | Catalan          | cs   | Czech            | cy   | Welsh            |
| da   | Danish           | de   | German           | el   | Greek            |
| en   | English          | es   | Spanish          | et   | Estonian         |
| eu   | Basque           | fa   | Persian          | fi   | Finnish          |
| fo   | Faroese          | fr   | French           | gl   | Galician         |
| gu   | Gujarati         | ha   | Hausa            | haw  | Hawaiian         |
| he   | Hebrew           | hi   | Hindi            | hr   | Croatian         |
| ht   | Haitian Creole   | hu   | Hungarian        | hy   | Armenian         |
| id   | Indonesian       | is   | Icelandic        | it   | Italian          |
| ja   | Japanese         | jw   | Javanese         | ka   | Georgian         |
| kk   | Kazakh           | km   | Khmer            | kn   | Kannada          |
| ko   | Korean           | la   | Latin            | lb   | Luxembourgish    |
| ln   | Lingala          | lo   | Lao              | lt   | Lithuanian       |
| lv   | Latvian          | mg   | Malagasy         | mi   | Maori            |
| mk   | Macedonian       | ml   | Malayalam        | mn   | Mongolian        |
| mr   | Marathi          | ms   | Malay            | mt   | Maltese          |
| my   | Myanmar          | ne   | Nepali           | nl   | Dutch            |
| nn   | Norwegian Nynorsk| no   | Norwegian        | oc   | Occitan          |
| pa   | Punjabi          | pl   | Polish           | ps   | Pashto           |
| pt   | Portuguese       | ro   | Romanian         | ru   | Russian          |
| sa   | Sanskrit         | sd   | Sindhi           | si   | Sinhala          |
| sk   | Slovak           | sl   | Slovenian        | sn   | Shona            |
| so   | Somali           | sq   | Albanian         | sr   | Serbian          |
| su   | Sundanese        | sv   | Swedish          | sw   | Swahili          |
| ta   | Tamil            | te   | Telugu           | tg   | Tajik            |
| th   | Thai             | tk   | Turkmen          | tl   | Tagalog          |
| tr   | Turkish          | tt   | Tatar            | uk   | Ukrainian        |
| ur   | Urdu             | uz   | Uzbek            | vi   | Vietnamese       |
| yi   | Yiddish          | yo   | Yoruba           | zh   | Chinese          |
| yue  | Cantonese        |      |                  |      |                  |

### Translation Languages (M2M100)
M2M100 supports translation to/from 100 languages.

| Code | Language                  | Code | Language                  | Code | Language                  |
|------|---------------------------|------|---------------------------|------|---------------------------|
| af   | Afrikaans                | am   | Amharic                  | ar   | Arabic                   |
| ast  | Asturian                 | az   | Azerbaijani              | ba   | Bashkir                  |
| be   | Belarusian               | bg   | Bulgarian                | bn   | Bengali                  |
| br   | Breton                   | bs   | Bosnian                  | ca   | Catalan; Valencian       |
| ceb  | Cebuano                  | cs   | Czech                    | cy   | Welsh                    |
| da   | Danish                   | de   | German                   | el   | Greek                    |
| en   | English                  | es   | Spanish                  | et   | Estonian                 |
| fa   | Persian                  | ff   | Fulah                    | fi   | Finnish                  |
| fr   | French                   | fy   | Western Frisian          | ga   | Irish                    |
| gd   | Gaelic; Scottish Gaelic  | gl   | Galician                 | gu   | Gujarati                 |
| ha   | Hausa                    | he   | Hebrew                   | hi   | Hindi                    |
| hr   | Croatian                 | ht   | Haitian; Haitian Creole  | hu   | Hungarian                |
| hy   | Armenian                 | id   | Indonesian               | ig   | Igbo                     |
| ilo  | Iloko                    | is   | Icelandic                | it   | Italian                  |
| ja   | Japanese                 | jv   | Javanese                 | ka   | Georgian                 |
| kk   | Kazakh                   | km   | Central Khmer            | kn   | Kannada                  |
| ko   | Korean                   | lb   | Luxembourgish            | lg   | Ganda                    |
| ln   | Lingala                  | lo   | Lao                      | lt   | Lithuanian               |
| lv   | Latvian                  | mg   | Malagasy                 | mk   | Macedonian               |
| ml   | Malayalam                | mn   | Mongolian                | mr   | Marathi                  |
| ms   | Malay                    | my   | Burmese                  | ne   | Nepali                   |
| nl   | Dutch; Flemish           | no   | Norwegian                | ns   | Northern Sotho           |
| oc   | Occitan (post 1500)      | or   | Oriya                    | pa   | Panjabi; Punjabi         |
| pl   | Polish                   | ps   | Pushto; Pashto           | pt   | Portuguese               |
| ro   | Romanian                 | ru   | Russian                  | sd   | Sindhi                   |
| si   | Sinhala; Sinhalese       | sk   | Slovak                   | sl   | Slovenian                |
| so   | Somali                   | sq   | Albanian                 | sr   | Serbian                  |
| ss   | Swati                    | su   | Sundanese                | sv   | Swedish                  |
| sw   | Swahili                  | ta   | Tamil                    | th   | Thai                     |
| tl   | Tagalog                  | tn   | Tswana                   | tr   | Turkish                  |
| uk   | Ukrainian                | ur   | Urdu                     | uz   | Uzbek                    |
| vi   | Vietnamese               | wo   | Wolof                    | xh   | Xhosa                    |
| yi   | Yiddish                  | yo   | Yoruba                   | zh   | Chinese                  |
| zu   | Zulu                     |      |                          |      |                          |

## How It Works
1. **Extract Audio**: Uses FFmpeg to pull audio from the video.
2. **Transcribe**: Whisper processes the full audio, generating segments with timestamps.
3. **Translate**: M2M100 translates each segment to the target language.
4. **Generate SRT**: Creates a subtitle file using pysrt.
5. **Embed Subtitles**: FFmpeg burns the subtitles into a new video.

Processing a 2-hour movie on a RTX 4070 Ti typically takes 5-15 minutes.

## Limitations & Improvements
- **Accuracy**: Whisper excels in clear audio; noisy or accented speech may need manual tweaks.
- **Languages**: Check the lists above for support; test with your specific languages.
- **Large Files**: Handles full movies well on GPU; if VRAM issues arise, switch to `whisper-small`.
- **Enhancements**: 
  - Add auto-language detection.
  - Support batch processing.
  - Integrate a simple GUI (e.g., with Tkinter).

Contributions welcome! Fork and PR.

## Troubleshooting
- **FFmpeg Not Found**: Ensure it's in your PATH.
- **Model Loading Errors**: Check internet for downloads; retry if interrupted.
- **VRAM Out of Memory**: Use a smaller Whisper model (edit `model="openai/whisper-small"`).
- **Language Codes**: Use standard ISO codes. List available in model docs.

For issues, open a GitHub issue with error logs.

## License
MIT License. Feel free to use, modify, and distribute.

## Acknowledgments
- Powered by [Whisper](https://huggingface.co/openai/whisper-medium) for transcription.
- [M2M100](https://huggingface.co/facebook/m2m100_418M) for translation.
- Thanks to FFmpeg and Hugging Face for amazing tools.

Built with ❤️ by Daniel. Star the repo if it helps! 🚀
---
# AutoSubber: Gerador Automático de Legendas para Vídeos

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Visão Geral

AutoSubber é uma ferramenta local em Python que gera automaticamente legendas cronometradas para qualquer vídeo, transcrevendo o áudio, traduzindo o texto para um idioma selecionado e embutindo as legendas de volta no vídeo (opcional). Utiliza modelos de IA de código aberto para transcrição (Whisper da OpenAI) e tradução (M2M100 do Facebook), tornando-o amigável à privacidade e sem custos para executar na sua máquina.

Perfeito para tornar vídeos acessíveis em vários idiomas—ótimo para filmes, palestras ou projetos pessoais. Executa totalmente offline após o download dos modelos, aproveitando sua GPU para velocidade.

### Funcionalidades
- **Transcrição de Áudio**: Extrai áudio do vídeo (ou usa arquivos de áudio diretamente) e transcreve com timestamps precisos usando Whisper.
- **Tradução Multi-Idioma**: Traduz transcrições para mais de 100 idiomas.
- **Geração de Legendas e Texto**: Gera arquivos SRT padrão e transcrições em texto simples (TXT).
- **Embutir no Vídeo**: Opcionalmente, embute legendas em um novo arquivo de vídeo.
- **Aceleração por GPU**: Otimizado para GPUs NVIDIA para processamento rápido.
- **CLI Simples**: Uso fácil via linha de comando—sem GUI necessária.

## Instalação

1. **Clone o Repositório**:
   ```
   git clone https://github.com/danielthejoker18/AutoSubber.git
   cd auto-subber
   ```

2. **Instale as Dependências**:
   Garanta que você tenha o Python 3.8+ instalado. Em seguida, instale os pacotes necessários:
   ```
   pip install -r requirements.txt
   ```

   Nota: Para suporte a GPU, instale o PyTorch com CUDA:
   ```
   pip install torch --index-url https://download.pytorch.org/whl/cu121  # Ajuste para sua versão de CUDA
   ```

3. **Instale o FFmpeg**:
   O FFmpeg é necessário para extração de áudio e processamento de vídeo. Baixe e instale:
   - **Windows**: Use [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
   - **macOS**: Use [Homebrew](https://brew.sh/): `brew install ffmpeg`
   - **Linux**: `sudo apt update && sudo apt install ffmpeg` (Ubuntu/Debian)

   Verifique a instalação: `ffmpeg -version`

4. **Download dos Modelos**:
   A primeira execução fará o download automático dos modelos Whisper e M2M100 do Hugging Face (~1-2GB no total). Garanta uma conexão com a internet para este passo.

## Uso

Execute o script pela linha de comando:

```
python main.py <arquivo_entrada> <saida> <idioma_origem> <idioma_destino> [--srt-only]
```

- `<arquivo_entrada>`: Caminho para o seu arquivo de vídeo ou áudio de entrada (ex: `filme.mp4`, `entrevista.mp3`).
- `<saida>`: Caminho para o arquivo de saída. Se `--srt-only` for usado ou a entrada for áudio, este é o nome base para os arquivos `.srt` e `.txt`. Caso contrário, é o caminho para o vídeo de saída com as legendas embutidas.
- `<idioma_origem>`: Código do idioma de origem (ex: `en` para inglês).
- `<idioma_destino>`: Código do idioma de destino (ex: `fr` para francês).
- `--srt-only` (opcional): Se especificado, o script irá gerar apenas o arquivo de legenda SRT e não o embutirá no vídeo.

### Variantes de Idioma
O script pode lidar com variantes de idioma como `pt-br` (Português Brasileiro) e `pt-pt` (Português Europeu), mapeando-os para o código de idioma base (ex: `pt`).

### Exemplos

**Gerar um vídeo legendado:**
```
python main.py video.mp4 video_legendado.mp4 en es
```
Este comando transcreve o áudio em inglês de `video.mp4`, traduz para espanhol e cria um novo arquivo de vídeo `video_legendado.mp4` com as legendas embutidas.

**Gerar apenas um arquivo SRT:**
```
python main.py video.mp4 video_legendado en es --srt-only
```
Este comando transcreve e traduz o vídeo, mas salva apenas as legendas em espanhol em `video_legendado.srt` e a transcrição em `video_legendado.txt`. Nenhum vídeo será criado.

**Transcrever um arquivo de áudio:**
```
python main.py entrevista.mp3 entrevista_transcrita en en
```
Este comando transcreve o áudio em inglês `entrevista.mp3` e salva o resultado em `entrevista_transcrita.srt` e `entrevista_transcrita.txt`.

## Como Funciona

O AutoSubber suporta transcrição multilíngue via Whisper (para idiomas de origem) e tradução via M2M100 (para idiomas de destino). Use os códigos ISO 639-1 de 2 letras listados abaixo ao especificar `<idioma_origem>` e `<idioma_destino>`. Para variantes de idiomas (ex: Português Brasileiro `pt-br`), mapeie para o código suportado mais próximo (ex: `pt` para Português). O desempenho pode variar com base na qualidade do áudio e sotaques.

### Linguagens de Transcrição (Whisper)
O Whisper suporta transcrição em ~99 idiomas. O modelo detecta automaticamente o idioma se não especificado, mas fornecer `<idioma_origem>` melhora a precisão.

| Código | Idioma            | Código | Idioma            | Código | Idioma            |
|--------|-------------------|--------|-------------------|--------|-------------------|
| af     | Africâner        | am     | Amárico          | ar     | Árabe            |
| as     | Assamês          | az     | Azerbaijano      | ba     | Bashkir          |
| be     | Bielorrusso      | bg     | Búlgaro          | bn     | Bengali          |
| bo     | Tibetano         | br     | Bretão           | bs     | Bósnio           |
| ca     | Catalão          | cs     | Tcheco           | cy     | Galês            |
| da     | Dinamarquês      | de     | Alemão           | el     | Grego            |
| en     | Inglês           | es     | Espanhol         | et     | Estoniano        |
| eu     | Basco            | fa     | Persa            | fi     | Finlandês        |
| fo     | Faroês           | fr     | Francês          | gl     | Galego           |
| gu     | Gujarati         | ha     | Hauçá            | haw    | Havaiano         |
| he     | Hebraico         | hi     | Hindi            | hr     | Croata           |
| ht     | Crioulo Haitiano | hu     | Húngaro          | hy     | Armênio          |
| id     | Indonésio        | is     | Islandês         | it     | Italiano         |
| ja     | Japonês          | jw     | Javanês          | ka     | Georgiano        |
| kk     | Cazaque          | km     | Khmer            | kn     | Canarês          |
| ko     | Coreano          | la     | Latim            | lb     | Luxemburguês     |
| ln     | Lingala          | lo     | Laosiano         | lt     | Lituano          |
| lv     | Letão            | mg     | Malgaxe          | mi     | Maori            |
| mk     | Macedônio        | ml     | Malaiala         | mn     | Mongol           |
| mr     | Marati           | ms     | Malaio           | mt     | Maltês           |
| my     | Birmanês         | ne     | Nepalês          | nl     | Holandês         |
| nn     | Norueguês Nynorsk| no     | Norueguês        | oc     | Occitano         |
| pa     | Punjabi          | pl     | Polonês          | ps     | Pashto           |
| pt     | Português        | ro     | Romeno           | ru     | Russo            |
| sa     | Sânscrito        | sd     | Sindi            | si     | Cingalês         |
| sk     | Eslovaco         | sl     | Esloveno         | sn     | Shona            |
| so     | Somali           | sq     | Albanês          | sr     | Sérvio           |
| su     | Sundanês         | sv     | Sueco            | sw     | Suaíli           |
| ta     | Tâmil            | te     | Telugu           | tg     | Tadjique         |
| th     | Tailandês        | tk     | Turcomeno        | tl     | Tagalo           |
| tr     | Turco            | tt     | Tártaro          | uk     | Ucraniano        |
| ur     | Urdu             | uz     | Usbeque          | vi     | Vietnamita       |
| yi     | Iídiche          | yo     | Iorubá           | zh     | Chinês           |
| yue    | Cantonês         |        |                  |        |                  |

### Linguagens de Tradução (M2M100)
O M2M100 suporta tradução para/de 100 idiomas.

| Código | Idioma                    | Código | Idioma                    | Código | Idioma                    |
|--------|---------------------------|--------|---------------------------|--------|---------------------------|
| af     | Africâner                | am     | Amárico                  | ar     | Árabe                    |
| ast    | Asturiano                | az     | Azerbaijano              | ba     | Bashkir                  |
| be     | Bielorrusso              | bg     | Búlgaro                  | bn     | Bengali                  |
| br     | Bretão                   | bs     | Bósnio                   | ca     | Catalão; Valenciano      |
| ceb    | Cebuano                  | cs     | Tcheco                   | cy     | Galês                    |
| da     | Dinamarquês              | de     | Alemão                   | el     | Grego                    |
| en     | Inglês                   | es     | Espanhol                 | et     | Estoniano                |
| fa     | Persa                    | ff     | Fula                     | fi     | Finlandês                |
| fr     | Francês                  | fy     | Frísio Ocidental         | ga     | Irlandês                 |
| gd     | Gaélico; Gaélico Escocês | gl     | Galego                   | gu     | Gujarati                 |
| ha     | Hauçá                    | he     | Hebraico                 | hi     | Hindi                    |
| hr     | Croata                   | ht     | Haitiano; Crioulo Haitiano| hu     | Húngaro                  |
| hy     | Armênio                  | id     | Indonésio                | ig     | Igbo                     |
| ilo    | Ilocano                  | is     | Islandês                 | it     | Italiano                 |
| ja     | Japonês                  | jv     | Javanês                  | ka     | Georgiano                |
| kk     | Cazaque                  | km     | Khmer Central            | kn     | Canarês                  |
| ko     | Coreano                  | lb     | Luxemburguês             | lg     | Ganda                    |
| ln     | Lingala                  | lo     | Laosiano                 | lt     | Lituano                  |
| lv     | Letão                    | mg     | Malgaxe                  | mk     | Macedônio                |
| ml     | Malaiala                 | mn     | Mongol                   | mr     | Marati                   |
| ms     | Malaio                   | my     | Birmanês                 | ne     | Nepalês                  |
| nl     | Holandês; Flamengo       | no     | Norueguês                | ns     | Sotho do Norte           |
| oc     | Occitano (pós 1500)      | or     | Oriá                     | pa     | Panjabi; Punjabi         |
| pl     | Polonês                  | ps     | Pushto; Pashto           | pt     | Português                |
| ro     | Romeno                   | ru     | Russo                    | sd     | Sindi                    |
| si     | Cingalês; Sinhala        | sk     | Eslovaco                 | sl     | Esloveno                 |
| so     | Somali                   | sq     | Albanês                  | sr     | Sérvio                   |
| ss     | Suazi                    | su     | Sundanês                 | sv     | Sueco                    |
| sw     | Suaíli                   | ta     | Tâmil                    | th     | Tailandês                |
| tl     | Tagalo                   | tn     | Tsuana                   | tr     | Turco                    |
| uk     | Ucraniano                | ur     | Urdu                     | uz     | Usbeque                  |
| vi     | Vietnamita               | wo     | Uolofe                   | xh     | Xhosa                    |
| yi     | Iídiche                  | yo     | Iorubá                   | zh     | Chinês                   |
| zu     | Zulu                     |        |                          |        |                          |

## Como Funciona
1. **Extrai o Áudio**: Usa o FFmpeg para extrair áudio do vídeo.
2. **Transcreve**: O Whisper processa o áudio completo, gerando segmentos com timestamps.
3. **Traduz**: O M2M100 traduz cada segmento para o idioma de destino.
4. **Gera SRT**: Cria um arquivo de legenda usando pysrt.
5. **Embute Legendas**: O FFmpeg embute as legendas em um novo vídeo.

Processar um filme de 2 horas em uma RTX 4070 Ti geralmente leva 5-15 minutos.

## Limitações & Melhorias
- **Precisão**: O Whisper se destaca em áudio claro; áudio ruidoso ou com sotaques pode precisar de ajustes manuais.
- **Idiomas**: Verifique as listas acima para suporte; teste com seus idiomas específicos.
- **Arquivos Grandes**: Lida bem com filmes completos em GPU; se houver problemas de VRAM, mude para `whisper-small`.
- **Melhorias**:
  - Adicionar detecção automática de idioma.
  - Suporte a processamento em lote.
  - Integrar uma GUI simples (ex: com Tkinter).

Contribuições bem-vindas! Fork e PR.

## Solução de Problemas
- **FFmpeg Não Encontrado**: Garanta que esteja no PATH.
- **Erros de Carregamento de Modelos**: Verifique a internet para downloads; tente novamente se interrompido.
- **Memória VRAM Insuficiente**: Use um modelo Whisper menor (edite `model="openai/whisper-small"`).
- **Códigos de Idioma**: Use códigos ISO padrão. Lista disponível na documentação dos modelos.

Para problemas, abra uma issue no GitHub com logs de erro.

## Licença
Licença MIT. Sinta-se livre para usar, modificar e distribuir.

## Agradecimentos
- Alimentado por [Whisper](https://huggingface.co/openai/whisper-medium) para transcrição.
- [M2M100](https://huggingface.co/facebook/m2m100_418M) para tradução.
- Graças ao FFmpeg e Hugging Face por ferramentas incríveis.

Construído com ❤️ por Daniel. Dê uma estrela no repo se ajudar! 🚀
````