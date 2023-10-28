# make-poly-from-image
Trabajo de título: Representación de imágenes mediante grafos planares

python 3.11.2

pip install -r requirements.txt

python make_poly.py filename.png

optional arguments:

--method

Representa el método a utilizar para la obtención de los bordes
Valor por defecto: "canny"
Valores posibles: "triangle" | "canny" | "t" | "c"

--show

Flag que muestra el resultado final del procesamiento, ya sea los bordes detectados para canny o los bordes y la malla generada para el método de triangulaciones.

Para canny:

--reduction

Representa el algoritmo a utilizar para la eliminación de vértices y aristas
Valor por defecto: "hybrid"
Valores posibles: "fixed" | "variable" | "hybrid" | "f" | "v" | "h"

--len

Representa la longitud máxima en pixeles de las aristas a generar (aplica sólo para método de reducción híbrido y fijo)

Valor por defecto: 20
Valores posibles: >0

--maxdist

Representa la distancia máxima en pixeles de las aristas generadas a los bordes detectados en la imagen (aplica solo para método de reducción híbrido y variable)

Valor por defecto: 1
Valores posibles: >0

--fusedist

Representa el largo mínimo de arista a generar en pixeles. Vértices a una distancia menor a este valor serán fusionados.

Valor por defecto: 5
Valores posibles: >0

Para triangulación:

--x

Representa la cantidad de celdas a generar para la malla inicial en el eje x

Valor por defecto: 20
Valores posibles: >0

--y

Representa la cantidad de celdas a generar para la malla inicial en el eje y

Valor por defecto: 20
Valores posibles: >0

--xy

Representa la cantidad de celdas a generar para ambos ejes. Toma prioridad por sobre los parámetros --x e --y.
Puede recibir un entero (en caso de que ambas dimensiones posean el mismo valor) o una tupla. NOTA: Considerar que todas las imágenes son superpuestas en un lienzo cuadrado para el procesamiento. Por lo tanto, la única forma de generar celdas rectangulares es definir x e y con valores distintos.

Valor por defecto: 20
Valores posibles: >0 | (>0,>0)

--it

Representa el número de iteraciones para el desplazamiento de vértices

Valor por defecto: 40
Valores posibles: >=0

--minlen

Representa la longitud mínima en pixeles de las aristas a generar. Si la longitud de una arista no supera este valor, se elimina de la malla.

Valor por defecto: 3
Valores posibles: >0

--verbose

Flag para mostrar logs en iteraciones de triángulos

--timelapse

Flag para la generación de un gif ilustrando la evolución de la malla


