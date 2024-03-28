# Estabilidad de cabezal de pilotes como base para tanques tipo copa.

El programa ayuda a calcular la estabilidad de la fundación, de pilotes con cabezales, para tanques tipo copa.

## Realiza lo siguiente:
1. Calcula las cargas de viento;
2. Calcula las reacciones en la base del tanque tipo copa;
3. Calcula la capacidad de los pilotes por el método Decourt-Quaresma;
4. Verifica el cabezal al vuelco;
5. Verifica la capacidad del pilote.

## No realiza (falta agregar)
1. Verificación al deslizamiento del cabezal;
2. Resistencia de los pilotes al empuje lateral;
3. Cálculos con otros tipos de fundaciones (zapatas y tubulones)

## Cómo funciona?
1. Importar la librería numpy;
2. Importar las librerías tanque y zpilot;
3. Agregar un numpy array con los valores SPT del estudio geotécnico;
4. Crear el viento a partir de su velocidad básica (opcional otros parámetros);
5. Crear un tanque con el viento anterior y su capacidad de almacenamiento de agua;
6. Obetener las cargas del tanque y aplicar coeficientes de seguridad según su norma de uso;
7. Crear un pilote a partir de su longitud, diámetro y ensayo SPT (opcional otros parámetros);
8. Obtener la capacidad portante del pilote;
9. Crear un cabezal a partir del pilote anterior, tipología, dimensiones y cargas;
10. Para ver los resultados se recomienda imprimir las informaciones según se muestra en el archivo ejemplo.py

## Notas adicionales:
1. Se recomienda usar el archivo ejemplo.py como guía de trabajo;
1. Todas las unidades de medida debe ser coherentes;
2. Se recomienda utilizar el Sistema Internacional sin múltiplos ni submúltiplos.

# Ejemplo de salida
Según ejemplo.py

  - VIENTO
  
    - Velocidad básica: 50 m/s
    
    - Presión a 10m de altura: 1.61 kN/m2
    
  - TANQUE
    
    - Capacidad: 30 m3
    
    - Carga vertical: 339.20 kN
    
    - Fuerza horizontal: 29.04 kN
    
    - Flector en la base: 363.05 kN
    
  - PILOTE:
    
    - Longitud del pilote: 15 m
    
    - Diámetro: 40 cm
  
    - Tipo de perforación: Excavada general (tipo Strauss)

    - Capacidad: 242.00 kN
  
  - CABEZAL CUADRADO
  
    - Cabezal con: 5 pilotes
    
    - Ancho mínimo del cabezal: 3.43 m
    
    - Ancho adoptado: 3.50 m
    
    - Altura del cabezal: 1.00 m
    
    - Acción máxima sobre pilotes: 211.09 kN
  
  - VERIFICACIÓN

    - Verificación de capacidad de pilote : Cumple
    
    - Debe verificar además: punzonamiento y flexión en el cabezal.
