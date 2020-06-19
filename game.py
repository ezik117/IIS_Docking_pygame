# *****************************************************************************
# ПРОЕКТ: ISS Docking Simulator
# ФАЙЛ: game.py
# ОПИСАНИЕ: основной модуль проекта
# *****************************************************************************

# -- ИМПОРТ БИБЛИОТЕК
import pygame, os, datetime, math as Math
from pygame.locals import *
from padlib import *

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50) # зададим координаты вывода главного окна

# ---- ФУНКЦИИ
def refineDest(sh, sv):
	a = set()
	if round(sh, 1) > 0.0:
		a.add("ВОСТОК")
	if round(sh, 1) < 0.0:
		a.add("ЗАПАД")
	if round(sv, 1) > 0.0:
		a.add("ЮГ")
	if round(sv, 1) < 0.0:
		a.add("СЕВЕР")
	return a

# -- ИНИЦИАЛИЗАЦИЯ
random.seed()
pygame.init()
screen = pygame.display.set_mode((800, 600)) # главная поверхность
pygame.display.set_caption('IIS Docking simulator')

pygame.font.init()
font_dot = pygame.font.Font('square_dot_digital-7.ttf', 30)

# -- ЗАДАЕМ НАЧАЛЬНЫЕ НАСТРОЙКИ
# загрузка картинок
img_scr_intro = pygame.image.load("Scr_Intro.jpg")
img_scr_task = pygame.image.load("Scr_Task.jpg")
img_progressm = pygame.image.load("img_progressm.png").convert_alpha()
img_background = pygame.image.load("background.jpg").convert()
img_brokenglass = pygame.image.load("img_brokenglass.png").convert_alpha()

# получить системный таймер для того, что бы задать FPS=25 кадров в секунду
clock = pygame.time.Clock()
fps = 25

# инициализация переменных
mainExit = False # флаг выхода из главного цикла
game_state = 0 # текущее состояние игры. То что будет обрабатывать главный цикл зависит от этой переменной
""" 
0 - начальный экран №1 (введение)
1 - начальный экран №2 (задача)
2 - игровой экран (сближение со станцией)
3 - финальный экран (сигнал потерян / стыковка)

"""

dp_x, dp_y = random.randrange(100, 700), random.randrange(100, 500) # координаты Прогресса
dp_w, dp_h = 3119, 1276 # ширина и высота картинки Прогресса
dp_scale, dp_scale_step, dp_scale_stop = 10.0, 0.008, 0.5 # коэффициент уменьшения Прогресса. Используется для маштабирования картинки с целью симуляции приближения
dp_rotation, dp_rotation_step = random.randrange(0, 359), 0.2 # вращение Прогресса (0.2)
dp_scale_suspended = 0

# скорость корабля является линейной. По хорошему должна быть логарифмическая, но она для земного сопротивления по воздуху
speed_h, speed_v = 0.0, 0.0 # горизонтальная и вертикальная скорости
speed_max, speed_step = 9.0, 0.1 # максимальная скорость сближения, шаг увеличения скорости

# вычисляем движение в зависимости от появления
if dp_x < 400 and dp_y < 300: speed_h, speed_v = 1.0, 1.0
if dp_x < 400 and dp_y >= 300: speed_h, speed_v = 1.0, -1.0
if dp_x >= 400 and dp_y < 300: speed_h, speed_v = -1.0, 1.0
if dp_x >= 400 and dp_y >= 300: speed_h, speed_v = -1.0, -1.0

speed_direction = refineDest(speed_h, speed_v) # направление движения

iis_hit = False # True если Прогресс врезался в МКС
disp_interlaced = False


# константы
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)

# расстояние между двумя точками по их координатам: от центра картинки до изображенного центра шлюза
docking_center = Math.sqrt(Math.pow((dp_w/2)-1604, 2) + Math.pow((dp_h/2)-705, 2)) 

