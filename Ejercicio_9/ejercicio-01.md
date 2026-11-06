# Ejercicio 1 — Encadenamiento en la biblioteca

## Contexto

El proyecto de referencia implementa inferencia con **cláusulas definidas**
(Russell y Norvig, *AIMA*, cap. 9): encadenamiento hacia adelante
(*forward chaining*) y hacia atrás (*backward chaining*). La base de
conocimiento se escribe en YAML. Una variable empieza con minúscula (`x`);
una constante, con mayúscula (`Ana`, `Hoy`).

Antes de programar, recorre el proyecto. El ejemplo de la clase es
`kb/cats.yaml` (`Mortal(Tom)?`) y el segundo es el de *West is a criminal*
(`kb/west.yaml`):

`/Users/victoruccetina/Documents/code/inteligencia-artificial/Razonamiento lógico/project`

Ese proyecto **ilustra el algoritmo**. La base que vas a resolver es otra:
la de la biblioteca, descrita abajo. No entregues `cats.yaml` ni `west.yaml`
como solución.

## Objetivo

Implementar encadenamiento hacia adelante y hacia atrás sobre cláusulas
definidas, y usarlos para decidir quién puede entrar de noche a la
biblioteca. Hacia adelante debe derivar **todas** las consecuencias, no
detenerse al probar la consulta. Hacia atrás debe probar solo la consulta
y no derivar átomos que no necesita.

## La base de conocimiento

Hechos:

- `Estudiante(Ana)`
- `Estudiante(Luis)`
- `Profesor(Marta)`
- `TieneCredencial(Ana)`
- `TieneCredencial(Marta)`
- `HorarioNocturno(Hoy)`

Reglas, en este orden:

| Id | Si | Entonces |
|---|---|---|
| `R_miembro_est` | `Estudiante(x)` y `TieneCredencial(x)` | `Miembro(x)` |
| `R_miembro_prof` | `Profesor(x)` | `Miembro(x)` |
| `R_acceso` | `Miembro(x)` y `HorarioNocturno(Hoy)` | `AccesoNoche(x)` |
| `R_beca` | `Estudiante(x)` y `TieneCredencial(x)` | `Becario(x)` |

`R_beca` no hace falta para decidir el acceso. Está para que se vea la
diferencia entre los dos algoritmos.

En YAML, las tres primeras letras de cada constante van en mayúscula y las
variables en minúscula, igual que en el proyecto. Un átomo con coma va
entre comillas si tu lector de YAML partiera la línea; en esta base ningún
átomo lleva coma.

## Qué debe hacer tu programa

1. **Cargar** hechos, reglas y una consulta. El formato puede ser el YAML
   del proyecto u otro equivalente, siempre que respete el orden de las
   reglas y de los hechos.
2. **Encadenamiento hacia adelante**, al estilo de `logic/forward.py`:
   - En cada ronda se recorren las reglas en el orden de la tabla, contra
     los hechos conocidos **al empezar la ronda**.
   - Si una regla tiene varias premisas, se unifican en ese orden, probando
     los hechos en el orden en que están.
   - Un átomo nuevo no se usa como premisa hasta la ronda siguiente.
   - No se vuelve a añadir un átomo que ya está.
   - Se sigue hasta que una ronda no produzca nada nuevo (aunque la consulta
     ya se hubiera probado antes).
   - Al final, la consulta se unifica con los hechos. Si hay varias
     respuestas, cuenta la primera en el orden en que quedaron los hechos.
3. **Encadenamiento hacia atrás**, al estilo de `logic/backward.py`:
   - Se parte de la consulta.
   - Para cada meta se prueban primero los hechos y después las reglas, en
     el orden de la tabla.
   - La primera prueba que tiene éxito se acepta; no se buscan más.
   - Si una meta ya está en la pila de metas, se corta ese camino (evita
     un ciclo).
   - No se añaden hechos que la consulta no pida.

Consultas que debes correr con **ambos** algoritmos, sobre la base de
arriba, sin añadir hechos:

