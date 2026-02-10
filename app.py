import streamlit as st
import re
import zipfile
import io
from pathlib import Path

st.set_page_config(
    page_title="教科書セクション分割ツール",
    page_icon="📚",
    layout="wide"
)

st.title("📚 教科書セクション分割ツール")
st.markdown("""
このアプリは、教科書のMarkdownテキストを**テーマ(### 見出し)**ごとに個別のTXTファイルに分割し、
ZIPファイルとして一括ダウンロードできるツールです。

**✨ 複数ファイルを一度にアップロード**して、自動的に全て処理できます!
""")

# ファイル名として使用できない文字を置換する関数
def sanitize_filename(filename):
    """ファイル名として使用できない文字をアンダースコアに置換"""
    # Windows/Mac/Linuxで使用できない文字を置換
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', filename)
    # 先頭・末尾の空白やドットを削除
    sanitized = sanitized.strip('. ')
    return sanitized

# ページ表記を削除する関数
def remove_page_markers(text):
    """[ページ x] 形式の表記を削除"""
    # **[ページ x]** の形式を削除
    text = re.sub(r'\*\*\[ページ\s+\d+\]\*\*\s*\n?', '', text)
    return text

# テキストを ### 見出しで分割する関数
def split_by_sections(text, remove_pages=False):
    """
    Markdownテキストを ### 見出しで分割
    
    Args:
        text: 入力テキスト
        remove_pages: ページ表記を削除するかどうか
    
    Returns:
        分割されたセクションのリスト [(番号, タイトル, 内容), ...]
    """
    # ページ表記の削除
    if remove_pages:
        text = remove_page_markers(text)
    
    # テキストを行ごとに分割
    lines = text.split('\n')
    
    sections = []
    current_section = None
    intro_content = []
    section_counter = 0
    
    for line in lines:
        # ### で始まる見出しを検出
        if line.startswith('### '):
            # 前のセクションを保存
            if current_section is not None:
                sections.append(current_section)
            
            # 新しいセクションを開始
            section_counter += 1
            heading = line.replace('### ', '').strip()
            current_section = {
                'number': section_counter,
                'title': heading,
                'content': [line]
            }
        elif current_section is not None:
            # 現在のセクションに行を追加
            current_section['content'].append(line)
        else:
            # ### より前の導入部分
            intro_content.append(line)
    
    # 最後のセクションを保存
    if current_section is not None:
        sections.append(current_section)
    
    # 導入部分を追加(内容がある場合のみ)
    intro_text = '\n'.join(intro_content).strip()
    if intro_text:
        result = [('00', '導入', intro_text)]
    else:
        result = []
    
    # セクションを整形して追加
    for section in sections:
        number = f"{section['number']:02d}"
        title = section['title']
        content = '\n'.join(section['content'])
        result.append((number, title, content))
    
    return result

# ZIPファイルを作成する関数(複数ファイル対応)
def create_zip_from_multiple_files(file_sections_dict):
    """
    複数のファイルから分割されたセクションをまとめてZIPファイルを作成
    
    Args:
        file_sections_dict: {元ファイル名: [(番号, タイトル, 内容), ...], ...}
    
    Returns:
        ZIPファイルのバイトデータ
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for original_filename, sections in file_sections_dict.items():
            # 元のファイル名から拡張子を除いたベース名を取得
            base_name = Path(original_filename).stem
            safe_base_name = sanitize_filename(base_name)
            
            # 各セクションをZIPに追加
            for number, title, content in sections:
                # ファイル名を作成: 元ファイル名_番号_タイトル.txt
                safe_title = sanitize_filename(title)
                filename = f"{safe_base_name}_{number}_{safe_title}.txt"
                
                # ZIPに追加
                zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# メインのUI
st.markdown("---")

# ファイルアップロード(複数対応)
uploaded_files = st.file_uploader(
    "📁 Markdownファイル(.md または .txt)をアップロードしてください",
    type=['md', 'txt'],
    accept_multiple_files=True,
    help="複数のファイルを一度に選択できます"
)

# オプション設定
st.markdown("### ⚙️ オプション設定")
remove_pages = st.checkbox(
    "ページ表記 [ページ x] を削除する",
    value=False,
    help="チェックすると、テキスト内の **[ページ x]** 形式の表記が削除されます"
)

if uploaded_files and len(uploaded_files) > 0:
    st.success(f"✅ {len(uploaded_files)}個のファイルを読み込みました")
    
    # アップロードされたファイル一覧を表示
    with st.expander("📄 アップロードされたファイル一覧", expanded=False):
        for i, file in enumerate(uploaded_files, 1):
            st.markdown(f"{i}. `{file.name}`")
    
    # 処理ボタン
    if st.button("🔄 全ファイルを分割処理", type="primary"):
        with st.spinner("処理中..."):
            all_file_sections = {}
            total_sections = 0
            error_files = []
            
            # 各ファイルを処理
            for uploaded_file in uploaded_files:
                try:
                    # ファイルを読み込み
                    text_content = uploaded_file.read().decode('utf-8')
                    
                    # テキストを分割
                    sections = split_by_sections(text_content, remove_pages)
                    
                    if len(sections) > 0:
                        all_file_sections[uploaded_file.name] = sections
                        total_sections += len(sections)
                    else:
                        error_files.append(f"{uploaded_file.name} (見出しが見つかりません)")
                
                except UnicodeDecodeError:
                    error_files.append(f"{uploaded_file.name} (エンコーディングエラー)")
                except Exception as e:
                    error_files.append(f"{uploaded_file.name} ({str(e)})")
            
            # 結果を表示
            st.markdown("---")
            st.markdown("### 📊 分割結果")
            
            if len(all_file_sections) > 0:
                st.info(f"**{len(all_file_sections)}個のファイル**から**{total_sections}個のセクション**に分割されました")
                
                # ファイルごとの詳細を表示
                st.markdown("#### 📄 生成されるファイル一覧:")
                for original_filename, sections in all_file_sections.items():
                    st.markdown(f"**{original_filename}** → {len(sections)}個のセクション")
                    
                    base_name = Path(original_filename).stem
                    safe_base_name = sanitize_filename(base_name)
                    
                    for number, title, content in sections:
                        safe_title = sanitize_filename(title)
                        filename = f"{safe_base_name}_{number}_{safe_title}.txt"
                        lines = len(content.split('\n'))
                        chars = len(content)
                        st.markdown(f"  - `{filename}` ({lines}行, {chars}文字)")
                
                # エラーがあったファイルを表示
                if error_files:
                    st.warning("⚠️ 以下のファイルは処理できませんでした:")
                    for error_file in error_files:
                        st.markdown(f"  - {error_file}")
                
                # ZIPファイルを作成
                zip_data = create_zip_from_multiple_files(all_file_sections)
                
                # ダウンロードボタン
                st.markdown("---")
                st.download_button(
                    label="📥 全ファイルをZIPでダウンロード",
                    data=zip_data,
                    file_name="textbook_sections_all.zip",
                    mime="application/zip",
                    type="primary"
                )
                
                st.success("✅ 処理が完了しました!上のボタンからZIPファイルをダウンロードできます。")
            else:
                st.error("❌ 処理できるファイルがありませんでした。")
                if error_files:
                    st.markdown("**エラー詳細:**")
                    for error_file in error_files:
                        st.markdown(f"  - {error_file}")

else:
    st.info("👆 まずはファイルをアップロードしてください(複数選択可能)")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>📚 Textbook Section Splitter v2.0</p>
    <p>複数のMarkdownテキストを ### 見出しで自動分割</p>
</div>
""", unsafe_allow_html=True)
