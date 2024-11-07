import numpy as np
import math

# Crear matriz de números aleatorios para el ejercicio
Encuesta = np.round(10 * np.random.rand(40, 5)).astype(int)
# Filas = Inquilinos, Columnas = Preferencias
Inquilinos = Encuesta.shape[0]
Preferencias = Encuesta.shape[1]

# Matriz de incompatibilidad
Incompatibilidad = np.zeros((Inquilinos, Inquilinos))

# Cálculo de la matriz de incompatibilidad
for i in range(Inquilinos - 1):
    for j in range(Inquilinos - 1):
        r = [(Encuesta[i, k] - Encuesta[j + 1, k]) ** 2 for k in range(Preferencias)]
        q = sum(r)
        incompat_value = round(math.sqrt(q))
        Incompatibilidad[i, j + 1] = incompat_value
        Incompatibilidad[j + 1, i] = incompat_value

# Solicitar el número de un inquilino
X = int(input('Por favor ingrese el número de un inquilino: ')) - 1  # Restamos 1 porque Python usa índices base 0

# Tomar la columna del inquilino
Vecinos = Incompatibilidad[:, X]

# Agregar al principio una columna con el número de inquilino
Vecinos = np.column_stack((np.arange(1, len(Vecinos) + 1), Vecinos))

# Ordenar de menor a mayor según la columna 2
Vecinos = Vecinos[Vecinos[:, 1].argsort()]

# Extraer los tres vecinos más compatibles
Vec1, Vec2, Vec3 = int(Vecinos[1, 0]), int(Vecinos[2, 0]), int(Vecinos[3, 0])

# Mostrar resultado
print(f'Los tres vecinos más compatibles con el inquilino solicitado son: {Vec1}, {Vec2} y {Vec3}')
