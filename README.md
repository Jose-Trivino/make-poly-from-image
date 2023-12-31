# Make .poly from images

Este repositorio contiene el proyecto para el trabajo de título "Representación de imágenes mediante grafos planares". Esta herramienta permite la generación de archivos .poly a partir de imágenes .png, tomando como requisito que estas posean un fondo blanco que permita distinguir el fondo de la imagen de la figura a detectar.

## Tabla de contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
  - [Parámetros a recibir](#parámetros-a-recibir)
    - [Parámetros universales](#parámetros-a-recibir)
    - [Parámetros para método de Canny](#parámetros-para-método-de-canny)
    - [Parámetros para método de triangulación](#parámetros-para-método-de-triangulación)
- [Herramientas extra](#herramientas-extra)

## Requisitos

- Python (Versión 3.11.2 o posteriores)

## Instalación

Para instalar las dependencias necesarias, es posible utilizar el siguiente comando:

`pip install -r requirements.txt`

## Uso

El programa se ejecuta mediante línea de comandos, siendo el único parámetro obligatorio una imagen de entrada:

`python make_poly.py <input_image_path>`

Esto dará inicio al proceso de detección de bordes y generación de un archivo .poly utilizando los parámetros por defecto, entregando como resultado el archivo .poly generado a partir de la imagen ingresada

### Parámetros a recibir

El programa posee una gran cantidad de parámetros opcionales, los cuales serán detallados a continuación:

#### Parámetros universales

- `--method`
  - **Tipo**: string
  - **Valores posibles**: 'canny', 'triangle', 'c', 't'
  - **Valor por defecto**: 'canny'
  - **Descripción**: Representa el método a utilizar para la obtención de los bordes.

- `--show`
  - **Tipo**: boolean (flag)
  - **Descripción**: Permite mostrar el resultado final del procesamiento, ya sea los bordes detectados para canny o los bordes y la malla generada para el método de triangulaciones.

- `--thresh`
  - **Tipo**: int
  - **Rango**: [0, 255]
  - **Valor por defecto**: 254
  - **Descripción**: Valor umbral para función de thresholding. Todo pixel cuyo valor en escala de grises supere el valor definido será transformado a blanco, y en caso contrario será transformado a negro.

#### Parámetros para método de Canny

- `--reduction`
  - **Tipo**: string
  - **Valores posibles**: 'fixed', 'variable', 'hybrid', 'f', 'v', 'h'
  - **Valor por defecto**: 'hybrid'
  - **Descripción**: Representa el algoritmo a utilizar para la eliminación de vértices y aristas.

- `--len`
  - **Tipo**: int
  - **Valor mínimo**: 1
  - **Valor por defecto**: 20
  - **Descripción**: Representa la longitud máxima en pixeles de las aristas a generar (aplica solamente para métodos de reducción híbrido y fijo).

- `--maxdist`
  - **Tipo**: int
  - **Valor mínimo**: 1
  - **Valor por defecto**: 1
  - **Descripción**: Representa la distancia máxima en pixeles entre las aristas generadas y los bordes detectados en la imagen (aplica solamente para métodos de reducción híbrido y variable).

- `--fusedist`
  - **Tipo**: int
  - **Valor mínimo**: 0
  - **Valor por defecto**: 5
  - **Descripción**: Representa el largo mínimo de arista a generar en pixeles. Vértices a una distancia menor a este valor serán fusionados.

- `--pathdist`
  - **Tipo**: int
  - **Valor mínimo**: 0
  - **Valor por defecto**: 15
  - **Descripción**: Representa la distancia en pixeles a partir de la cual se llevará a cabo la fusión de caminos disjuntos y la generación de caminos cerrados.

#### Parámetros para método de triangulación

- `--x`
  - **Tipo**: int
  - **Valor mínimo**: 1
  - **Valor por defecto**: 20
  - **Descripción**: Representa la cantidad de celdas a generar para la malla inicial en el eje x.

- `--y`
  - **Tipo**: int
  - **Valor mínimo**: 1
  - **Valor por defecto**: 20
  - **Descripción**: Representa la cantidad de celdas a generar para la malla inicial en el eje y.

- `--xy`
  - **Tipo**: int or tuple
  - **Valor por defecto**: (20,20)
  - **Descripción**: Representa la cantidad de celdas a generar para ambos ejes. Toma prioridad por sobre los parámetros --x e --y. Puede recibir un entero (en caso de que ambas dimensiones posean el mismo valor) o una tupla. NOTA: Considerar que todas las imágenes son superpuestas en un lienzo cuadrado para el procesamiento. Por lo tanto, la única forma de generar celdas rectangulares es definir x e y con valores distintos.

- `--it`
  - **Tipo**: int
  - **Valor mínimo**: 0
  - **Valor por defecto**: 40
  - **Descripción**: Representa el número de iteraciones para el desplazamiento de vértices.

- `--minlen`
  - **Tipo**: int
  - **Valor mínimo**: 1
  - **Valor por defecto**: 3
  - **Descripción**: Representa la longitud mínima en pixeles de las aristas a generar. Si la longitud de una arista no supera este valor, se elimina de la malla.

- `--verbose`
  - **Tipo**: boolean (flag)
  - **Descripción**: Flag para mostrar detalles de cada iteración del proceso en consola.

- `--timelapse`
  - **Tipo**: boolean (flag)
  - **Descripción**: Flag para la generación de un .gif ilustrando la evolución de la malla.

## Herramientas extra

El repositorio también incluye el archivo `view_poly.py`, el cual permite la visualización de archivos .poly a través de la generación de una imagen en formato .png. Es posible ejecutar este programa mediante el siguiente comando:

`python view_poly.py <poly_file_path>`

De esta forma, es posible visualizar el archivo .poly inmediatamente después de su generación.

Junto con eso, en la carpeta extra_tools se incluyen dos herramientas que permiten obtener información tanto acerca de la imagen como de los archivos generados. El primero es el archivo `poly_metrics.py`, el cual permite generar un gráfico con las métricas de un archivo .poly. Este se ejecuta mediante el siguiente comando:

`python poly_metrics.py <poly_file_path>`

De esta forma, es posible determinar la cantidad de elementos generados, así como medidas de tendencia central para las longitudes de las aristas generadas.

El segundo archivo presente en la carpeta extra_tools corresponde a `view_thresh.py`, a través del cual es posible visualizar el resultado de aplicar la función de thresholding a una imagen. Este se ejecuta mediante el siguiente comando:

`python thresholding.py <input_image_path> <threshold_value>`

Esto mostrará la imagen tras aplicar la función de thresholding, siendo los valores posibles para el threshold enteros entre 0 y 255.