# -*- coding: utf-8 -*-
#
#    Created on 2011/05/19
#    Created by H.Hiro
#
# キー/ゲームパッドのボタンが連打と判定されるのを抑制するための機構
# 
# つかいかた（例）
# 
# from pygame.locals import *
# from pywaz.device.key import Key
# from keysuppressor import KeySuppressor
# 
# # 0.2秒の間は、そのキーが押し続けられていても連打とみなさない
# keysupp = KeySuppressor(0.2)
# 
# if Key.is_press(K_RETURN):
#     if keysupp.press(K_RETURN):
#         # ここに、キーが押されたと判断されたときの処理を書く
# elif Key.is_press(K_BACKSPACE):
#     if keysupp.press(K_BACKSPACE):
#         # ここに、キーが押されたと判断されたときの処理を書く
# 
# keysupp.tryの引数は、
# * 押されたキーに対して一意に決定できること
# * dictionaryのキーに出来ること
# が必要です。なのでゲームパッドの場合、例えば
#     keysupp.try("%d %d" % (gamepad_id, button_id))
# のようにする必要があります。

import time

class KeySuppressor:
    def __init__(self, seconds):
        self.seconds = seconds
        self.last_press_key = {}
    
    def press(self, keyname):
        time_now = time.time()
        if (keyname not in self.last_press_key) or (time_now - self.last_press_key[keyname] >= self.seconds):
            # キーを押されたと判断する場合
            self.last_press_key[keyname] = time_now
            return True
        
        # キーを押されてない（前回そのキーを押してから十分時間が経ってない）場合
        return False
