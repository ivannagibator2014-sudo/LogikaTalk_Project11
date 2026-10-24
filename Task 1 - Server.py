import socket
import threading

# Налаштування мережі:
# HOST = '0.0.0.0' означає, що сервер слухає підключення на всіх доступних мережевих інтерфейсах
HOST = '0.0.0.0'
PORT = 8080  # Порт, на якому працюватиме сервер

# Список для зберігання активних підключень клієнтів
clients = []


def broadcast(data, exclude_socket=None):
  """Функція розсилки (трансляції) отриманих даних усім підключеним клієнтам,

  окрім відправника (exclude_socket).
  """
  for client in clients:
    # Перевіряємо, щоб не надсилати повідомлення назад тому ж клієнту, який його надіслав
    if client != exclude_socket:
      try:
        client.sendall(data)
      except:
        # У разі помилки надсилання виводимо повідомлення про помилку
        print("ER40R 4O4")


def handle_client(client_socket):
  """Функція для обробки взаємодії з окремим підключеним клієнтом у фоновому потоці."""
  while True:
    try:
      # Отримуємо дані від клієнта (буфер обміну 4096 байт)
      data = client_socket.recv(4096)
      if not data:
        break  # Якщо дані відсутні, клієнт відключився
      # Пересилаємо отримані дані всім іншим клієнтам
      broadcast(data, exclude_socket=client_socket)
    except:
      break  # Перериваємо цикл у разі виникнення помилки зв'язку

  # Видаляємо сокет клієнта зі списку активних, якщо він там є
  if client_socket in clients:
    clients.remove(client_socket)
  # Закриваємо з'єднання
  client_socket.close()


def main():
  """Головна функція запуску та ініціалізації сервера."""
  # Створюємо TCP/IP сокет (AF_INET — IPv4, SOCK_STREAM — TCP)
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # Дозволяємо повторне використання адреси/порту відразу після закриття сервера
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

  # Прив'язуємо сокет до вказаного хоста та порту
  server_socket.bind((HOST, PORT))

  # Переводимо сервер у режим прослуховування (черга підключень до 5)
  server_socket.listen(5)
  print(f"Сервер запущено на {HOST}:{PORT}")

  # Головний цикл прийняття нових підключень від клієнтів
  while True:
    # Приймаємо нове з'єднання (повертає новий сокет клієнта та його адресу)
    client_socket, addr = server_socket.accept()
    print(f"Підключився клієнт: {addr}")

    # Додаємо нового клієнта до загального списку
    clients.append(client_socket)

    # Створюємо окремий потік для обробки цього клієнта, щоб не блокувати інших
    t = threading.Thread(target=handle_client, args=(client_socket,))
    t.start()


if __name__ == "__main__":
  main()