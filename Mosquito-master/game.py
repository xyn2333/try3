import pygame
import time
import random
from settings import *
from background import Background
from hand import Hand
from hand_tracking import HandTracking
from mosquito import Mosquito
from butterfly import Butterfly
from bee import Bee
import cv2
import ui
import image

class Game:
    def __init__(self, surface):
        self.surface = surface
        self.background = Background()

        # Load camera
        self.cap = cv2.VideoCapture(0)

        self.sounds = {}
        self.sounds["slap"] = pygame.mixer.Sound(f"Assets/Sounds/slap.wav")
        self.sounds["slap"].set_volume(SOUNDS_VOLUME)
        self.sounds["screaming"] = pygame.mixer.Sound(f"Assets/Sounds/screaming.wav")
        self.sounds["screaming"].set_volume(SOUNDS_VOLUME)
        # 加载左手图像并缩放
        self.orig_image_l = image.load("Assets/hand_l.png", size=(HAND_SIZE, HAND_SIZE))
        self.image_smaller_l = image.load("Assets/hand_l.png", size=(HAND_SIZE - 50, HAND_SIZE - 50))
        # 加载右手图像并缩放
        self.orig_image_r = image.load("Assets/hand_r.png", size=(HAND_SIZE, HAND_SIZE))
        self.image_smaller_r = image.load("Assets/hand_r.png", size=(HAND_SIZE - 50, HAND_SIZE - 50))

        # Load the basket image
        self.basket_image = image.load("Assets/basket.png", size=(100, 100))
        self.basket_rect = self.basket_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def reset(self): # reset all the needed variables
        self.hand_tracking = HandTracking()
        self.hand = Hand()
        self.hands=[]
        self.insects = []
        self.insects_spawn_timer = 0
        self.score = 0
        self.game_start_time = time.time()


    def spawn_insects(self):
        t = time.time()
        if t > self.insects_spawn_timer:
            self.insects_spawn_timer = t + MOSQUITOS_SPAWN_TIME

            # increase the probability that the insect will be a bee over time
            nb = (GAME_DURATION-self.time_left)/GAME_DURATION * 100  / 2  # increase from 0 to 50 during all  the game (linear)
            if random.randint(0, 100) < nb:
                self.insects.append(Bee())

            else:
                self.insects.append(Mosquito())

            # spawn a other mosquito after the half of the game
            if self.time_left < GAME_DURATION/2:
                self.insects.append(Mosquito())

            # spawn a butterfly with some probability
            if random.randint(0, 100) < BUTTERFLY_SPAWN_PROBABILITY:
                self.insects.append(Butterfly())

    def load_camera(self):
        # 从摄像头捕获实际的图像数据
        _, self.frame = self.cap.read()


    def set_hand_position(self):
        self.frame = self.hand_tracking.scan_hands(self.frame)
        for h in range(len(self.hand_tracking.hands_closed)):
            hand = Hand()
            hand.rect.center = (self.hand_tracking.hands_x[h], self.hand_tracking.hands_y[h])
            hand.left_click = self.hand_tracking.hands_closed[h]
            self.hands.append(hand)

    def catch_insects(self, hand):
        for insect in self.insects:
            if isinstance(insect, Butterfly):
                if hand.dragging_insect == insect:
                    insect.rect.center = hand.rect.center
                    if self.basket_rect.colliderect(insect.rect):
                        self.score += 3
                        self.insects.remove(insect)

    def draw(self):
        # draw the background
        self.background.draw(self.surface)
        # draw the insects
        for insect in self.insects:
            insect.draw(self.surface)
        # draw the basket
        self.surface.blit(self.basket_image, self.basket_rect.topleft)
        # draw the hand
        for hand in self.hands:
            hand.draw(self.surface)
        # draw the score
        ui.draw_text(self.surface, f"Score : {self.score}", (5, 5), COLORS["score"], font=FONTS["medium"],
                    shadow=True, shadow_color=(255, 255, 255))
        # draw the time left
        timer_text_color = (160, 40, 0) if self.time_left < 5 else COLORS["timer"]  # change the text color if less than 5 s left
        ui.draw_text(self.surface, f"Time left : {self.time_left}", (SCREEN_WIDTH // 2, 5), timer_text_color, font=FONTS["medium"],
                    shadow=True, shadow_color=(255, 255, 255))


    def game_time_update(self):
        self.time_left = max(round(GAME_DURATION - (time.time() - self.game_start_time), 1), 0)

    def set_hand_image(self, hand,h):
        if hand.left_click:
            if self.hand_tracking.hands_type[h]==1:
                return self.image_smaller_l.copy()
            else:
                return self.image_smaller_r.copy()
        else:
            if self.hand_tracking.hands_type[h]==1:
                return self.orig_image_l.copy()
            else:
                return self.orig_image_r.copy()

    def update(self):
        self.hands = []
        self.load_camera()
        self.set_hand_position()
        self.game_time_update()

        if self.time_left > 0:
            self.spawn_insects()
            for h, hand in enumerate(self.hands):
                hand.image = self.set_hand_image(hand, h)
                self.score = hand.kill_insects(self.insects, self.score, self.sounds)
                hand.update_dragging()
                for insect in self.insects:
                    insect.move()
                self.catch_insects(hand)
        else:
            if ui.button(self.surface, 540, "Continue", click_sound=self.sounds["slap"]):
                return "menu"

        self.draw()
        cv2.imshow("Frame", self.frame)
        cv2.waitKey(1)

