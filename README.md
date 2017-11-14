# Audio to Graphic

El proposito de este proyecto es visualizar el input del microfono como formas que recorren un camino predeterminado en pantalla.


## Instalar

Todos los requerimientos se encuentran en el archivo `requirements.txt`. Simplemente correr

```
pip install -r requirements.txt
```

## Ejecutar

Ejecutar usando:

```
python path_drawing.py
```

## Modificar sensibilidad

Si las formas geometricas no son muy grandes, aumentar el valor de `MAX_MIC_READING_MODIFIER` en el archivo `path_drawing.py`. Se recomienda primero asegurarse de que el volumen del microfono no este bajo.

Si las formas geometricas tienen colores muy apagados, aumentar el valor de `MAX_FFT_READING_MODIFIER` en el archivo `path_drawing.py`. Esto hara que las formas geometricas tomen colores mas vivos con menor volumen.
