以下のプロンプト例をそのまま **“コーディングエージェント”** に渡せば、
Flask＋Jinja2 で **教員名セレクトボックス ➜ 研究業績表の表示** までを実装してくれるはずです。
（必要に応じて数値やディレクトリ名を調整してください）

---

## プロンプト例

> ### 背景
>
> * 研究者情報が入った **SQLite データベース `teachers.db`** がある。
> * 主要テーブルは
>
>   * `teacher(id, name, ruby …)`
>   * `research_area(teacher_id, area)`
>   * `major_paper(teacher_id, title, link)`
>     など。
> * Flask を API 兼テンプレートサーバーとして使い、静的ファイルは `/static/`, HTML テンプレートは `/templates/` に置く。
>
> ### 作りたい機能
>
> 1. **トップページ `/` (index.html)**
>
>    * ページ読み込み時に DB から教員の `id` と `name` を取得し、**セレクトボックス**に一覧表示する。
>    * 「表示」ボタン or `change` イベントで教員 ID をサーバーへ送信。
> 2. **詳細ページ `/teacher/<int:id>` (detail.html)**
>
>    * 選択された教員の **研究業績情報** を取得し、表形式で表示する。
>    * 表には少なくとも
>
>      * <研究分野> (`research_area.area`)
>      * <主要論文タイトル> と <リンク> (`major_paper.title`, `major_paper.link`)
>        を含めること。
> 3. **DB アクセス方法**
>
>    * 追加ライブラリは使わず **Python 標準の `sqlite3`** を使用する。
>    * 冗長な SQL は関数化して OK。
> 4. **前提ディレクトリ構造 (抜粋)**
>
> ```text
> teacher-info/
> ├── app.py
> ├── teachers.db
> ├── templates/
> │   ├── index.html
> │   └── detail.html
> └── static/
>     ├── css/style.css
>     └── js/script.js
> ```
>
> ### 実装要件
>
> * Flask 3.x 準拠。`app.py` から実行したらローカルで動くこと。
> * Jinja2 でテンプレートレンダリング。JS は任意だが、ページ遷移（form POST / GET）でも AJAX でも可。
> * コードは読みやすいよう関数や Blueprint を分けてもよい。
> * **セレクトボックス → 詳細表表示** まで一通り動作するサンプルデータとともに動くことを確認できるようにする。
>
> ### 出力フォーマット
>
> * 完成した **`app.py`** と **2 つのテンプレートファイル** (`index.html`, `detail.html`) を提示せよ。
> * 必要なら `static/js/script.js` と `static/css/style.css` も含めること。
> * 各ファイルの中身のみをコードブロックで示し、説明は簡潔に。
> * 仮に追加パッケージが必要な場合は `requirements.txt` を併記する。

---

このプロンプトをベースに渡せば、「セレクトボックスで教員を選択 → 研究業績を表で表示」という最小要件を満たすコード一式が返ってくるはずです。
