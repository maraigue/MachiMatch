# -*- coding: utf-8 -*-
#
#    Created on 2011/05/05
#    Created by giginet
#
import random
import pygame
import settings
from pywaz.core.game import Game
from pywaz.utils.vector import Vector
from main.panel import Panel

class Immigrant(Panel):
    IMAGEPATH = u"../resources/image/main/human00.png"
    MAXFRAME = 4
    IMAGEWIDTH = 15
    IMAGEHEIGHT = 30
    APF = 2
    u"""移民クラス"""
    SPEED = 3
    def __init__(self, x, y, world):
        u"""移民を生成するマップ座標x, y, """
        super(Immigrant, self).__init__(x, y)
        self.direction = 0    #右上から時計回りに0~3
        self.world = world    #ステージ情報を保持しておく
        self.current_ground = self.world.get_panel_on(self.point)   #今いるパネル
        self.goal_ground = self.current_ground #ゴールのあるパネル
        self.x, self.y = self.current_ground.surface_bottom_edge.to_pos()
        self.animation_enable = True
        self.population = None
    u"""
        とりあえずマスの真ん中まで進む
        真ん中まで辿り着いたら、その床と周辺の床のnode情報を見て、繋がっているかどうか判定する
        直進できる場合、直進して次の床へ
        直進できない場合、向かって左右いずれかへランダムに進む
        それもできない場合、進行方向逆向きに進む
    """
    def update(self):
        current = Vector(self.x, self.y)
        sub = self.goal - current
        if sub.length < self.SPEED:
            u"""ゴールに到着したとき"""
            self.current_ground = self.goal_ground
            if not self.current_ground.is_road():
                u"""道以外のマスの時"""
                if self.current_ground.is_territory():
                    u"""領土の時"""
                    self.current_ground.owner.city.increase_population(self.population) # 街の人口を増やす
                self.world.i_manager.remove_immigrant(self)
                return
            else:
                u"""道の時"""
                self.x, self.y = self.goal.to_pos()
                self._set_goal()
        else:
            u"""ゴールに到着していないとき"""
            sub = sub.resize(self.SPEED)
            current = current + sub
            self.x, self.y = current.to_pos()
        super(Panel, self).update()
    def draw(self, surface=Game.get_screen()):
        x = self.x - 7
        y = self.y - 25
        #pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), 3)
        # ToDo　画像を差し替えたら書き直すからとりあえずハードコーディング
        return super(Panel, self).draw(surface, dest=pygame.rect.Rect(x, y, settings.PANELSIZE, settings.PANELSIZE))
    def _set_goal(self):
        u"""隣接した4つのパネルを見て動きを決める"""
        front = self.world.get_panel_from(self.current_ground, self.direction) #自分の前方にあるパネルを取ってくる
        if front.is_connect_with(self.current_ground):
            u"""前方に進めるとき"""
            self.goal_ground = front
        else:
            left_direction = (self.direction-1)%4
            right_direction = (self.direction+1)%4
            if left_direction < 0: left_direction = 3
            left = self.world.get_panel_from(self.current_ground, left_direction)
            right = self.world.get_panel_from(self.current_ground, right_direction)
            next_goals = [] #ゴール候補リスト (ground, direction)を格納
            if left.is_connect_with(self.current_ground): next_goals.append((left, left_direction))
            if right.is_connect_with(self.current_ground): next_goals.append((right, right_direction))
            if next_goals:
                u"""左右いずれかに進めるとき"""
                u"""奥側（direction=0）に進めたら優先的に採用"""
                for g, d in next_goals:
                    if d == 0:
                        self.goal_ground = g
                        self.direction = d
                        break
                else:
                    u"""それ以外の時はランダム"""
                    self.goal_ground, self.direction = random.choice(next_goals)
            else:
                u"""左右いずれにも進めないとき"""
                d = (self.direction+2)%4
                back = self.world.get_panel_from(self.current_ground, d)
                if back.is_connect_with(self.current_ground):
                    self.goal_ground = back
                    self.direction = d
            self.ainfo.index = self.direction
    @property
    def goal(self):
        u"""次に移民が向かう座標を返す"""
        if not self.goal_ground.is_road():
            u"""道以外の場合、端の座標を返す"""
            if self.direction == 0:
                return self.goal_ground.surface_bottom_edge
            elif self.direction == 1:
                return self.goal_ground.surface_left_edge
            elif self.direction == 2:    
                return self.goal_ground.surface_above_edge    
            elif self.direction == 3:
                return self.goal_ground.surface_right_edge
        return self.goal_ground.surface_center