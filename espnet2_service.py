from flask import Flask, request, jsonify,send_file
import mysql.connector
from espnet2.bin.tts_inference import Text2Speech
import torch
import soundfile as sf
import uuid
import os

# English model is loaded by default
fs, lang = 44100, "English"
text2speech_en = Text2Speech.from_pretrained(
    model_tag="kan-bayashi/ljspeech_vits",
    device="cpu",  # or "cuda"
    speed_control_alpha=1.0,
    noise_scale=0.333,
    noise_scale_dur=0.333,
)

#tag = 'kan-bayashi/jsut_full_band_vits_prosody'(girl) #@param ["kan-bayashi/jsut_tacotron2", "kan-bayashi/jsut_transformer", "kan-bayashi/jsut_fastspeech", "kan-bayashi/jsut_fastspeech2", "kan-bayashi/jsut_conformer_fastspeech2", "kan-bayashi/jsut_conformer_fastspeech2_accent", "kan-bayashi/jsut_conformer_fastspeech2_accent_with_pause", "kan-bayashi/jsut_vits_accent_with_pause", "kan-bayashi/jsut_full_band_vits_accent_with_pause", "kan-bayashi/jsut_tacotron2_prosody", "kan-bayashi/jsut_transformer_prosody", "kan-bayashi/jsut_conformer_fastspeech2_tacotron2_prosody", "kan-bayashi/jsut_vits_prosody", "kan-bayashi/jsut_full_band_vits_prosody", "kan-bayashi/jvs_jvs010_vits_prosody", "kan-bayashi/tsukuyomi_full_band_vits_prosody"] {type:"string"}
text2speech_ja = Text2Speech.from_pretrained(
    model_tag="kan-bayashi/jsut_full_band_vits_prosody", 
    device="cpu",  # or "cuda"
    speed_control_alpha=1.0,
    noise_scale=0.333,
    noise_scale_dur=0.333,
)


@app.route('/texttospeech', methods=['POST'])
def texttospeech():
    data = request.json
    input_text = data.get('text', '')
    lang = data.get('lang', 'English')

    print(input_text)
    print(lang)

    filename = str(uuid.uuid4())
    relative_path = f"{filename}.wav"
    output_path = os.path.join(output_folder, relative_path)

    with torch.no_grad():
        if lang == "en":
            wav = text2speech_en(input_text)["wav"]
            sf.write(output_path, wav.view(-1).cpu().numpy(), text2speech_en.fs)
        elif lang == "ja":
            wav = text2speech_ja(input_text)["wav"]
            sf.write(output_path, wav.view(-1).cpu().numpy(), text2speech_ja.fs)
        else:
            return jsonify({'error': 'Unsupported language'})

    # Return the path of the generated WAV file
    return jsonify({'audio_path': relative_path})


@app.route('/get_espnet_batch', methods=['POST'])
def get_espnet_batch():
    try:
        data = request.json
        file_path = data.get('file_path')
        lang = data.get('lang')
        input_text = data.get('text')
        print(input_text)

        output_folder = "/data/"
        relative_path = "gen_wav_esp/" + file_path

        output_path = os.path.join(output_folder, relative_path)

        with torch.no_grad():
            if lang == "en":
                wav = text2speech_en(input_text)["wav"]
                sf.write(output_path, wav.view(-1).cpu().numpy(), text2speech_en.fs)
            elif lang == "ja":
                wav = text2speech_ja(input_text)["wav"]
                sf.write(output_path, wav.view(-1).cpu().numpy(), text2speech_ja.fs)
            else:
                return jsonify({'error': 'Unsupported language'}), 400

            print("Generated WAV file path:", output_path)
            return jsonify({'audio_path': file_path}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
