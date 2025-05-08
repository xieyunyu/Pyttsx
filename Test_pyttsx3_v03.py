"""
pip install scipy
pip install pyttsx3
pip install pydub
pip install numpy
pip install simpleaudio
"""
#---------------------------------------
"""
import pyttsx3 # type: ignore

# 初始化語音引擎
engine = pyttsx3.init()

# 選擇女聲（根據系統可用語音調整索引）
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 替換為合適的語音索引

# 設置溫柔語音參數
engine.setProperty('rate', 180)  # 稍慢的語速
engine.setProperty('volume', 0.8)  # 柔和的音量

# 測試語音
engine.say("你好，我是小智，我會講台灣狗已")
engine.runAndWait()

for voice in voices:
    print('id = {} \nname = {} \n'.format(voice.id, voice.name))
"""
#-------------------------------------------------------------------------

from pydub import AudioSegment
import pyttsx3
import tempfile
import os

def text_to_speech(text, rate=150, pitch=20):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('pitch', pitch)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        engine.save_to_file(text, tmp_file.name)
        engine.runAndWait()
        temp_file_name = tmp_file.name
    return temp_file_name

def adjust_pitch(audio_file, semitones):
    sound = AudioSegment.from_wav(audio_file)
    new_sample_rate = int(sound.frame_rate * (2**(semitones/12.0)))
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_sound = pitched_sound.set_frame_rate(sound.frame_rate)
    return pitched_sound

text = "你好，我是小智，我會講台灣狗已"
temp_audio_file = text_to_speech(text)

# 嘗試升高音高 (半音)
pitched_audio = adjust_pitch(temp_audio_file, 2)
pitched_audio.export("pitched_output.wav", format="wav")

os.remove(temp_audio_file)


#-------------------------------------------------------------------------

from pydub import AudioSegment
from scipy.signal import convolve
import numpy as np

# ... (text_to_speech 函式同上) ...

text = "你好，我是小智，我會講台灣狗已"
temp_audio_file = text_to_speech(text)

sound = AudioSegment.from_wav(temp_audio_file)
# 加入混響效果 (自定義實現)
def apply_reverb(audio_segment, decay=0.5):
    samples = np.array(audio_segment.get_array_of_samples())
    impulse_response = np.zeros(int(audio_segment.frame_rate * 0.5))
    impulse_response[0] = 1
    for i in range(1, len(impulse_response)):
        impulse_response[i] = impulse_response[i - 1] * decay
    reverbed_samples = convolve(samples, impulse_response, mode='full')[:len(samples)]
    reverbed_samples = np.clip(reverbed_samples, -2**15, 2**15 - 1).astype(np.int16)
    return audio_segment._spawn(reverbed_samples.tobytes())

reverbed_sound = apply_reverb(sound)
reverbed_sound.export("reverbed_output.wav", format="wav")

os.remove(temp_audio_file)
"""
pip install scipy
pip install pyttsx3
pip install pydub
pip install numpy
pip install simpleaudio
"""
#---------------------------------------
"""
import pyttsx3 # type: ignore

# 初始化語音引擎
engine = pyttsx3.init()

# 選擇女聲（根據系統可用語音調整索引）
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 替換為合適的語音索引

# 設置溫柔語音參數
engine.setProperty('rate', 180)  # 稍慢的語速
engine.setProperty('volume', 0.8)  # 柔和的音量

# 測試語音
engine.say("你好，我是小智，我會講台灣狗已")
engine.runAndWait()

for voice in voices:
    print('id = {} \nname = {} \n'.format(voice.id, voice.name))
"""
#-------------------------------------------------------------------------

from pydub import AudioSegment
import pyttsx3
import tempfile
import os

def text_to_speech(text, rate=150, pitch=20):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('pitch', pitch)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        engine.save_to_file(text, tmp_file.name)
        engine.runAndWait()
        temp_file_name = tmp_file.name
    return temp_file_name

def adjust_pitch(audio_file, semitones):
    sound = AudioSegment.from_wav(audio_file)
    new_sample_rate = int(sound.frame_rate * (2**(semitones/12.0)))
    pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    pitched_sound = pitched_sound.set_frame_rate(sound.frame_rate)
    return pitched_sound

text = "你好，我是小智，我會講台灣狗已"
temp_audio_file = text_to_speech(text)

# 嘗試升高音高 (半音)
pitched_audio = adjust_pitch(temp_audio_file, 2)
pitched_audio.export("pitched_output.wav", format="wav")

os.remove(temp_audio_file)


#-------------------------------------------------------------------------

from pydub import AudioSegment
from scipy.signal import convolve
import numpy as np

# ... (text_to_speech 函式同上) ...

text = "你好，我是小智，我會講台灣狗已"
temp_audio_file = text_to_speech(text)

sound = AudioSegment.from_wav(temp_audio_file)
# 加入混響效果 (自定義實現)
def apply_reverb(audio_segment, decay=0.5):
    samples = np.array(audio_segment.get_array_of_samples())
    impulse_response = np.zeros(int(audio_segment.frame_rate * 0.5))
    impulse_response[0] = 1
    for i in range(1, len(impulse_response)):
        impulse_response[i] = impulse_response[i - 1] * decay
    reverbed_samples = convolve(samples, impulse_response, mode='full')[:len(samples)]
    reverbed_samples = np.clip(reverbed_samples, -2**15, 2**15 - 1).astype(np.int16)
    return audio_segment._spawn(reverbed_samples.tobytes())

reverbed_sound = apply_reverb(sound)
reverbed_sound.export("reverbed_output.wav", format="wav")

os.remove(temp_audio_file)
