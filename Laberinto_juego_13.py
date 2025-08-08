# laberinto_juego.py

import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


# ==========================================================
# --- INICIO CREACIÓN DEL LABERINTO ---
# Esta función genera:
# 1. Paredes exteriores (1)
# 2. Caminos interiores (0)
# 3. Entrada (2)
# 4. Tesoro (3)
# 5. Trampas (4)
# Garantiza que haya un camino entre la entrada y el tesoro
# ==========================================================
def generar_matriz_con_camino(n):
    matriz = [[1 if i in [0, n - 1] or j in [0, n - 1] else (0 if random.random() < 0.7 else 1)
               for j in range(n)] for i in range(n)]

    def colocar_entrada():
        lados = ['arriba', 'abajo', 'izquierda', 'derecha']
        lado = random.choice(lados)
        if lado == 'arriba':
            x = random.randint(1, n - 2)
            return (0, x), (1, x)
        elif lado == 'abajo':
            x = random.randint(1, n - 2)
            return (n - 1, x), (n - 2, x)
        elif lado == 'izquierda':
            y = random.randint(1, n - 2)
            return (y, 0), (y, 1)
        else:
            y = random.randint(1, n - 2)
            return (y, n - 1), (y, n - 2)

    while True:
        (ey, ex), (ady_y, ady_x) = colocar_entrada()
        if matriz[ady_y][ady_x] == 0:
            break

    matriz[ey][ex] = 2  # Entrada
    entrada = (ady_y, ady_x)

    while True:
        ty, tx = random.randint(1, n - 2), random.randint(1, n - 2)
        if matriz[ty][tx] == 0:
            dist = abs(entrada[0] - ty) + abs(entrada[1] - tx)
            if dist >= n // 4:
                break

    matriz[ty][tx] = 3  # Tesoro
    tesoro = (ty, tx)

    def dfs(y, x, visitado):
        if (y, x) == tesoro:
            return True
        visitado.add((y, x))
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < n and 0 <= nx < n and matriz[ny][nx] in [0, 3] and (ny, nx) not in visitado:
                if dfs(ny, nx, visitado):
                    return True
        return False

    if not dfs(*entrada, set()):
        return generar_matriz_con_camino(n)

    # Colocar trampas (4) según el tamaño
    if n < 10:
        cant = 2
    elif n < 20:
        cant = 4
    elif n < 30:
        cant = 8
    elif n < 40:
        cant = 12
    else:
        cant = 16

    colocadas = 0
    while colocadas < cant:
        y, x = random.randint(1, n - 2), random.randint(1, n - 2)
        if matriz[y][x] == 0:
            matriz[y][x] = 4
            colocadas += 1

    return matriz
# --- FIN CREACIÓN DEL LABERINTO ---


