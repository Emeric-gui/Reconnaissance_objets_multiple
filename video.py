import cv2
import numpy as np
import time

#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################

net = cv2.dnn.readNet('./yolo/yolov3.weights', './yolo/yolov3.cfg')
classes = []
with open('./yolo/coco.names', 'r') as f:
    classes = f.read().splitlines()


def yolo(img):
    """
        Pour détecter nos différents objets sur une frame
    Parameters
    ----------
    img

    Returns
    -------

    """
    width, height = img.shape[1], img.shape[0]
    blob = cv2.dnn.blobFromImage(img, 1 / 256, (416, 416), (0, 0, 0), swapRB=True, crop=False)

    net.setInput(blob)
    output_layers_names = net.getUnconnectedOutLayersNames()
    layerOutputs = net.forward(output_layers_names)
    boxes = []
    confidences = []
    class_ids = []
    # loop over the layer output
    # first to extract info form the layer output
    # second loop extract info from each output
    for output in layerOutputs:
        for detection in output:
            # first four elements are the location of the bounding box
            # fifth element is the confidence
            # from sixth to end the object predictions
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            #         print(confidence)
            threshold = 0.5
            if confidence > threshold:
                # if confidence > 0.5 display the bbox
                # all this are normalized, we have to make it back to the original size
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # position of the upper left corner
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, threshold, 0.45)  # threshold - maximum suppression

    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(len(boxes), 3))
    try:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = colors[i]
            cv2.rectangle(img, (x, y), ((x + w), (y + h)), color, 2)
            cv2.putText(img, label + " " + confidence, (x, y + 20), font, 2, (0, 255, 0), 2)
    except:
        pass

    return img


#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################
#############################################################

def yolo_final(chemin=0, chemin_video_retour="assets/result.mp4"):
    """
        Appelée lorsqu'on souhaite traitée une vidéo
    Parameters
    ----------
    chemin
    chemin_video_retour

    Returns
    -------

    """
    cap = cv2.VideoCapture(chemin)
    img_array = []
    if cap.isOpened() is False:
        print("Error opening the video file!")

    frame_rate = 1
    prev = 0
    fps = None
    while cap.isOpened():
        ret, frame = cap.read()
        time_elapsed = time.time() - prev
        if time_elapsed > 1. / frame_rate:
            prev = time.time()
            if ret is True:
                width, height = frame.shape[1], frame.shape[0]
                while (width > 1000) & (height > 1000):
                    width, height = width // 2, height // 2
                img = cv2.resize(frame, (width, height))
                img = yolo(img)
                fps = cap.get(cv2.CAP_PROP_FPS)
                img_array.append(img)
                # cv2.imshow('Grayscale frame', img)

            else:
                break

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    height, width, layers = img_array[0].shape
    size = (width, height)

    out = cv2.VideoWriter(chemin_video_retour, cv2.VideoWriter_fourcc(*'avc1'), fps, size)

    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()
    print("Ecriture de la vidéo terminé")
    cap.release()