# -- ОСНОВНОЙ ЦИКЛ ВЫПОЛНЕНИЯ ПРОГРАММЫ
while not mainExit:

	# обработка событий
	for event in pygame.event.get():
		# нажат крестик окна - выход из программы
		if event.type == QUIT:
			mainExit = True
		# если щелчок мыши или любой клавишей
		elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
			if game_state < 2:
				game_state += 1
			elif game_state == 2:
				if event.key and event.key == K_SPACE:
					disp_interlaced = not disp_interlaced
				elif event.key and event.key == K_RETURN:
					if dp_scale_step != 0:
						dp_scale_suspended = dp_scale_step
						dp_scale_step = 0
					else:
						dp_scale_step = dp_scale_suspended

	# ОБРАБОТКА ВЫВОДА ВСЕХ ИЗОБРАЖЕНИЙ В ЭКРАННЫЙ БУФЕР
	if game_state == 0:
		""" основной экран """
		screen.blit(img_scr_intro, (0,0))

	elif game_state == 1:
		""" задача симуляции полета """
		screen.blit(img_scr_task, (0,0))

	elif game_state >= 2:
		""" симулятор """

	# если это игровой экран, задаем направление движения
		keys = pygame.key.get_pressed()
		if len(keys) != 0:
			if keys[K_LEFT]:
				if abs(speed_h) <= speed_max and dp_x < 800:
					speed_h += speed_step

			if keys[K_RIGHT]:
				if abs(speed_h) <= speed_max and dp_x > 0:
					speed_h -= speed_step

			if keys[K_UP]:
				if abs(speed_v) <= speed_max and dp_y < 600:
					speed_v += speed_step

			if keys[K_DOWN]:
				if abs(speed_v) <= speed_max and dp_y > 0:
					speed_v -= speed_step

			# ограничение на скорость
			if abs(speed_h) > speed_max:
				speed_h = speed_max * (-1 if speed_h < 0 else 1)
			if abs(speed_v) > speed_max:
				speed_v = speed_max * (-1 if speed_v < 0 else 1)

		# перемещение и вращение
		if dp_scale != dp_scale_stop:
			dp_x += speed_h
			dp_y += speed_v
			dp_rotation -= dp_rotation_step # вращение
			dp_rotation %= 360

		# ограничение на выход за пределы экрана
		if dp_x <= 0:
			dp_x = 0.0
			speed_h = 0
		if dp_y <= 0:
			dp_y = 0.0
			speed_v = 0
		if dp_x >= 800:
			dp_x = 800
			speed_h = 0.0
		if dp_y >= 600:
			dp_y = 600
			speed_v = 0.0

		speed_direction = refineDest(speed_h, speed_v)

		# вычисляем сближение
		dp_scale -= dp_scale_step
		if dp_scale < 1:
			dp_scale -= (dp_scale_step * 1.3)
		elif dp_scale < 2:
			dp_scale -= (dp_scale_step * 1.1)
		if dp_scale <= dp_scale_stop:
			# сближение закончено
			dp_scale = dp_scale_stop

		# очистили экран
		screen.fill(black)

		# поворачиваем Прогресс
		dp_rotated = pygame.transform.rotate(
				pygame.transform.scale(img_progressm, (int(dp_w/dp_scale), int(dp_h/dp_scale))),
				dp_rotation)
		#dp_rotated = pygame.transform.rotozoom(img_progressm, dp_rotation, 1/dp_scale)

		# высчитываем координаты 
		r = docking_center / dp_scale

		# -- координаты вывода картинки
		xImg = dp_x - dp_rotated.get_rect().center[0]
		yImg = dp_y - dp_rotated.get_rect().center[1]

		# -- центр стыковки
		x0 = dp_x + r * Math.cos(Math.radians(57-dp_rotation))
		y0 = dp_y + r * Math.sin(Math.radians(57-dp_rotation))
		rc = pygame.Rect( int(x0-50/dp_scale), int(y0-50/dp_scale), int(100/dp_scale), int(100/dp_scale) )
		rc1 = pygame.Rect( int(x0-25/dp_scale), int(y0-25/dp_scale), int(50/dp_scale), int(50/dp_scale) )

		# отрисовываем Прогресс
		screen.blit(img_background, (0,0), (0,0,800,600))
		screen.blit(dp_rotated, (int(xImg), int(yImg)))

		# имитация чресстрочной развертки
		if disp_interlaced:
			for iy in range(0, 600, 2):
				pygame.draw.line(screen, (10,10,10), (0, iy), (800, iy), 1)

		# вычисляем находится ли перекрестие в допустимой зоне стыковки
		# а заодно определяем - успешно ли мы пристыковались или врезались
		# и выводим прямоугольник зоны стыковки
		if dp_scale < 5:
			if rc.collidepoint(400, 300):
				pygame.draw.rect(screen, green, rc, 2)
			else:
				pygame.draw.rect(screen, red, rc, 2)
		# вторая мишень
		if dp_scale < 2:
			if rc1.collidepoint(400, 300):
				pygame.draw.rect(screen, yellow, rc1, 1)
				if dp_scale == dp_scale_stop:
					iis_hit = False # успешно
					game_state = 3 # следующий игровой экран
			else:
				pygame.draw.rect(screen, red, rc1, 1)
				if dp_scale == dp_scale_stop:
					iis_hit = True # врезались
					game_state = 3 # следующий игровой экран

		# рисуем вид из камеры грузового корабля
		DashedLine(screen, white, black, (400, -13), (400, 599), 11) #верт линия
		DashedLine(screen, white, black, (-1, 300), (799, 300), 11) #гориз линия

		# выводим всякие типа служебные надписи для красоты
		fnt = font_dot.render("Ф44   СБЛИЖ         ПРИЧАЛ Т={}".format(
			       datetime.datetime.now().strftime("%H:%M:%S")), True, white)
		screen.blit(fnt, (95, 30))
		fnt = font_dot.render("ЛСК               ГСО 1234", True, white)
		screen.blit(fnt, (95, 60))
		fnt = font_dot.render("СКОРОСТЬ: {}H {}V".format(round(speed_h, 2), round(speed_v, 2)), True, white)
		screen.blit(fnt, (30, 110))
		fnt = font_dot.render("КУРС: {}".format( ("-".join(d for d in speed_direction)) if len(speed_direction) != 0 else "НЕТ"), True, white)
		screen.blit(fnt, (30, 140))
		fnt = font_dot.render("СБЛИЖЕНИЕ: {}".format(-1 * round(dp_scale - 1, 3)), True, white)
		screen.blit(fnt, (30, 190))	
		fnt = font_dot.render("ВРАЩЕНИЕ: {}".format(round(dp_rotation % 360, 2)), True, white)
		screen.blit(fnt, (30, 220))
		fnt = font_dot.render("dX: {}".format(400-int(x0)), True, white)
		screen.blit(fnt, (650, 270))
		fnt = font_dot.render("dY: {}".format(300-int(y0)), True, white)
		screen.blit(fnt, (650, 300))	
		fnt = font_dot.render("ДЕЛЬТА R {:f}".format(r), True, black)
		screen.blit(fnt, (30, 560))		

		if dp_scale_step == 0:
			fnt = font_dot.render("SPEED PAUSED", True, white)
			screen.blit(fnt, (30, 330))
		if disp_interlaced:
			fnt = font_dot.render("INTERLACED VIEW", True, white)
			screen.blit(fnt, (30, 360))	

		fnt = font_dot.render("ИН: ЕСТЬ ССВП ГТ", True, black)
		screen.blit(fnt, (420, 560))

		# если дистанция равна 0
		if dp_scale == dp_scale_stop:
			if iis_hit:
				screen.blit( pygame.transform.scale(img_brokenglass, (800, 600)), (0,0) )
				pygame.draw.rect(screen, red, (238,280,275, 40), 2)
				pygame.draw.rect(screen, red, (243,285,265, 30))
				fnt = font_dot.render("СИГНАЛ ПОТЕРЯН", True, white)
				screen.blit(fnt, (250,285))	
				
			else:
				pygame.draw.rect(screen, green, (218,280,330, 40), 2)
				pygame.draw.rect(screen, green, (223,285,320, 30))
				fnt = font_dot.render("УСПЕШНАЯ СТЫКОВКА", True, black)
				screen.blit(fnt, (230,285))					

	# обновить главную поверхность с частотой FPS
	pygame.display.flip()
	clock.tick(fps)


pygame.quit()