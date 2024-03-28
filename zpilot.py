'''
Verificaciones estructurales para el equilibrio de fundación profunda de tanques tipo copa.

Autor: Fredy Gabriel Ramírez Villanueva
Fecha primera versión viable: 27 de marzo de 2024
Coronel Oviedo - Paraguay
'''

import math
import numpy as np
import pandas as pd

from dataclasses import dataclass, field
from typing import Union


# Parámetros para el método Decourt-Quaresma
SUELOS = {0: "Arcilla", 1: "Limo arcilloso", 2: "Limo arenoso", 3: "Arena"}
PERFORACIONES = {0: "Clavada", 1: "Excavada general (tipo Strauss)",
                 2: "Excavada con bentonita", 3: "Hélice continua", 4: "Raíz",
                 5: "Inyectada bajo altas presiones"}

ALPHA = {PERFORACIONES[0]:[1.0, 1.0, 1.0, 1.0], PERFORACIONES[1]:[0.85,0.60, 0.60, 0.50],
            PERFORACIONES[2]:[0.85, 0.60, 0.60, 0.50], PERFORACIONES[3]:[0.30,0.30,
            0.30,0.30], PERFORACIONES[4]:[0.85,0.60,0.60,0.50], 
            PERFORACIONES[5]:[1.0,1.0,1.0,1.0]}

C = list(PERFORACIONES.values())
IDX = list(SUELOS.values())
TABLALPHA = pd.DataFrame(ALPHA, columns=C, index=IDX)

BETA = {PERFORACIONES[0]:[1.0, 1.0, 1.0, 1.0],
        PERFORACIONES[1]:[0.85,0.65, 0.65, 0.50],
        PERFORACIONES[2]:[0.90, 0.75, 0.75, 0.60],
        PERFORACIONES[3]:[1.0,1.0,1.0,1.0],
        PERFORACIONES[4]:[1.5,1.5,1.5,1.5],
        PERFORACIONES[5]:[3.0,3.0,3.0,3.0]}

TABLABETA = pd.DataFrame(BETA, columns=C, index=IDX)

# Valores K para resistencia por punta
DK = [120000, 200000, 250000, 400000]  # N/m2

@dataclass
class Hormigon:
    '''Características del hormigón armado

    Las unidades deben ser coherentes.
    
    Atributos:
        peso_esp (float): peso específico = 25 kN/m3 por defecto.

    '''
    peso_esp: float = 24000  # N/m3
    elasticidad: float = 35954e6  # MPa


