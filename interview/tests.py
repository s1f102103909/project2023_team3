from django.test import TestCase

# Create your tests here.
import os
import openai
import cv2

API_KEY = "7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw"
API_BASE = "https://api.openai.iniad.org/api/v1"

def generate_answer(prompt):
    openai.api_key = API_KEY
    openai.api_base = API_BASE
    openai.Model.list() #OpenAIのインスタンスを生成
    
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {'role':'user', 'content':prompt}
        ],
        temperature = 0,
        max_tokens = 1024,
        top_p = 1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response['choices'][0]['message']['content']
    return answer


def display_camera():
    # カメラキャプチャの初期化
    cap = cv2.VideoCapture(0)

    while True:
        # フレームをキャプチャ
        ret, frame = cap.read()

        if ret:
            # フレームを表示
            cv2.imshow('Camera Feed', frame)

        # 'q' キーが押されたら表示終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 後処理
    cap.release()
    cv2.destroyAllWindows()

# メインの表示処理を呼び出し
#display_camera()