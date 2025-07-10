# Symphony Bot PoC

Symphonyのbotでフォーム送信を監視するPoCプロジェクト

## セットアップ

1. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

2. 設定ファイルを作成:
```bash
cp config.json.template config.json
```

3. `config.json`を編集して以下を設定:
   - Symphony pod情報
   - Bot認証情報
   - 監視対象のルームID

4. RSA鍵ペアを`rsa/`フォルダに配置

5. Botを実行:
```bash
python main.py
```

## 使用方法

1. 監視対象のルームで「@bot」「フォーム」「入力」などのキーワードを含むメッセージを送信
2. Botが入力フォームを投稿
3. フォームに入力してSubmitボタンをクリック
4. Botが入力内容を受信・処理して確認メッセージを返信

## 機能

- 特定ルームの監視
- キーワードベースのフォーム表示
- ユーザー入力の受信・処理
- 確認メッセージの自動返信
