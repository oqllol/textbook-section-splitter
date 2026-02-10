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

# ZIPファイルを作成する関数
def create_zip(sections):
    """
    セクションのリストからZIPファイルを作成
    
    Args:
        sections: [(番号, タイトル, 内容), ...] のリスト
    
    Returns:
        ZIPファイルのバイトデータ
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for number, title, content in sections:
            # ファイル名を作成
            safe_title = sanitize_filename(title)
            filename = f"{number}_{safe_title}.txt"
            
            # ZIPに追加
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# メインのUI
st.markdown("---")

# ファイルアップロード
uploaded_file = st.file_uploader(
    "📁 Markdownファイル(.md または .txt)をアップロードしてください",
    type=['md', 'txt'],
    help="教科書の文字起こしテキストファイルを選択してください"
)

# オプション設定
st.markdown("### ⚙️ オプション設定")
remove_pages = st.checkbox(
    "ページ表記 [ページ x] を削除する",
    value=False,
    help="チェックすると、テキスト内の **[ページ x]** 形式の表記が削除されます"
)

if uploaded_file is not None:
    # ファイルを読み込み
    try:
        text_content = uploaded_file.read().decode('utf-8')
        
        st.success(f"✅ ファイル「{uploaded_file.name}」を読み込みました")
        
        # 処理ボタン
        if st.button("🔄 分割処理を実行", type="primary"):
            with st.spinner("処理中..."):
                # テキストを分割
                sections = split_by_sections(text_content, remove_pages)
                
                if len(sections) == 0:
                    st.error("❌ ### 見出しが見つかりませんでした。ファイルの形式を確認してください。")
                else:
                    # 結果を表示
                    st.markdown("---")
                    st.markdown("### 📊 分割結果")
                    st.info(f"**{len(sections)}個のファイル**に分割されました")
                    
                    # ファイル一覧を表示
                    st.markdown("#### 📄 生成されるファイル一覧:")
                    for number, title, content in sections:
                        safe_title = sanitize_filename(title)
                        filename = f"{number}_{safe_title}.txt"
                        lines = len(content.split('\n'))
                        chars = len(content)
                        st.markdown(f"- `{filename}` ({lines}行, {chars}文字)")
                    
                    # ZIPファイルを作成
                    zip_data = create_zip(sections)
                    
                    # ダウンロードボタン
                    st.markdown("---")
                    st.download_button(
                        label="📥 ZIPファイルをダウンロード",
                        data=zip_data,
                        file_name="textbook_sections.zip",
                        mime="application/zip",
                        type="primary"
                    )
                    
                    st.success("✅ 処理が完了しました!上のボタンからZIPファイルをダウンロードできます。")
    
    except UnicodeDecodeError:
        st.error("❌ ファイルの読み込みに失敗しました。UTF-8エンコーディングのテキストファイルを使用してください。")
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {str(e)}")

else:
    st.info("👆 まずはファイルをアップロードしてください")

# フッター
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    <p>📚 Textbook Section Splitter v1.0</p>
    <p>Markdownテキストを ### 見出しで自動分割</p>
</div>
""", unsafe_allow_html=True)