1. `AccesoNoche(Ana)`
2. `AccesoNoche(Luis)`
3. `AccesoNoche(Marta)`

## Pasos sugeridos

1. Lee el README del proyecto y corre el ejemplo de la clase:

```bash
cd "Razonamiento lógico/project"
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python 01_show_kb.py
python 02_forward_chaining.py
python 03_backward_chaining.py
python 04_compare.py
```

2. En `logic/forward.py` sigue `forward_chain`: una ronda aplica todas las
   reglas y solo entonces incorpora los átomos nuevos. En
   `logic/backward.py` sigue `bc_or` y `bc_and`: hechos primero, reglas
   después, y se regresa en cuanto hay una prueba.
3. Escribe la base de la biblioteca y las tres consultas.
4. Imprime, para cada consulta y cada algoritmo, si quedó **probada** y la
   traza (reglas disparadas, o metas y fallos).

## Criterios de aceptación

Hacia adelante, en las tres consultas, los átomos nuevos son exactamente
estos, en este orden:

1. `Miembro(Ana)`
2. `Miembro(Marta)`
3. `Becario(Ana)`
4. `AccesoNoche(Ana)`
5. `AccesoNoche(Marta)`

`AccesoNoche(Ana)` y `AccesoNoche(Marta)` quedan **probadas**.
`AccesoNoche(Luis)` **no**. Luis sigue siendo solo `Estudiante(Luis)`: no
hay `Miembro(Luis)`, ni `Becario(Luis)`, ni `AccesoNoche(Luis)`.

Hacia atrás:

- `AccesoNoche(Ana)` se prueba con `R_acceso` y `R_miembro_est`, apoyada en
  los hechos `Estudiante(Ana)`, `TieneCredencial(Ana)` y
  `HorarioNocturno(Hoy)`. La traza no menciona a Felix-equivalente: no
  aparecen Luis, Marta, `R_beca` ni `Becario`.
- `AccesoNoche(Marta)` intenta primero `R_miembro_est`, falla porque no
  existe `Estudiante(Marta)`, y entonces prueba `R_miembro_prof` con
  `Profesor(Marta)`.
- `AccesoNoche(Luis)` falla: `TieneCredencial(Luis)` no es un hecho y
  `Profesor(Luis)` tampoco.

La solución es código tuyo. `Razonamiento lógico/project` queda como
referencia.

## Entrega

1. El código del encadenamiento hacia adelante y hacia atrás, y el archivo
   de la base.
2. La traza de las tres consultas con cada algoritmo, y el sí o no de cada
   una.
3. Un reporte breve (media página) que responda:
   - ¿Por qué `Becario(Ana)` sale en el encadenamiento hacia adelante de
     `AccesoNoche(Ana)` y no en el de hacia atrás?
   - ¿Por qué hacia atrás prueba `R_miembro_est` al buscar `Miembro(Marta)`,
     si Marta es profesora?
   - Si se añade el hecho `TieneCredencial(Luis)` y se vuelve a preguntar
     `AccesoNoche(Luis)`, ¿qué átomos nuevos aparecen y la consulta queda
     probada? Compruébalo con tu programa y escribe el resultado.

## Pistas

- Hacia adelante es **dirigido por los datos**: dispara toda regla cuyas
  premisas ya son hechos. Hacia atrás es **dirigido por la meta**: solo
  abre reglas cuya cabeza unifica con la meta actual.
- `R_acceso` no puede dispararse en la primera ronda hacia adelante:
  `Miembro(Ana)` y `Miembro(Marta)` todavía no están en los hechos de esa
  ronda; se usan en la siguiente.
- En un empate de varias pruebas, gana la primera regla de la tabla. Por
  eso el camino de Marta pasa antes por la regla de estudiante y falla.
- El proyecto renombra las variables de cada uso de una regla (`x` pasa a
  ser `x_1`, `x_2`, …) para que dos disparos no compartan variable. Puedes
  hacer lo mismo. En el reporte basta la sustitución sobre las constantes
  (`x` queda en `Ana`, `Luis` o `Marta`), no el índice del renombrado.
