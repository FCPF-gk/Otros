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

    matriz[ey][ex] = 2
    entrada = (ady_y, ady_x)

    while True:
        ty, tx = random.randint(1, n - 2), random.randint(1, n - 2)
        if matriz[ty][tx] == 0:
            dist = abs(entrada[0] - ty) + abs(entrada[1] - tx)
            if dist >= n // 4:
                break

    matriz[ty][tx] = 3
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

def bresenham(x0, y0, x1, y1):
    """Devuelve los puntos de la línea entre (x0,y0) y (x1,y1)."""
    puntos = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        puntos.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return puntos

def linea_visible(matriz, x0, y0, x1, y1):
    """Chequea si el jugador puede ver la casilla destino sin que un muro la bloquee."""
    for (x, y) in bresenham(x0, y0, x1, y1):
        if matriz[y][x] == 1 and (x, y) != (x1, y1):
            return False
    return True

def casillas_visibles(matriz, jugador_x, jugador_y, rango=4):
    visibles = set()
    for dy in range(-rango, rango+1):
        for dx in range(-rango, rango+1):
            x, y = jugador_x + dx, jugador_y + dy
            if 0 <= x < len(matriz) and 0 <= y < len(matriz):
                if linea_visible(matriz, jugador_x, jugador_y, x, y):
                    visibles.add((x, y))
    return visibles

# --- FIN CREACIÓN DEL LABERINTO ---


class LaberintoWidget(Widget):
    def __init__(self, matriz, **kwargs):
        super().__init__(**kwargs)
        self.matriz = matriz
        self.n = len(matriz)
        self.jugador_pos = (1, 1)  # entrada
        self.en_busca_tesoro = True
        self.vidas = 3
        self.tesoros = 0
        self.label_vidas = Label(text=f"Vidas: {self.vidas}", size_hint=(1, None), height=30)
        self.label_tesoros = Label(text=f"Tesoros: {self.tesoros}", size_hint=(1, None), height=30)
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()


        for y in range(self.n):
            for x in range(self.n):
                if matriz[y][x] == 2:
                    self.jugador_pos = (y, x)

        Window.bind(on_key_down=self.on_key_down)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
        import copy
        self.matriz_inicial = copy.deepcopy(matriz)
        self.pos_inicial = self.jugador_pos

    def mover_jugador(self, dy, dx):
        y, x = self.jugador_pos
        ny, nx = y + dy, x + dx
        if 0 <= ny < self.n and 0 <= nx < self.n and self.matriz[ny][nx] != 1:
            self.jugador_pos = (ny, nx)
            if self.matriz[ny][nx] == 3 and self.en_busca_tesoro:
                self.tesoros += 1
                self.label_tesoros.text = f"Tesoros: {self.tesoros}"  # actualizacion de tesoro
                self.en_busca_tesoro = False
                self.matriz[ny][nx] = 0
            elif self.matriz[ny][nx] == 2 and not self.en_busca_tesoro:
                if self.vidas < 1:
                    self.popup("Escapaste como fantasma")
                else:
                    self.popup("Escapaste exitosamente")
                return
            self.chequear_trampas()
            self.update_canvas()
            
    def reiniciar(self, regenerar=False):
        import copy
        if regenerar:
            from random import randint
            # ⚠️ Aquí deberías volver a llamar a tu función que genera la matriz del laberinto
            # Por ejemplo: nueva_matriz = generar_matriz(self.n)
            # Por ahora reutilizamos la inicial como placeholder:
            self.matriz = copy.deepcopy(self.matriz_inicial)
        else:
            self.matriz = copy.deepcopy(self.matriz_inicial)

        self.jugador_pos = self.pos_inicial
        self.vidas = 3
        self.tesoros = 0
        self.en_busca_tesoro = True
        self.update_canvas() 

    def chequear_trampas(self):
        y, x = self.jugador_pos
        for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.n and 0 <= nx < self.n and self.matriz[ny][nx] == 4:
                self.vidas -= 1
                self.label_vidas.text = f"Vidas: {self.vidas}"   # actualiza vidas
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
            273: (-1, 0),   # Arriba
            274: (1, 0),  # Abajo
            275: (0, 1),   # Derecha
            276: (0, -1),  # Izquierda
        }
        if key in direcciones:
            self.mover_jugador(*direcciones[key])

    # -----------------------------
    # Algoritmo de visibilidad (FOV + Bresenham)
    # -----------------------------
    def bresenham(self, x0, y0, x1, y1):
        """Algoritmo de Bresenham entre dos puntos"""
        puntos = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        if dx > dy:
            err = dx / 2.0
            while x != x1:
                puntos.append((y, x))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                puntos.append((y, x))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy
        puntos.append((y1, x1))
        return puntos

    def linea_visible(self, x0, y0, x1, y1):
        """Chequea si hay línea de visión sin muros"""
        for (y, x) in self.bresenham(x0, y0, x1, y1):
            if self.matriz[y][x] == 1:  # muro
                return False
        return True

    def casillas_visibles(self, jugador_y, jugador_x, rango=4):
        """Devuelve casillas visibles dentro del rango usando FOV"""
        visibles = set()
        for dy in range(-rango, rango + 1):
            for dx in range(-rango, rango + 1):
                y, x = jugador_y + dy, jugador_x + dx
                if 0 <= y < self.n and 0 <= x < self.n:
                    if self.linea_visible(jugador_x, jugador_y, x, y):
                        visibles.add((y, x))
        return visibles

    # -----------------------------
    # Render del laberinto
    # -----------------------------
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Fondo negro
            Color(0, 0, 0)
            Rectangle(pos=self.pos, size=self.size)

            cell_size = min(self.width, self.height) / self.n
            j_y, j_x = self.jugador_pos

            # Casillas visibles por FOV
            rango = 4
            visibles_fov = self.casillas_visibles(j_y, j_x, rango)

            # Además, limitar a un área 9x9 centrada en el jugador
            visibles_9x9 = {
                (y, x)
                for y in range(j_y - 4, j_y + 5)
                for x in range(j_x - 4, j_x + 5)
                if 0 <= y < self.n and 0 <= x < self.n
            }

            # Intersección: solo dibujamos lo que está en ambos
            visibles = visibles_fov & visibles_9x9

            for (y, x) in visibles:
                valor = self.matriz[y][x]
                # Colores de casilla
                if valor == 1:  # muro
                    Color(0.3, 0.3, 0.3)
                elif valor == 2:  # salida
                    Color(0, 1, 0)
                elif valor == 3:  # tesoro
                    Color(1, 1, 0)
                elif valor == 4:  # trampa
                    Color(1, 0, 0)
                else:  # piso
                    Color(0.6, 0.6, 0.6)

                Rectangle(pos=(self.x + x * cell_size, self.y + (self.n - 1 - y) * cell_size),
                          size=(cell_size, cell_size))

            # Dibujar jugador siempre
            jy, jx = self.jugador_pos
            Color(0, 0, 1)
            Rectangle(pos=(self.x + jx * cell_size, self.y + (self.n - 1 - jy) * cell_size),
                      size=(cell_size, cell_size))



