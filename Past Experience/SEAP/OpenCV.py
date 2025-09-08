import numpy as np
import cv2

corner_track_params = dict(maxCorners = 100,qualityLevel=0.3,minDistance=7,blocksize=7)

lk_params = dict(winSize=(200,200),maxLevel = 2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03))

cap = cv2.VideoCapture(0)

ret , prev_frame = cap.read()

prev_gray = cv2.cvtColor(prev_frame,cv2.COLOR_BGR2GRAY)

# PTS TO TRACK
prevPts = cv2.goodFeaturesToTrack(prev_gray,mask=None,**corner_track_params)

# Draw lines on video
mask = np.zeros_like(prev_frame)


while True:
    # get next frame
    ok, frame = cap.read()
    if not ok:
        print("[INFO] end of file reached")
        break
    # prepare grayscale image
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # update object corners by comparing with found edges in initial frame
    update_edges, status, errors = cv2.calcOpticalFlowPyrLK(frame_gray_init, frame_gray, edges, None,
                                                         **parameter_lucas_kanade)
    # only update edges if algorithm successfully tracked
    new_edges = update_edges[status == 1]
    # to calculate directional flow we need to compare with previous position
    old_edges = edges[status == 1]

    for i, (new, old) in enumerate(zip(new_edges, old_edges)):
        a, b = new.ravel()
        c, d = old.ravel()

        # draw line between old and new corner point with random colour
        mask = cv2.line(canvas, (int(a), int(b)), (int(c), int(d)), colours[i].tolist(), 2)
        # draw circle around new position
        frame = cv2.circle(frame, (int(a), int(b)), 5, colours[i].tolist(), -1)

    result = cv2.add(frame, mask)
    cv2.imshow('Optical Flow (sparse)', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # overwrite initial frame with current before restarting the loop
    frame_gray_init = frame_gray.copy()
    # update to new edges before restarting the loop
    edges = new_edges.reshape(-1, 1, 2)
