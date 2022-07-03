import cv2
import mediapipe as mp
import time

class hand_detector():
    def __init__(self, mode=False, max_hands=2, model_complex=1, detection_con=0.5, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.model_complex = model_complex
        self.detection_con = detection_con
        self.track_con = track_con

        self.media_hands = mp.solutions.hands
        self.hands = self.media_hands.Hands()
        self.media_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_color = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.img_loc = self.hands.process(img_color)

        if self.img_loc.multi_hand_landmarks:
            for hand_landmark in self.img_loc.multi_hand_landmarks:
                if draw:
                    self.media_draw.draw_landmarks(img, hand_landmark, self.media_hands.HAND_CONNECTIONS)
        return img

    def find_pos(self, img, hand_num=0, draw=True):
        landmark_array = []

        if self.img_loc.multi_hand_landmarks:
            hand_on_screen = self.img_loc.multi_hand_landmarks[hand_num]
            for id, landmarks in enumerate(hand_on_screen.landmark):
                height, width, circle = img.shape
                circle_x, circle_y = int(landmarks.x * width), int(landmarks.y * height)
                landmark_array.append([id, circle_x, circle_y])
                if draw:
                    cv2.circle(img, (circle_x, circle_y), 8, (0, 255, 0), cv2.FILLED)
        return landmark_array

def main():
    cap = cv2.VideoCapture(0)
    detect_hands = hand_detector()

    run = True
    while run:
        frame, img = cap.read()
        img = detect_hands.find_hands(img)
        landmark_array = detect_hands.find_pos(img)
        if len(landmark_array) !=0:
           print(landmark_array[0])

        cv2.imshow('Image', img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()




