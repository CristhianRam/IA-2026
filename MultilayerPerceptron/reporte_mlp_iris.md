### ¿Bajar más el error al añadir dos capas, o se estancó / empeoró? ¿Igual en NumPy y en Keras?

El error no disminuyó, sino que se estancó y empeoró el aprendizaje. Al pasar de 2 a 4 capas con activación sigmoide, la velocidad de convergencia cayó drásticamente y el modelo quedó con un error residual mayor en las mismas épocas. Este comportamiento ocurrió igual en NumPy y en Keras, demostrando que añadir profundidad con sigmoides dificulta la optimización en ambas implementaciones.

---

### ¿Las curvas de la notebook 01 y de Keras se parecen con la misma topología? Si no, ¿qué diferencias de implementación podrían explicarlo (orden de los datos, inicialización, vectorización, etc.)?

Muestran una tendencia similar, pero no son idénticas debido a diferencias clave de implementación:
1. **Modo de optimización:** NumPy usa SGD *online* muestra por muestra (`batch_size=1`), mientras que Keras usa *mini-batch* (`batch_size=32` por defecto), generando curvas más suaves.
2. **Barajado de datos (*Shuffle*):** NumPy procesa el dataset en orden fijo por clases (sesgando el aprendizaje por bloques), mientras que Keras baraja los datos aleatoriamente en cada época.
3. **Inicialización:** NumPy utiliza una distribución uniforme en `[-0.5, 0.5]` con sesgo aleatorio, mientras que Keras emplea *Glorot Uniform* (Xavier) con sesgos en cero.
4. **Escala de pérdida:** Keras divide el MSE entre el número de clases de salida (3), cambiando la escala numérica del eje Y frente a NumPy.

---

### Con sigmoides apiladas y MSE, ¿tiene sentido que una red más profunda no aprenda mejor en Iris? Relaciónalo con lo que viste en las gráficas.

Sí, tiene total sentido por las siguientes razones:
- **Desvanecimiento del gradiente:** La derivada máxima de la sigmoide es $0.25$. Al encadenar 4 capas, la regla de la cadena reduce los gradientes a valores cercanos a cero ($\le 0.25^4$), impidiendo que las capas iniciales actualicen sus pesos.
- **Saturación con MSE:** Si las salidas caen en los extremos planos de la sigmoide, las derivadas se anulan y el gradiente no corrige el error.
- **Simplicidad de Iris:** Es un problema de baja dimensionalidad (4 entradas, 3 clases casi lineales) que no requiere profundidad; las capas extra solo añaden fricción numérica.
- **Reflejo en las gráficas:** En la red de 2 capas el error desciende rápidamente, mientras que en la de 4 capas la curva se aplana en una meseta horizontal casi sin aprendizaje.
