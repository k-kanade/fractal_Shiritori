import os
import requests
import numpy as np
import sounddevice as sd
import io
import wave

WORDS_DIR = os.path.join(os.path.dirname(__file__), "3word")
COEIROINK_URL = "http://localhost:50032"

def load_words():
    words = set()
    if not os.path.exists(WORDS_DIR):
        print(f"エラー: 単語フォルダ '{WORDS_DIR}' が見つかりません")
        return words

    for filename in os.listdir(WORDS_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(WORDS_DIR, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if len(word) == 3:
                        words.add(word)
    print(f"ロード完了: {len(words)} 単語が読み込まれました")
    return words

def normalize(letter):
    mapping = {
        'ゃ': 'や',
        'ゅ': 'ゆ',
        'ょ': 'よ',
        'っ': 'つ'
    }
    return mapping.get(letter, letter)

def is_valid_transition(current, candidate):
    if len(current) != 3 or len(candidate) != 3:
        return False
    c0, c1, c2 = normalize(current[0]), normalize(current[1]), normalize(current[2])
    cand0, cand1, cand2 = normalize(candidate[0]), normalize(candidate[1]), normalize(candidate[2])
    
    if cand0 == c0 and cand2 == c1:
        return True
    
    if cand0 == c1 and cand2 == c2:
        return True
    return False

def generate_audio(text):
    url = f"{COEIROINK_URL}/v1/synthesis"
    data = {
        "speakerUuid": "3c37646f-3881-5374-2a83-149267990abc",
        "styleId": "0",
        "text": text,
        "speedScale": 1.0,
        "volumeScale": 1.0,
        "pitchScale": 0.0,
        "intonationScale": 1.0,
        "prePhonemeLength": 0.1,
        "postPhonemeLength": 0.1,
        "outputSamplingRate": 44100
    }
    synthesis_res = requests.post(url, json=data)
    if synthesis_res.status_code != 200:
        raise Exception(f"Synthesis failed: {synthesis_res.status_code}, {synthesis_res.text}")
    return synthesis_res.content

def play_audio(audio_data):
    with wave.open(io.BytesIO(audio_data), 'rb') as wf:
        sample_rate = wf.getframerate()
        num_channels = wf.getnchannels()
        audio_array = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        if num_channels == 2:
            audio_array = audio_array.reshape(-1, 2)
        sd.play(audio_array, samplerate=sample_rate)
        sd.wait()

def get_valid_start_word():
    while True:
        start_word = input("スタート単語を入力してください (3文字): ").strip()
        if len(start_word) == 3:
            return start_word
        else:
            print("エラー: スタート単語は3文字で入力してください。")

def interactive_shiritori():
    words = load_words()
    if not words:
        print("単語の読み込みに失敗しました。プログラムを終了します。")
        return

    used_words = set()
    current_word = get_valid_start_word()
    used_words.add(current_word)
    print("スタート単語:", current_word)

    while True:
        valid_candidates = [w for w in words if w not in used_words and is_valid_transition(current_word, w)]
        if not valid_candidates:
            print("プログラム: 次の単語が見つかりません。あなたの勝ちです！")
            break

        program_choice = valid_candidates[0]
        print("プログラムの出力:", program_choice)
        used_words.add(program_choice)
        current_word = program_choice

        final_text_audio = f"私の単語は {program_choice} です"
        try:
            audio_data = generate_audio(final_text_audio)
            play_audio(audio_data)
        except Exception as e:
            print("音声生成エラー:", e)

        while True:
            human_input = input("あなたの番です。単語を入力してください (3文字): ").strip()
            if human_input == "こうさん":
                print("『こうさん』と入力しました。負けです！")
                break
            if len(human_input) != 3:
                print("エラー: 単語は3文字で入力してください。もう一度入力してください。")
                continue
            if human_input in used_words:
                print("エラー: その単語は既に使用されています。もう一度入力してください。")
                continue
            if not is_valid_transition(current_word, human_input):
                print("エラー: 入力された単語はルールに従っていません。もう一度入力してください。")
                continue
            break

        if human_input == "こうさん":
            break

        used_words.add(human_input)
        current_word = human_input

    again = input("もう一度やりますか？ (y/n): ").strip().lower()
    if again == "y":
        interactive_shiritori()
    else:
        print("ゲーム終了")

if __name__ == '__main__':
    interactive_shiritori()
