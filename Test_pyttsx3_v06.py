import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
from scipy.signal import convolve
import numpy as np
import random
import time
import tempfile
import os

def text_to_speech(text, rate=95, volume=0.8):
    """
    使用 pyttsx3 生成 WAV 檔案，固定 Voice 0 (Hanhan)。
    
    參數：
        text (str): 要轉換的文本。
        rate (int): 語速（默認 95）。
        volume (float): 音量（默認 0.8）。
    
    返回：
        str: 臨時 WAV 檔案路徑。
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 固定 Hanhan
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        engine.save_to_file(text, tmp_file.name)
        engine.runAndWait()
        temp_file_name = tmp_file.name
    return temp_file_name

def adjust_pitch(audio_segment, semitones):
    """
    調整音高，模擬成熟女聲。
    
    參數：
        audio_segment (AudioSegment): 音訊對象。
        semitones (float): 半音數（正數升高，負數降低）。
    
    返回：
        AudioSegment: 調整後的音訊。
    """
    new_sample_rate = int(audio_segment.frame_rate * (2**(semitones/12.0)))
    pitched_sound = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
    return pitched_sound.set_frame_rate(audio_segment.frame_rate)

def apply_reverb(audio_segment, decay=0.2):
    """
    加入輕微混響，增加溫暖感。
    
    參數：
        audio_segment (AudioSegment): 音訊對象。
        decay (float): 混響衰減係數（默認 0.2）。
    
    返回：
        AudioSegment: 加入混響的音訊。
    """
    samples = np.array(audio_segment.get_array_of_samples())
    impulse_response = np.zeros(int(audio_segment.frame_rate * 0.2))  # 縮短混響時間
    impulse_response[0] = 1
    for i in range(1, len(impulse_response)):
        impulse_response[i] = impulse_response[i - 1] * decay
    reverbed_samples = convolve(samples, impulse_response, mode='full')[:len(samples)]
    reverbed_samples = np.clip(reverbed_samples, -2**15, 2**15 - 1).astype(np.int16)
    return audio_segment._spawn(reverbed_samples.tobytes())

def natural_tts(text, base_rate=95, base_volume=0.8):
    """
    生成接近人類成熟女聲的語音，說繁體中文，直接播放。
    
    參數：
        text (str): 要轉換的文本。
        base_rate (int): 基礎語速（默認 95）。
        base_volume (float): 基礎音量（默認 0.8）。
    
    返回：
        None
    """
    # 分割句子
    sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
    sentences = [s.strip() for s in sentences if s.strip()]

    for i, sentence in enumerate(sentences):
        # 關鍵詞強調
        emphasis = 1.0
        if any(keyword in sentence for keyword in ['你好', '小智', '歡迎', '試試', '台灣']):
            emphasis = 1.003  # 極微強調，成熟語氣

        # 隨機調整語速（±0.3%）
        rate = int(base_rate * (0.997 + random.uniform(0.0, 0.006)) * emphasis)
        
        # 隨機調整音量（±0.3%）
        volume = base_volume * (0.997 + random.uniform(0.0, 0.006)) * emphasis
        if i == 0:
            volume *= 0.85  # 開頭柔和
        elif i == len(sentences) - 1:
            volume *= 1.05  # 結尾微上揚
        
        # 生成語音
        temp_audio_file = text_to_speech(sentence, rate=rate, volume=min(volume, 1.0))
        
        # 波形處理
        try:
            audio = AudioSegment.from_wav(temp_audio_file)
            if len(audio) < 100:  # 音訊過短，跳過處理
                play(audio)
                os.remove(temp_audio_file)
                continue
            
            # 音高調整（+0.3 半音）
            audio = adjust_pitch(audio, 0.3)
            # 低通濾波
            audio = audio.low_pass_filter(4500)
            # 混響
            audio = apply_reverb(audio, decay=0.2)
            # 正規化音量
            audio = audio.normalize()
            
            # 直接播放
            play(audio)
        except Exception as e:
            print(f"音訊處理失敗: {e}")
            play(AudioSegment.from_wav(temp_audio_file))  # 播放原始音訊
        
        # 清理臨時檔案
        os.remove(temp_audio_file)
        
        # 句子間停頓（0.5-0.8 秒）
        time.sleep(random.uniform(0.5, 0.8))

if __name__ == "__main__":
    # 測試語音
    test_text = "你好，我是小智，我會講台灣狗已！"
    natural_tts(test_text)
    
    # 測試單獨「你好」
    time.sleep(2)
    natural_tts("你好")