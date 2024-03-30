'''
Parámetros y cálculos en suelos

Autor: Fredy Gabriel Ramírez Villanueva
Fecha primera versión viable: 28 de marzo de 2024
Coronel Oviedo - Paraguay
'''

import numpy as np
import pandas as pd


class Suelo:
    '''Características del suelo.
    
    Las unidades deben ser coherentes.

    tipo_ref (str): tipo de suelo para referencia.
        Según la siguiente clasificación:
        ("Grava", "Arena densa", "Arena semidensa", "Arena suelta", "Limo",
        "Arcilla densa", "Arcilla semidensa", "Arcilla blanda")
    '''

    def __init__(self, tipo_ref="Arcilla blanda", spt=np.ones(15)*5) -> None:
        self.tipo_ref = tipo_ref
        self.spt = spt
    
    def tipos_referencia(self) -> pd.DataFrame:
        '''Tipos de suelo para referencia.
        
        Según se propone en cype.'''
        return pd.read_csv('parametros/tipo_main.csv', index_col=0, sep=";")

    def spt_ajustado(self) -> np.ndarray:
        '''Ajuste de valores SPT.
        
        Los valores SPT menores a 3, deben ser considerados iguales a 3, 
        los mayores a 50 deben ser considerados 50. Práctica común en Brasil.
        '''
        nuevo_spt = np.where(self.spt < 3, 3, self.spt)
        nuevo_spt = np.where(nuevo_spt > 50, 50, nuevo_spt)
        
        return nuevo_spt
    
    def profundidad_sondeada(self) -> float:
        '''Profundidad sondeada con el ensayo SPT'''
        return len(self.spt)
    
    def Np(self, longitud_pilote=10) -> float:
        '''Promedio de valores SPT alrededor de la punta de un pilote'''
        S = self.spt_ajustado()
        ps = self.profundidad_sondeada()
        L = int(longitud_pilote)
        if ps == L:
            return (S[-3] + S[-2] + S[-1])/3
        elif ps > L:
            return (S[L-2] + S[L-1] + S[L])/3
        else:
            raise IndexError(f"La longitud dada {longitud_pilote} m debe ser \
                             menor a la profundidad sondeada {ps} m")
        
    def NL(self, longitud_pilote=10) -> float:
        '''Promedio SPT a lo largo del fuste'''
        
        # Todos los valores SPT ajustados menos los 3 que rodean la punta
        L = int(longitud_pilote)
        spt_L = self.spt_ajustado()[:(L - 2)]
        return np.mean(spt_L)

if __name__ == '__main__':
    suelo = Suelo()

    # Acceder a los atributos
    print(suelo.tipo_ref)

    # Modificar el valor de un atributo
    suelo.tipo_ref = "Arena densa"

    # Usar los métodos
    spt_ajustado = suelo.spt_ajustado()
    Np = suelo.Np(longitud_pilote=10)
    NL = suelo.NL(longitud_pilote=10)

    print(spt_ajustado)
