import pygame
import numpy as np
import urllib.request
import cv2
import math
import time
import re

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Interfaz de Magnitud de Velocidad")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (144, 238, 144)
LIGHT_BLUE = (173, 216, 230)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 102)
PURPLE = (186, 85, 211)

# Fuente para el texto
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 48)
subtitle_font = pygame.font.Font(None, 28)

# URLs de la cámara, temperatura y posición
camera_url = 'http://192.168.20.39/cam-hi.jpg'
temperature_url = 'http://192.168.20.39/termometer'
position_url = 'http://192.168.20.39/accelerometer'

# Variables para la gráfica de velocidad
velocity_magnitudes = []
SCALE_FACTOR = 50 # Ajustado para ampliar valores pequeños

# Intervalos de actualización en segundos
TEMP_UPDATE_INTERVAL = 0.1
POSITION_UPDATE_INTERVAL = 0.1
last_temp_time = time.time()
last_position_time = time.time()

temperature = 25  # Valor inicial de temperatura

# Función para obtener la imagen desde el servidor
def fetch_image(url):
    try:
        img_response = urllib.request.urlopen(url, timeout=5)
        img_np = np.array(bytearray(img_response.read()), dtype=np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        if frame is not None:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as e:
        print(f"Error fetching image: {e}")
    return None

# Función para obtener datos de temperatura desde el servidor
def get_temperature_data(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        temperature_data = response.read().decode()
        print("Datos de temperatura recibidos:", temperature_data)
        
        # Usar expresión regular para extraer la temperatura en Celsius
        match = re.search(r"Temperatura:\s*([\d.]+)", temperature_data)
        if match:
            return float(match.group(1))
        else:
            print("No se encontró el valor de temperatura en los datos.")
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
    return 25  # Valor predeterminado si hay error

# Función para obtener la magnitud de la velocidad desde el servidor
def get_velocity_magnitude(url):
    try:
        response = urllib.request.urlopen(url, timeout=5)
        position_data = response.read().decode()
        print("Datos recibidos:", position_data)
        
        # Extraer las velocidades en X y Y
        vel_x_match = re.search(r"Velocidad Integrada x:\s*([-]?\d+\.\d+)", position_data)
        vel_y_match = re.search(r"Velocidad Integrada y:\s*([-]?\d+\.\d+)", position_data)
        
        if vel_x_match and vel_y_match:
            vel_x = float(vel_x_match.group(1))
            vel_y = float(vel_y_match.group(1))
            
            # Calcular la magnitud de la velocidad en XY
            velocity_magnitude = math.sqrt(vel_x**2 + vel_y**2)
            return velocity_magnitude
        else:
            print("No se encontraron los valores de velocidad en los datos.")
    except Exception as e:
        print(f"Error fetching position data: {e}")
    return 0  # Valor predeterminado si hay error

# Función para graficar la magnitud de la velocidad
def draw_velocity_graph():
    start_x = 400  # Punto de inicio en X dentro del cuadro púrpura
    start_y = 400  # Punto base en Y (parte inferior del cuadro púrpura)
    max_points = 50  # Número máximo de puntos a dibujar dentro del cuadro
    spacing = 7      # Espaciado entre puntos en la gráfica

    for i in range(1, len(velocity_magnitudes)):
        if i < max_points:
            x1 = start_x + (i - 1) * spacing
            y1 = start_y - int(velocity_magnitudes[i - 1] * SCALE_FACTOR)
            x2 = start_x + i * spacing
            y2 = start_y - int(velocity_magnitudes[i] * SCALE_FACTOR)
            pygame.draw.line(window, GREEN, (x1, y1), (x2, y2), 2)

# Función para determinar el color y tamaño de la pelota según la temperatura
def get_ball_properties(temperature):
    if temperature < 23:
        color = LIGHT_BLUE
        size = 20
    elif 24 <= temperature < 25:
        color = GREEN
        size = 40
    elif 25 <= temperature < 26:
        color = ORANGE
        size = 60
    else:
        color = RED
        size = 80
    return color, size

# Función para verificar si un botón es presionado
def is_button_pressed(button_rect, mouse_pos):
    return button_rect.collidepoint(mouse_pos)

# Función para reiniciar la gráfica
def reset_graph():
    global velocity_magnitudes
    velocity_magnitudes = []

# Función para dibujar la interfaz
def draw_interface(image, temperature):
    window.fill(YELLOW)

    # Título
    title_text = title_font.render("Curling", True, BLACK)
    window.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 20))

    # Área de la cámara con título
    cam_title_text = subtitle_font.render("¡Mírate aquí!", True, PURPLE)
    window.blit(cam_title_text, (160, 80))
    if image is not None:
        frame_surface = pygame.surfarray.make_surface(image)
        frame_surface = pygame.transform.scale(frame_surface, (320, 240))
        pygame.draw.rect(window, PURPLE, (50, 100, 320, 240), border_radius=15)
        window.blit(frame_surface, (50, 100))
    else:
        pygame.draw.rect(window, PURPLE, (50, 100, 320, 240), border_radius=15)
        cam_text = font.render("Área de visualización", True, BLACK)
        window.blit(cam_text, (120, 210))

    # Mostrar la temperatura con el círculo de la "pelota"
    pygame.draw.rect(window, PURPLE, (50, 360, 300, 50), border_radius=10)
    temp_text = font.render(f"Temperatura: {temperature:.2f} °C", True, WHITE)
    window.blit(temp_text, (60, 370))

    # Determinar las propiedades de la pelota según la temperatura
    ball_color, ball_size = get_ball_properties(temperature)

    # Dibujar la pelota con ajuste de posición
    ball_position_y = 500
    pygame.draw.circle(window, ball_color, (200, ball_position_y), ball_size)

    # Gráfico de velocidad
    pygame.draw.rect(window, PURPLE, (400, 100, 350, 300), border_radius=10, width=2)
    graph_label = font.render("Magnitud de Velocidad", True, PURPLE)
    window.blit(graph_label, (450, 80))
    
    # Dibujar la gráfica de magnitud de velocidad
    draw_velocity_graph()

    # Botón para reiniciar la gráfica
    reset_button_rect = pygame.draw.rect(window, RED, (530, 450, 120, 50), border_radius=10)
    reset_button_text = font.render("Reiniciar", True, WHITE)
    window.blit(reset_button_text, (reset_button_rect.x + (reset_button_rect.width - reset_button_text.get_width()) // 2, 
                                    reset_button_rect.y + (reset_button_text.get_height()) // 2))

    pygame.display.flip()

# Bucle principal de la interfaz
running = True
clock = pygame.time.Clock()
last_image = None
last_image_time = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if is_button_pressed(pygame.Rect(650, 450, 120, 50), mouse_pos):
                reset_graph()  # Reiniciar la gráfica

    # Obtener la imagen del ESP32-CAM cada 0.1 segundos para evitar sobrecarga
    current_time = time.time()
    if current_time - last_image_time > 0.1:
        new_image = fetch_image(camera_url)
        if new_image is not None:
            last_image = new_image
            last_image_time = current_time

    # Actualizar la temperatura cada TEMP_UPDATE_INTERVAL segundos
    if current_time - last_temp_time >= TEMP_UPDATE_INTERVAL:
        temperature = get_temperature_data(temperature_url)
        last_temp_time = current_time

    # Actualizar la posición cada POSITION_UPDATE_INTERVAL segundos
    if current_time - last_position_time >= POSITION_UPDATE_INTERVAL:
        velocity_magnitude = get_velocity_magnitude(position_url)
        velocity_magnitudes.append(velocity_magnitude)
        
        # Limitar el número de puntos en la gráfica a 100
        if len(velocity_magnitudes) > 100:
            velocity_magnitudes.pop(0)
        
        last_position_time = current_time

    # Dibujar la interfaz usando la última imagen válida
    draw_interface(last_image, temperature)

    clock.tick(30)

pygame.quit()
