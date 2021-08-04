import time
import asyncio
import threading
import math
from adafruit_servokit import ServoKit

pca = ServoKit(channels=16)
pca.frequency = 50

# define 12 servos for 4 legs
# define servos ports
servo_pin = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]
# Размеры составных частей робота (в мм) ---------------------------------------------------------
length_a = 55  # femur (вторая деталь от корпуса) размер от центра до центра двух серв на одной плоскости
length_b = 80  # tiba (кисть) размер от центра оси сервы до кончика
length_c = 27.5  # coxa (первая деталь от корпуса двигающ.) размер от центра оси сервы базы до перпендикуляра оси
# второй сервы
length_side = 71  # длина базы, от оси одного серво до другой сбоку
z_absolute = -28  # Высота, когда кончики tiba ровно на уровне конца нижней части корпуса, не доходят до осей
# Constants for movement ----------------------------------------------------*/
z_default = -50  # Стандартная высота подъёма над землёй (чем меньше, тем выше над землёй)
# ( abs(z_default) - abs(z_absolute) = высота нижней части корпуса над землёй )
z_up = -30  # Высота подъёма ноги над землёй ( abs(z_up) - abs(z_absolute) = высота кончика tiba над
# землёй )
z_boot = z_absolute
x_default = 62
x_offset = 0
y_start = 0
y_step = 40
z_current = z_default  # Изменяемая высота подъёма над землёй
# y_default = x_default
# variables for movement ----------------------------------------------------
site_now = [[0, 0, 0], [0, 0, 0],
            [0, 0, 0], [0, 0, 0]]  # текущие координаты кончика каждой ноги
site_expect = [[0, 0, 0], [0, 0, 0],
               [0, 0, 0], [0, 0, 0]]  # ожидаемые координаты кончика каждой ноги
temp_speed = [[0, 0, 0], [0, 0, 0],
              [0, 0, 0], [0, 0, 0]]  # each axis' speed, needs to be recalculated before each movement
move_speed = 0  # скорость движения
speed_multiple = 7  # главная умножаемая скорость на основную
spot_turn_speed = 4
leg_move_speed = 8
body_move_speed = 3
stand_seat_speed = 1
# functions parameter
KEEP = 255
# define PI for calculation
pi = 3.1415926
# Constants for turn --------------------------------------------------------
# temp length
temp_a = math.sqrt(pow(2 * x_default + length_side, 2) + pow(y_step, 2))
temp_b = 2 * (y_start + y_step) + length_side
temp_c = math.sqrt(pow(2 * x_default + length_side, 2) + pow(2 * y_start + y_step + length_side, 2))
temp_alpha = math.acos((pow(temp_a, 2) + pow(temp_b, 2) - pow(temp_c, 2)) / 2 / temp_a / temp_b)
# site for turn
turn_x1 = (temp_a - length_side) / 2
turn_y1 = y_start + y_step / 2
turn_x0 = turn_x1 - temp_b * math.cos(temp_alpha)
turn_y0 = temp_b * math.sin(temp_alpha) - turn_y1 - length_side

servo_service_active = True


async def start():
    print("Start func")

    #for leg in range(4):
    #    for part in range(3):
    #        pca.servo[servo_pin[leg][part]].set_pulse_width_range(min_pulse=500, max_pulse=1800)

    set_site(0, x_default - x_offset, y_start + y_step, z_boot)
    set_site(1, x_default - x_offset, y_start + y_step, z_boot)
    set_site(2, x_default + x_offset, y_start, z_boot)
    set_site(3, x_default + x_offset, y_start, z_boot)

    for i in range(4):
        for j in range(3):
            site_now[i][j] = site_expect[i][j]

    #pack()
    stand()
    sit()
    # stand()
    # sit()
    # changeClearance(-20)
    # await asyncio.sleep(2)
    # changeClearance(-60)
    # changeClearance(-80)
    # changeClearance(-80)
    stand()
    step_forward(3)
    # turn_left(3)
    # turn_right(3)
    # step_back(3)
    # sit()


def update():
    print("Update func")


async def update_loop():
    await start()
    while True:
        await asyncio.sleep(1)
        update()


def servo_service_worker():
    global servo_service_active
    servo_service_active = True
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    new_loop.run_until_complete(servo_service())
    return


def setup():
    threading.Thread(target=servo_service_worker).start()

    loop = asyncio.get_event_loop()
    asyncio.ensure_future(update_loop())
    loop.run_forever()


# def servo_attach():
#    for i in range(4):
#        for j in range(3):
#            pca.servo[servo_pin[i][j]].set_pulse_width_range(500, 2500)
#            #move_servo(servo_pin[i][j], 90)


