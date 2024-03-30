import numpy as np

import tanque as tq
import zpilot as zp
from suelo import Suelo

######################
## PREPROCESAMIENTO ##
######################

# CREAMOS UN VIENTO
viento = tq.Viento(velocidad_basica=50)

# CREAMOS UN TANQUE
# El viento anterior actúa sobre este tanque
tanque = tq.Tanque(viento=viento, capacidad=30)  # capacidad en m3

# CREAMOS UN SUELO
#Valores SPT de los sondeos
SPT1 = np.array([2, 2, 2, 2, 2, 2, 4, 4, 6, 4, 5, 4, 5, 4, 6, 7, 8, 8, 8, 8, 
                 11, 15])
SPT2 = np.array([2, 2, 2, 2, 2, 2, 2, 3, 6, 5, 6, 6, 6, 6, 8, 8, 8, 8, 9, 10, 
                 13, 16])
spt = (SPT1 + SPT2)/2  # Debe ser el promedio de todos los sondeos
suelo = Suelo(spt=spt)

# CREAMOS UN PILOTE
# Longitud y diámetro en metros
pilote = zp.Pilote(suelo=suelo, longitud=15, diametro=0.40, 
                   suelo_fuste='Limo arcilloso', suelo_punta='Limo arcilloso')


###################
## PROCESAMIENTO ##
###################

# Obtenemos las cargas del tanque
H, V, M = tanque.reacciones_mayoradas()

# Creamos un cabezal que va a recibir esas cargas
B = 3.5  # m  Lado del cabezal cuadrado
h = 1.0  # m  Altura del cabezao
tipo = 2  # 5 pilotes
cabezal = zp.Cabezal(suelo=suelo, pilote=pilote, tipo=tipo, B=B, h=h, N=V, H=H, 
                    M=M)

################
## RESULTADOS ##
################

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