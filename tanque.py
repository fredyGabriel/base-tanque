'''
Cálculo de acciones de tanque tipo copa sobre fundación.

Autor: Fredy Gabriel Ramírez Villanueva
Fecha primera versión viable: 27 de marzo de 2024
Coronel Oviedo - Paraguay
'''

from dataclasses import dataclass
import pandas as pd
import sympy as sp
from typing import Tuple


@dataclass
class Viento:
    '''Viento según NP196'''

    velocidad_basica: float = 50.  # m/s velocidad básica
    altura_basica: float = 10.  # m  altura básica
    gamma: float = 2/7  # Coeficiente de perfil de viento
    S1: float = 1.00  # Factor topográfico
    S2: float = 1.00  # Factor combinado
    S3: float = 1.00  # Factor estadístico
    rho: float = 1.29  # kg/m3  Densidad del aire

    def velocidad_caracteristica(self):
        '''Velocidad característica del viento'''

        return self.S1 * self.S2 * self.S3 * self.velocidad_basica
    
    def velocidad_z(self) -> sp.core.expr.Expr:
        '''Velocidad del viento a una altura z simbólica (m)'''
        z = sp.symbols('z')

        vk = self.velocidad_caracteristica()
        h0 = self.altura_basica

        return vk*(z/h0)**self.gamma  # Velocidad del viento a una altura z
    
    def presion(self) -> sp.core.expr.Expr:
        return self.rho*self.velocidad_z()**2/2  # Presión de viento sin coeficiente de arrastre
    
    def presion_10(self) -> float:
        '''Presión a 10m de altura'''
        return self.rho * (self.velocidad_caracteristica())**2 / 2

    def info_viento(self) -> None:
        '''Imprime información sobre el viento.
        
        Se considera que los datos fueron introducidos en el Sistema Internacional
        de unidades, sin múltiplos ni submúltiplos.
        '''
        print("\nVIENTO")
        print(f"Velocidad básica: {self.velocidad_basica} m/s")
        print(f"Presión a 10m de altura: {self.presion_10()/1000:.2f} kN/m2")


