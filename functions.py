import os
import cv2

def imagenIndividual(nombre):
    path_string = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"frames") + '\\' + nombre
    single_image = cv2.imread(path_string, cv2.IMREAD_GRAYSCALE)  # Read image in grayscale
    return single_image

def imagenIndividual2(nombre):
    path_string = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"frames") + '\\' + nombre
    single_image = cv2.imread(path_string)    
    return single_image

def imagen_stitching(nombre):
    path_string = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames", nombre)
    single_image = cv2.imread(path_string, cv2.COLOR_BGR2GRAY)  # Read image in RGB color format
    return single_image

def conjunto_imagenesdiv(set_nomb):
    images = []
    for foto in set_nomb:
        single_image = imagen_stitching(foto)
        images.append(single_image)
    return images

def get_frames(video_path, output_folder, frame_skip=7, thumbnail_size=(120, 90)):
    # print(f"get_frames called with video_path: {video_path}, output_folder: {output_folder}, frame_skip: {frame_skip}")
    frame_names = []
    cap = cv2.VideoCapture(video_path)
    count = 0
    frame_count = 0
    if not cap.isOpened():
        # print(f"Failed to open video file: {video_path}")
        return frame_names

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_skip == 0:
            frame_name = f"{count}.png"
            frame_path = os.path.join(output_folder, frame_name)

            # Save the full-size frame
            cv2.imwrite(frame_path, frame)
            print(f"Saved frame: {frame_path}")
            frame_names.append(frame_name)

            # Generate and save the thumbnail
            thumbnail = cv2.resize(frame, thumbnail_size)
            thumbnail_path = os.path.join(output_folder, f"thumb_{frame_name}")
            cv2.imwrite(thumbnail_path, thumbnail)
            print(f"Saved thumbnail: {thumbnail_path}")

            count += 1
        frame_count += 1
    cap.release()
    # print(f"Total frames extracted: {len(frame_names)}")
    return frame_names

def create_paths():
    # Save the path to the uploaded videos
    UPLOAD_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    # Check if the path exists. If it does not, then create a folder called "uploads"
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    # Save the path to the extracted frames and if the path does not exist, then create it
    FRAME_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
    if not os.path.exists(FRAME_DIRECTORY):
        os.makedirs(FRAME_DIRECTORY)

    # Save the path to the resulting panorama, if it does not exist, then create it
    RESULT_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    if not os.path.exists(RESULT_DIRECTORY):
        os.makedirs(RESULT_DIRECTORY)

    return UPLOAD_DIRECTORY, FRAME_DIRECTORY, RESULT_DIRECTORY


def comparador(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    return matches

def group_of_ten(frame_name, nombres):
    answer = {}
    ind = int(frame_name[:-4]) - 1
    frame_amount = len(nombres)
    max_iteration = min(10, frame_amount - ind)
    
    for i in range(max_iteration):
        img1 = imagenIndividual(nombres[ind + i])
        for j in range(i + 1, max_iteration):
            img2 = imagenIndividual(nombres[ind + j])
            matches = comparador(img1, img2)
            answer[nombres[ind + j]] = len(matches)
    
    answer = sorted(answer.items(), key=lambda x: x[1])
    return answer

def variance_of_laplacian(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

def is_blurry(img_1, img_2, img_3):
    vl_first = variance_of_laplacian(imagenIndividual2(img_1))
    vl_second = variance_of_laplacian(imagenIndividual2(img_2))
    vl_third = variance_of_laplacian(imagenIndividual2(img_3))
    values = [vl_first, vl_second, vl_third]
    maxim = max(values)
    if maxim == vl_first:
        best_img = img_1
    elif maxim == vl_second:
        best_img = img_2
    else:
        best_img = img_3
    return best_img

def find_non_blurry(nombres, threshold):
    imagenes_correctas = [nombres[0]]
    processed_indices = set()
    
    while True:
        answer = group_of_ten(imagenes_correctas[-1], nombres)  
        # Check if we have enough frames to continue processing
        if len(answer) < 3:
            break
        
        blurry_detected = False
        
        for i in range(len(answer) - 1, -1, -1):
            if answer[i][0] not in processed_indices:
                processed_indices.add(answer[i][0])
                if answer[i][1] >= threshold:
                    if i >= 2:
                        result = is_blurry(answer[i][0], answer[i-1][0], answer[i-2][0])
                        imagenes_correctas.append(result)
                    elif i == 1:
                        result = is_blurry(answer[i][0], answer[i-1][0], answer[i-1][0])
                        imagenes_correctas.append(result)
                    else:
                        result = is_blurry(answer[i][0], answer[i][0], answer[i][0])
                        imagenes_correctas.append(result)
                    blurry_detected = True
                    break
                    
            print(f'La mejor imagen ha sido {result}')
        if not blurry_detected:
            break
    print("Termino el proceso")
    return imagenes_correctas

def remove_from_list(nombres, to_delete):
    for img_name in to_delete:
        nombres.remove(img_name)
    return nombres

def descartar(nombres, matches_treshold):
    actual = 0 # An index to the very first image in the list
    to_delete = [] # A list containing all the images that won't be used during the stitching process
    while actual < len(nombres) - 2: # As long as there's something to compare
        print(to_delete)
        img1 = imagenIndividual(nombres[actual]) # The image being compared to the others
        for j in range(actual + 1, len(nombres)): # To compare from the very next image to the last of them
            img2 = imagenIndividual(nombres[j]) # The image being compared to the other one
            matches = comparador(img1, img2) # Amount of common points between the two images
            print("Comparando:", nombres[actual], "con", nombres[j] + ". Hay", len(matches), "matches")
            if (j == len(nombres) - 1):
                for k in range(actual + 1, len(nombres) - 1):
                    to_delete.append(nombres[k])
                    return to_delete
            if (j == actual + 1 and len(matches) <= matches_treshold):
                actual = j
                break
            elif(len(matches) <= matches_treshold):
                for k in range(actual + 1, j - 1):
                    to_delete.append(nombres[k])
                    actual = j - 1
                    break
    final_imgs = remove_from_list(nombres, to_delete)
    return final_imgs

def proce_stitcher(images, nombre, output_path):
    stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
    
    (status, stitched) = stitcher.stitch(images, None)
    if status == 0:
        img_name = str(nombre)+".png"
        png_compression_level = 0 #Para no perder calidad en png
        dst = cv2.detailEnhance(stitched, sigma_s=1, sigma_r=0.07)

        cv2.imwrite(os.path.join(output_path, img_name), dst, [int(cv2.IMWRITE_PNG_COMPRESSION), png_compression_level])
        print(f"La imagen ha sido guardada en la ruta {os.path.join(output_path, img_name)}")
        return(status)
    else:
        print("Se ha presentado un error. Status devolvió el valor:", status)
        return(status)