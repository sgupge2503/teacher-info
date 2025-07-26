import os
import sqlite3
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- 定数 ---
BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'teachers.db')

# --- FastAPIアプリケーションの初期化 ---
app = FastAPI()

# --- CORSミドルウェアの設定 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# --- データベース接続 ---
def get_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()

# --- APIルーターの作成 ---
api_router = APIRouter()

@api_router.get("/api/teachers")
async def get_teachers(db: sqlite3.Connection = Depends(get_db)):
    cur = db.execute('SELECT id, name, ruby, image FROM teacher ORDER BY name')
    teachers = [dict(row) for row in cur.fetchall()]
    return teachers

@api_router.get("/api/teacher/{teacher_id}")
async def get_teacher_detail(teacher_id: int, db: sqlite3.Connection = Depends(get_db)):
    teacher_cur = db.execute('SELECT * FROM teacher WHERE id = ?', (teacher_id,))
    teacher = teacher_cur.fetchone()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    basic_info_cur = db.execute('SELECT key, value FROM basic_info WHERE teacher_id = ?', (teacher_id,))
    keywords_cur = db.execute('SELECT keyword FROM research_keyword WHERE teacher_id = ?', (teacher_id,))
    areas_cur = db.execute('SELECT area FROM research_area WHERE teacher_id = ?', (teacher_id,))
    papers_cur = db.execute('SELECT title, link FROM major_paper WHERE teacher_id = ? AND title IS NOT NULL', (teacher_id,))

    response_data = {
        "teacher": dict(teacher),
        "basic_info": [dict(row) for row in basic_info_cur.fetchall()],
        "keywords": [row['keyword'] for row in keywords_cur.fetchall()],
        "areas": [row['area'] for row in areas_cur.fetchall()],
        "papers": [dict(row) for row in papers_cur.fetchall()]
    }
    return response_data

# --- ルーターと静的ファイルのマウント ---
app.include_router(api_router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# サーバーを起動するには、ターミナルで `uvicorn app:app --reload` を実行します。