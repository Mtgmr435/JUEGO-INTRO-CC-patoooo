import math
import os
import pygame

pygame.init()

#tamano de la pantalla y otros como el suelo la escala y el rendimiento en general
ANCHO = 1080
ALTO = 720
SUELO_Y = 520
FPS = 30
ESCALA = 10                 

pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("juego intro cc :P")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 25)

#las imagenes que le puse 
def cargar_imagen(nombre, tamano):
    
    ruta = os.path.join("assets", nombre)

    imagen = pygame.image.load(ruta).convert_alpha()

    return pygame.transform.smoothscale(imagen, tamano)


catapulta_img = cargar_imagen("catapulta.png", (140, 90))
pato_img = cargar_imagen("patoooo.png", (48, 48))
obstaculo_img = cargar_imagen("inflable.png", (150, 100))

#se crean los primeros obstaculos y despues cada 350 pixeles se crea otro 
obstaculos = [
    pygame.Rect(500, SUELO_Y - 25, 150, 25),
    pygame.Rect(850, SUELO_Y - 25, 150, 25),
    pygame.Rect(1200, SUELO_Y - 25, 150, 25),
]

# aca es donde cada 350 se crean
def crear_mas_obstaculos(posicion_jugador):
    while obstaculos[-1].x < posicion_jugador + ANCHO * 2:
        nueva_x = obstaculos[-1].x + 350
        obstaculos.append(pygame.Rect(nueva_x, SUELO_Y - 25, 150, 25))

# la fisica que propusimos en clase, igual algunos de estos valores se ajustan despues
angulo = 45
potencia = 35.0
masa = 1.0
rozamiento = 0.03
viento = 0.0
rebote = 0.9
delta_t = 1.0 / FPS

tracj = []


def reiniciar():
    global x, v, a, F, tracj, lanzado, terminado, camara_x

    #aca enpieza el senor patooo
    x = [15.0, 6.0]

    #estos vectores parecidos a los que vimos en clase los iniciamos en 0
    v = [0.0, 0.0]
    a = [0.0, 0.0]
    F = [0.0, 0.0]

    tracj = []
    lanzado = False
    terminado = False
    camara_x = 0.0  #aca esta la posicion de la camara


reiniciar()

