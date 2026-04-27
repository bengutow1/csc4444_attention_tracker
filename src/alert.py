# This module issues the alert, lets the user know the cause
# Issues the alert using tkinter
# Plays the Skyrim skeleton gif meme with the RAHH sound :P

import tkinter as tk
import pygame
from PIL import Image, ImageTk
import os

class Alert:
    
    def __init__(self):
        #asset file paths

        #get the base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.gif_path = os.path.join(base_dir, "assets", "skeleton.gif")
        self.sound_path = os.path.join(base_dir, "assets", "RAHHH.wav")

        #initializing pygame audio mixer
        pygame.mixer.init()

    def get_message(self, alert_reason):
        """returns the display msg using the alert_reason
            from tracker.py
        """
        if alert_reason == "gaze":
            return "THOU SHALLN'T AVERT THY GAZE!"
        elif alert_reason == "head":
            return "THOU SHALLN'T SWIVEL THY SKULL!"
        elif alert_reason == "both":
            return "THOU SHALLN'T SWIVEL THY SKULL OR AVERT THY GAZE!"
        else:
            #this logically should never set
            return "LOCK IN GANG!"
    
    def trigger(self, alert_reason):
        """opens a tkinter window w/ the skeleton gif,
            plays audio, and displays the alert msg
        """

        message = self.get_message(alert_reason)
        
        #play RAHHHHHH sound
        pygame.mixer.music.load(self.sound_path)
        pygame.mixer.music.play()

        #setting up tkinter window
        window = tk.Tk()
        window.title("LOCK IN GANG!")
        window.geometry("600x500")
        window.configure(bg="black")     #black background
        window.resizable(False, False)

        #loading skeleton meme gif
        gif = Image.open(self.gif_path)
        frames = []

        try:
            while True:
                #append current frame
                frames.append(ImageTk.PhotoImage(gif.copy().convert("RGBA")))
                #move to next frame
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

        #gif label - displays the gif
        gif_label = tk.Label(window, bg="black")
        gif_label.pack()

        #alert msg label - displays the msg
        msg_label = tk.Label(window, text=message, fg="red",
            bg="black", font=("Arial", 20, "bold"),
            wraplength=550)
        msg_label.pack()

        #force close the window after 5 secs
        window.after(5000, window.destroy)

        self.run_gif(gif_label, frames, 0, window)
        window.mainloop()
    
    def run_gif(self, label, frames, index, window):
        """recursively cycles through gif frames &
            animates it :D
        """
        
        #starts @ 0 initially
        frame = frames[index]
        label.configure(image=frame)
        next_index = (index + 1) % len(frames)  #loops
        window.after(50, self.run_gif, label, frames, next_index, window)


