
import cv2
import mediapipe as mp
# Bibliothèque qui permet d'intéragir avec des langages de bas niveau comme le C, C++
from ctypes import cast, POINTER
# Bibliothèque qui permet d'intéragir avec des langages de bas niveau comme le C, C++
# Elle permet également d'accéder aux objets COM pour automatiser de actions windows ou excel à partir de python  
from comtypes import CLSCTX_ALL
# Bibliothèque qui sert a récupérer des informations JSON des packages via une API
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
# Bibliothèque qui va me permettre de controler la luminositer d'un pc
import screen_brightness_control as sbc

# Gestions des varriables pour augmenter le volume ou le diminuer 
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Varriables pour le traitement du visage 
mpDraw = mp.solutions.drawing_utils

mpfaceMesh = mp.solutions.face_mesh
faceMesh = mpfaceMesh.FaceMesh(max_num_faces=2)
drawSpec = mpDraw.DrawingSpec(thickness=2 , circle_radius=2)

# variable pour le traitement des mains 
mp_drawing = mp.solutions.drawing_utils
mpface = mp.solutions.hands
face = mpface.Hands()

cam = cv2.VideoCapture(0)

while cam.isOpened:
    ret, frame = cam.read()

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faceFrame = faceMesh.process(imgRGB)

    handFrame = face.process(imgRGB)

    image_height, image_width, _ = frame.shape
    # détection des mains 
    if handFrame.multi_hand_landmarks:
        # print(handFrame.hand_landmarks)

        # if not handFrame.multi_hand_landmarks:
        #     continue
        for hand_landmark in handFrame.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmark,mpface.HAND_CONNECTIONS)
            # Détection et affichage du pouce 
            thumb_lambmark = hand_landmark.landmark[4]
            cv2.putText(frame, "Pouce X :{0:6.3f}".format(thumb_lambmark.x)  ,(10,40), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2 )
           
            # Détection et affichage de l'oriculaire 
            thumb_lambmark_index = hand_landmark.landmark[8]
            # Détection du majeur 
            thumb_lambmark_majeur = hand_landmark.landmark[12]



            cv2.putText(frame, "Index X :{0:6.3f}".format(thumb_lambmark_index.x) ,(10,100), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2 )

            differencex = math.hypot(thumb_lambmark_index.x - thumb_lambmark.x, thumb_lambmark_index.y - thumb_lambmark.y)  # obtient la longueur entre les doigts
            differencexLuminosite = math.hypot(thumb_lambmark_majeur.x - thumb_lambmark.x, thumb_lambmark_majeur.y - thumb_lambmark.y)  # obtient la longueur entre les doigts


            cv2.putText(frame, "delta :"+str(differencex) ,(10,120), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2 )
            currentVolumeDb = volume.GetMasterVolumeLevel()
            currentLuminosite = sbc.get_brightness()

            volumeMain = 65-(differencex)*300

            differencexLuminosite = (differencexLuminosite) * 300
            sbc.set_brightness(differencexLuminosite)

            if volumeMain < 0 :
                volumeMain = 0
                
            if volumeMain <= -52 :
                volumeMain = -60

            volume.SetMasterVolumeLevel(-volumeMain, None)
            # sbc.set_brightness(differencexLuminosite)



            

            

    if faceFrame.multi_face_landmarks :
        # Détection des landmarks faciaux
        for faceLms in faceFrame.multi_face_landmarks:
            mpDraw.draw_landmarks(frame, faceLms,mpfaceMesh.FACEMESH_TESSELATION, landmark_drawing_spec=None,connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
            mpDraw.draw_landmarks(frame, faceLms,mpfaceMesh.FACEMESH_CONTOURS,landmark_drawing_spec=None,connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_contours_style())
            # mpDraw.draw_landmarks(frame, faceLms,mpfaceMesh.FACEMESH_IRISES, landmark_drawing_spec=None,connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_iris_connections_style())
        
        # Traitement du résultat de la détection

    # la gestion de la taille de la fenetre sera manuel
    cv2.namedWindow('fenetre', cv2.WINDOW_NORMAL)
    # getsion de la taille de la fenetre sera automatique
    # cv2.namedWindow('fenetre', cv2.WINDOW_AUTOSIZE)

    cv2.imshow('fenetre', frame)

    if cv2.waitKey(1) == ord("q"):
        break
cam.release()
cv2.destroyAllWindows()
  
