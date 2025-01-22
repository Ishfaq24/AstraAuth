from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from hoverable import HoverBehavior
from datetime import datetime
from pathlib import Path
import random
import sqlite3
import glob

Builder.load_file('design.kv')

# Database setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")
conn.commit()


class LoginScreen(Screen):
    def sign_up(self):
        self.manager.current = "sign_up_screen"

    def login(self, username, password):
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result and result[0] == password:
            self.manager.current = 'login_screen_success'
        else:
            self.ids.login_wrong.text = "Wrong username or password"


class RootWidget(ScreenManager):
    pass


class SignUpScreen(Screen):
    def add_user(self, username, password):
        try:
            cursor.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)", 
                           (username, password, datetime.now().strftime("%d/%m/%Y, %H:%M:%S")))
            conn.commit()
            self.manager.current = "sign_up_screen_success"
        except sqlite3.IntegrityError:
            self.ids.signup_error.text = "Username already exists"


class SignUpScreenSuccess(Screen):
    def go_to_login(self):
        self.manager.transition.direction = "right"
        self.manager.current = "login_screen"


class LoginScreenSuccess(Screen):
    def log_out(self):
        self.manager.transition.direction = "right"
        self.manager.current = "login_screen"

    def get_quote(self, feel):
        feel = feel.lower()
        available_feelings = glob.glob("quotes/*.txt")
        available_feelings = [Path(filename).stem for filename in available_feelings]
        if feel in available_feelings:
            with open(f"quotes/{feel}.txt", 'r', encoding='utf-8') as file:
                quotes = file.readlines()
            self.ids.quote.text = random.choice(quotes).strip()
        else:
            self.ids.quote.text = "Sorry, no quotes available for this feeling"


class ImageButton(ButtonBehavior, HoverBehavior, Image):
    pass

class ForgotPasswordScreen(Screen):
    def send_reset_link(self, username):
        # Basic validation
        if username.strip():
            # Feedback message
            self.ids.feedback_label.text = "Reset link sent to your email!"
            self.ids.feedback_label.color = (0.2, 0.8, 0.4, 1)
        else:
            self.ids.feedback_label.text = "Please enter your username or email."
            self.ids.feedback_label.color = (1, 0, 0, 1)

    def go_to_login(self):
        # Navigate back to login screen
        self.manager.current = "login_screen"

class RootWidget(ScreenManager):
    pass



class MainApp(App):
    def build(self):
        return RootWidget()


if __name__ == "__main__":
    MainApp().run()
    conn.close()  
