import os
import sqlite3
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# --- 定数 ---
BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'teachers.db')

# --- FastAPIアプリケーションの初期化 ---
app = FastAPI()

# --- 静的ファイルのマウント ---
# 'static'という名前で'static'ディレクトリをマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- テンプレートエンジンの設定 ---
# 'templates'ディレクトリをJinja2のテンプレートディレクトリとして設定
templates = Jinja2Templates(directory="templates")

# --- データベース接続 ---
# FastAPIの依存性注入システムを使って、リクエストごとにDB接続を提供
def get_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # カラム名でアクセスできるように RowFactory を設定
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()

# --- ルーティング ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: sqlite3.Connection = Depends(get_db)):
    """教員一覧ページ"""
    cur = db.execute('SELECT id, name, ruby, image FROM teacher ORDER BY name')
    teachers = cur.fetchall()
    # テンプレートをレンダリングしてHTMLレスポンスを返す
    template = templates.get_template("index.html")
    html_content = template.render(request=request, teachers=teachers)
    return HTMLResponse(content=html_content)

@app.get("/teacher/{teacher_id}", response_class=HTMLResponse)
async def teacher_detail(request: Request, teacher_id: int, db: sqlite3.Connection = Depends(get_db)):
    """教員詳細ページ"""
    # 教員基本情報
    teacher_cur = db.execute('SELECT * FROM teacher WHERE id = ?', (teacher_id,))
    teacher = teacher_cur.fetchone()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # 基本情報
    basic_info_cur = db.execute('SELECT key, value FROM basic_info WHERE teacher_id = ?', (teacher_id,))
    basic_info = basic_info_cur.fetchall()
    
    # 研究キーワード
    keywords_cur = db.execute('SELECT keyword FROM research_keyword WHERE teacher_id = ?', (teacher_id,))
    keywords = [row['keyword'] for row in keywords_cur.fetchall()]
    
    # 研究分野
    areas_cur = db.execute('SELECT area FROM research_area WHERE teacher_id = ?', (teacher_id,))
    areas = [row['area'] for row in areas_cur.fetchall()]
    
    # 主要論文
    papers_cur = db.execute('SELECT title, link FROM major_paper WHERE teacher_id = ? AND title IS NOT NULL', (teacher_id,))
    papers = papers_cur.fetchall()
    
    template = templates.get_template("detail.html")
    html_content = template.render(
        request=request,
        teacher=teacher,
        basic_info=basic_info,
        keywords=keywords,
        areas=areas,
        papers=papers
    )
    return HTMLResponse(content=html_content)

@app.post("/select_teacher")
async def select_teacher(teacher_id: str = Form(...)):
    """教員選択処理"""
    if teacher_id:
        # RedirectResponseを使って詳細ページへリダイレクト
        return RedirectResponse(url=f"/teacher/{teacher_id}", status_code=303)
    return RedirectResponse(url="/", status_code=303)

# サーバーを起動するには、ターミナルで `uvicorn app:app --reload` を実行します。