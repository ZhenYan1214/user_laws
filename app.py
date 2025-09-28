from flask import Flask, request
import json
import os
from datetime import datetime
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    FlexSendMessage, PostbackEvent, PostbackAction,
    QuickReply, QuickReplyButton, MessageAction
)

app = Flask(__name__)

# 用戶數據文件路徑
USER_DATA_FILE = "user_data.json"

def load_user_data():
    """載入用戶數據"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_data(data):
    """保存用戶數據"""
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存用戶數據失敗: {e}")

# 載入用戶同意狀態
user_consent = load_user_data()

def create_terms_flex_message():
    """創建專業的用戶條款 Flex Message"""
    return {
        "type": "flex",
        "altText": "糖小護服務條款",
        "contents": {
            "type": "bubble",
            "size": "mega",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🩺 糖小護",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#2E86AB",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "個人健康數據服務條款",
                        "size": "md",
                        "color": "#5A9FD4",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#F0F8FF",
                "paddingAll": "20px",
                "cornerRadius": "10px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "歡迎使用糖小護健康管理服務！",
                        "weight": "bold",
                        "size": "lg",
                        "color": "#2E86AB",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#E6F3FF"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "📊 資料蒐集範圍",
                                "weight": "bold",
                                "size": "sm",
                                "color": "#2E86AB",
                                "margin": "lg"
                            },
                            {
                                "type": "text",
                                "text": "• 血糖數值記錄\n• 健康諮詢對話內容\n• 上傳的醫療相關圖片\n• 使用行為統計資料",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🎯 使用目的",
                                "weight": "bold",
                                "size": "sm",
                                "color": "#2E86AB",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• 提供個人化健康建議\n• 生成專屬健康報表\n• 改善服務品質\n• 緊急健康提醒",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🔒 隱私保護",
                                "weight": "bold",
                                "size": "sm",
                                "color": "#2E86AB",
                                "margin": "md"
                            },
                            {
                                "type": "text",
                                "text": "• 資料採用加密儲存\n• 不會與第三方分享\n• 可隨時要求刪除資料\n• 符合個資法規範",
                                "size": "xs",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "sm"
                            }
                        ]
                    }
                ],
                "paddingAll": "20px",
                "spacing": "sm"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "繼續使用即表示您同意上述條款",
                        "size": "xs",
                        "color": "#999999",
                        "align": "center",
                        "margin": "sm"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#E6F3FF"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "style": "secondary",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "暫不同意",
                                    "text": "不同意"
                                },
                                "color": "#CCCCCC",
                                "flex": 1
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "action": {
                                    "type": "message",
                                    "label": "同意並開始使用",
                                    "text": "同意"
                                },
                                "color": "#2E86AB",
                                "flex": 2
                            }
                        ],
                        "spacing": "sm",
                        "margin": "md"
                    }
                ],
                "paddingAll": "20px"
            }
        }
    }

def create_welcome_message():
    """創建歡迎訊息 Flex Message"""
    return {
        "type": "flex",
        "altText": "歡迎使用糖小護",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "🎉 歡迎加入糖小護！",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFF",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "您的專屬健康管理助手",
                        "size": "md",
                        "color": "#E6F3FF",
                        "align": "center",
                        "margin": "sm"
                    }
                ],
                "backgroundColor": "#2E86AB",
                "paddingAll": "20px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "✅ 條款同意完成",
                        "weight": "bold",
                        "size": "md",
                        "color": "#2E86AB",
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": "#E6F3FF"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "🩺 您現在可以：",
                                "weight": "bold",
                                "size": "sm",
                                "color": "#2E86AB",
                                "margin": "lg"
                            },
                            {
                                "type": "text",
                                "text": "📝 記錄每日血糖數值\n💬 諮詢健康相關問題\n📸 上傳檢查報告圖片\n📊 查看個人健康報表",
                                "size": "sm",
                                "color": "#666666",
                                "wrap": True,
                                "margin": "sm"
                            }
                        ]
                    },
                    {
                        "type": "text",
                        "text": "現在就開始輸入您的血糖數值或問我任何健康問題吧！",
                        "size": "sm",
                        "color": "#5A9FD4",
                        "wrap": True,
                        "margin": "lg",
                        "align": "center"
                    }
                ],
                "paddingAll": "20px"
            }
        }
    }

@app.route("/callback", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        access_token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
        secret = os.environ.get('LINE_CHANNEL_SECRET')
        
        if not access_token or not secret:
            print("錯誤: LINE_CHANNEL_ACCESS_TOKEN 或 LINE_CHANNEL_SECRET 環境變數未設定")
            return
        line_bot_api = LineBotApi(access_token)
        handler = WebhookHandler(secret)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)

        tk = json_data['events'][0]['replyToken']
        user_id = json_data['events'][0]['source']['userId']  # 使用者 ID
        msg_type = json_data['events'][0]['message']['type']

        if msg_type == 'text':
            msg = json_data['events'][0]['message']['text']
            print(f"收到: {msg}")

            # 檢查是否已經同意
            if user_id not in user_consent:
                # 新用戶 → 發送專業的條款頁面
                flex_message = create_terms_flex_message()
                line_bot_api.reply_message(tk, FlexSendMessage(
                    alt_text=flex_message["altText"],
                    contents=flex_message["contents"]
                ))
                user_consent[user_id] = {
                    "status": "pending",
                    "first_contact": datetime.now().isoformat(),
                    "blood_sugar_records": []
                }
                save_user_data(user_consent)
                return

            elif user_consent[user_id].get("status") == "pending":
                # 等待用戶回覆
                if msg == "同意":
                    # 發送歡迎訊息
                    welcome_message = create_welcome_message()
                    line_bot_api.reply_message(tk, FlexSendMessage(
                        alt_text=welcome_message["altText"],
                        contents=welcome_message["contents"]
                    ))
                    user_consent[user_id]["status"] = "agreed"
                    user_consent[user_id]["agreed_time"] = datetime.now().isoformat()
                    save_user_data(user_consent)
                    return
                elif msg == "不同意":
                    reply = "感謝您的回覆。如果您改變心意，歡迎隨時重新開始對話。\n\n為了保護您的隱私，我們將不會保存任何資料。"
                    user_consent[user_id]["status"] = "disagreed"
                    user_consent[user_id]["disagreed_time"] = datetime.now().isoformat()
                    save_user_data(user_consent)
                else:
                    reply = "請點選條款頁面中的「同意並開始使用」或「暫不同意」按鈕，或直接回覆「同意」或「不同意」。"

            else:
                # 已經有狀態了
                if user_consent[user_id].get("status") == "agreed":
                    # 這裡可以加入您的主要功能邏輯
                    if "血糖" in msg or any(char.isdigit() for char in msg):
                        # 記錄血糖數據
                        blood_sugar_record = {
                            "value": msg,
                            "timestamp": datetime.now().isoformat()
                        }
                        user_consent[user_id]["blood_sugar_records"].append(blood_sugar_record)
                        save_user_data(user_consent)
                        
                        record_count = len(user_consent[user_id]["blood_sugar_records"])
                        reply = f"📊 已記錄您的血糖數據：{msg}\n\n這是您的第 {record_count} 筆記錄。如需查看報表或更多功能，請繼續輸入指令。"
                    elif "報表" in msg or "圖表" in msg:
                        record_count = len(user_consent[user_id]["blood_sugar_records"])
                        if record_count > 0:
                            recent_records = user_consent[user_id]["blood_sugar_records"][-5:]
                            records_text = "\n".join([f"• {r['value']} ({r['timestamp'][:10]})" for r in recent_records])
                            reply = f"📈 您的血糖記錄（最近5筆）：\n{records_text}\n\n總共已記錄 {record_count} 筆數據。完整報表功能開發中！"
                        else:
                            reply = "📈 您還沒有血糖記錄。請先輸入血糖數值開始記錄！"
                    else:
                        reply = f"💬 糖小護收到您的訊息：{msg}\n\n我正在學習更多健康知識來更好地為您服務！您可以輸入血糖數值或健康相關問題。"
                elif user_consent[user_id].get("status") == "disagreed":
                    reply = "由於您尚未同意服務條款，目前無法使用糖小護的功能。\n\n如果您想重新開始，請輸入「重新開始」。"
                    if msg == "重新開始":
                        del user_consent[user_id]
                        save_user_data(user_consent)
                        flex_message = create_terms_flex_message()
                        line_bot_api.reply_message(tk, FlexSendMessage(
                            alt_text=flex_message["altText"],
                            contents=flex_message["contents"]
                        ))
                        return

        else:
            reply = "糖小護目前支援文字訊息，圖片功能正在開發中！\n\n請輸入您的血糖數值或健康相關問題。"

        print("回覆:", reply)
        line_bot_api.reply_message(tk, TextSendMessage(reply))

    except Exception as e:
        print("錯誤:", e)
        print("收到內容:", body)
    
    return "OK"

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)