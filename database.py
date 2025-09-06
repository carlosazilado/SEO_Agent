import sqlite3
import json
from datetime import datetime

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect("seo_analysis.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            analysis_result TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            seo_score INTEGER DEFAULT 0
        )
    """)
    
    # 检查是否需要添加新列
    cursor.execute("PRAGMA table_info(analyses)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'status' not in columns:
        cursor.execute("ALTER TABLE analyses ADD COLUMN status TEXT DEFAULT 'completed'")
    
    if 'seo_score' not in columns:
        cursor.execute("ALTER TABLE analyses ADD COLUMN seo_score INTEGER DEFAULT 0")
    
    conn.commit()
    conn.close()

def save_analysis(analysis_id: str, url: str, result: dict):
    """保存分析结果"""
    conn = sqlite3.connect("seo_analysis.db")
    cursor = conn.cursor()
    
    status = 'completed' if 'error' not in result else 'error'
    seo_score = result.get('seo_score', 0)
    
    cursor.execute("""
        INSERT INTO analyses (id, url, analysis_result, status, seo_score)
        VALUES (?, ?, ?, ?, ?)
    """, (analysis_id, url, json.dumps(result, ensure_ascii=False), status, seo_score))
    
    conn.commit()
    conn.close()

def get_analysis_history(limit: int = 50):
    """获取分析历史"""
    conn = sqlite3.connect("seo_analysis.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, url, timestamp, status, seo_score
        FROM analyses
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0], 
            "url": r[1], 
            "timestamp": r[2],
            "status": r[3],
            "seo_score": r[4]
        } 
        for r in results
    ]

def get_analysis_by_id(analysis_id: str):
    """根据ID获取分析结果"""
    conn = sqlite3.connect("seo_analysis.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "url": result[1],
            "timestamp": result[2],
            "analysis_result": json.loads(result[3])
        }
    return None
