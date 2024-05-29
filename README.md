## Отчет

### Шапка

```python
ФИО: Хабнер Георгий Евгеньевич
Группа: P3231
Вариант: asm | risc | harv | hw | instr | binary -> struct | trap -> stream | port | cstr | prob1 | cache
Усложнение: без усложнения
```

---

### Язык программирования

#### Описание синтаксиса

Используется ассемблер для RISC процессора с поддержкой меток. Ниже представлена грамматика в форме Бэкуса-Наура:

```bnf
program ::= { line }

line ::= label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"
    
label ::= label_name ":"

instr ::= op0
        | op1 reg, reg
        | op1 reg, literal
        | op2 address
        | op2 reg, address
        | op3 reg
        | op4 reg, address
        | op5 address


op0 ::= "HLT"
      | "RST"

op1 ::= "ADD"
      | "SUB"
      | "MUL"
      | "DIV"

op2 ::= "LD"
      | "ST"

op3 ::= "OUT"

op4 ::= "JE"

op5 ::= "JMP"

literal ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

address ::= <any of *> { <any of "0-9"> }

reg ::= "R" { <any of "0-1"> }

comment ::= ";" <any symbols except "\n">
```
Поддерживаются однострочные комментарии, начинающиеся с ;.

#### Описание семантики

- **Стратегия вычислений**: Последовательное выполнение инструкций с возможностью переходов.
- **Области видимости**: Глобальная память данных, доступная всем инструкциям.
- **Типизация**: Неявная типизация, все операции производятся над 32-битными словами.
- **Виды литералов**: Целые числа, (возможно будет поддержка символов, которые будут преобразованы в ASCII).

### Организация памяти

#### Модель памяти процессора

- **Размеры машинного слова**: 32 бита.
- **Варианты адресации**: Прямая 

#### Механика отображения программы и данных на процессор

- **Доступные виды памяти и регистров**: Раздельные память инструкций и память данных.
- **Хранение инструкций**: В памяти инструкций.
- **Хранение статических и динамических данных**: статические данные не поддерживаются, динамические данные хранятся в памяти данных.

##### Registers
```
+------------------------------+
| R0 | R1                      |
+------------------------------+
```

##### Instruction memory
```
+------------------------------+
| 00  : Handler                |
| 01  : Instruction 1          |
| 02  : Instruction 2          |
|    ...                       |
| 20  : Instruction n          |
|    ...                       |
+------------------------------+
```

##### Data memory
```
+------------------------------+
| 00  : Saved R0               |
| 01  : Saved R1               |
| 02  : Saved PC               |
| 03  : Input Value            |
| 04  : variable 2             |
|    ...                       |
| 20  : variable 1             |
|    ...                       |
+------------------------------+
```

#### Работа с различными типами данных

1. **Литералы**:
    - Поддерживаются целые числа и символы, которые будут преобразованы в ASCII.
    - Могут быть использованы в качестве операндов инструкций.

2. **Константы**:
    - Не поддерживаются.

3. **Переменные**:
    - Могут быть отображены на регистры или в память данных.

4. **Инструкции**:
    - Хранятся в памяти инструкций.
  
5. **Процедуры**:
    - Не поддерживаются.

6. **Прерывания**:
    - Вызываются посредством запроса на прерывание и далее обработчик прерывания выполняет необходимые действия, во время которых запрещены другие прерывания.

### Система команд

#### Особенности процессора

- **Типы данных**: 32-битные слова.
- **Машинные слова**: 32 бита.
- **Устройство памяти**: Гарвардская архитектура с раздельными памятью инструкций и данных.
- **Адресация**: Прямая.
- **Устройство ввода-вывода**: Использует порт-мэппинг с адресацией портов.
- **Поток управления**: Линейный с возможностью переходов и прерываний.
- **Система прерываний**: Поддержка прерываний со специальным регистром для разрешения прерываний (IE).

#### Набор инструкций

| Код операции | Количество тактов | Описание                      |
|--------------|---------------|-------------------------------|
| `ADD`        | 1             | Сложение                      |
| `SUB`        | 1             | Вычитание                     |
| `MUL`        | 1             | Умножение                     |
| `DIV`        | 1             | Деление                       |
| `JMP`        | 1             | Безусловный переход           |
| `JE `        | 1             | Переход, если равно           |
| `LD`         | 1             | Загрузка данных из памяти     |
| `ST`         | 1             | Сохранение данных в память    |
| `OUT`        | 1             | Вывод данных в порт           |
| `RST`        | 3             | Восстановление регистров      |
| `HLT`        | 0             | Остановка процессора          |

#### Способ кодирования инструкций

Инструкции кодируются в бинарном виде.

<!-- ADD SUB MUL DIV 01XXADS/LIT A - выбор (r, r или r/lit) D - dest S - source LIT - literal -->

<!-- распиши красиво данные инструкции -->

| Код операции | Формат инструкции |
|--------------|-------------------|
| `ADD`        | `0100 A D S/LIT`     |
| `SUB`        | `0101 A D S/LIT`     |
| `MUL`        | `0110 A D S/LIT`     |
| `DIV`        | `0111 A D S/LIT`     |
| `JMP`        | `1000 0 ADDR`        |
| `JE `        | `1001 R ADDR`        |
| `LD`         | `1100 R ADDR`        |
| `ST`         | `1101 R ADDR`        |
| `OUT`        | `1110 R ---`         |
| `RST`        | `1111 ---`           |
| `HLT`        | `0000 ---`           |

A - выбор (r, r или r/lit) D - dest S - source LIT - literal
R - выбор регистра (0 или 1)
ADDR - адрес в памяти


### Транслятор

#### Консольное приложение

##### Входные данные:

- Имя файла с исходным кодом на ассемблере.
- Имя файла для сохранения машинного кода.

##### Выходные данные:

- Имя файла с машинным кодом.

#### Описание интерфейса командной строки

```bash
$ ./translator.py input.asm output.bin
```
