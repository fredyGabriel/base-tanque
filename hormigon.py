'''
Material Hormigón. Características y utilidades.

Autor: Fredy Gabriel Ramírez Villanueva
Fecha primera versión viable: 27 de marzo de 2024
Coronel Oviedo - Paraguay
'''

from dataclasses import dataclass


@dataclass
class Hormigon:
    '''Características del hormigón armado

    Las unidades deben ser coherentes.
    
    Atributos:
        peso_esp (float): peso específico = 25 kN/m3 por defecto.
        fck (float): Resistencia característica del hormigón
        gC (float): Coneficiente de minoración del hormigón

    '''
    peso_esp: float = 24000  # N/m3
    fck = 20e6  # Resistencia característica del hormigón
    gC = 1.5  # Coeficiente de minoración del hormigón

    @property
    def elasticidad(self):
        '''Módulo de elasticidad del hormigón'''
        return 1.2*22*(self.fck*1e-6/10/self.gC)**0.3 * 1e9