#aca esta el ciclo principal, aca defini los controles del juego y el disparo descompuesto en trigonometria(x,y)
ejecutando = True
while ejecutando:
    reloj.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False

            if evento.key == pygame.K_r:
                reiniciar()

            if evento.key == pygame.K_SPACE and not lanzado and not terminado:
                radianes = math.radians(angulo)
                v[0] = potencia * math.cos(radianes)
                v[1] = potencia * math.sin(radianes)
                lanzado = True

    teclas = pygame.key.get_pressed()

    if not lanzado and not terminado: #aca ya se definen las ultimas teclas que cambian los valores antes vistos
        if teclas[pygame.K_LEFT]:
            angulo = max(15, angulo - 1)
        if teclas[pygame.K_RIGHT]:
            angulo = min(75, angulo + 1)
        if teclas[pygame.K_DOWN]:
            potencia = max(15.0, potencia - 0.2)
        if teclas[pygame.K_UP]:
            potencia = min(45.0, potencia + 0.2)

    #aca se operan basado en lo que vimos en clase igual anadi el viento pero lo deje en 0 pq no es tan divertido
    if lanzado:
        # gravedad.
        f1 = [0.0, -9.8 * masa]

        # resistencia del aire.
        f2 = [-rozamiento * v[0], -rozamiento * v[1]]

        #  viento horizontal.
        f3 = [viento, 0.0]

        # Fuerza total.
        F[0] = f1[0] + f2[0] + f3[0]
        F[1] = f1[1] + f2[1] + f3[1]

        #  F = m*a.
        a[0] = F[0] / masa
        a[1] = F[1] / masa

        # velocidad.
        v[0] = v[0] + delta_t * a[0]
        v[1] = v[1] + delta_t * a[1]

        # posicion.
        x[0] = x[0] + delta_t * v[0]
        x[1] = x[1] + delta_t * v[1]

        # Posicion del jugador dentro del mundo completo
        jugador_mundo_x = int(x[0] * ESCALA)
        crear_mas_obstaculos(jugador_mundo_x)
        jugador_mundo_y = int(SUELO_Y - x[1] * ESCALA)
        jugador_rect_mundo = pato_img.get_rect(
            center=(jugador_mundo_x, jugador_mundo_y)
        )

        # aca se definen los rebotes donde se pierde fuerza y cambia la posicion para q reboteee
        for obstaculo_rect in obstaculos:
            if jugador_rect_mundo.colliderect(obstaculo_rect) and v[1] < 0:
                jugador_mundo_y = (
                    obstaculo_rect.top - jugador_rect_mundo.height // 2
                )
                x[1] = (SUELO_Y - jugador_mundo_y) / ESCALA
                v[1] = abs(v[1]) * rebote
                v[0] = v[0] * 0.96
                break

        # el tracj de clase se guarda en puntos para la trayectoria 
        tracj.append(
            [
                int(x[0] * ESCALA),
                int(SUELO_Y - x[1] * ESCALA),
            ]
        )

        # se pone que termino el juego cuando toca suelo diferente a las bolas
        mitad_altura_m = (pato_img.get_height() / 2) / ESCALA
        if x[1] <= mitad_altura_m:
            x[1] = mitad_altura_m
            v = [0.0, 0.0]
            lanzado = False
            terminado = True

    #aca se definio la camara donde se puso la velocidad y que el pato se mantenga en pantalla
    jugador_mundo_x = int(x[0] * ESCALA)
    objetivo_camara = max(0, jugador_mundo_x - int(ANCHO * 0.40))
    camara_x = camara_x + (objetivo_camara - camara_x) * 0.12

    #el fondo suelo 
    pantalla.fill((180, 225, 255))

    
    pygame.draw.rect(
        pantalla,
        (45, 115, 220),
        (0, SUELO_Y, ANCHO, ALTO - SUELO_Y),
    )

    # la catapulta se va por la izquierda y desaparece restando la cordeanda x 
    catapulta_x_pantalla = int(75 - camara_x)
    pantalla.blit(catapulta_img, (catapulta_x_pantalla, SUELO_Y - 90))

    for obstaculo_rect in obstaculos:
        rect_pantalla = obstaculo_rect.move(-int(camara_x), 0)

        # Solo se dibuja si esta cerca de la pantalla
        if rect_pantalla.right >= 0 and rect_pantalla.left <= ANCHO:
            pantalla.blit(obstaculo_img, rect_pantalla)

    #la fisica del disparo igual se dibuja la linea con el tracj de clase
    if not lanzado and not terminado:
        inicio_mundo = (150, SUELO_Y - 60)
        inicio = (int(inicio_mundo[0] - camara_x), inicio_mundo[1])
        largo = potencia * 3
        final = (
            int(inicio[0] + largo * math.cos(math.radians(angulo))),
            int(inicio[1] - largo * math.sin(math.radians(angulo))),
        )
        pygame.draw.line(pantalla, (40, 40, 40), inicio, final, 4)

    # aca la trayectoria del pato
    if len(tracj) > 1:
        trayectoria_pantalla = [
            (int(punto[0] - camara_x), punto[1]) for punto in tracj
        ]
        pygame.draw.lines(
            pantalla,
            (70, 70, 70),
            False,
            trayectoria_pantalla,
            2,
        )

    #centra el pato
    jugador_pantalla_x = int(x[0] * ESCALA - camara_x)
    jugador_pantalla_y = int(SUELO_Y - x[1] * ESCALA)
    jugador_rect_pantalla = pato_img.get_rect(
        center=(jugador_pantalla_x, jugador_pantalla_y)
    )
    pantalla.blit(pato_img, jugador_rect_pantalla)

    # la info para que se vea lo que esta cambiando 
    distancia = max(0.0, x[0] - 15.0)
    texto1 = fuente.render(f"Angulo: {angulo} grados", True, (25, 25, 25))
    texto2 = fuente.render(f"Potencia: {potencia:.1f} m/s", True, (25, 25, 25))
    texto3 = fuente.render(f"Distancia: {distancia:.1f} m", True, (25, 25, 25))
    texto4 = fuente.render(
        "Flechas: ajustar | ESPACIO: lanzar | R: reiniciar",
        True,
        (25, 25, 25),
    )

    pantalla.blit(texto1, (20, 20))
    pantalla.blit(texto2, (20, 48))
    pantalla.blit(texto3, (20, 76))
    pantalla.blit(texto4, (20, 110))

    if terminado:
        texto_final = fuente.render(
            "Lanzamiento terminado. Presiona R para reiniciar.",
            True,
            (25, 25, 25),
        )
        pantalla.blit(texto_final, (20, 145))
#es como el otro pero este dibuja mas rapido y se ve mas fluido 
    pygame.display.flip()
#cierra el juego cuando salimos del bucle mientras ejecutando sea truee
pygame.quit()
