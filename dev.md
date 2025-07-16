## 1. データベースの選択 — SQLite が最適

| 候補              | 特徴                                                       | 今回向きかどうか                                   |
| --------------- | -------------------------------------------------------- | ------------------------------------------ |
| **SQLite**      | ・単一ファイルで完結<br>・Python に標準搭載 (`sqlite3`)<br>・移行はファイルコピーだけ | **◎** サーバへそのまま転送可。インストール不要で最小構成            |
| MySQL / MariaDB | ・複数ユーザ・同時書込に強い                                           | ○ ただし FreeBSD + Apache 側で DB daemon の設定が必要 |
| PostgreSQL      | ・機能が豊富／堅牢                                                | △ 学習コストと運用コストが増える                          |

> **結論**: “簡易” 要件／ローカル作成→サーバ転送という運用に最も合う **SQLite** がベスト。後で本格運用に広げたくなったら MySQL/MariaDB へ移行しやすいように ORM（SQLAlchemy）を経由しておくと楽。

---

## 2. システム構成（フロント / バックエンド）

```
┌──────────────┐        ┌──────────────────┐
│  ブラウザ     | ⇄ JS  　│  Apache (FreeBSD)│
│(HTML/CSS/JS) │        │  ├─ mod_wsgi ── Flask app ── SQLite
└──────────────┘        └──────────────────┘
```

| レイヤ        | 推奨技術                                                                                 | 理由                                                                  |
| ---------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **フロント**   | - HTML + Tailwind (CDN)<br>- 少量の Vanilla JS or Alpine.js                             | ・ビルド不要（シンプル）<br>・セレクトボックスと表描画だけなら React などは過剰                       |
| **バックエンド** | - **Flask** (Jinja2 テンプレート)<br>- OR **FastAPI** + Jinja2 + mod\_proxy\_uwsgi (やや設定重) | ・Flask は CGI/mod\_wsgi で Apache と親和性◎<br>・テンプレートでサーバ側レンダリング→JS ほぼ不要 |
| **通信方式**   | GET/POST のみ                                                                          | SPA にしない方が構成が単純                                                     |
| **デプロイ**   | mod\_wsgi + virtualenv                                                               | Rust/C++ 禁止でも問題なし                                                   |

---

## 3. その他の考慮事項

| 項目            | 注意点                                                                                  |
| ------------- | ------------------------------------------------------------------------------------ |
| **スクレイピング**   | ・対象サイトの利用規約を確認<br>・1回だけ実行し、結果を CSV/JSON→SQLite にロードしてサーバへ転送                          |
| **文字コード**     | 佐賀大学サイトは UTF-8。DB/HTML とも UTF-8 で統一                                                  |
| **Apache 設定** | `public_html` 内なら .htaccess で<br>`SetHandler wsgi-script` が許可されているか確認（学内共用サーバの制限に注意） |
| **セキュリティ**    | - DB は read-only 権限で OK<br>- 学外公開なら CSRF 対策より先に Basic 認証を入れると楽                       |
| **将来拡張**      | ORM / 依存を requirements.txt に明示→ Heroku/Render など別環境へもデプロイしやすい                        |

---

## 4. 作成手順アウトライン

1. **準備**

   ```bash
   mkdir teacher-info && cd teacher-info
   python -m venv venv
   source venv/bin/activate
   pip install Flask SQLAlchemy pandas
   ```

2. **データ取得**

   1. Python でスクレイピング or 手動ダウンロード
   2. `pandas` で整形 → `to_sql()` で SQLite (`teacher.db`) 生成

3. **Flask アプリ実装**

   ```text
   app.py
   templates/
     ├─ base.html
     ├─ index.html   # 教員選択フォーム
     └─ detail.html  # 表形式で情報表示
   static/
     └─ style.css    # Tailwind CDN で最小に
   ```

   * `/`       : セレクトボックスに教員名を列挙（DBから取得）
   * `/detail` : 選択された教員IDを受け取り、情報を SELECT → テーブル表示

4. **ローカル動作確認**

   ```bash
   export FLASK_APP=app.py
   flask run
   ```

   ブラウザで `http://127.0.0.1:5000/`。

5. **サーバへ配置**

   * `scp teacher-info` → `~/public_html/teacher-info`
   * `.htaccess` 例

     ```apache
     Options +ExecCGI
     AddHandler wsgi-script .py
     RewriteEngine On
     RewriteRule ^(.*)$ /teacher-info/app.py/$1 [QSA,PT,L]
     ```
   * `python -m pip install --target ~/lib ...` など学内ルールに合わせる

6. **最終チェック**

   * VPN 外からアクセス → 表示速度／リンク切れ確認
   * レポートに **URL** と **改良点** を記載

---

> これで “シンプル・最小構成” を維持しつつ、後で FastAPI への置き換えや MySQL 化も容易です。疑問点があれば続けて相談してください。
