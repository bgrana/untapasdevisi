# Estandar de codificación




## Estructura del proyecto

| Carpeta                  | Uso                                |
|--------------------------+------------------------------------|
|/doc                      | Documentación                      |
|/test                     | Tests                              |
|/untapasdevisi/static     | Ficheros estáticos (html/css/js)   |
|/untapasdevisi/templates  | Templates de jinja2                |
|/untapasdevisi/core.py    | Inicialización y rutas             |
|/untapasdevisi/models.py  | Modelos de la BD                   |
|/untapasdevisi/utils.py   | Metodos de ayuda                   |




## Estilo general

### Tamaño de linea
Mantener las lineas por debajo de 80 caracteres.

### Lenguaje
Usar inglés para código y comentarios.




## Estilo para Python

### Identación
Usar cuatro espacios en blanco.

### Espacios en blanco
Usar espacios en blanco entre operadores y operandos.

### Parentesis
Solo cuando sean necesarios.

### Saltos de linea
Usar un dos saltos de linea entre declaracioes en un modulo y un salto de linea entre declaraciones en una clase.

### Nombres

```python
CONSTANT_NAME = 33

def function_name(argument_name):
  variable_name = 1

class ClassName():
  def __init__(self, argument_name):
    # ...
  def method_name():
    # ...
```

### Strings
Usar comillas simples para simbolos y comillas dobles para textos.

```python
msg = "this is a long-ish message"
state = 'finished'
```

## Estilo para JavaScript

### Identación
Usar dos espacios por nivel de identación.

### Var
Usar siempre var al declarar una variable

### Punto y coma
Usar siempre punto y coma en los statements;

### Nombres

```javascript
var CONSTANT_NAME = 33;
var variableName = true;
var namespaceName = {};

function functionName() {
  // ...
}

function ConstructorName(argumentName) {
  this.attributeName = argumentName;
}

ConstructorName.prototype.methodName() {
  // ...
}
```

### Llaves
Abrir llaves en la misma linea.

```javascript
if (something) {
  // ...
} else {
  // ...
}
```

### Parentesis
Solo cuando sean requeridos

### Strings
Usar comillas simples.

```javascript
var msg = 'Hello, word!';
```

### Strings multilinea
Concatenar strings sumandolos

```javascript
var myString = 'A rather long string of English text, an error message ' +
  'actually that just keeps going and going -- an error ' +
  'message to make the Energizer bunny blush (right through ' +
  'those Schwarzenegger shades)!;
```

### Expressiones de igualdad
Usar tiple igual.

```javascript
ìf (a === b && c !== d) {
  // ...
}
```



## Estilo para HTML

### Identación
Usar dos espacios por nivel de identación.

```html
<ul>
  <li>Fantastic
  <li>Great
</ul>
```

### Nombres
Usar solo minisculas, separando las palabras con guiones.

### Document Type
Usar la sintaxis de html5

```html
<!DOCTYPE html>
```

### Protocolo
Omitir el protocolo en los recursos

```html
<script src="//www.google.com/js/gweb/analytics/autotrack.js"></script>
```

### Semantica
Usar los tags semánticamente.




## Estilo para CSS

### Identación
Usar dos espacios por nivel de identación.

```css
.example {
  color: blue;
}
```

### Nombres
Usar solo minisculas, separando las palabras con guiones.

### Separación entre reglas
Usar siempre un salto de linea entre reglas

```css
html {
  background: #fff;
}

body {
  margin: auto;
  width: 50%;
}
```


## Referencias

1. [PEP 8: Style Guide for Python Code](http://legacy.python.org/dev/peps/pep-0008/)
2. [Google JavaScript Style Guide](http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml)
3. [Google HTML/CSS Style Guide](http://google-styleguide.googlecode.com/svn/trunk/htmlcssguide.xml)