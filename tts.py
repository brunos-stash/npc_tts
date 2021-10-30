import sys
from datetime import datetime
from pathlib import Path
from app.utils import *
from subprocess import Popen, PIPE
import shlex, re
try:
    from vits.synthesizer import Synthesizer

    synthesizer = Synthesizer(TTS_CONFIG_PATH)

    if TTS_MODEL_PATH.exists():
        synthesizer.load_model(TTS_MODEL_PATH)
    else:
        download_model("G_600000.pth")
        synthesizer.load_model(TTS_MODEL_PATH)

    synthesizer.init_speaker_map(SPEAKER_CONFIG)

except ImportError as err:
    print(err)

def synthesize(text, variance_a='0.35', variance_b='0.5', speed='1.3'):
    _var_a = float(variance_a)
    _var_b = float(variance_b)
    _speed = float(speed)
    _var_a = 0 if _var_a < 0 else _var_a
    _var_a = 1.1 if _var_a > 1.1 else _var_a
    _var_b = 0 if _var_b < 0 else _var_b
    _var_b = 0.9 if _var_b > 0.9 else _var_b
    _speed = 0.2 if _speed < 0.2 else _speed
    _speed = 5 if _speed > 5 else _speed
    var_a = str(_var_a)
    var_b = str(_var_b)
    speed = str(_speed)
    print(f'a: {var_a}, b: {var_b}, speed: {speed}')
    _params = {'speaker_id': '47',
        'speaker_name': 'Christian Wewerka',
        'text_selected': 'true',
        'out_path_use': False,
        'speech_speed': speed,
        'speech_var_a': var_a,
        'speech_var_b': var_b,
        'file_export_ext': 'wav',
        'text': text,
        'file_content': None,
        'out_path': None}
    audio_data = synthesizer.synthesize(text, _params['speaker_id'], _params)
    cur_timestamp = datetime.now().strftime("%m%d%f")
    tmp_path = Path("data/speech")

    if not tmp_path.exists():
        tmp_path.mkdir()

    file_name = "_".join(
        [str(_params['speaker_id']), _params['speaker_name'], str(cur_timestamp), "tmp_file"]
    )
    file_path = save_audio(tmp_path, file_name, audio_data)

    if _params["out_path"]:
        save_file_name = "_".join([cur_timestamp, _params['speaker_id'], _params['speaker_name'], text[:15]])
        save_file_path = Path(_params["out_path"])
        file_path = save_audio(
            save_file_path, save_file_name, audio_data, _params["file_export_ext"]
        )
    return file_path

def add_padding(file_path: Path, background_path: Path):
    cmd = f'ffmpeg -i "{str(background_path)}" -i "{str(file_path)}" -filter_complex "[1]volume=volume=3.0[speech];[0]volume=volume=0.5[npc];[speech]adelay=1500ms|1500ms[speech];[speech]apad=pad_len=75000[speech];[npc][speech]amix=duration=shortest" data/output/out.mp3 -y'
    args = shlex.split(cmd)
    with Popen(args, stdout=PIPE) as proc:
        print(proc.stdout.read())
    return Path('data/output/out.mp3')


# def regtest(text):
#     try:
#         match = re.search("\s-a\s(\d+(\.\d+)?)",text)
#         var_a = match.group(1)
#         text = text.replace(match.group(0), "")
#     except:
#         pass
#     try:
#         match = re.search("\s-b\s(\d+(\.\d+)?)",text)
#         var_b = match.group(1)
#         text = text.replace(match.group(0), "")
#     except:
#         pass
#     try:
#         match = re.search("\s-speed\s(\d+(\.\d+)?)",text)
#         speed = match.group(1)
#         text = text.replace(match.group(0), "")
#     except:
#         pass
#     print(text)

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     raise Exception("needs text")
    # text = sys.argv[1]
    text = " -a 34 -b 994009 -speed 3.434. fkkl lekj"
    text = " -b 994009 -speed 39 fkjekfjkl -speed 3.434fkkl lekj"

    # regtest(f'"{text}"')
    # background = Path('data/background/npc.mp3')
    # fp = synthesize(text, variance_a='3', variance_b='3', speed='7')
    # add_padding(fp, background)