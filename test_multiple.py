#!/usr/bin/env python3
"""
複数ファイル処理のテストスクリプト
"""

import sys
sys.path.insert(0, '/home/ubuntu/textbook_splitter')

from pathlib import Path
import zipfile
import io

# app.pyから関数をインポート
from app import split_by_sections, create_zip_from_multiple_files, sanitize_filename

# テストファイルのリスト
test_files = [
    "/home/ubuntu/textbook_splitter/05_第3編_17章_本文のみ.md",
    "/home/ubuntu/textbook_splitter/05_第3編_18章_本文のみ.md",
    "/home/ubuntu/textbook_splitter/05_第3編_19章_本文のみ.md",
    "/home/ubuntu/textbook_splitter/06_第4編_20章_本文のみ.md"
]

print("=" * 60)
print("複数ファイル処理テスト")
print("=" * 60)

all_file_sections = {}
total_sections = 0

for test_file in test_files:
    file_path = Path(test_file)
    
    if not file_path.exists():
        print(f"❌ ファイルが見つかりません: {test_file}")
        continue
    
    print(f"\n📄 処理中: {file_path.name}")
    
    # ファイルを読み込み
    with open(file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # 分割処理
    sections = split_by_sections(text_content, remove_pages=True)
    
    print(f"  ✅ {len(sections)}個のセクションに分割")
    
    # 結果を保存
    all_file_sections[file_path.name] = sections
    total_sections += len(sections)

print("\n" + "=" * 60)
print(f"📊 処理結果: {len(all_file_sections)}個のファイルから{total_sections}個のセクションに分割")
print("=" * 60)

# 生成されるファイル一覧を表示
print("\n📄 生成されるファイル一覧:")
for original_filename, sections in all_file_sections.items():
    print(f"\n【{original_filename}】 → {len(sections)}個のセクション")
    
    base_name = Path(original_filename).stem
    safe_base_name = sanitize_filename(base_name)
    
    for number, title, content in sections:
        safe_title = sanitize_filename(title)
        filename = f"{safe_base_name}_{number}_{safe_title}.txt"
        lines = len(content.split('\n'))
        chars = len(content)
        print(f"  - {filename} ({lines}行, {chars}文字)")

# ZIPファイルを作成してテスト
print("\n" + "=" * 60)
print("ZIPファイル作成テスト")
print("=" * 60)

zip_data = create_zip_from_multiple_files(all_file_sections)
print(f"✅ ZIPファイル作成成功 (サイズ: {len(zip_data):,} bytes)")

# ZIPの内容を確認
zip_buffer = io.BytesIO(zip_data)
with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
    file_list = zip_file.namelist()
    print(f"✅ ZIP内のファイル数: {len(file_list)}個")
    print("\nZIP内のファイル一覧:")
    for i, filename in enumerate(file_list, 1):
        file_info = zip_file.getinfo(filename)
        print(f"  {i}. {filename} ({file_info.file_size:,} bytes)")

print("\n" + "=" * 60)
print("✅ テスト完了!")
print("=" * 60)
