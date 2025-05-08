import pyttsx3
from pydub import AudioSegment
from pydub.effects import speedup
from scipy.signal import convolve
import numpy as np
import simpleaudio as sa
import io

def text_to_speech(text, rate=140, volume=0.7, voice_id=None):
    """
    使用 pyttsx3 將文字轉換為語音，並將音訊資料以 bytes 形式返回。

    Args:
        text (str): 要轉換的文字。
        rate (int, optional): 語速 (words per minute). Defaults to 140.
        volume (float, optional): 音量 (0.0 to 1.0). Defaults to 0.7.
        voice_id (str, optional): 指定語音 ID. Defaults to None (系統預設).

    Returns:
        bytes: 包含 WAV 格式音訊資料的 bytes。
    """
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)
    if voice_id:
        engine.setProperty('voice', voice_id)

    # 使用 io.BytesIO 儲存到記憶體
    with io.BytesIO() as wav_output:
        engine.save_to_file(text, wav_output)
        engine.runAndWait()
        wav_data = wav_output.getvalue()  # 獲取記憶體中的 WAV 資料
    return wav_data

def adjust_pitch_and_speed(audio_data, pitch_change=0, speed_change=1.0, frame_rate=22050):
    """
    調整音高和語速，直接處理音訊資料 (bytes)。

    Args:
        audio_data (bytes): WAV 格式的音訊資料。
        pitch_change (int, optional): 音高調整的半音數. Defaults to 0.
        speed_change (float, optional): 語速調整倍數. Defaults to 1.0.
        frame_rate (int, optional): 音訊的採樣率. Defaults to 22050.

    Returns:
        AudioSegment: 處理後的 AudioSegment 物件。
    """
    sound = AudioSegment.from_wav(io.BytesIO(audio_data))

    # 調整音高
    if pitch_change != 0:
        semitones_to_speed_ratio = 1.05946
        pitch_factor = semitones_to_speed_ratio ** pitch_change
        new_frame_rate = int(sound.frame_rate * pitch_factor)
        pitched_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_frame_rate})
        pitched_sound = pitched_sound.set_frame_rate(sound.frame_rate)
        sound = pitched_sound

    # 調整語速
    if speed_change != 1.0:
        sound = speedup(sound, speed_change)

    return sound

def apply_reverb(audio_segment, reverb_level=0.15, delay=0.1, frame_rate=22050):
    """
    加入簡單混響效果，直接處理 AudioSegment 物件。

    Args:
        audio_segment (AudioSegment): 輸入的 AudioSegment 物件。
        reverb_level (float, optional): 混響強度. Defaults to 0.15.
        delay (float, optional): 混響延遲時間 (秒). Defaults to 0.1.
        frame_rate (int, optional): 音訊的採樣率. Defaults to 22050.

    Returns:
        AudioSegment: 處理後的 AudioSegment 物件。
    """
    samples = np.array(audio_segment.get_array_of_samples())
    impulse_response = np.zeros(int(frame_rate * 0.5))
    impulse_response[0] = 1
    impulse_response[int(frame_rate * delay)] = reverb_level
    reverbed_signal = convolve(samples, impulse_response, mode='full')[:len(samples)]
    reverbed_signal = np.clip(reverbed_signal, -2**15, 2**15 - 1).astype(np.int16)
    reverbed_sound = audio_segment._spawn(reverbed_signal.tobytes())
    return reverbed_sound

def play_audio(audio_segment, frame_rate=22050):
    """
    播放 AudioSegment 物件。

    Args:
        audio_segment (AudioSegment): 要播放的 AudioSegment 物件。
        frame_rate (int, optional): 音訊的採樣率. Defaults to 22050.
    """
    play_obj = sa.play_buffer(
        audio_segment.raw_data,
        numchannels=audio_segment.channels,
        bytespersec=audio_segment.frame_rate * audio_segment.sample_width,
        sampwidth=audio_segment.sample_width,
        framerate=audio_segment.frame_rate
    )
    play_obj.wait_done()

def show_available_voices():
    """
    列出系統中可用的語音。
    """
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    if not voices:
        print("錯誤：沒有找到任何語音，請檢查系統語音設定！")
        return False

    print("可用語音索引：")
    for index, voice in enumerate(voices):
        print(f"索引 {index}:")
        print(f"  ID: {voice.id}")
        print(f"  名稱: {voice.name}")
        print(f"  語言: {voice.languages}")
        print("-" * 50)
    return True

if __name__ == '__main__':
    # 1. 顯示可用語音，選擇 voice_id
    if not show_available_voices():
        exit()

    desired_voice_id = None  # 請在此處填入您選擇的 voice_id
    if desired_voice_id is None:
        print("請選擇一個 voice_id 並修改程式碼!")
        exit()

    # 2. 文字轉語音 (直接取得音訊資料)
    text = "哈囉，你好呀！今天天氣真不錯呢，你想做點什麼呢？我會講台灣狗語喔。"
    audio_data = text_to_speech(text, voice_id=desired_voice_id)

    # 3. 音訊修飾 (全部在記憶體中處理)
    modified_audio = adjust_pitch_and_speed(audio_data, pitch_change=2, speed_change=1.05)
    final_audio = apply_reverb(modified_audio, reverb_level=0.15, delay=0.1)

    # 4. 播放修飾後的語音
    play_audio(final_audio)