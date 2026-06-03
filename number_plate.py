import cv2
import easyocr
import tkinter as tk
from PIL import Image, ImageTk
import pygame  # For playing sound
import os

harcascade = "model/number_plate.xml"

reader = easyocr.Reader(['en'])

cap = cv2.VideoCapture(0)

cap.set(3, 640)  # width
cap.set(4, 480)  # height

min_area = 500
count = 0
alarm_sound_path = "alarm.wav"  # Change to your WAV file path
matched_plates = []  # List to store matched plates history

def compare_plates(entered_plate, detected_plate, img_roi):
    global matched_plates
    if entered_plate == detected_plate:
        print("Matching plates detected!")
        pygame.mixer.init()
        pygame.mixer.music.load(alarm_sound_path)
        pygame.mixer.music.play()
        # Update label text below the entry box
        status_label.config(text="Matching plate detected!", fg="green")
        # Append the new matched plate to the list
        matched_plates.append(detected_plate)
        update_history()
        
        # Save the image
        img_name = f"scanned_img_{count}.jpg"
        img_path = os.path.join("D:\\anpr\\plates", img_name)
        cv2.imwrite(img_path, img_roi)
        print("Image saved:", img_path)
    else:
        # Update label text below the entry box
        status_label.config(text="No matching plate detected", fg="red")

def update_history():
    history_listbox.delete(0, tk.END)
    for plate in matched_plates:
        history_listbox.insert(tk.END, plate)

def detect_plate():
    global count
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            img_roi = img[y:y + h, x:x + w]

            result = reader.readtext(img_roi)

            # Display the recognized text on the image
            if result:
                plate_number = result[0][1]
                cv2.putText(img, plate_number, (x, y - 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                plate_label.config(text=f"Number Plate: {plate_number}")
                
                # Compare with entered plate and ring alarm if they match
                entered_plate = plate_entry.get()
                compare_plates(entered_plate, plate_number, img_roi)

            # Save the detected plate when 's' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('s'):
                cv2.imwrite("plates/scanned_img_" + str(count) + ".jpg", img_roi)
                cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, "Plate Saved", (150, 265), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 2)
                cv2.waitKey(500)
                count += 1

    cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, detect_plate)

# Tkinter setup
window = tk.Tk()
window.title("Automated Numberplate Recognition System")

# Set the window to fullscreen
window.attributes('-fullscreen', True)

# Load the background image
background_image_path = r"D:\anpr\background.jpg"  # Replace with your image path
background_image = Image.open(background_image_path)

# Get the screen width and height
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Resize the background image to fit the screen
resized_background = background_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
background_photo = ImageTk.PhotoImage(resized_background)

# Create a Canvas widget
canvas = tk.Canvas(window, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)

# Set the background image
canvas.create_image(0, 0, image=background_photo, anchor="nw")

# Add title label
title_label = tk.Label(canvas, text="Automated Numberplate Recognition System", font=("Helvetica", 24), bg="black", fg="white")
canvas.create_window(screen_width // 2, 50, window=title_label)

# Create a label for the video feed
video_label = tk.Label(canvas, bg="black")
canvas.create_window(screen_width // 2, screen_height // 2, window=video_label)

# Create a label for the plate number
plate_label = tk.Label(canvas, text="Number Plate:", font=("Helvetica", 16), bg="black", fg="white")
canvas.create_window(screen_width // 2, screen_height - 250, window=plate_label)

# Entry for user to input the number plate
plate_entry = tk.Entry(canvas, font=("Helvetica", 16))
canvas.create_window(screen_width // 2, screen_height - 200, window=plate_entry)

# Label to show status message
status_label = tk.Label(canvas, font=("Helvetica", 14), bg="black", fg="red")
canvas.create_window(screen_width // 2, screen_height - 150, window=status_label)

# Create a label for the history
history_heading_label = tk.Label(canvas, text="Catched!", font=("Helvetica", 16), bg="black", fg="red")
canvas.create_window(screen_width // 4, screen_height // 2 - 150, window=history_heading_label)

# Listbox to display history of matched plates
history_listbox = tk.Listbox(canvas, font=("Helvetica", 12), bg="black", fg="white")
canvas.create_window(screen_width // 4, screen_height // 2, window=history_listbox)

# Run
detect_plate()
window.mainloop()

# Release the capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