class LaberintoApp(App):
    def build(self):
        self.root = BoxLayout(orientation='horizontal')  # Layout horizontal
        self.left_panel = BoxLayout(orientation='vertical', size_hint=(0.8, 1))
        self.right_panel = BoxLayout(orientation='vertical', size_hint=(0.2, 1), spacing=10, padding=10)

        # Entrada inicial
        self.entrada = TextInput(
            hint_text="Tamaño del laberinto (7-50)",
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        self.entrada.bind(on_text_validate=self.generar_laberinto)  # 👈 Enter dispara generar_laberinto

        btn_generar = Button(text="Generar laberinto", size_hint=(1, None), height=40)
        btn_generar.bind(on_press=self.generar_laberinto)
        self.left_panel.add_widget(self.entrada)
        self.left_panel.add_widget(btn_generar)

        # Botones laterales
        btn_reiniciar = Button(text="Reiniciar", size_hint=(1, None), height=50)
        btn_nuevo = Button(text="Nuevo laberinto", size_hint=(1, None), height=50)
        self.right_panel.add_widget(btn_reiniciar)
        self.right_panel.add_widget(btn_nuevo)
        
        # Vincular funciones
        btn_reiniciar.bind(on_press=lambda *a: self.reiniciar(None))
        btn_nuevo.bind(on_press=lambda *a: self.nuevo_laberinto(None))
        
        self.root.add_widget(self.left_panel)
        self.root.add_widget(self.right_panel)
        return self.root

    def generar_laberinto(self, instancia, n=None):
        try:
            if n is None:
                n = int(self.entrada.text)
            if not (7 <= n <= 50):
                raise ValueError
        except:
            popup = Popup(title="Error", content=Label(text="Ingrese un número entre 7 y 50"),
                          size_hint=(None, None), size=(300, 200))
            popup.open()
            return

        self.left_panel.clear_widgets()
        matriz = generar_matriz_con_camino(n)
        self.laberinto_widget = LaberintoWidget(matriz)   # <-- ahora es laberinto_widget
        box = BoxLayout(orientation='vertical')
        self.laberinto_widget.parent_box = box
        box.add_widget(self.laberinto_widget.label_vidas)
        box.add_widget(self.laberinto_widget.label_tesoros)
        box.add_widget(self.laberinto_widget)
        self.left_panel.add_widget(box)

    def reiniciar(self, instancia):
        if hasattr(self, "laberinto_widget") and self.laberinto_widget:
            n = self.laberinto_widget.n
            self.generar_laberinto(None, n)

    def nuevo_laberinto(self, instancia):
        self.left_panel.clear_widgets()
        self.entrada = TextInput(hint_text="Tamaño del laberinto (7-50)", multiline=False, size_hint=(1, None), height=40)
        btn = Button(text="Generar laberinto", size_hint=(1, None), height=40)
        btn.bind(on_press=self.generar_laberinto)
        self.left_panel.add_widget(self.entrada)
        self.left_panel.add_widget(btn)


if __name__ == '__main__':
    LaberintoApp().run()