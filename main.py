from wxauto import WeChat
import requests
import time
import threading
from datetime import datetime

import os
import pprint

from config import *


### 全局变量 ###

# 存储上下文
CHAT_CONTEXTS = {} 


### 函数 ###

def current_time():
    # 添加时间戳
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

def get_deepseek_response(message, user_name):
    # 调用 DeepSeek API 获取回复
    try:
        # 添加上下文
        if user_name not in CHAT_CONTEXTS:
            CHAT_CONTEXTS[user_name] = []

        CHAT_CONTEXTS[user_name].append({"role": "user", "content": message})

        # 保持上下文长度不超过10条消息
        if len(CHAT_CONTEXTS[user_name]) > 10:
            CHAT_CONTEXTS[user_name] = CHAT_CONTEXTS[user_name][-10:]

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": PROMPT_CONTENT},
                *CHAT_CONTEXTS[user_name]
            ],
            "max_tokens": MAX_TOKEN,
            "temperature": TEMPERATURE
        }

        # 把每次的对话打印出来，方便排查
        logger.info(data["messages"])

        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        reply = response.json()['choices'][0]['message']['content']

        # 添加回复到上下文
        CHAT_CONTEXTS[user_name].append({"role": "assistant", "content": reply})

        return reply
    except Exception as e:
        logger.error(f"调用 DeepSeek API 失败: {str(e)}")
        return "我肚子疼..."


def get_wx_obj(who='文件传输助手'):
    try:
        # 获取微信窗口对象
        wx = WeChat()
        # 输出 > 初始化成功，获取到已登录窗口：xxxx
        # 切换到聊天页面
        # wx.SwitchToChat()
        # 切换到指定好友聊天框
        # wx.ChatWith(who)
        # print(wx)
        return wx
    except Exception as e:
        logger.critical(f"发生异常: {str(e)}", exc_info=True)


def reply_person(wx, listen_list):
    # 首先设置一个监听列表，列表元素为指定好友（或群聊）的昵称 LISTEN_LIST
    # 然后调用`AddListenChat`方法添加监听对象，其中可选参数`savepic`为是否保存新消息图片

    for chat_name in listen_list:
        wx.AddListenChat(who=chat_name, savepic=True)

    # 持续监听消息，并且收到消息后进行回复
    # GetListenMessage方法获取到的msgs是一个字典，键为监听对象，值为消息对象列表；值的列表与GetAllMessage方法获取到的消息对象列表一样
    # wait_time = 2  # 设置1秒查看一次是否有新消息
    is_first = True
    while True:
        # 5s 内一直去监听聊天窗口，获取聊天信息
        chat_msgs_list = []
        wait_time = 1
        while wait_time < 6:
            # 获取一次聊天记录
            chat_msgs = wx.GetListenMessage()
            # 存起来
            chat_msgs_list.append(chat_msgs)
            time.sleep(1)
            wait_time += 1 

        # 初始化一个空字典来存储合并后的结果
        merged_chat_msgs_list = {}
        # 遍历输入数据
        for chat_msgs in chat_msgs_list:
            for key, value in chat_msgs.items():
                if key not in merged_chat_msgs_list:
                    merged_chat_msgs_list[key] = []
                merged_chat_msgs_list[key].extend(value)

        # 打印输出，进行调试
        # print(current_time())
        # pprint.pprint(msgs)
        for chat in merged_chat_msgs_list:
            chat_name = chat.who        # 获取聊天窗口名（人或群名）
            chat_msgs = merged_chat_msgs_list.get(chat)   # 获取消息内容，一组对话
            # print(type(chat_msgs))
            # print(chat_msgs[-1].sender)

            # 保留 friend 和 self 类型的消息
            filtered_chat_msgs = [msg for msg in chat_msgs if msg.type == 'friend' or msg.type == 'self']
            # 合并相邻相同key值的元素
            merged_chat_msgs = []
            for msg in filtered_chat_msgs:
                # msg.type: 获取消息类型
                # msg.sender: 消息发送者的名称
                # msg.content: 获取消息内容，字符串类型的消息内容
                if not merged_chat_msgs or merged_chat_msgs[-1].sender != msg.sender:
                    merged_chat_msgs.append(msg)
                else:
                    merged_chat_msgs[-1].content += msg.content      

            if is_first:
                # 如果是第一次
                reply = '我现在是AI，如果你想和我聊天，给我打个招呼吧！\n\n' + PROMPT_CONTENT
                chat.SendMsg(reply)
            else:
                msg = merged_chat_msgs[-1]
                if msg.type == 'friend':
                    # 如果最后是对方发的消息，就回复   
                    reply = get_deepseek_response(msg.content, msg.sender)
                    # ！！！ 回复收到，此处为`chat`而不是`wx` ！！！
                    for item in reply.split('。'):
                        chat.SendMsg(item)
        is_first = False    
        # time.sleep(wait)

def reply_group():
    pass
    

if __name__ == '__main__':
    try:
        wx = get_wx_obj()
        reply_person(wx, PERSON_LISTEN_LIST)
    except KeyboardInterrupt:
        logger.info("用户终止")
    except Exception as e:
        logger.critical(f"发生异常: {str(e)}", exc_info=True)