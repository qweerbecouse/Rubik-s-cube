from ursina import *

# Создание объекта приложения Ursina
app = Ursina()

# Создание списка цветов для граней куба
cube_colors = [
    color.red,
    color.orange,
    color.white,
    color.yellow,
    color.blue,
    color.green,
]

# Создание группы для комбинирования геометрических объектов
combine_group = Entity(enabled=False)

# Создание и добавление граней куба в группу
for i in range(3):
    # Создание вектора для текущей оси
    axis_direction = Vec3(0, 0, 0)
    axis_direction[i] = 1

    # Создание грани для текущей оси
    face = Entity(parent=combine_group, model='plane', origin_y=-.5, texture='white_cube', color=cube_colors[i * 2])
    # Поворот грани так, чтобы её нормаль указывала вдоль текущей оси, верхний край смотрит вверх
    face.look_at(axis_direction, 'up')

    # Создание отраженной грани для противоположного направления
    flipped_face = Entity(parent=combine_group, model='plane', origin_y=-.5, texture='white_cube',
                          color=cube_colors[(i * 2) + 1])
    # Поворот отраженной грани в противоположное направление
    flipped_face.look_at(-axis_direction, 'up')

# Объединение созданных граней в группу
combine_group.combine()


# Создание массива кубов, размещенных в 3D-пространстве
# Инициализация пустого списка для хранения кубов
cubes = []

# Вложенные циклы для создания кубов в трехмерной сетке
for x in range(3):
    for y in range(3):
        for z in range(3):
            # Создание куба с параметрами
            cube = Entity(
                model=copy(combine_group.model),  # Копирование модели из combine_group
                position=Vec3(x, y, z) - (Vec3(3, 3, 3) / 3),  # Позиция куба в трехмерной сетке
                texture='white_cube'  # Текстура куба
            )
            # Добавление созданного куба в список cubes
            cubes.append(cube)


# Создание вспомогательного объекта для вращения граней
rotation_helper = Entity()

# Создание невидимого коллайдера-куба для обработки ввода
rotation_collider = Entity(model='cube', scale=3, collider='box', visible=False)


# Вращение грани куба в зависимости от направления
def rotate_face(normal, direction=1, speed=1):
    # Проверка условий вращения в зависимости от переданной нормали (вектора)
    if normal == Vec3(1, 0, 0):
        # Для всех кубов с положительным x устанавливаем rotation_helper в качестве родителя
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.x > 0]
        # Анимация вращения вокруг оси X на 90 или -90 градусов в зависимости от направления
        rotation_helper.animate('rotation_x', 90 * direction, duration=.15 * speed, curve=curve.linear, interrupt='finish')
    elif normal == Vec3(-1, 0, 0):
        # Для всех кубов с отрицательным x устанавливаем rotation_helper в качестве родителя
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.x < 0]
        # Анимация вращения вокруг оси X на -90 или 90 градусов в зависимости от направления
        rotation_helper.animate('rotation_x', -90 * direction, duration=.15 * speed, curve=curve.linear, interrupt='finish')
    elif normal == Vec3(0, 1, 0):
        # Аналогичные шаги для оси Y
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.y > 0]
        rotation_helper.animate('rotation_y', 90 * direction, duration=.15 * speed, curve=curve.linear, interrupt='finish')
    elif normal == Vec3(0, -1, 0):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.y < 0]
        rotation_helper.animate('rotation_y', -90 * direction, duration=.15 * speed, curve=curve.linear, interrupt='finish')
    elif normal == Vec3(0, 0, 1):
        # Аналогичные шаги для оси Z
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.z > 0]
        rotation_helper.animate('rotation_z', -90 * direction, duration=.15 * speed, curve=curve.linear, interrupt='finish')
    elif normal == Vec3(0, 0, -1):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.z < 0]
        rotation_helper.animate('rotation_z', 90 * direction, duration=.15 * speed, curve=curve.linear, interrupt='finish')

    # Вызов функции сброса параметров вращения с небольшой задержкой
    invoke(reset_rotation_helper, delay=.2 * speed)

    # Если задана скорость, игнорируем пользовательский ввод на время анимации
    if speed:
        rotation_collider.ignore_input = True

        # После некоторой задержки восстанавливаем обработку пользовательского ввода
        @after(.25 * speed)
        def _():
            rotation_collider.ignore_input = False
            # Проверяем условия победы
            check_for_win()


