# Flask ESPnet2 Text-to-Speech Service

This repository provides a Flask-based web service for converting text to speech in multiple languages using the ESPnet framework. It supports English and Japanese text-to-speech conversion, allowing users to generate audio files from text input.

## Features

- **Multi-language Support**: Convert text to speech in English and Japanese.
- **Audio File Generation**: Output audio files in WAV format.
- **REST API**: Simple endpoints for text-to-speech conversion.

## Requirements

- Python 3.7 or higher
- Flask
- ESPnet
- PyTorch
- SoundFile
- MySQL Connector

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/thisiscatcode/espnet2.git
   cd repo-name
   ```

2. **Install required packages**:
   ```bash
   pip install flask mysql-connector-python torch soundfile espnet
   ```

3. **Download ESPnet models** (if not already available):
   - [English Model](https://huggingface.co/kan-bayashi/ljspeech_vits)
   - [Japanese Model](https://huggingface.co/kan-bayashi/jsut_full_band_vits_prosody)

## Usage

1. **Run the Flask application**:
   ```bash
   python app.py
   ```

2. **Send a POST request to convert text to speech**:
   ```bash
   curl -X POST http://127.0.0.1:5000/texttospeech -H "Content-Type: application/json" -d '{"text": "Hello, world!", "lang": "English"}'
   ```

3. **Response**: The service will return a JSON object containing the path of the generated WAV file:
   ```json
   {
       "audio_path": "unique_filename.wav"
   }
   ```

## Endpoints

- **`/texttospeech`**: Converts text to speech. Accepts JSON with `text` and `lang` parameters.
- **`/get_espnet_batch`**: Generates audio files in batch mode based on input parameters.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests. If you encounter any issues or have suggestions, please open an issue.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- **ESPnet**: For providing state-of-the-art text-to-speech models.
- **Flask**: For creating the web service.
- **PyTorch**: For deep learning functionalities.