@dataclass
class Pilote(Hormigon):
    '''Clase para manipular características de pilotes.
    
    Las unidades deben ser coherentes.

    Atributos:
        longitud (float): longitud del pilote
        diametro (float): diámetro del pilote
        spt (numpy array): Golpes SPT en cada metro. Si hay varios
                            sondeos, introducir el promedio.

        CONDICIONES DEL PILOTE
        ----------------------

        suelo_punta (int): Tipo de suelo en la punta del pilote. 
        suelo_fuste (int): Tipo de suelo alrededor del fuste del pilote
            Suelos permitidos: {0:"Arcilla", 1:"Limo arcilloso", 2:"Limo arenoso",
            3:"Arena"}
        
        perforacion_tipo (int):
            permitidos: {0: "Clavada", 1:"Excavada general (tipo Strauss)",
            2:"Excavada con bentonita", 3:"Hélice continua", 4:"Raíz",
            5:"Inyectada bajo altas presiones"}
        
        Coeficientes de seguridad:
            gamma_p: float = 4  Coeficiente de seguridad para la capacidad por punta.
            gamma_L: float = 1.3  Coeficiente de seguridad para la capacidad por fricción.
    '''
    # Geometría
    longitud: float = 10.  # longitud del pilote
    diametro: float = 0.30  # diámetro del pilote

    # TODO agregar un cálculo de tracción
    traccion: float = 0.  # capacidad a tracción

    # Golpes SPT en cada metro. Si hay varios sondeos, ingresar el promedio.
    spt: Union[np.ndarray, float] = field(default_factory=np.ones(int(longitud))*3)

    # Condiciones del pilote
    suelo_punta: int = 1  # Tipo de suelo en la punta del pilote
    suelo_fuste: int = 1  # Tipo de suelo alrededor del fuste del pilote
    perforacion_tipo = 1  # Tipo de perforación

    # Coeficientes de seguridad:
    gamma_p: float = 4  # Coeficiente de seguridad para la capacidad por punta
    gamma_L: float = 1.3  # Coeficiente de seguridad para la capacidad por fricción

    # Cuestiones geométricas
    def area(self):
        '''Área de la sección transversal'''
        return math.pi * (self.diametro / 2)**2
    
    def area_lateral(self):
        '''Área lateral del pilote'''
        return math.pi * self.diametro * self.longitud

    def volumen(self):
        '''Volumen del pilote'''
        return self.area(self.diametro) * self.longitud
    
    # Cuestiones de físicas
    def peso(self) -> float:
        return self.volumen() * self.peso_esp
    
    def rigidez_axial(self):
        return self.elasticidad * self.area / self.longitud
    
    # Sobre el SPT
    def profundidad_sondeada(self):
        '''Profundidad sondeada con el ensayo SPT'''
        try:
            ps = len(self.spt)  # Profundidad sondeada
            return ps
        except KeyError:
            raise ValueError(f"La profundidad sondeada: {ps} \
                             debe ser mayor que la longitud del pilote: \
                             {self.longitud}")
    
    def spt_ajustado(self) -> np.ndarray:
        '''Ajuste de valores SPT.
        
        Los valores SPT menores a 3, deben ser considerados iguales a 3, 
        los mayores a 50 deben ser considerados 50.
        '''
        nuevo_spt = np.where(self.spt < 3, 3, self.spt)
        nuevo_spt = np.where(nuevo_spt > 50, 50, nuevo_spt)
        
        return nuevo_spt
    
    ################################
    ### Método Decourt Quaresma  ###
    ###############################
    
    # Condiciones del pilote
    def suelos(self) -> dict:
        '''Tipos de suelos permitidos'''
        return SUELOS
    
    def perforaciones(self) -> dict:
        '''Perforaciones consideradas'''
        return PERFORACIONES
    
    def s_punta(self) -> str:
        '''Muestra el tipo de suelo en la punta del pilote'''
        return SUELOS[self.suelo_punta]
    
    def s_fuste(self) -> str:
        '''Muestra el tipo de suelo en la punta del pilote'''
        return SUELOS[self.suelo_fuste]
    
    def perforacion(self) -> str:
        '''Muestra el tipo de perforación adoptado'''
        return PERFORACIONES[self.perforacion_tipo]
    
    ## RESISTENCIA POR PUNTA
    def alpha(self):
        '''Valor alpha para la resistencia por punta'''
        return TABLALPHA.iloc[self.suelo_punta, self.perforacion_tipo]
    
    def valor_K(self):
        '''Valor K del método Decourt-Quaresma para la resistencia por punta'''
        return DK[self.suelo_punta]
    
    def Np(self):
        '''Np como promedio de valores SPT alrededor de la punta'''
        S = self.spt_ajustado()
        L = int(self.longitud)
        if len(self.spt) == L:
            return (S[-3], S[-2], S[-1])/3
        else:
            return (S[L-2] + S[L-1] + S[L])/3
        
    def rp(self):
        '''Resistencia unitaria por punta'''
        return self.valor_K() * self.Np()
    
    def Rp(self):
        '''Resistencia admisible por punta'''
        return self.alpha() * self.rp() * self.area() / self.gamma_p
    
    ## RESISTENCIA LATERAL
    def beta(self):
        '''Coeficiente de fricción'''
        return TABLABETA.iloc[self.suelo_fuste, self.perforacion_tipo]

    def NL(self):
        '''Promedio SPT a lo largo del fuste'''
        
        # Todos los valores SPT ajustados menos los 3 que rodean la punta
        L = int(self.longitud)
        spt_L = self.spt_ajustado()[:L-2]
        return np.mean(spt_L)
    
    def rL(self):
        '''Frición lateral unitaria'''
        return 10e3*(self.NL()/3 + 1)
    
    def RL(self):
        '''Resistencia lateral admisible'''
        return self.beta() * self.rL() * self.area_lateral() / self.gamma_L
    
    def Rtotal(self):
        '''Resistencia total'''
        return self.Rp + self.RL
    
    def R_adm(self):
        '''Resistencia adoptada final
        
        Aplicación de la condición de la Norma NBR6122, sección 8.2.1.2
        '''

        Rp1 = self.Rp()  # Resistencia calculada por punta
        RL = self.RL()

        if self.perforacion_tipo in [1, 2]:  # Perforación excavada
            # Máximo valor permitido para la resitencia por punta
            Rp2 = 0.25 * RL
            Rp_max = min(Rp1, Rp2)
        else:
            Rp_max = Rp1

        return Rp_max + RL
    
    def info_pilote(self):
        '''Imprime información sobre el pilote.
        
        Se considera que los datos fueron introducidos en el Sistema Internacional
        de unidades, sin múltiplos ni submúltiplos.
        '''
        print('\nPILOTE:')
        print(f"Longitud del pilote: {self.longitud} m")
        print(f"Diámetro: {self.diametro*100:.0f} cm")
        print("Tipo de perforación: " + self.perforacion())
        print(f'Capacidad: {self.R_adm()/1000:.2f} kN')

    
