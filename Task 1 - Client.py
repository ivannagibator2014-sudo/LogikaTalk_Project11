from socket import *
import threading
from customtkinter import *


class LogiTalk(CTk):

  def __init__(self):
    super().__init__()

    # Налаштування головного вікна додатку
    self.title("LogiTalk")
    self.geometry("400x300")
    self.minsize(400, 300)

    # Початкове ім'я користувача за замовчуванням
    self.username = "Клієнт"

    # Налаштування сітки (Grid) головного вікна
    self.grid_columnconfigure(1, weight=1)
    self.grid_rowconfigure(0, weight=1)

    # Створення бічної панелі (сайдбару) з фіксованою шириною
    self.frame = CTkFrame(self, width=200)
    self.frame.grid(row=0, column=0, rowspan=2, sticky="ns")
    self.frame.grid_propagate(False)

    # Вітальний напис та поле для зміни нікнейму на бічній панелі
    self.label = CTkLabel(self.frame, text=f"Привіт, {self.username}")
    self.label.pack(pady=30)
    self.entry = CTkEntry(self.frame)
    self.entry.pack()

    # Кнопка підтвердження нового імені користувача
    CTkButton(
        self.frame, text="Прийняти", command=self.set_username
    ).pack(pady=30)
    # Випадаючий список для перемикання теми оформлення (Світла/Темна)
    CTkOptionMenu(
        self.frame, values=["Світла", "Темна"], command=self.change_theme
    ).pack(side="bottom", pady=20)

    # Область для виведення повідомлень чату (скроливна панель)
    self.chat_text = CTkScrollableFrame(self)
    self.chat_text.grid(row=0, column=1, sticky="nsew")

    # Нижня панель для введення та відправки повідомлень
    bottom = CTkFrame(self)
    bottom.grid(row=1, column=1, sticky="ew")
    bottom.grid_columnconfigure(0, weight=1)

    # Поле вводу текстового повідомлення
    self.message_input = CTkEntry(bottom, placeholder_text="Ваше повідомлення")
    self.message_input.grid(
        row=0, column=0, sticky="ew", padx=(5, 0), pady=5
    )

    # Кнопка відправки повідомлення
    self.send_button = CTkButton(
        bottom, text="▶️", width=40, command=self.send_message
    )
    self.send_button.grid(row=0, column=1, padx=5, pady=5)

    # Спроба підключення до сервера по TCP на локалхост (127.0.0.1) та порт 8080
    try:
      self.sock = socket(AF_INET, SOCK_STREAM)
      self.sock.connect(("127.0.0.1", 8080))
      # Формуємо привітальне повідомлення про приєднання до чату у спеціальному протоколі (TEXT@користувач@повідомлення)
      hello = (
          f"TEXT@{self.username}@[SYSTEM] {self.username} приєднується до"
          " чату!\n"
      )
      self.sock.send(hello.encode())
      # Запускаємо фоновий потік для постійного прослуховування вхідних повідомлень від сервера
      threading.Thread(target=self.recv_message, daemon=True).start()
    except Exception as e:
      # Якщо підключитись не вдалося — виводимо помилку в чат
      self.add_message(f"Не вдалось підключитись: {e}")

  def set_username(self):
    """Зберігає нове ім'я користувача, введене у полі, та оновлює інтерфейс."""
    self.username = self.entry.get()
    self.label.configure(text=f"Привіт, {self.username}")
    self.entry.delete(0, END)

  def add_message(self, message, img=None, own_message=False):
    """Додає нове повідомлення (фрейм) у стрічку чату.

    Власні повідомлення вирівнюються праворуч і мають інший колір тла.
    """
    bg = "#4a4a4a" if own_message else "#2d2d2d"
    f = CTkFrame(self.chat_text, fg_color=bg)
    f.pack(anchor="e" if own_message else "w", pady=5, padx=5)
    CTkLabel(f, text=message, wraplength=260, justify="left").pack(
        padx=10, pady=5
    )

  def send_message(self):
    """Зчитує текст із поля вводу, додає локально та відправляє на сервер."""
    msg = self.message_input.get()
    if not msg:
      return
    # Відображаємо власне повідомлення в інтерфейсі (праворуч)
    self.add_message(f"{self.username}: {msg}", own_message=True)
    try:
      # Надсилаємо запаковане у форматі протоколу повідомлення на сервер
      self.sock.sendall(f"TEXT@{self.username}@{msg}\n".encode())
    except:
      pass
    self.message_input.delete(0, END)

  def recv_message(self):
    """Фоновий потік: приймає байти від сервера та розбиває потік на окремі рядки (повідомлення)."""
    buf = ""
    while True:
      try:
        data = self.sock.recv(4096)
        if not data:
          break
        buf += data.decode(errors="ignore")
        # Опрацьовуємо повідомлення, розділені символом нового рядка '\n'
        while "\n" in buf:
          line, buf = buf.split("\n", 1)
          self.handle_line(line)
      except:
        break

  def handle_line(self, line):
    """Розбирає отриманий від сервера рядок згідно з протоколом та виводить у чат."""
    parts = line.split("@", 3)
    if parts[0] == "TEXT" and len(parts) == 3:
      self.add_message(f"{parts[1]}: {parts[2]}")

  def change_theme(self, value):
    """Змінює тему інтерфейсу програми на 'dark' (темну) або 'light' (світлу)."""
    set_appearance_mode("dark" if value == "Темна" else "light")


# Запуск графічного додатку
LogiTalk().mainloop()