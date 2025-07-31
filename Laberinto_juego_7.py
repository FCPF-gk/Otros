import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label as KivyLabel


def generar_matriz_con_camino(n):
    if n < 7:
        n = 7
    matriz = [[1 for _ in range(n)] for _ in range(n)]

    for i in range(1, n - 1):
        for j in range(1, n - 1):
            matriz[i][j] = 0 if random.random() < 0.7 else 1

    entrada_borde = random.choice(['top', 'bottom', 'left', 'right'])
    if entrada_borde == 'top':
        x, y = 0, random.randint(1, n - 2)
        dx, dy = 1, 0
    elif entrada_borde == 'bottom':
        x, y = n - 1, random.randint(1, n - 2)
        dx, dy = -1, 0
    elif entrada_borde == 'left':
        x, y = random.randint(1, n - 2), 0
        dx, dy = 0, 1
    else:
        x, y = random.randint(1, n - 2), n - 1
        dx, dy = 0, -1

    entrada = (x, y)
    matriz[x][y] = 2

    camino = [(x, y)]
    while True:
        x += dx
        y += dy
        if 0 < x < n - 1 and 0 < y < n - 1:
            matriz[x][y] = 0
            camino.append((x, y))
        else:
            break

    tx, ty = camino[-1]
    matriz[tx][ty] = 3

    cantidad_4 = 0
    if n < 10:
        cantidad_4 = 2
    elif 10 <= n < 20:
        cantidad_4 = 4
    elif 20 <= n < 30:
        cantidad_4 = 8
    elif 30 <= n < 40:
        cantidad_4 = 12
    elif 40 <= n <= 50:
        cantidad_4 = 16

    colocados = 0
    while colocados < cantidad_4:
        i = random.randint(1, n - 2)
        j = random.randint(1, n - 2)
        if matriz[i][j] == 0:
            matriz[i][j] = 4
            colocados += 1

    return matriz


class LaberintoWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.n = int(input("Ingrese la dimensión del laberinto (mínimo 7, máximo 50): "))
        self.n = max(7, min(self.n, 50))

        self.matriz = generar_matriz_con_camino(self.n)
        self.cell_size = min(Window.width, Window.height) / self.n

        self.entrada = [(i, j) for i in range(self.n) for j in range(self.n) if self.matriz[i][j] == 2][0]
        self.personaje_pos = list(self.entrada)
        self.tesoro_encontrado = False
        self.vidas = 3
        self.tesoros = 0

        self.contador_label = KivyLabel(text=self.estado_texto(), size_hint=(None, None),
                                        pos=(10, Window.height - 40), color=(0, 0, 0, 1))
        self.add_widget(self.contador_label)

        Window.bind(on_key_down=self.on_key_down)
        self.bind(size=self.redibujar)
        self.redibujar()

    def estado_texto(self):
        return f"Vidas: {self.vidas}  |  Tesoros: {self.tesoros}"

    def redibujar(self, *args):
        self.canvas.clear()
        with self.canvas:
            for i in range(self.n):
                for j in range(self.n):
                    valor = self.matriz[i][j]
                    x = j * self.cell_size
                    y = Window.height - (i + 1) * self.cell_size

                    if valor == 1:
                        Color(0.2, 0.2, 0.2)
                    elif valor == 0:
                        Color(1, 1, 1)
                    elif valor == 2:
                        Color(0, 1, 0)
                    elif valor == 3:
                        Color(1, 0.84, 0)
                    elif valor == 4:
                        Color(1, 0, 0)

                    Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

            i, j = self.personaje_pos
            x = j * self.cell_size
            y = Window.height - (i + 1) * self.cell_size
            Color(0, 0, 1)
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

        self.contador_label.text = self.estado_texto()

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        dx, dy = 0, 0
        if key == 273:
            dx = -1
        elif key == 274:
            dx = 1
        elif key == 275:
            dy = 1
        elif key == 276:
            dy = -1
        self.mover_personaje(dx, dy)

    def mover_personaje(self, dx, dy):
        x, y = self.personaje_pos
        nx, ny = x + dx, y + dy

        if 0 <= nx < self.n and 0 <= ny < self.n:
            if self.matriz[nx][ny] in [0, 2, 3]:
                self.personaje_pos = [nx, ny]

                if not self.tesoro_encontrado and self.matriz[nx][ny] == 3:
                    self.tesoro_encontrado = True
                    self.tesoros += 1
                    print("¡Encontraste el tesoro! Ahora escapá por la entrada.")
                elif self.tesoro_encontrado and (nx, ny) == self.entrada:
                    print("¡Escapaste del laberinto con el tesoro! 🎉")
                    self.mostrar_popup("¡Felicidades!", "¡Escapaste exitosamente del laberinto!")
                    return

                # Revisar casillas adyacentes para obstáculos
                if self.esta_cerca_de_obstaculo(nx, ny):
                    self.vidas -= 1
                    print(f"¡Cuidado! Perdiste una vida. Vidas restantes: {self.vidas}")
                    if self.vidas == 0:
                        self.mostrar_popup("Game Over", "Te quedaste sin vidas.")
                        return

                self.redibujar()

    def esta_cerca_de_obstaculo(self, x, y):
        adyacentes = [(x + dx, y + dy) for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]]
        for i, j in adyacentes:
            if 0 <= i < self.n and 0 <= j < self.n:
                if self.matriz[i][j] == 4:
                    return True
        return False

    def mostrar_popup(self, titulo, mensaje):
        popup = Popup(
            title=titulo,
            content=Label(text=mensaje),
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=True
        )
        popup.open()


class LaberintoApp(App):
    def build(self):
        return LaberintoWidget()


if __name__ == '__main__':
    LaberintoApp().run()
