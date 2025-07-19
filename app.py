import os
import sqlite3
from flask import Flask, g, render_template, abort, request, redirect, url_for

# プロジェクトルートからの DB パス
BASE_DIR = os.path.dirname(__file__)
DATABASE = os.path.join(BASE_DIR, 'teachers.db')

def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(DATABASE)
        # カラム名でアクセスできるように RowFactory を設定
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

app = Flask(__name__)
app.teardown_appcontext(close_db)

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT id, name, ruby, image FROM teacher ORDER BY name')
    teachers = cur.fetchall()
    return render_template('index.html', teachers=teachers)

@app.route('/teacher/<int:teacher_id>')
def teacher_detail(teacher_id):
    db = get_db()
    
    # 教員基本情報
    teacher_cur = db.execute('SELECT * FROM teacher WHERE id = ?', (teacher_id,))
    teacher = teacher_cur.fetchone()
    if not teacher:
        abort(404)
    
    # 基本情報
    basic_info_cur = db.execute('SELECT key, value FROM basic_info WHERE teacher_id = ?', (teacher_id,))
    basic_info = basic_info_cur.fetchall()
    
    # 研究キーワード
    keywords_cur = db.execute('SELECT keyword FROM research_keyword WHERE teacher_id = ?', (teacher_id,))
    keywords = keywords_cur.fetchall()
    
    # 研究分野
    areas_cur = db.execute('SELECT area FROM research_area WHERE teacher_id = ?', (teacher_id,))
    areas = areas_cur.fetchall()
    
    # 主要論文
    papers_cur = db.execute('SELECT title, link FROM major_paper WHERE teacher_id = ? AND title IS NOT NULL', (teacher_id,))
    papers = papers_cur.fetchall()
    
    return render_template('detail.html', 
                          teacher=teacher,
                          basic_info=basic_info,
                          keywords=keywords,
                          areas=areas,
                          papers=papers)

@app.route('/select_teacher', methods=['POST'])
def select_teacher():
    """教員選択処理"""
    teacher_id = request.form.get('teacher_id')
    if teacher_id:
        return redirect(url_for('teacher_detail', teacher_id=int(teacher_id)))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