def pack():
    global servo_service_active
    servo_service_active = False

    pca.servo[servo_pin[0][1]].angle = 0
    pca.servo[servo_pin[2][1]].angle = 180
    pca.servo[servo_pin[1][1]].angle = 180
    pca.servo[servo_pin[3][1]].angle = 0

    pca.servo[servo_pin[0][0]].angle = 0
    pca.servo[servo_pin[2][0]].angle = 180
    pca.servo[servo_pin[1][0]].angle = 180
    pca.servo[servo_pin[3][0]].angle = 0

    pca.servo[servo_pin[0][2]].angle = 60
    pca.servo[servo_pin[2][2]].angle = 120
    pca.servo[servo_pin[1][2]].angle = 120
    pca.servo[servo_pin[3][2]].angle = 60

    # pca.servo[servo_pin[0][2]].angle = 180
    # pca.servo[servo_pin[2][2]].angle = 0
    # pca.servo[servo_pin[1][2]].angle = 0
    # pca.servo[servo_pin[3][2]].angle = 180

    for leg in range(4):
        for part in range(3):
            pca.servo[servo_pin[leg][part]].angle = None


# -20 / -80 (-120)
def changeClearance(z):
    global z_current, move_speed
    z_current = z
    move_speed = stand_seat_speed
    for leg in range(4):
        set_site(leg, KEEP, KEEP, z_current)
    wait_all_reach()


def stand():
    global move_speed
    move_speed = stand_seat_speed
    for leg in range(4):
        set_site(leg, KEEP, KEEP, z_current)
    wait_all_reach()


def sit():
    global move_speed
    move_speed = stand_seat_speed
    for leg in range(4):
        set_site(leg, KEEP, KEEP, z_boot)
    wait_all_reach()