@dataclass
class Tanque:
    '''Características del tanque'''

    viento: Viento
    capacidad: int = 20  # m3
    factor_pp: float = 1.5

    def capacidades_permitidas(self):
        '''Capacidades permitidas de tanque'''

        return [15, 20, 30, 60]

    @property
    def capacidad(self):
        return self._capacidad

    @capacidad.setter
    def capacidad(self, nueva_capacidad):
        valores_permitidos = self.capacidades_permitidas()
        if nueva_capacidad in valores_permitidos:
            self._capacidad = nueva_capacidad
        else:
            raise ValueError(f"La capacidad {nueva_capacidad} no es válida. Debe ser uno de los siguientes valores: {valores_permitidos}")

    def datos_tanques(self) -> pd.DataFrame:
        '''Datos geométricos del tanque'''

        datos = {
            "capacidad": self.capacidades_permitidas(),
            "diam_fuste": [0.80, 0.80, 0.80, 1.50],
            "altura_fuste": [12., 12., 12., 14.],
            "diam_copa": [2., 2., 2.3, 3.2],
            "altura_copa": [5.60, 5.90, 5.90, 5.40]
            }
        return pd.DataFrame(datos)
    
    def diam_fuste(self):
        '''Diámetro del fuste'''
        datos = self.datos_tanques()
        return datos.loc[datos['capacidad'] == self.capacidad, 'diam_fuste'].item()
    
    def altura_fuste(self):
        '''Altura del fuste'''
        datos = self.datos_tanques()
        return datos.loc[datos['capacidad'] == self.capacidad, 'altura_fuste'].item()
    
    def diam_copa(self):
        '''Diámetro de la copa'''
        datos = self.datos_tanques()
        return datos.loc[datos['capacidad'] == self.capacidad, 'diam_copa'].item()
    
    def altura_copa(self):
        '''Altura de la copa'''
        datos = self.datos_tanques()
        return datos.loc[datos['capacidad'] == self.capacidad, 'altura_copa'].item()

    def pp(self):
        '''Peso propio del tanque en kN.
        
        Se estima multiplicando un factor por la capacidad del tanque.
        '''

        return self.capacidad * self.factor_pp * 1000
    
    def peso_agua(self):
        '''Peso del agua, en kN, con tanque lleno.'''

        return self.capacidad * 9.80665 * 1000
    
    def carga_normal(self, agua: bool = True) -> float:
        '''Carga de gravedad total'''
        if agua:  # Tanque lleno
            return self.pp() + self.peso_agua()
        else:  # Tanque vacío
            return self.pp()

    
    ###########################
    #### Cargas de viento  ####
    ###########################
        
    # Función interpoladora
    def coef_resist(self, dh: float):
        '''Devuelve el coeficiente de resistencia aerodinámica
        de cilindros, dada la relación dh = diámetro/altura'''
        
        #Tabla de CD: Coeficiente de resistencia aerodinámica
        #Fuente: Raquel Gálvez Román
        #"Cálculo de torre de aerogenerador". 2005, página 69.
        #Tomado de Frank M. White "Mecánica de fluidos"
        
        #Relación Diámetro/Altura
        DsH = [0,0.025,0.05,0.1,0.2,1/3,0.5,1]
        #Coeficientes de resistencia aerodinámica
        CD = [1.2,0.98,0.91,0.82,0.74,0.72,0.68,0.74]
        
        contador = 0
        menor = 2 # cualquier número algo 'grande'
        for i in DsH:
            x = abs(dh - i)
            if x < menor:
                menor = x
                punto = i #valor más cercano a Dhf
                u = contador #ubicación del punto más cercano a Dhf
            contador += 1
        if punto < dh:
            C_D = (CD[u]-CD[u+1])/(DsH[u+1]-DsH[u])*(DsH[u+1]-dh) + CD[u+1]
        elif punto > dh:
            C_D = (CD[u-1]-CD[u])/(DsH[u]-DsH[u-1])*(DsH[u]-dh) + CD[u]
        else:
            C_D = punto
        return C_D

    def cd_fuste(self):
        '''Coeficiente de resistencia del fuste'''
        return self.coef_resist(self.diam_fuste() / self.altura_fuste())

    def cd_copa(self):
        '''Coeficiente de resistencia del fuste'''
        return self.coef_resist(self.diam_copa() / self.altura_copa())
    
    def reacciones(self) -> Tuple[float, float]:
        '''Fuerza horizontal (N) y momento flector en la base (Nm)'''
        z = sp.symbols('z') #cota vertical, m
        Dc = self.diam_copa()
        Df = self.diam_fuste()
        hf = self.altura_fuste()
        hc = self.altura_copa()
        cdf = self.cd_fuste()
        cdc = self.cd_copa()

        qz = self.viento.presion()

        F_fuste =  sp.N(sp.integrate(cdf*Df*qz, (z, 0, hf)))
        M_fuste = sp.N(sp.integrate(cdf*Df*qz*z, (z, 0, hf)))
        
        F_copa = sp.N(sp.integrate(cdc*Dc*qz, (z, hf, hf + hc)))
        
        M_copa = sp.N(sp.integrate(cdc*Dc*qz*z, (z, hf, hf+hc)))

        # Fuerza horizontal total en la base
        H = F_fuste + F_copa

        # Momento flector total en la base
        M = M_fuste + M_copa

        return H, M
    
    def info_tanque(self):
        '''Imprime información sobre el tanque.
        
        Se considera que los datos fueron introducidos en el Sistema Internacional
        de unidades, sin múltiplos ni submúltiplos.
        '''
        print("\nTANQUE")
        print(f"Capacidad: {self.capacidad} m3")
        print(f"Carga vertical: {self.carga_normal()/1000:.2f} kN")

        H1, M1 = self.reacciones()  # Fuerza horizontal y momento flector en la base
        print(f"Fuerza horizontal: {H1/1000:.2f} kN")
        print(f"Flector en la base: {M1/1000:.2f} kN")