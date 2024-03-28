import numpy as np

import tanque as tq
import zpilot as zp

#Valores SPT de los sondeos
SPT1 = np.array([2, 2, 2, 2, 2, 2, 4, 4, 6, 4, 5, 4, 5, 4, 6, 7, 8, 8, 8, 8, 11, 15])
SPT2 = np.array([2, 2, 2, 2, 2, 2, 2, 3, 6, 5, 6, 6, 6, 6, 8, 8, 8, 8, 9, 10, 13, 16])
spt = (SPT1 + SPT2)/2  # Debe ser el promedio de todos los sondeos

# Creamos un viento
velocidad_viento = 50  # m/s
viento = tq.Viento(velocidad_basica=velocidad_viento)

# Luego un tanque con ese viento
capacidad_tanque = 30  # m3
tanque = tq.Tanque(viento, capacidad=capacidad_tanque)

# Coeficientes de seguridad
gG = 1.35  # Para cargas permanentes
gQ = 1.50  # Para cargas variables

# Obtenemos las cargas del tanque
Ne = tanque.carga_normal(agua=False)  # carga con tanque vacío
Nf = gG*Ne + gQ*tanque.peso_agua() 
H1, M1 = tanque.reacciones()  # Fuerza horizontal y momento flector en la base
H = gQ*H1
M = gQ*M1

# Creamos un pilote
L = 15  # Longitud
D = 0.40  # Diámetro
pilote = zp.Pilote(longitud=L, diametro=D, spt=spt)

# Calculamos la capacidad del pilote
# (Verificar tipo de suelo)
P = pilote.R_adm()

# Creamos un cabezal
B = 3.5  # m  Lado del cabezal cuadrado
h = 1.0  # m  Altura del cabezao
tipo = 2  # 5 pilotes
cabezal = zp.Cabezal(pilote=pilote, tipo=2, B=B, h=h, N=Nf, H=H, M=M)

# Imprimir información del viento
viento.info_viento()

# Imprimir información del tanque
tanque.info_tanque()

# Imprimir información del pilote
pilote.info_pilote()

# Imprimir información del cabezal
cabezal.info_cabezal()

# Verificaciones
cabezal.cumplimiento()