def step_forward(step):
    global move_speed
    move_speed = leg_move_speed
    while step > 0:
        step -= 1
        if site_now[2][1] == y_start:
            # leg 2&1 move
            set_site(2, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(2, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(2, x_default + x_offset, y_start + 2 * y_step, z_current)
            wait_all_reach()

            move_speed = body_move_speed

            set_site(0, x_default + x_offset, y_start, z_current)
            set_site(1, x_default + x_offset, y_start + 2 * y_step, z_current)
            set_site(2, x_default - x_offset, y_start + y_step, z_current)
            set_site(3, x_default - x_offset, y_start + y_step, z_current)
            wait_all_reach()

            move_speed = leg_move_speed

            set_site(1, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(1, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(1, x_default + x_offset, y_start, z_current)
            wait_all_reach()
        else:
            # leg 0&3 move
            set_site(0, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(0, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(0, x_default + x_offset, y_start + 2 * y_step, z_current)
            wait_all_reach()

            move_speed = body_move_speed

            set_site(0, x_default - x_offset, y_start + y_step, z_current)
            set_site(1, x_default - x_offset, y_start + y_step, z_current)
            set_site(2, x_default + x_offset, y_start, z_current)
            set_site(3, x_default + x_offset, y_start + 2 * y_step, z_current)
            wait_all_reach()

            move_speed = leg_move_speed

            set_site(3, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(3, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(3, x_default + x_offset, y_start, z_current)
            wait_all_reach()


def step_back(step):
    global move_speed
    move_speed = leg_move_speed
    while step > 0:
        step -= 1
        if site_now[3][1] == y_start:
            # leg 3&0 move
            set_site(3, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(3, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(3, x_default + x_offset, y_start + 2 * y_step, z_current)
            wait_all_reach()

            move_speed = body_move_speed

            set_site(0, x_default + x_offset, y_start + 2 * y_step, z_current)
            set_site(1, x_default + x_offset, y_start, z_current)
            set_site(2, x_default - x_offset, y_start + y_step, z_current)
            set_site(3, x_default - x_offset, y_start + y_step, z_current)
            wait_all_reach()

            move_speed = leg_move_speed

            set_site(0, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(0, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(0, x_default + x_offset, y_start, z_current)
            wait_all_reach()
        else:
            # leg 1&2 move
            set_site(1, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(1, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(1, x_default + x_offset, y_start + 2 * y_step, z_current)
            wait_all_reach()

            move_speed = body_move_speed

            set_site(0, x_default - x_offset, y_start + y_step, z_current)
            set_site(1, x_default - x_offset, y_start + y_step, z_current)
            set_site(2, x_default + x_offset, y_start + 2 * y_step, z_current)
            set_site(3, x_default + x_offset, y_start, z_current)
            wait_all_reach()

            move_speed = leg_move_speed

            set_site(2, x_default + x_offset, y_start + 2 * y_step, z_up)
            wait_all_reach()
            set_site(2, x_default + x_offset, y_start, z_up)
            wait_all_reach()
            set_site(2, x_default + x_offset, y_start, z_current)
            wait_all_reach()


def turn_left(step):
    global move_speed
    move_speed = spot_turn_speed
    while step > 0:
        step -= 1
        if site_now[3][1] == y_start:
            # leg 3&1 move
            set_site(3, x_default + x_offset, y_start, z_up)
            wait_all_reach()

            set_site(0, turn_x1 - x_offset, turn_y1, z_current)
            set_site(1, turn_x0 - x_offset, turn_y0, z_current)
            set_site(2, turn_x1 + x_offset, turn_y1, z_current)
            set_site(3, turn_x0 + x_offset, turn_y0, z_up)
            wait_all_reach()

            set_site(3, turn_x0 + x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(0, turn_x1 + x_offset, turn_y1, z_current)
            set_site(1, turn_x0 + x_offset, turn_y0, z_current)
            set_site(2, turn_x1 - x_offset, turn_y1, z_current)
            set_site(3, turn_x0 - x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(1, turn_x0 + x_offset, turn_y0, z_up)
            wait_all_reach()

            set_site(0, x_default + x_offset, y_start, z_current)
            set_site(1, x_default + x_offset, y_start, z_up)
            set_site(2, x_default - x_offset, y_start + y_step, z_current)
            set_site(3, x_default - x_offset, y_start + y_step, z_current)
            wait_all_reach()

            set_site(1, x_default + x_offset, y_start, z_current)
            wait_all_reach()
        else:
            # leg 0&2 move
            set_site(0, x_default + x_offset, y_start, z_up)
            wait_all_reach()

            set_site(0, turn_x0 + x_offset, turn_y0, z_up)
            set_site(1, turn_x1 + x_offset, turn_y1, z_current)
            set_site(2, turn_x0 - x_offset, turn_y0, z_current)
            set_site(3, turn_x1 - x_offset, turn_y1, z_current)
            wait_all_reach()

            set_site(0, turn_x0 + x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(0, turn_x0 - x_offset, turn_y0, z_current)
            set_site(1, turn_x1 - x_offset, turn_y1, z_current)
            set_site(2, turn_x0 + x_offset, turn_y0, z_current)
            set_site(3, turn_x1 + x_offset, turn_y1, z_current)
            wait_all_reach()

            set_site(2, turn_x0 + x_offset, turn_y0, z_up)
            wait_all_reach()

            set_site(0, x_default - x_offset, y_start + y_step, z_current)
            set_site(1, x_default - x_offset, y_start + y_step, z_current)
            set_site(2, x_default + x_offset, y_start, z_up)
            set_site(3, x_default + x_offset, y_start, z_current)
            wait_all_reach()

            set_site(2, x_default + x_offset, y_start, z_current)
            wait_all_reach()


def turn_right(step):
    global move_speed
    move_speed = spot_turn_speed
    while step > 0:
        step -= 1
        if site_now[2][1] == y_start:
            # leg 2&0 move
            set_site(2, x_default + x_offset, y_start, z_up)
            wait_all_reach()

            set_site(0, turn_x0 - x_offset, turn_y0, z_current)
            set_site(1, turn_x1 - x_offset, turn_y1, z_current)
            set_site(2, turn_x0 + x_offset, turn_y0, z_up)
            set_site(3, turn_x1 + x_offset, turn_y1, z_current)
            wait_all_reach()

            set_site(2, turn_x0 + x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(0, turn_x0 + x_offset, turn_y0, z_current)
            set_site(1, turn_x1 + x_offset, turn_y1, z_current)
            set_site(2, turn_x0 - x_offset, turn_y0, z_current)
            set_site(3, turn_x1 - x_offset, turn_y1, z_current)
            wait_all_reach()

            set_site(0, turn_x0 + x_offset, turn_y0, z_up)
            wait_all_reach()

            set_site(0, x_default + x_offset, y_start, z_up)
            set_site(1, x_default + x_offset, y_start, z_current)
            set_site(2, x_default - x_offset, y_start + y_step, z_current)
            set_site(3, x_default - x_offset, y_start + y_step, z_current)
            wait_all_reach()

            set_site(0, x_default + x_offset, y_start, z_current)
            wait_all_reach()
        else:
            # leg 1&3 move
            set_site(1, x_default + x_offset, y_start, z_up)
            wait_all_reach()

            set_site(0, turn_x1 + x_offset, turn_y1, z_current)
            set_site(1, turn_x0 + x_offset, turn_y0, z_up)
            set_site(2, turn_x1 - x_offset, turn_y1, z_current)
            set_site(3, turn_x0 - x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(1, turn_x0 + x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(0, turn_x1 - x_offset, turn_y1, z_current)
            set_site(1, turn_x0 - x_offset, turn_y0, z_current)
            set_site(2, turn_x1 + x_offset, turn_y1, z_current)
            set_site(3, turn_x0 + x_offset, turn_y0, z_current)
            wait_all_reach()

            set_site(3, turn_x0 + x_offset, turn_y0, z_up)
            wait_all_reach()

            set_site(0, x_default - x_offset, y_start + y_step, z_current)
            set_site(1, x_default - x_offset, y_start + y_step, z_current)
            set_site(2, x_default + x_offset, y_start, z_current)
            set_site(3, x_default + x_offset, y_start, z_up)
            wait_all_reach()

            set_site(3, x_default + x_offset, y_start, z_current)
            wait_all_reach()


def set_site(leg, x, y, z):
    global move_speed
    length_x = 0
    length_y = 0
    length_z = 0

    if x != KEEP:
        length_x = x - site_now[leg][0]
    if y != KEEP:
        length_y = y - site_now[leg][1]
    if z != KEEP:
        length_z = z - site_now[leg][2]

    length = math.sqrt(pow(length_x, 2) + pow(length_y, 2) + pow(length_z, 2))

    temp_speed[leg][0] = (length_x / length * move_speed * speed_multiple) if length != 0 else 0
    temp_speed[leg][1] = (length_y / length * move_speed * speed_multiple) if length != 0 else 0
    temp_speed[leg][2] = (length_z / length * move_speed * speed_multiple) if length != 0 else 0

    if x != KEEP:
        site_expect[leg][0] = x
    if y != KEEP:
        site_expect[leg][1] = y
    if z != KEEP:
        site_expect[leg][2] = z


def wait_reach(leg):
    while True:
        if site_now[leg][0] == site_expect[leg][0]:
            if site_now[leg][1] == site_expect[leg][1]:
                if site_now[leg][2] == site_expect[leg][2]:
                    break


def wait_all_reach():
    for i in range(4):
        wait_reach(i)


async def servo_service():
    global servo_service_active
    while True:
        await asyncio.sleep(0.02)
        if not servo_service_active:
            break
        for i in range(4):
            for j in range(3):
                if abs(site_now[i][j] - site_expect[i][j]) >= abs(temp_speed[i][j]):
                    site_now[i][j] += temp_speed[i][j]
                else:
                    site_now[i][j] = site_expect[i][j]

            alpha, beta, gamma = cartesian_to_polar(site_now[i][0], site_now[i][1], site_now[i][2])
            polar_to_servo(i, alpha, beta, gamma)


def cartesian_to_polar(x, y, z):
    # calculate w-z degree
    w = (1 if x >= 0 else -1) * (math.sqrt(pow(x, 2) + pow(y, 2)))
    v = w - length_c
    alpha = math.atan2(z, v) + math.acos(
        (pow(length_a, 2) - pow(length_b, 2) + pow(v, 2) + pow(z, 2)) / 2 / length_a / math.sqrt(pow(v, 2) + pow(z, 2)))
    beta = math.acos((pow(length_a, 2) + pow(length_b, 2) - pow(v, 2) - pow(z, 2)) / 2 / length_a / length_b)
    # calculate x-y-z degree
    gamma = math.atan2(y, x) if (w >= 0) else math.atan2(-y, -x)
    # trans degree pi->180
    alpha = alpha / pi * 180
    beta = beta / pi * 180
    gamma = gamma / pi * 180
    return alpha, beta, gamma


def polar_to_servo(leg, alpha, beta, gamma):
    if leg == 0:
        alpha = 90 - alpha
        beta = beta
        gamma += 90
    elif leg == 1:
        alpha += 90
        beta = 180 - beta
        gamma = 90 - gamma
    elif leg == 2:
        alpha += 90
        beta = 180 - beta
        gamma = 90 - gamma
    elif leg == 3:
        alpha = 90 - alpha
        beta = beta
        gamma += 90

    move_servo(servo_pin[leg][0], alpha)
    move_servo(servo_pin[leg][1], beta)
    move_servo(servo_pin[leg][2], gamma)


def move_servo(pin, angle):
    if 0 <= angle <= 180:
        pca.servo[pin].angle = angle


if __name__ == "__main__":
    print('Rob service init...')
    setup()
