import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai
import pymysql

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

openai.api_key = open_file('openaiapikey_haekang.txt') # 해강 계정의 키값 받아오기

class Input(BaseModel):
    randomNumber: str
    passage: str = '랜덤 수능 영어 지문'
    content: str = '같은 내용'
    word: str = '보통'
    grammar: str = '보통'

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
#     "http://서버주소:포트넘버",
    # "http://localhost:8000",  # 허용하려는 클라이언트의 주소를 추가해야 합니다.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/items")
async def read_item(input: Input):
    # 사용자가 난수를 입력하지 않은 경우
    if not input.randomNumber.strip():
        raise HTTPException(status_code=400, detail="토큰을 입력해주세요.")

    # DB에 연결
    connection = pymysql.connect(host='server_host_input',
                                 user='user_input',
                                 password='passwd_input',
                                 db='db_input')

    try:
        with connection.cursor() as cursor:
            # DB에서 사용자가 입력한 난수 검색
            sql = "SELECT * FROM random_strings_token WHERE token = %s"
            cursor.execute(sql, (input.randomNumber,))
            result = cursor.fetchone()

            # 일치하는 난수가 없는 경우
            if result is None:
                raise HTTPException(status_code=400, detail="입력하신 토큰이 유효하지 않습니다.")

    finally:
        connection.close()

    # input에 빈값이 올 때, 예외 처리
    if input.passage.strip() == "":
        input.passage = '랜덤 영어 지문'

    if input.content.strip() == "":
        input.content = '같은 내용'

    if input.word.strip() == "":
        input.word = '보통'

    if input.grammar.strip() == "":
        input.grammar = '보통'

    # 받은 인자들로 prompt 구성
    messages = []
    messages.append({'role':'system',
                     'content':'너는 현재 대한민국 입시 영어 학원 선생님으로서, 학생들에게 출제하기 위한 다양한 영어 지문을 만들고 있어.'})
    messages.append({'role':'user',
                     'content':f"""아래 영어 지문을 다음 조건들에 맞게 바꾸고, 변경된 영어 지문만 출력해줘.
                     1.내용: {input.content}, 2.단어의 난이도: {input.word}, 3.문법의 난이도: {input.grammar}.
                     {input.passage}"""})

    # 작성한 prompt로 gpt에 질문하기
    try:
        completion = openai.ChatCompletion.create(model="gpt-4-0613",
                                                  # model="gpt-3.5-turbo-0301",
                                                  messages=messages,
                                                  temperature=0.5)
    # 예외처리 코드
    except openai.error.RateLimitError:
        raise HTTPException(status_code=429, detail="사용 가능한 이 달의 GPT의 요금을 초과했습니다.")
    except openai.error.APIError:
        raise HTTPException(status_code=502, detail="Bad gateway. API 요청에 문제가 발생했습니다. 커피 한 잔 마시고 다시 시도해주세요.")

    # gpt의 대답
    gpt_completion = completion['choices'][0]['message']['content']

    return gpt_completion

if __name__ == "__main__":
    uvicorn.run("mainV2:app", host="0.0.0.0", port=8400, reload=True)
    # uvicorn.run(app, host='host_address', port=8000)


