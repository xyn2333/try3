import pygame
import image
from settings import *
from hand_tracking import HandTracking
import cv2
import time
from butterfly import Butterfly
class Hand:
    def __init__(self):
        self.orig_image = image.load("Assets/hand_l.png", size=(HAND_SIZE, HAND_SIZE))
        self.image = self.orig_image.copy()
        self.image_smaller = image.load("Assets/hand_l.png", size=(HAND_SIZE - 50, HAND_SIZE - 50))
        self.rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, HAND_HITBOX_SIZE[0], HAND_HITBOX_SIZE[1])
        self.left_click = False
        self.close_start_time = None
        #self.hand_tracking = HandTracking()
        self.drag_start_time = None  # 记录手掌闭合的开始时间
        self.last_pos = self.rect.center
        self.dragging_insect = None  # 记录被拖拽的蝴蝶

    def follow_mouse(self): # change the hand pos center at the mouse pos
        self.rect.center = pygame.mouse.get_pos()
        #self.hand_tracking.display_hand()

    def follow_mediapipe_hand(self, x, y):
        self.rect.center = (x, y)

    def draw_hitbox(self, surface):
        pygame.draw.rect(surface, (200, 60, 0), self.rect)


    def draw(self, surface):
        image.draw(surface, self.image, self.rect.center, pos_mode="center")

        if DRAW_HITBOX:
            self.draw_hitbox(surface)


    def on_insect(self, insects): # return a list with all insects that collide with the hand hitbox
        return [insect for insect in insects if self.rect.colliderect(insect.rect)]


    def kill_insects(self, insects, score, sounds): # will kill the insects that collide with the hand when the left mouse button is pressed
        if self.left_click: # if left click
            for insect in self.on_insect(insects):
                insect_score = insect.kill(insects)
                score += insect_score
                sounds["slap"].play()
                if insect_score < 0:
                    sounds["screaming"].play()
        else:
            self.left_click = False
        return score

    def kill_insects(self, insects, score, sounds):
        if self.left_click:
            for insect in self.on_insect(insects):
                if isinstance(insect, Butterfly):
                    self.dragging_insect = insect  # 立即开始拖动蝴蝶
                    # 不杀死蝴蝶，只是开始拖动
                else:
                    insect_score = insect.kill(insects)
                    score += insect_score
                    sounds["slap"].play()
                    if insect_score < 0:
                        sounds["screaming"].play()
        else:
            self.left_click = False
            self.dragging_insect = None
        return score

    def update_dragging(self):
        if not self.left_click:
            self.dragging_insect = None

