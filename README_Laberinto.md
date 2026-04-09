## Juego del Laberinto

Juego desarrollado en Python con Kivy donde el jugador debe encontrar un tesoro y regresar a la puerta de entrada evitando las trampas.

### Gameplay

-Controlas el personaje (azul)
-Debes encontrar el tesoro (amarillo)
-EvitaR las trampas (rojo): son un anillo, el borde daña pero en centro no
-Para ganar: regresar a la puerta de entrada (verde)


### Características

- Generación aleatoria de laberintos 2D (cuadrados), con tamaño configurable
- Camino libre, no lineal, desde la entrada hasta el tesoro garantizado
- Distancia de Manhattan mínima según las dimensiones seleccionadas
- Sistema de 3 vidas (incluye modo fantasma)
- Trampas y obstáculos.
- Visión centrada en el personaje, limitada por distancia y por paredes
- Uso de línea de Bresenham para cálculo de visibilidad
- Recolección del tesoro.


### Cómo ejecutar

- Clonar el repositorio
  git clone https://github.com/FCPF-gk/laberinto.git cd laberinto

- Instalar dependencias
  pip install -r requirements.txt
  
- Ejecutar el juego
  python main.py