# Инициализация переменной режима
mode = 0


# Функция переключения между режимами
def toggle_mode():
    global mode
    if mode == 0:
        # Переключение на режим сборки
        mode = 1
        reset_button.enabled = True
        randomize_button.enabled = True
        rotation_collider.ignore_input = False
        win_text_entity.text = ''
        toggle_mode_button.text = 'Режим сборки'
        toggle_mode_button.color = color.red
        solve_button.enabled = False
    else:
        # Переключение на авторежим
        mode = 0
        reset_button.enabled = False
        randomize_button.enabled = False
        rotation_collider.ignore_input = True
        toggle_mode_button.text = 'Авторежим'
        toggle_mode_button.color = color.green
        solve_button.enabled = True


# Обработчик ввода мыши для вращения граней
def collider_input(key):
    # Проверка, что указатель мыши находится над rotation_collider и активен режим сборки (mode == 1)
    if mouse.hovered_entity == rotation_collider and mode == 1:
        # В зависимости от кнопки мыши вызывается функция rotate_face с соответствующим направлением
        if key == 'left mouse down':
            rotate_face(mouse.normal, 1)
        elif key == 'right mouse down':
            rotate_face(mouse.normal, -1)


# Назначение функции `collider_input` как обработчика ввода для коллайдера
rotation_collider.input = collider_input


# Функция для сброса вращения вспомогательного объекта
def reset_rotation_helper():
    [setattr(cube, 'world_parent', scene) for cube in cubes]
    rotation_helper.rotation = (0, 0, 0)


# Создание текстовой сущности для отображения сообщения о завершении
win_text_entity = Text(y=.35, text='', color=color.green, origin=(0, 0), scale=3)


# Проверка на завершение сборки куба
def check_for_win():
    # Если все кубы имеют нулевое вращение, то куб собран
    if {cube.world_rotation for cube in cubes} == {Vec3(0, 0, 0)}:
        # Вывод сообщения о завершении
        win_text_entity.text = 'РЕШЕНО!'
        win_text_entity.appear()
    else:
        # Сброс сообщения
        win_text_entity.text = ''


# Функция для случайного перемешивания куба
def randomize():
    # Возможные направления вращения граней
    faces = (Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1), Vec3(-1, 0, 0), Vec3(0, -1, 0), Vec3(0, 0, -1))
    # Случайное вращение граней для перемешивания
    for _ in range(42):
        rotate_face(random.choice(faces), random.choice((-1, 1)), 0)


# Сброс вращения куба
def reset_cube():
    # Установка нулевого вращения для каждого куба
    for cube in cubes:
        cube.rotation = (0, 0, 0)


# Обработка клавиши Escape для выхода из приложения
def input(key):
    if key == 'escape':
        application.quit()


# Создание кнопок для управления режимами и операциями
toggle_mode_button = Button(text='Выбрать режим', color=color.green, position=(-.7, -.4), on_click=toggle_mode)
toggle_mode_button.fit_to_text()

solve_button = Button(text='Собрать', color=color.green, position=(0, -.4), enabled=False)
solve_button.fit_to_text()

randomize_button = Button(text='Перемешать', color=color.azure, position=(.7, -.4), on_click=randomize)
randomize_button.fit_to_text()

reset_button = Button(text='В начало', color=color.red, position=(.7, .4), on_click=reset_cube)
reset_button.fit_to_text()

# Настройка окна приложения
window.fullscreen = True
EditorCamera()

# Запуск приложения Ursina
app.run()
