##############################################
# Parámetros para el método Decourt-Quaresma #
##############################################

import numpy as np

SUELOS = ("Arcilla", "Limo arcilloso", "Limo arenoso", "Arena")
PERFORACIONES = ("Clavada", "Strauss", "Excavada con bentonita", 
                 "Hélice continua", "Raiz", "Inyectada bajo altas presiones")

# ALPHA
#   Filas: PERFORACIONES
#   Columnas: SUELOS
ALPHA = np.array([
    [1.00, 1.00, 1.00, 1.00],
    [0.85, 0.60, 0.60, 0.50],
    [0.85, 0.60, 0.60, 0.50],
    [0.30, 0.30, 0.30, 0.30],
    [0.85, 0.60, 0.60, 0.50],
    [1.00, 1.00, 1.00, 1.00]
])

# BETA
#   Filas: PERFORACIONES
#   Columnas: SUELOS
BETA = np.array([
    [1.00, 1.00, 1.00, 1.00],
    [0.85, 0.65, 0.65, 0.50],
    [0.90, 0.75, 0.75, 0.60],
    [1.00, 1.00, 1.00, 1.00],
    [1.50, 1.50, 1.50, 1.50],
    [3.00, 3.00, 3.00, 3.00]
])

# Valores K, en orden de SUELOS
DK = np.array([120000, 200000, 250000, 400000])