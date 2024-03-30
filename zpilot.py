'''
Verificaciones estructurales para el equilibrio de fundación profunda de
tanques tipo copa.

Autor: Fredy Gabriel Ramírez Villanueva
Fecha primera versión viable: 27 de marzo de 2024
Coronel Oviedo - Paraguay
'''

import math
import numpy as np

from dataclasses import dataclass, field
from typing import Tuple

from hormigon import Hormigon
import suelos.decourt_quaresma as dq
from suelo import Suelo

@dataclass
class Pilote(Hormigon):
    '''Clase para manipular características de pilotes.

    Las unidades deben ser coherentes. Se recomienda el Sistema Internacional
    sin múltiplos ni submúltiplos.

    Atributos:
        suelo (Suelo): objeto de tipo Suelo (librería propia)
        longitud (float): longitud del pilote
        diametro (float): diámetro del pilote

        CONDICIONES DEL PILOTE
        ----------------------

        suelo_punta (str): Tipo de suelo en la punta del pilote.
        suelo_fuste (str): Tipo de suelo alrededor del fuste del pilote
            Suelos permitidos: ("Arcilla", "Limo arcilloso", "Limo arenoso",
                                "Arena")

        perforacion_tipo (str):
            permitidos: ("Clavada", "Excavada general (tipo Strauss)",
            "Excavada con bentonita", "Hélice continua", "Raíz",
            "Inyectada bajo altas presiones"}

        Coeficientes de seguridad:
            gamma_p: float = 4 Coef. de seguridad para la capacidad por punta.
            gamma_L: float = 1.3 Coef. seguridad para capacidad por fricción.
    '''
    # Suelo
    suelo: Suelo = Suelo()

    # Geometría
    longitud: float = 10.  # longitud del pilote
    diametro: float = 0.30  # diámetro del pilote

    # TODO agregar un cálculo de tracción
    traccion: float = 0.  # capacidad a tracción

    # Condiciones del pilote para el método Decourt-Quaresma
    suelo_punta: int = "Limo arcilloso"  # Suelo en la punta del pilote
    suelo_fuste: int = "Limo arcilloso"  # Suelo en el fuste del pilote
    perforacion_tipo = "Strauss"  # Tipo de perforación

    # Coeficientes de seguridad:
    gamma_p: float = 4  # Coeficiente de seguridad para la capacidad por punta
    gamma_L: float = 1.3  # Coef. de seguridad para la capacidad por fricción

    # Cuestiones geométricas
    def area(self):
        '''Área de la sección transversal'''
        return math.pi * (self.diametro / 2)**2

    def area_lateral(self):
        '''Área lateral del pilote'''
        return math.pi * self.diametro * self.longitud

    def volumen(self):
        '''Volumen del pilote'''
        return self.area() * self.longitud

    def inercia(self):
        '''Inercia de la sección transversal circular'''
        return math.pi * (self.diametro/2)**4 / 4

    # Cuestiones físicas
    def peso(self) -> float:
        return self.volumen() * self.peso_esp

    def rigidez_axial(self):
        return self.elasticidad * self.area / self.longitud


    ################################
    ### Método Decourt Quaresma  ###
    ################################

    # Condiciones del pilote
    def suelos(self) -> Tuple[str]:
        '''Tipos de suelos permitidos'''
        return list(dq.SUELOS)

    def perforaciones(self) -> Tuple[str]:
        '''Perforaciones consideradas'''
        return list(dq.PERFORACIONES)

    def id_suelo_punta(self) -> int:
        '''Índice correspondiente al suelo en la punta del pilote'''
        return self.suelos().index(self.suelo_punta)

    def id_suelo_fuste(self) -> int:
        '''Muestra el tipo de suelo en la punta del pilote'''
        return self.suelos().index(self.suelo_fuste)

    def id_perforacion(self) -> int:
        '''Muestra el tipo de perforación adoptado'''
        return self.perforaciones().index(self.perforacion_tipo)

    ## RESISTENCIA POR PUNTA
    def alpha(self):
        '''Valor alpha para la resistencia por punta'''
        return dq.ALPHA[self.id_suelo_punta(), self.id_perforacion()]

    def valor_K(self):
        '''Valor K del método Decourt-Quaresma para la resistencia por punta'''
        return dq.DK[self.id_suelo_punta()]

    def rp(self):
        '''Resistencia unitaria por punta'''
        return self.valor_K() * self.suelo.Np(self.longitud)

    def Rp(self):
        '''Resistencia admisible por punta'''
        return self.alpha() * self.rp() * self.area() / self.gamma_p

    ## FRICCIÓN LATERAL
    def beta(self) -> float:
        '''Coeficiente de fricción'''
        return dq.BETA[self.id_suelo_fuste(), self.id_perforacion()]

    def rL(self) -> float:
        '''Frición lateral unitaria'''
        NL = self.suelo.NL(self.longitud)
        return 10e3*(NL/3 + 1)

    def RL(self) -> float:
        '''Resistencia lateral admisible'''
        return self.beta() * self.rL() * self.area_lateral() / self.gamma_L

    def Rtotal(self) -> float:
        '''Resistencia total'''
        return self.Rp + self.RL

    def R_adm(self) -> float:
        '''Resistencia adoptada final

        Aplicación de la condición de la Norma NBR6122, sección 8.2.1.2
        '''

        Rp1 = self.Rp()  # Resistencia calculada por punta
        RL = self.RL()

        if self.id_perforacion in [1, 2]:  # Perforación excavada
            # Máximo valor permitido para la resitencia por punta
            Rp2 = 0.25 * RL
            Rp_max = min(Rp1, Rp2)
        else:  # Para el caso de perforaciones no excavadas
            Rp_max = Rp1

        return Rp_max + RL

    ##########################################
    ### Resistencia a la fuerza horizontal ###
    ##########################################

    def n_spt(self, z:float) -> int:
        '''Número de golpes (N) del ensayo SPT a una profunidad dada.

        z: profundidad en m

        - En el primer metro devuelve cero;
        - En el segundo metro devuelve N a la profundidad de 1m;
        - En el tercer metro devuelve N a la profundidad de 2m;
        - En el n-ésimo metro devuelve N a la profundidad de (n-1) metros
        '''
        p = math.floor(z)
        if p <= 0:
            return 0
        elif p <= self.longitud:
            return suelo.spt_ajustado()[p]
        else:
            raise ValueError(f"La profundidad dada {p} m no puede ser mayor a \
                             la longitud del pilote {self.longitud} m")


    def s(self, profundidad:float):
        '''Módulo de reacción horizontal por unidad de longitud del pilote.

        profundidad: profundidad considerada en m.

        Devuelve el valor correspondiente a una profundidad dada.
        Fórmula de Terzaghi.
        '''
        nspt = self.n_spt(profundidad)

        if profundidad <= self.longitud:
            if self.id_suelo_fuste in [0, 1]:  # Suelos cohesivos
                # TODO implementar suelos cohesivos
                raise ValueError("Aún no implementado para suelos cohesivos")
            else: # Suelos no cohesivos
                return 6000 * 10**((nspt - 28)/40) * profundidad * 1e3
        else:
            raise ValueError(f"La profundidad dada {profundidad} m debe ser \
                             menor a la longitud del pilote {self.longitud} m")

    def info_pilote(self):
        '''Imprime información sobre el pilote.

        Se considera que las unidades corresponden al Sistema Internacional
        de unidades, sin múltiplos ni submúltiplos.
        '''
        print('\nPILOTE:')
        print(f"Longitud del pilote: {self.longitud} m")
        print(f"Diámetro: {self.diametro*100:.0f} cm")
        print("Tipo de perforación: " + self.perforacion_tipo)
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
        H: Tanque lleno con viento
    '''

    # Suelo
    suelo: Suelo = Suelo(np.ones(15)*5)
    
    # Pilotes para el cabezal
    pilote: Pilote = field(default_factory=Pilote(suelo=suelo, longitud=15, 
                                                  diametro=0.40, 
                                                  suelo_fuste='Arcilla', 
                                                  suelo_punta='Arena'))

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
        '''Diccionario que relaciona tipo de cabezal con número de pilotes.'''
        return {1: "4 pilotes", 2: "5 pilotes", 3: "9 pilotes"}

    def tipos_permitidos(self):
        return list(self.tipologia().keys())

    @property
    def tipo(self):
        '''Devuelve el valor del atributo _tipo'''
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        '''Valida y asigna el valor del atributo '_tipo'.
        
        Args:
            valor: El nuevo valor para el atributo 'tipo'

        Raises:
            ValueError: si el valor no es válido
        '''
        if valor in self.tipos_permitidos():
            self._tipo = valor
        else:
            ValueError(f'Tipo de cabezal inválido: {valor}. \
                       Tipos permitidos: {self.tipos_permitidos()}')

    def factores(self) -> dict:
        '''Factores según la cantidad de pilotes para las ecuaciones.

        Se relaciona con factor_pilote()
        '''
        return {1: 2, 2: 2, 3: 3}

    def numero_pilotes(self) -> int:
        """Número de pilotes según la tipología seleccionada"""
        return {1: 4, 2: 5, 3: 9}[self.tipo]

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
        # TODO considerar excentricidad de la carga vertical.
        b2 = 2*(self.H*self.h + self.M) / (n*P + n*T)

        # Separación mínima entre ejes de pilotes extremos
        b_min = max(b1, b2)

        return 2*v + D + b_min

    def cargaH(self) -> float:
        '''Carga máxima en pilotes con hipótesis H: Tanque lleno con viento'''

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

    def verif_pilote(self) -> bool:
        '''Verificación de la capacidad de carga del pilote'''
        return self.cargaH() < self.pilote.R_adm()

    def info_cabezal(self):
        '''Imprime información sobre el cabezal.

        Se considera las unidades del Sistema Internacional, sin múltiplos ni
        submúltiplos.
        '''
        print("\nCABEZAL CUADRADO")
        print(f"Cabezal tipo {self.tipo} con: {self.numero_pilotes()} pilotes")
        print(f"Ancho mínimo del cabezal: {self.ancho_min():.2f} m")
        print(f"Ancho adoptado: {self.B:.2f} m")
        print(f"Altura del cabezal: {self.h:.2f} m")
        print(f"Acción máx. sobre pilotes: {self.cargaH()/1000:.2f} kN")

    def cumplimiento(self):
        c = 'Cumple' if self.verif_pilote() else 'No cumple'

        print("\nVERIFICACIÓN")
        print(f"Verificación de capacidad de pilote : {c}")
        print('Debe verificar además: punzonamiento y flexión en el cabezal.')



if __name__ == "__main__":
    suelo = Suelo(spt=np.ones(15)*5)
    pilote = Pilote(suelo=suelo, longitud=15, diametro=0.40,
                   suelo_fuste='Limo arcilloso', suelo_punta='Limo arcilloso')
    cabezal = Cabezal(suelo=suelo, pilote=pilote)
    pilote.info_pilote()
    cabezal.info_cabezal()