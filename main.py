import os
import openai
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# ✅ 올바른 환경 변수 접근
API_KEY = os.environ.get("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("환경 변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")

# ✅ 올바른 OpenAI API 설정
openai.api_key = API_KEY

app = FastAPI()

# "static" 폴더의 파일들을 자동으로 서빙
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# CORS 설정 추가
origins = [
    "http://localhost:3000",  
    "https://test-mmb0.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 시스템 프롬프트 정의
system_prompt = """
You are a helpful assistant for the company ZyntriQix. Your task is to correct
any spelling discrepancies in the transcribed text. Make sure that the names of
the following products are spelled correctly: ZyntriQix, Digique Plus,
CynapseFive, VortiQore V8, EchoNix Array, OrbitalLink Seven, DigiFractal
Matrix, PULSE, RAPT, B.R.I.C.K., Q.U.A.R.T.Z., F.L.I.N.T. Only add necessary
punctuation such as periods, commas, and capitalization, and use only the
context provided.
"""

# ✅ Whisper 변환 결과를 GPT로 수정
def generate_corrected_transcript(temperature, system_prompt, audio_file):
    try:
        # ✅ 올바른 파일 객체 전달
        transcription = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file  # ✅ 올바른 파일 객체 전달
        )

        # ✅ GPT-4를 사용하여 텍스트 수정
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcription["text"]}
            ]
        )

        return response["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

# ✅ 업로드된 오디오 파일 처리
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        corrected_text = generate_corrected_transcript(0, system_prompt, file.file)
        return PlainTextResponse(corrected_text)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return PlainTextResponse(f"Error: {str(e)}", status_code=500)
