from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pymysql.cursors

app = FastAPI()

def get_db_connection():
    return pymysql.connect(
        host='gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
        user='2b26cwtACNaoCtX.root',
        password='WFdsCr8Hew5tJh7z',
        database='test',
        ssl={'ssl': {}}, # 👈 クラウドDBへの安全な通信に必要です
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return html_content

# 🆕新機能：ジャンル（タグ）の一覧をデータベースから持ってくる
@app.get("/genres")
def get_genres():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM genres")
            return {"genres": cursor.fetchall()}
    finally:
        connection.close()

# ⚙️パワーアップ：ジャンルIDを受け取って、該当する漫画だけを絞り込む
# （上の get_genres などの部分はそのまま）

# ⚙️さらにパワーアップ：ジャンルIDとキーワードの両方で絞り込む
@app.get("/mangas")
def get_mangas(genre_ids: str = None, keyword: str = None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # ベースとなるSQL
            sql = "SELECT DISTINCT m.* FROM mangas m"
            params = []
            
            # ジャンル検索がある場合は中間テーブルを結合する
            if genre_ids:
                sql += " JOIN manga_genres mg ON m.id = mg.manga_id"
                
            wheres = []
            
            # ① ジャンルでの絞り込み
            if genre_ids:
                ids = [int(x) for x in genre_ids.split(',')]
                format_strings = ','.join(['%s'] * len(ids))
                wheres.append(f"mg.genre_id IN ({format_strings})")
                params.extend(ids)
                
            # ② タイトルキーワードでの絞り込み（前後を%で囲むと「〜を含む」という検索になる）
            if keyword:
                wheres.append("m.title LIKE %s")
                params.append(f"%{keyword}%")
                
            # 条件があれば WHERE で繋げる
            if wheres:
                sql += " WHERE " + " AND ".join(wheres)
                
            cursor.execute(sql, tuple(params))
            return {"mangas": cursor.fetchall()}
    finally:
        connection.close()
