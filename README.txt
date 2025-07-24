ffmpeg -i guaraná.webm -o guarana.wav

# separar vocais e instrumentos

https://vocalremover.org/pt/

guarana_vocals.mp3
guarana_instruments.mp3

# install Python

python3 --version

apt list -a python3-venv
sudo apt install python3-venv

python3 -m venv karaoke-venv
source karaoke-venv/bin/activate
pip install --upgrade pip
pip install git+https://github.com/m-bain/whisperx.git

install whisperx

# install niniconda

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash ~/Miniconda3-latest-Linux-x86_64.sh -p ~/miniconda3
rm Miniconda3-latest-Linux-x86_64.sh

# install mfa

source ~/miniconda3/bin/activate

conda install -c conda-forge montreal-forced-aligner
mfa version

mfa model download acoustic portuguese_mfa
mfa model download dictionary portuguese_mfa
mfa model download g2p portuguese_mfa

conda deactivate

# reconhecimento da letra

# whisperx guarana_vocals.mp3 --model large --language pt --align_model jonatasgrosman/wav2vec2-large-xlsr-53-portuguese --segment_resolution sentence
whisperx guarana_vocals.mp3 --model large --language pt

# ajustar/corrigir a letra manualmente

# converter e normalizar vocals para 16 kHz mono wav

ffmpeg -i guarana_vocals.mp3 -ac 1 -ar 16000 -af "dynaudnorm" guarana_vocals.wav

# criar estrutura para o MFA

./guarana/
./guarana/guarana_vocals.txt
./guarana/guarana_vocals.wav

# alinhamento forçado

mfa align guarana portuguese_mfa portuguese_mfa guarana_aligned --clean --verbose --beam 400 --retry_beam 800

./textGrid2json.py guarana_vocals.TextGrid  guarana_vocals.json
./restoreCase.py guarana_vocals.txt guarana_vocals.json guarana_vocals_restored.json
./json_to_ass.py guarana_vocals_restored.json guarana_vocals.ass

ffmpeg -loop 1 -i background.jpg -i guarana_instruments.mp3 -vf "ass=lyrics.ass" -c:v libx264 -preset veryfast -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest karaoke.mp4

# links

https://jsonformatter.org/
https://github.com/m-bain/whisperX
https://www.anaconda.com/docs/getting-started/miniconda/main
https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner

