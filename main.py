#!/usr/bin/env python3

import logging
import json
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.listeners.im_listener_test_imp import IMListenerTestImp
from sym_api_client_python.listeners.room_listener_test_imp import RoomListenerTestImp
from sym_api_client_python.listeners.elements_listener_test_imp import ElementsListenerTestImp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymphonyFormBot:
    def __init__(self, config_path="config.json"):
        # 設定ファイルを読み込み
        self.configure = SymConfig(config_path)
        self.configure.load_config()
        
        # RSA認証
        auth = SymBotRSAAuth(self.configure)
        auth.authenticate()
        
        # Bot クライアントを初期化
        self.bot_client = SymBotClient(auth, self.configure)
        
        # 監視対象のルームID（設定から読み込み）
        self.target_room_id = self.configure.data.get('target_room_id', '')
        
        # リスナーを設定
        self.setup_listeners()
        
    def setup_listeners(self):
        # ルームリスナー
        room_listener = CustomRoomListener(self)
        self.bot_client.get_datafeed_event_service().add_room_listener(room_listener)
        
        # エレメントリスナー（フォーム送信用）
        elements_listener = CustomElementsListener(self)
        self.bot_client.get_datafeed_event_service().add_elements_listener(elements_listener)
        
    def send_form_message(self, stream_id):
        """入力フォームをチャットに送信"""
        form_message = '''
        <messageML>
            <form id="user-info-form">
                <h2>ユーザー情報入力フォーム</h2>
                <text-field name="name" placeholder="お名前" required="true"/>
                <text-field name="email" placeholder="メールアドレス" required="true"/>
                <select name="department">
                    <option value="sales">営業部</option>
                    <option value="engineering">エンジニアリング部</option>
                    <option value="marketing">マーケティング部</option>
                    <option value="hr">人事部</option>
                </select>
                <textarea name="comment" placeholder="コメント（任意）"/>
                <button name="submit" type="action">送信</button>
                <button type="reset">リセット</button>
            </form>
        </messageML>
        '''
        
        try:
            self.bot_client.get_message_client().send_msg(stream_id, form_message)
            logger.info(f"フォームを送信しました: {stream_id}")
        except Exception as e:
            logger.error(f"フォーム送信エラー: {e}")
    
    def process_form_submission(self, form_data, stream_id):
        """フォーム送信データを処理"""
        try:
            # フォームデータから値を抽出
            name = form_data.get('name', 'N/A')
            email = form_data.get('email', 'N/A')
            department = form_data.get('department', 'N/A')
            comment = form_data.get('comment', 'N/A')
            
            logger.info(f"フォームデータ受信:")
            logger.info(f"  名前: {name}")
            logger.info(f"  メール: {email}")
            logger.info(f"  部署: {department}")
            logger.info(f"  コメント: {comment}")
            
            # 確認メッセージを送信
            response_message = f'''
            <messageML>
                <h3>✅ 入力内容を受信しました</h3>
                <p><b>名前:</b> {name}</p>
                <p><b>メールアドレス:</b> {email}</p>
                <p><b>部署:</b> {department}</p>
                <p><b>コメント:</b> {comment}</p>
                <p>データが正常に処理されました。</p>
            </messageML>
            '''
            
            self.bot_client.get_message_client().send_msg(stream_id, response_message)
            
            # 必要に応じてここでデータベースへの保存や外部APIへの送信などを実行
            
        except Exception as e:
            logger.error(f"フォームデータ処理エラー: {e}")
            error_message = "<messageML>❌ データ処理中にエラーが発生しました。</messageML>"
            self.bot_client.get_message_client().send_msg(stream_id, error_message)
    
    def start_listening(self):
        """データフィードのリスニングを開始"""
        logger.info(f"Bot started. Monitoring room: {self.target_room_id}")
        try:
            self.bot_client.get_datafeed_event_service().start_datafeed()
        except Exception as e:
            logger.error(f"Datafeed error: {e}")

class CustomRoomListener(RoomListenerTestImp):
    def __init__(self, bot):
        self.bot = bot
    
    def on_room_msg(self, msg):
        """ルームメッセージを受信した際の処理"""
        try:
            stream_id = msg.get('stream', {}).get('streamId')
            message_text = msg.get('message', '')
            user_id = msg.get('user', {}).get('userId')
            
            # 監視対象のルームかチェック
            if stream_id != self.bot.target_room_id:
                return
            
            # Bot自身のメッセージは無視
            if user_id == self.bot.bot_client.get_bot_user_info().get('userId'):
                return
            
            # フォーム要求のコマンドをチェック
            if any(keyword in message_text.lower() for keyword in ['@bot', 'フォーム', 'form', '入力']):
                logger.info(f"フォーム要求を受信: {message_text}")
                self.bot.send_form_message(stream_id)
                
        except Exception as e:
            logger.error(f"ルームメッセージ処理エラー: {e}")

class CustomElementsListener(ElementsListenerTestImp):
    def __init__(self, bot):
        self.bot = bot
    
    def on_elements_action(self, action):
        """エレメントアクション（フォーム送信）を受信した際の処理"""
        try:
            stream_id = action.get('stream', {}).get('streamId')
            form_id = action.get('formId')
            form_values = action.get('formValues', {})
            
            # 監視対象のルームかチェック
            if stream_id != self.bot.target_room_id:
                return
            
            # 対象のフォームかチェック
            if form_id == 'user-info-form' and form_values.get('action') == 'submit':
                logger.info(f"フォーム送信を受信: {form_id}")
                self.bot.process_form_submission(form_values, stream_id)
                
        except Exception as e:
            logger.error(f"エレメントアクション処理エラー: {e}")

if __name__ == "__main__":
    try:
        bot = SymphonyFormBot()
        bot.start_listening()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
