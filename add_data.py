import pymysql.cursors

# データベース接続
connection = pymysql.connect(
    host='localhost',
    user='app_user',
    password='app_password',
    database='manga_db',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # 1. 今までのダミーデータをリセット
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE manga_genres;")
        cursor.execute("TRUNCATE TABLE mangas;")
        cursor.execute("TRUNCATE TABLE genres;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        # 2. ジャンル（タグ）の登録
        genres = ['バトル', 'ファンタジー', 'ラブコメ', '日常', 'サスペンス']
        for g in genres:
            cursor.execute("INSERT INTO genres (name) VALUES (%s)", (g,))

        # 3. 本物の漫画データの登録 (タイトル, 作者, あらすじ, 画像URL, ジャンルIDのリスト)
        mangas = [
            ("呪術廻戦", "芥見下々", "呪いを祓う呪術師たちの闘いを描くダークファンタジー。", "https://dosbg3xlm0x1t.cloudfront.net/images/items/9784088815169/1200/9784088815169.jpg", [1, 2]),
            ("葬送のフリーレン", "山田鐘人・アベツカサ", "魔王討伐後のエルフの魔法使いの旅路。", "https://assets.mercari-shops-static.com/-/large/plain/JPvn4CidkXC42D3Kz4cHnH.jpg@jpg", [2, 4]),
            ("かぐや様は告らせたい", "赤坂アカ", "天才たちの恋愛頭脳戦を描くラブコメディ。", "https://dosbg3xlm0x1t.cloudfront.net/images/items/9784088904320/1200/9784088904320.jpg", [3, 4]),
            ("チェンソーマン", "藤本タツキ", "悪魔を狩るデビルのダークヒーローアクション。", "https://dosbg3xlm0x1t.cloudfront.net/images/items/08881780881780315501/1200/08881780881780315501.jpg", [1, 5]),
            ("SPY×FAMILY", "遠藤達哉", "スパイと超能力者と殺し屋の仮初めの家族を描くコメディ。", "https://dosbg3xlm0x1t.cloudfront.net/images/items/9784088820118/1200/9784088820118.jpg", [1, 4])
        ]

        for i, manga in enumerate(mangas, start=1):
            # 漫画本体の保存
            cursor.execute(
                "INSERT INTO mangas (title, author, description, image_url) VALUES (%s, %s, %s, %s)",
                (manga[0], manga[1], manga[2], manga[3])
            )
            # ジャンルとの紐付け
            for genre_id in manga[4]:
                cursor.execute(
                    "INSERT INTO manga_genres (manga_id, genre_id) VALUES (%s, %s)",
                    (i, genre_id)
                )

        # データベースに変更を確定させる
        connection.commit()
        print("🎉 本物の漫画データの登録が完了しました！")

finally:
    connection.close()
