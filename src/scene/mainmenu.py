# -*- coding: utf-8 -*-
#
#    Created on 2011/04/17
#    Created by giginet
#
import pygame
from pygame.locals import *

from pywaz.scene.abstractscene import Scene
from pywaz.core.game import Game
from pywaz.sprite.image import Image
from pywaz.sprite.animation import Animation, AnimationInfo
from pywaz.mixer.bgm import BGM
from pywaz.utils.vector import Vector
from pywaz.utils.timer import Timer
from pywaz.device.mouse import Mouse
from pywaz.sprite.button import Button
from pywaz.device.joypad import JoyPad
from pywaz.device.key import Key

from keysuppressor import KeySuppressor
import os.path
import sys # for debug

class MainMenuScene(Scene):
    BACKGROUND = (255,255,255)
    CURSOR_BORDER = 10 # カーソルを表す画像が、選択肢を表す画像からどれだけずらして配置されるか
    IMAGE_PATH = "../resources/image/menu"
    KEY_REPEAT_TIME = 0.2 # 何秒以内の間なら、キーが押され続けていても連打とみなさないか
    
    # 2Players, 3Players, 4Playersの画像を読み込む
    def load_player_selection(self, joypad_number):
        fail = ("" if joypad_number >= 2 else "x")
        self.player2 = Image(os.path.join(self.IMAGE_PATH, "player2%s.png" % fail), alpha=False)
        
        fail = ("" if joypad_number >= 3 else "x")
        self.player3 = Image(os.path.join(self.IMAGE_PATH, "player3%s.png" % fail), alpha=False)
        
        fail = ("" if joypad_number >= 4 else "x")
        self.player4 = Image(os.path.join(self.IMAGE_PATH, "player4%s.png" % fail), alpha=False)
    
    # カーソルをx方向にdir_x、y方向にdir_yだけ動かす
    def set_cursor_pos(self, dir_x, dir_y):
        target_option = False
        sys.stderr.write("(%d,%d)" % (self.cursor_logical_x, self.cursor_logical_y))
        while not target_option:
            # y方向
            self.cursor_logical_y = (self.cursor_logical_y + dir_y) % len(self.menu_options)
            # x方向
            self.cursor_logical_x = (self.cursor_logical_x + dir_x) % len(self.menu_options[self.cursor_logical_y])
            sys.stderr.write("->(%d,%d)" % (self.cursor_logical_x, self.cursor_logical_y))
            # 描画位置の計算
            target_option = self.menu_options[self.cursor_logical_y][self.cursor_logical_x]
            # ここで、指定した位置に選択肢がなかった場合、
            # もう一度カーソルの移動を適用する。例えば
            # [Option1] [Option2] [Option3]
            # [Option4]           [Option6]
            # という並びで、[Option4]にカーソルがある状態で右キーを
            # 押したとする。このとき、カーソルは一度[Option4]と[Option6]の
            # 間に行こうとするが、それが無効と判断され、もう一度
            # カーソルが右に動く（結果、[Option6]でカーソルが止まる）。
        
        sys.stderr.write("\n")
        # 指定した位置に選択肢があった場合に、はじめてwhileループを抜ける。
        # ここでカーソルの描画位置を計算。
        self.cursor.x = target_option.x - self.CURSOR_BORDER
        self.cursor.y = target_option.y - self.CURSOR_BORDER
    
    # ゲームを始める
    def start_game(self, player_number):
        # TODO: ここに、ゲーム画面へ移動するコードを書く
        pass
    
    def ready(self, *args, **kwargs):
        super(MainMenuScene, self).ready()
        
        self.joypads = JoyPad().sticks
        
        self.logo = Image(os.path.join(self.IMAGE_PATH, "kawaz.png"), alpha=False)
        self.config = Image(os.path.join(self.IMAGE_PATH, "config.png"), alpha=False)
        self.exit = Image(os.path.join(self.IMAGE_PATH, "exit.png"), alpha=False)
        self.cursor = Image(os.path.join(self.IMAGE_PATH, "cursor.png"), alpha=True)
        self.load_player_selection(len(self.joypads))
        
        self.logo.x = 353; self.logo.y = 260
        self.player2.x = 160; self.player2.y = 400
        self.player3.x = 380; self.player3.y = 400
        self.player4.x = 600; self.player4.y = 400
        self.config.x  = 380; self.config.y  = 460
        self.exit.x    = 600; self.exit.y    = 460
        # カーソル位置を初期化
        self.menu_options = ((self.player2, self.player3, self.player4),
                             (None, self.config, self.exit))
        self.menu_actions = (
            (lambda:self.start_game(2), # self.player2
             lambda:self.start_game(3), # self.player3
             lambda:self.start_game(4),)# self.player4
            ,
            (lambda:0, # None
             lambda:Game.get_scene_manager().change_scene('keysetting'), #self.config
             lambda:sys.exit()) # self.exit
            )
        self.cursor_logical_x = 0;
        self.cursor_logical_y = 0;
        self.set_cursor_pos(0, 0)
        
        self.sprites.add(self.logo)
        self.sprites.add(self.player2)
        self.sprites.add(self.player3)
        self.sprites.add(self.player4)
        self.sprites.add(self.config)
        self.sprites.add(self.exit)
        self.sprites.add(self.cursor)
        
        self.keysupp = KeySuppressor(self.KEY_REPEAT_TIME)
    
    def update(self):
        # Joypadによるカーソル操作
        # 各Joypadについて動きをチェックする
        for joypad_id in range(len(self.joypads)):
            # 直近のキー操作から
            xaxis = self.joypads[joypad_id].get_axis(0)
            yaxis = self.joypads[joypad_id].get_axis(1)
            if xaxis > 0.9:
                if self.keysupp.press("%d %d" % (joypad_id, K_RIGHT)):
                    self.set_cursor_pos(1, 0)
            elif xaxis < -0.9:
                if self.keysupp.press("%d %d" % (joypad_id, K_LEFT)):
                    self.set_cursor_pos(-1, 0)
            elif yaxis > 0.9:
                if self.keysupp.press("%d %d" % (joypad_id, K_DOWN)):
                    self.set_cursor_pos(0, 1)
            elif yaxis < -0.9:
                if self.keysupp.press("%d %d" % (joypad_id, K_UP)):
                    self.set_cursor_pos(0, -1)
            
            # ボタン
            for button_id in range(self.joypads[joypad_id].get_numbuttons()):
                if self.joypads[joypad_id].get_button(button_id):
                    self.menu_actions[self.cursor_logical_y][self.cursor_logical_x]()
        
        # キーボードによるカーソル操作
        if Key.is_press(K_RIGHT):
            if self.keysupp.press(K_RIGHT):
                self.set_cursor_pos(1, 0)
        elif Key.is_press(K_LEFT):
            if self.keysupp.press(K_LEFT):
                self.set_cursor_pos(-1, 0)
        elif Key.is_press(K_DOWN):
            if self.keysupp.press(K_DOWN):
                self.set_cursor_pos(0, 1)
        elif Key.is_press(K_UP):
            if self.keysupp.press(K_UP):
                self.set_cursor_pos(0, -1)
        elif Key.is_press(K_RETURN):
            self.menu_actions[self.cursor_logical_y][self.cursor_logical_x]()
