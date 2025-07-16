#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3

DB_PATH = 'teachers.db'
JSON_PATH = 'teachers.json'

def init_db(conn):
    c = conn.cursor()
    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS teacher (
        id   INTEGER PRIMARY KEY,
        url  TEXT UNIQUE,
        name TEXT,
        ruby TEXT
    );

    CREATE TABLE IF NOT EXISTS basic_info (
        teacher_id INTEGER,
        key        TEXT,
        value      TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teacher(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS research_keyword (
        teacher_id INTEGER,
        keyword    TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teacher(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS research_area (
        teacher_id INTEGER,
        area       TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teacher(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS major_paper (
        teacher_id INTEGER,
        title      TEXT,
        link       TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teacher(id) ON DELETE CASCADE
    );
    """)
    conn.commit()

def load_data(conn):
    with open(JSON_PATH, encoding='utf-8') as f:
        teachers = json.load(f)

    c = conn.cursor()
    for t in teachers:
        # teacher table
        c.execute(
            "INSERT OR IGNORE INTO teacher (url, name, ruby) VALUES (?, ?, ?)",
            (t['url'], t['name'], t.get('ruby'))
        )
        # get its id
        c.execute("SELECT id FROM teacher WHERE url = ?", (t['url'],))
        teacher_id = c.fetchone()[0]

        # basic_info table
        for key, val in t.get('basic_info', {}).items():
            c.execute(
                "INSERT INTO basic_info (teacher_id, key, value) VALUES (?, ?, ?)",
                (teacher_id, key, val)
            )

        # research_keyword table
        for kw in t.get('research_keywords', []):
            c.execute(
                "INSERT INTO research_keyword (teacher_id, keyword) VALUES (?, ?)",
                (teacher_id, kw)
            )

        # research_area table
        for area in t.get('research_areas', []):
            c.execute(
                "INSERT INTO research_area (teacher_id, area) VALUES (?, ?)",
                (teacher_id, area)
            )

        # major_paper table
        for paper in t.get('major_papers', []):
            c.execute(
                "INSERT INTO major_paper (teacher_id, title, link) VALUES (?, ?, ?)",
                (teacher_id, paper.get('title'), paper.get('link'))
            )

    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    load_data(conn)
    conn.close()
    print(f"Initialized `{DB_PATH}` and loaded data from `{JSON_PATH}`.")

if __name__ == '__main__':
    main()
