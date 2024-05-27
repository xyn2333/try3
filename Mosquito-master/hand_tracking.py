import cv2
import mediapipe as mp
from settings import *
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands



class HandTracking:
    def __init__(self):
        self.hand_tracking = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.hand_x = 0
        self.hands_x = []
        self.hand_y = 0
        self.hands_y = []
        self.results = None

        self.hands_closed = []
        self.hands_type = []  # 1为左手，2为右手

    def scan_hands(self, image):

        rows, cols, _ = image.shape

        # Flip the image horizontally for a later selfie-view display, and convert
        # the BGR image to RGB.翻转图像
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        # 处理图像以检测手部位置
        self.results = self.hand_tracking.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # 初始化手部信息列表
        self.hands_closed = []  # 手部是否闭合
        self.hands_type = []  # 左手还是右手
        self.hands_x = []
        self.hands_y = []
        print(self.results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for h,hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # 中指指根
                x, y = hand_landmarks.landmark[9].x, hand_landmarks.landmark[9].y
                # 小指指根
                x2, y2 = hand_landmarks.landmark[17].x, hand_landmarks.landmark[17].y

                # 判断手的类型（左手或右手），并将相应的类型添加到 self.hands_type 列表
                if x2 < x:
                    self.hands_type.append(1)
                else:
                    self.hands_type.append(2)

                # 将手的中心位置（中指指根位置）转换为屏幕坐标并添加到 self.hands_x 和 self.hands_y 列表
                self.hands_x.append(int(x * SCREEN_WIDTH))
                self.hands_y.append(int(y * SCREEN_HEIGHT))

                # 中指指尖
                x1, y1 = hand_landmarks.landmark[12].x, hand_landmarks.landmark[12].y

                # 通过判断中指指尖是否在中指指根之下来判断手是否握紧
                if y1 > y:
                    self.hands_closed.append(True)
                else:
                    self.hands_closed.append(False)

                # # 绘制手部关键节点和连接线
                # mp_drawing.draw_landmarks(
                #     image,
                #     hand_landmarks,
                #     mp_hands.HAND_CONNECTIONS,
                #     mp_drawing_styles.get_default_hand_landmarks_style(),
                #     mp_drawing_styles.get_default_hand_connections_style())
        return image

    def get_hand_center(self):
        return (self.hand_x, self.hand_y)

    def display_hand(self):
        cv2.imshow("image", self.image)
        cv2.waitKey(1)

    def is_hand_closed(self):

        pass


