from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
import sqlitecloud
from flask_cors import CORS
import traceback

# 初始化 Flask 應用
app = Flask(__name__)
CORS(app)
load_dotenv()

# 讀取資料庫連線字串
db_url = os.getenv("DATABASE_URL")

# 白名單限制可查詢的資料表
ALLOWED_TABLES = {
    "article", "bank", "cloud", "experience", "food", "host",
    "inventory", "mail", "member", "routine", "subscription", "video"
}

# 查詢資料表資料（每次請求建立獨立連線）
def select_table(table_name, limit=100):
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")
    
    query = f"SELECT * FROM {table_name} LIMIT ?;"
    
    try:
        with sqlitecloud.connect(db_url) as conn:
            cursor = conn.execute(query, (limit,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print("資料庫查詢錯誤:", traceback.format_exc())
        raise

# 首頁：列出所有可查詢連結
@app.route("/")
def index():
    links = "".join(
        f'<li><a href="/{table}">{table}</a></li>' for table in sorted(ALLOWED_TABLES)
    )
    return f"<ul>{links}</ul>"

# 查詢指定資料表
@app.route("/<table_name>")
def get_table(table_name):
    try:
        limit = int(request.args.get("limit", 100))
        data = select_table(table_name, limit=limit)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "trace": traceback.format_exc(limit=1)
        }), 500

# 主程式執行點
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
