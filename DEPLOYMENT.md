# 🚀 Streamlit Community Cloudへのデプロイ手順

このアプリを永久的なウェブサイトとして公開するための手順です。

## 📋 前提条件

✅ GitHubリポジトリが作成されている  
✅ リポジトリが公開(public)になっている  
✅ GitHubアカウントを持っている

## 🌐 デプロイ手順

### ステップ1: Streamlit Community Cloudにアクセス

1. [https://share.streamlit.io/](https://share.streamlit.io/) にアクセス
2. 「Sign up」または「Sign in」をクリック
3. GitHubアカウントでログイン

### ステップ2: 新しいアプリをデプロイ

1. 「New app」ボタンをクリック
2. 以下の情報を入力:
   - **Repository**: `oqllol/textbook-section-splitter`
   - **Branch**: `master`
   - **Main file path**: `app.py`
3. 「Deploy!」ボタンをクリック

### ステップ3: デプロイ完了を待つ

- 数分でデプロイが完了します
- 完了すると、永久的なURLが発行されます
- 例: `https://textbook-section-splitter.streamlit.app/`

## 🔗 公開URL

デプロイが完了すると、以下のような形式のURLが発行されます:

```
https://[app-name]-[random-string].streamlit.app/
```

このURLは永久的に有効で、誰でもアクセスできます。

## ⚙️ カスタムドメイン (オプション)

独自ドメインを使用したい場合:
1. Streamlit Community Cloudの設定画面で「Custom domain」を選択
2. 独自ドメインを設定

## 🔄 アプリの更新

GitHubリポジトリにコードをプッシュすると、自動的にアプリが更新されます:

```bash
git add .
git commit -m "Update app"
git push origin master
```

## 📊 使用制限

Streamlit Community Cloud 無料プランの制限:
- ✅ 無制限のアクセス
- ✅ 自動スリープ(非アクティブ時)
- ✅ 1つのアプリあたり1GBのメモリ
- ✅ 1つのアカウントで3つまでのアプリ

## 🆘 トラブルシューティング

### デプロイに失敗する場合

1. `requirements.txt` が正しいか確認
2. `app.py` にエラーがないか確認
3. Streamlit Community Cloudのログを確認

### アプリが起動しない場合

1. ローカルで `streamlit run app.py` を実行してテスト
2. エラーメッセージを確認
3. 必要に応じて依存パッケージを更新

## 📞 サポート

問題が発生した場合:
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Happy Deploying! 🚀**