class LaberintoWidget(Widget):
    def __init__(self, matriz, **kwargs):
        super().__init__(**kwargs)
        self.matriz = matriz
        self.n = len(matriz)
        self.cell_size = min(Window.width, Window.height - 50) / self.n
        self.vidas = 3
        self.tesoros = 0
        self.en_busca_tesoro = True
        self.label_vidas = Label(text=f"Vidas: {self.vidas}", size_hint=(1, None), height=30, color=(1,1,1,1))
        self.label_tesoros = Label(text=f"Tesoros: {self.tesoros}", size_hint=(1, None), height=30, color=(1,1,1,1))
        self.parent_box = None

        for y in range(self.n):
            for x in range(self.n):
                if matriz[y][x] == 2:
                    self.jugador_pos = (y, x)

        Window.bind(on_key_down=self.on_key_down)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()

    def mover_jugador(self, dy, dx):
        y, x = self.jugador_pos
        ny, nx = y + dy, x + dx
        if 0 <= ny < self.n and 0 <= nx < self.n and self.matriz[ny][nx] != 1:
            self.jugador_pos = (ny, nx)
            if self.matriz[ny][nx] == 3 and self.en_busca_tesoro:
                self.tesoros += 1
                self.en_busca_tesoro = False
                self.matriz[ny][nx] = 0
            elif self.matriz[ny][nx] == 2 and not self.en_busca_tesoro:
                self.popup("Escapaste exitosamente")
                return
            self.chequear_trampas()
            self.update_canvas()

    def chequear_trampas(self):
        y, x = self.jugador_pos
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.n and 0 <= nx < self.n and self.matriz[ny][nx] == 4:
                self.vidas -= 1
                break
        if self.vidas <= 0:
            self.popup("Game Over")

    def popup(self, texto):
        contenido = BoxLayout(orientation='vertical')
        contenido.add_widget(Label(text=texto))
        btn = Button(text='Cerrar')
        contenido.add_widget(btn)
        popup = Popup(title='Fin del juego', content=contenido, size_hint=(None, None), size=(300, 200))
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        direcciones = {
            273: (1, 0),  # Arriba
            274: (-1, 0),   # Abajo
            275: (0, 1),   # Derecha
            276: (0, -1),  # Izquierda
        }
        if key in direcciones:
            self.mover_jugador(*direcciones[key])

    # ==========================================================
    # --- INICIO RENDERIZADO CON VISIÓN LIMITADA ---
    # Solo dibuja un cuadrado 9x9 alrededor del jugador
    # El resto queda negro (efecto "niebla" o máscara)
    # ==========================================================
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            y_centro, x_centro = self.jugador_pos
            radio = 4  # Radio para un área total de 9x9
            for y in range(self.n):
                for x in range(self.n):
                    # Verificar si la celda está dentro del área visible
                    if abs(y - y_centro) <= radio and abs(x - x_centro) <= radio:
                        valor = self.matriz[y][x]
                        if valor == 1:
                            Color(0, 0, 0)
                        elif valor == 0:
                            Color(1, 1, 1)
                        elif valor == 2:
                            Color(0, 1, 0)
                        elif valor == 3:
                            Color(1, 0.84, 0)
                        elif valor == 4:
                            Color(1, 0, 0)
                    else:
                        # Fuera del rango visible → negro
                        Color(0, 0, 0)

                    Rectangle(pos=(x * self.cell_size, y * self.cell_size),
                              size=(self.cell_size, self.cell_size))

            # Dibujar jugador (azul)
            Color(0, 0, 1)
            Rectangle(pos=(x_centro * self.cell_size, y_centro * self.cell_size),
                      size=(self.cell_size, self.cell_size))

        self.label_vidas.text = f"Vidas: {self.vidas}"
        self.label_tesoros.text = f"Tesoros: {self.tesoros}"
    # --- FIN RENDERIZADO CON VISIÓN LIMITADA ---


class LaberintoApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical')
        self.entrada = TextInput(hint_text="Tamaño del laberinto (7-50)", multiline=False, size_hint=(1, None), height=40)
        btn = Button(text="Generar laberinto", size_hint=(1, None), height=40)
        btn.bind(on_press=self.generar_laberinto)
        self.root.add_widget(self.entrada)
        self.root.add_widget(btn)
        return self.root

    def generar_laberinto(self, instancia):
        try:
            n = int(self.entrada.text)
            if not (7 <= n <= 50):
                raise ValueError
        except:
            popup = Popup(title="Error", content=Label(text="Ingrese un número entre 7 y 50"),
                          size_hint=(None, None), size=(300, 200))
            popup.open()
            return

        self.root.clear_widgets()
        matriz = generar_matriz_con_camino(n)
        widget = LaberintoWidget(matriz)
        box = BoxLayout(orientation='vertical')
        widget.parent_box = box
        box.add_widget(widget.label_vidas)
        box.add_widget(widget.label_tesoros)
        box.add_widget(widget)
        self.root.add_widget(box)

    def show_popup(self, mensaje):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        label = Label(text=mensaje)
        btn_restart = Button(text="Volver a elegir tamaño")
        content.add_widget(label)
        content.add_widget(btn_restart)

        popup = Popup(title=mensaje, content=content,
                      size_hint=(None, None), size=(300, 200))

        btn_restart.bind(on_release=lambda *args: (popup.dismiss(), self.volver_a_selector()))
        popup.open()


if __name__ == '__main__':
    LaberintoApp().run()