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
    axis_direction = Vec3(0, 0, 0)
    axis_direction[i] = 1

    # Создание грани и вращение её в нужном направлении
    face = Entity(parent=combine_group, model='plane', origin_y=-.5, texture='white_cube', color=cube_colors[i * 2])
    face.look_at(axis_direction, 'up')

    # Создание отраженной грани и вращение её в противоположном направлении
    flipped_face = Entity(parent=combine_group, model='plane', origin_y=-.5, texture='white_cube',
                          color=cube_colors[(i * 2) + 1])
    flipped_face.look_at(-axis_direction, 'up')

# Комбинирование граней в группе
combine_group.combine()

# Создание массива кубов, размещенных в 3D-пространстве
cubes = []
for x in range(3):
    for y in range(3):
        for z in range(3):
            cube = Entity(model=copy(combine_group.model), position=Vec3(x, y, z) - (Vec3(3, 3, 3) / 3),
                          texture='white_cube')
            cubes.append(cube)

# Создание вспомогательного объекта для вращения граней
rotation_helper = Entity()

# Создание невидимого коллайдера-куба для обработки ввода
rotation_collider = Entity(model='cube', scale=3, collider='box', visible=False)


# Вращение грани куба в зависимости от направления
def rotate_face(normal, direction=1, speed=1):
    if normal == Vec3(1, 0, 0):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.x > 0]
        rotation_helper.animate('rotation_x', 90 * direction, duration=.15 * speed, curve=curve.linear,
                                interrupt='finish')
    elif normal == Vec3(-1, 0, 0):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.x < 0]
        rotation_helper.animate('rotation_x', -90 * direction, duration=.15 * speed, curve=curve.linear,
                                interrupt='finish')

    elif normal == Vec3(0, 1, 0):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.y > 0]
        rotation_helper.animate('rotation_y', 90 * direction, duration=.15 * speed, curve=curve.linear,
                                interrupt='finish')
    elif normal == Vec3(0, -1, 0):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.y < 0]
        rotation_helper.animate('rotation_y', -90 * direction, duration=.15 * speed, curve=curve.linear,
                                interrupt='finish')

    elif normal == Vec3(0, 0, 1):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.z > 0]
        rotation_helper.animate('rotation_z', -90 * direction, duration=.15 * speed, curve=curve.linear,
                                interrupt='finish')
    elif normal == Vec3(0, 0, -1):
        [setattr(cube, 'world_parent', rotation_helper) for cube in cubes if cube.z < 0]
        rotation_helper.animate('rotation_z', 90 * direction, duration=.15 * speed, curve=curve.linear,
                                interrupt='finish')

    invoke(reset_rotation_helper, delay=.2 * speed)

    if speed:
        rotation_collider.ignore_input = True

        @after(.25 * speed)
        def _():
            rotation_collider.ignore_input = False
            check_for_win()


# Режим (0 - авторежим, 1 - режим сборки)
mode = 0


# Переключение между режимами
def toggle_mode():
    global mode
    if mode == 0:
        mode = 1
        reset_button.enabled = True
        randomize_button.enabled = True
        rotation_collider.ignore_input = False
        win_text_entity.text = ''
        toggle_mode_button.text = 'Режим сборки'
        toggle_mode_button.color = color.red
        solve_button.enabled = False
    else:
        mode = 0
        reset_button.enabled = False
        randomize_button.enabled = False
        rotation_collider.ignore_input = True
        toggle_mode_button.text = 'Авторежим'
        toggle_mode_button.color = color.green
        solve_button.enabled = True


# Обработка ввода с помощью мыши для вращения граней
def collider_input(key):
    if mouse.hovered_entity == rotation_collider and mode == 1:
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
    if {cube.world_rotation for cube in cubes} == {Vec3(0, 0, 0)}:
        win_text_entity.text = 'РЕШЕНО!'
        win_text_entity.appear()
    else:
        win_text_entity.text = ''


# Функция для случайного перемешивания куба
def randomize():
    faces = (Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1), Vec3(-1, 0, 0), Vec3(0, -1, 0), Vec3(0, 0, -1))
    for _ in range(42):
        rotate_face(random.choice(faces), random.choice((-1, 1)), 0)


# Сброс вращения куба
def reset_cube():
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
