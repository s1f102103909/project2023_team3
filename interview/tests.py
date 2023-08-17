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


def record_video(output_file, duration=10):
    # カメラキャプチャの初期化
    cap = cv2.VideoCapture(0)

    # ビデオ書き込みの設定
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    # 指定した秒数だけ録画を行う
    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
        ret, frame = cap.read()
        if ret:
            # フレームを表示
            cv2.imshow('Recording', frame)
            # フレームをビデオに書き込み
            out.write(frame)
        else:
            break

        # 'q' キーが押されたら録画終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 後処理
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# メインの録画処理を呼び出し
output_filename = 'output.avi'
record_duration = 10  # 録画する秒数
record_video(output_filename, record_duration)