@dataclass
class Cabezal(Hormigon):
    ''' Cabezal CUADRADO de hormigón armado.
    
    Las dimensiones debe ser coherentes.

    Atributos:
        tipo (int):
            1: 4 pilotes
            --------
            | O  O |
            | O  O |
            --------

            2: 5 pilotes (1 en c/ esquina del cuadrado y 1 en el centro)
            --------
            | O   O |
            |   O   |
            | O   O |
            ---------
            3: 9 pilotes (3 filas y 3 columnas)
            ---------
            | O O O |
            | O O O |
            | O O O |
            ---------
        
        - Geometría:
        B (float): lado del cabezal
        h (float): altura del cabezal
        v (float): voladizo desde cara externa de pilate

        - Cargas:
        N (float): Carga vertical hacia abajo sobre el cabezal
        H (float): Fuerza horizontal
        M (float): Momento flector en la cara superior del cabezal

        - Hipótesis de carga
        H1: Tanque lleno sin viento
        H2: Tanque lleno con viento
    '''

    # Pilotes para el cabezal
    pilote: Pilote = field(default_factory=Pilote(longitud=10, diametro=0.30, 
                                                  spt=np.ones(10)*3))

    # Tipo de cabezal
    tipo: int = 1

    # Geometría
    B: float = 3.  # Dimensión del cabezal cuadrado en planta
    h: float = 1.  # Altura del cabezal
    v: float = 0.3  # Dist. e/ cara externa de pilote y borde del cabezal

    # Cargas. Ya deben estar mayoradas.
    N: float = 100000  # Carga vertical hacia abajo sobre el cabezal
    H: float = 0  # Fuerza horizontal
    M: float = 0  # Momento flector en la cara superior del cabezal


    def peso(self) -> float:
        '''Peso total del cabezal (prisma recto cuadrangular)'''
        return (self.B)**2 * self.h * self.peso_esp
    
    def tipologia(self):
        '''Diccionario que relaciona el tipo de cabezal con el número de pilotes.'''
        return {1: 4, 2: 5, 3: 9}
    
    def tipos_permitidos(self):
        return self.tipologia().keys()
    
    @property
    def tipo(self):
        return self._tipo
    
    @tipo.setter
    def tipo(self, tipo2):
        if tipo2 in self.tipos_permitidos():
            self._tipo = tipo2
        else:
            ValueError(f'Tipo de cabezal inválido: {self.tipo}. Tipos permitidos: {list(self.tipologia.keys())}')
    
    def factores(self) -> dict:
        '''Factores según la cantidad de pilotes para las ecuaciones.
        
        Se relaciona con factor_pilote()
        '''
        return {1: 2, 2: 2, 3: 3}
    
    def numero_pilotes(self) -> int:
        """Número de pilotes según la tipología seleccionada"""
        return self.tipologia()[self.tipo]
        
    def factor_pilote(self) -> int:
        '''Factor que considera la cantidad de pilotes para las ecuaciones'''
        return self.factores()[self.tipo]
    
    def separacion_min(self):
        '''Separación mínima entre ejes de pilotes'''
        return 2.5 * self.pilote.diametro

    def ancho_min(self) -> float:
        '''Ancho mínimo del cabezal para evitar vuelco'''
        
        D = self.pilote.diametro
        P = self.pilote.R_adm()
        T = self.pilote.traccion
        NP = self.numero_pilotes
        n = self.factor_pilote()
        v = self.v

        # Considera la separación mínima entre pilotes
        factores = {4: 1, 5: math.sqrt(2), 9: 2}
        s_min = self.separacion_min()
        b1 = factores.get(NP, 1) * s_min

        # Separación por ecuación de equilibrio
        b2 = 2*(self.H*self.h + self.M) / (n*P + n*T)

        # Separación mínima entre ejes de pilotes extremos
        b_min = max(b1, b2) 

        return 2*v + D + b_min
    
    def cargaH1(self) -> float:
        '''Carga máxima en pilotes con hipótesis H1: Tanque lleno sin viento'''
        N = self.N  # Carga vertical sobre el cabezal
        W = self.peso()  # Peso del cabezal
        NP = self.numero_pilotes()  # Número total de pilotes

        return (N + W)/NP
    
    def cargaH2(self) -> float:
        '''Carga máxima en pilotes con hipótesis H2: Tanque lleno con viento'''
        
        N = self.N  # Carga vertical sobre el cabezal
        W = self.peso()  # Peso del cabezal
        H = self.H  # Carga horizontal de viento
        M = self.M  # Momento flector en la base
        n = self.factor_pilote()  # Factor que considera el número de pilotes
        h = self.h  # Altura del cabezal
        b = self.B - 2*self.v - self.pilote.diametro

        if self.tipo == 1:
            return ((N + W)/2 + (H*h + M)/b)/n
        elif self.tipo in [2, 3]:
            return (2/3*((N + W)/2 + (H*h + M)/b)) / n

    def carga_pilote(self) -> float:
        '''Carga máxima sobre un pilote'''
        H1 = self.cargaH1()
        H2 = self.cargaH2()

        return max(H1, H2)
    
    def verif_pilote(self) -> bool:
        '''Verificación de la capacidad de carga del pilote'''
        return self.carga_pilote() < self.pilote.R_adm()
    
    def info_cabezal(self):
        '''Imprime información sobre el cabezal.
        
        Se considera que los datos fueron introducidos en el Sistema Internacional
        de unidades, sin múltiplos ni submúltiplos.
        '''
        print("\nCABEZAL CUADRADO")
        print(f"Cabezal con: {self.numero_pilotes()} pilotes")
        print(f"Ancho mínimo del cabezal: {self.ancho_min():.2f} m")
        print(f"Ancho adoptado: {self.B:.2f} m")
        print(f"Altura del cabezal: {self.h:.2f} m")
        print(f"Acción máxima sobre pilotes: {self.carga_pilote()/1000:.2f} kN")

    def cumplimiento(self):
        c = 'Cumple' if self.verif_pilote() else 'No cumple'

        print("\nVERIFICACIÓN")
        print(f"Verificación de capacidad de pilote : {c}")
        print('Debe verificar además: punzonamiento y flexión en el cabezal.')



