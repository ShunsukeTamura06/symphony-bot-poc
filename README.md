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

## SSL証明書関連の注意事項

企業環境で自己署名証明書やプロキシが使用されている場合のSSL証明書検証エラーに対応済みです。

### 対応内容:
- SSL証明書検証の無効化（開発/テスト環境用）
- urllib3の警告メッセージ抑制
- プロキシ設定対応（config.json.templateに設定例あり）

### プロキシ環境での設定:
必要に応じて`config.json`に以下のプロキシ設定を追加:
```json
{
  "proxyURL": "http://proxy.company.com:8080",
  "proxyUsername": "username",
  "proxyPassword": "password"
}
```

## 本番環境での注意点

本番環境では適切な証明書を使用し、SSL検証を有効にすることを推奨します。