if __name__ == '__main__':

    import tanque as tq
    
    # Creamos primero un viento
    viento = tq.Viento(50)

    # Luego un tanque con ese viento
    tanque = tq.Tanque(viento, 30)

    # Coeficientes de seguridad
    gG = 1.35  # Para cargas permanentes
    gQ = 1.50  # Para cargas variables

    # Obtenemos las cargas del tanque
    Ne = tanque.carga_normal(agua=False)  # carga con tanque vacío
    Nf = gG*Ne + gQ*tanque.peso_agua() 
    H1, M1 = tanque.reacciones()  # Fuerza horizontal y momento flector en la base
    H = gQ*H1
    M = gQ*M1

    #Valores SPT de los sondeos
    SPT1 = np.array([2, 2, 2, 2, 2, 2, 4, 4, 6, 4, 5, 4, 5, 4, 6, 7, 8, 8, 8, 8, 11, 15])
    SPT2 = np.array([2, 2, 2, 2, 2, 2, 2, 3, 6, 5, 6, 6, 6, 6, 8, 8, 8, 8, 9, 10, 13, 16])
    spt = (SPT1 + SPT2)/2
    
    # Crear un pilote
    L = 15  # Longitud
    D = 0.40  # Diámetro
    pilote = Pilote(longitud=L, diametro=D, spt=spt)

    # Capacidad del pilote
    P = pilote.R_adm()

    # Crear un cabezal
    B = 3.5
    h = 1.0
    tipo = 2  # 5 pilotes
    cabezal = Cabezal(pilote=pilote, tipo=2, B=B, h=h, N=Nf, H=H, M=M)

    # Imprimir información del tanque
    tanque.info_tanque()

    # Imprimir información del pilote
    pilote.info_pilote()

    # Imprimir información del cabezal
    cabezal.info_cabezal()

    # Verificaciones
    print("\nVERIFICACIÓN")
    print(f"Verificación de capacidad de pilote : {cabezal.verif_pilote()}")

