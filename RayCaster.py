import pygame as pg
#import pygame.gfxdraw as gfx
 
from math import cos, sin, pi

RAY_AMOUNT = 60
WHITE = pg.Color('white')
BLACK = pg.Color('black')
GRAY = pg.Color("gray")
SADDLEBROWN = pg.Color("saddlebrown")
DIMGRAY = pg.Color("dimgray")

wallcolors = {
    '1': pg.Color('red'),
    '2': pg.Color('green'),
    '3': pg.Color('blue'),
    '4': pg.Color('yellow'),
    '5': pg.Color('purple')
    }

wallTextures = {
    '1': pg.image.load('wall1.png'),
    '2': pg.image.load('wall2.png'),
    '3': pg.image.load('wall3.png'),
    '4': pg.image.load('wall4.png'),
    '5': pg.image.load('wall5.png')
    }


class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallheight = 50

        self.maxdistance = 300

        self.stepSize = 5
        self.turnSize = 5

        self.player = {
           'x' : 100,
           'y' : 175,
           'fov': 60,
           'angle': 0 }


    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append( list(line.rstrip()) )

    def drawBlock(self, x, y, id):
        tex = wallTextures[id]
        tex = pg.transform.scale(tex, (self.blocksize, self.blocksize) )
        rect = tex.get_rect()
        rect = rect.move((x,y))
        self.screen.blit(tex, rect)


    def drawPlayerIcon(self, color):
        self.screen.fill(color, (self.player['x'] - 2, self.player['y'] - 2, 5,5))

    def castRay(self, angle):
        rads = angle * pi / 180
        dist = 0
        stepSize = 1
        stepX = stepSize * cos(rads)
        stepY = stepSize * sin(rads)

        playerPos = (self.player['x'],self.player['y'] )

        x = playerPos[0]
        y = playerPos[1]

        while True:
            dist += stepSize      

            x += stepX
            y += stepY

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':

                        hitX = x - i*self.blocksize
                        hitY = y - j*self.blocksize

                        hit = 0

                        if 1 < hitX < self.blocksize-1:
                            if hitY < 1:
                                hit = self.blocksize - hitX
                            elif hitY >= self.blocksize-1:
                                hit = hitX
                        elif 1 < hitY < self.blocksize-1:
                            if hitX < 1:
                                hit = hitY
                            elif hitX >= self.blocksize-1:
                                hit = self.blocksize - hitY

                        tx = hit / self.blocksize
                        pg.draw.line(self.screen, WHITE, playerPos, (x,y))
                        return dist, self.map[j][i], tx


    def render(self):
        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):

                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if j < len(self.map):
                    if i < len(self.map[j]):
                        if self.map[j][i] != ' ':
                            self.drawBlock(x, y, self.map[j][i])

        self.drawPlayerIcon(BLACK)

        rayWidth = int(( 1 / RAY_AMOUNT) * halfWidth)
        h_precalc = self.height * self.wallheight
        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] - (self.player['fov'] / 2) + (self.player['fov'] * column / RAY_AMOUNT)
            dist, id, tx = self.castRay(angle)


            startX = halfWidth + int(( (column / RAY_AMOUNT) * halfWidth))

            # perceivedHeight = screenHeight / (distance * cos( rayAngle - viewAngle)) * wallHeight
            h = h_precalc / (dist * cos( (angle - self.player["angle"]) * pi / 180)) 
            startY = int(halfHeight - h/2)

            color_k = (1 - min(1, dist / self.maxdistance)) * 255

            tex = wallTextures[id]
            tex = pg.transform.scale(tex, (tex.get_width() * rayWidth, int(h)))
            tex.fill((color_k,color_k,color_k), special_flags=pg.BLEND_MULT)
            tx = int(tx * tex.get_width())
            self.screen.blit(tex, (startX, startY), (tx,0,rayWidth,tex.get_height()))

        # Columna divisora
        pg.draw.line(self.screen, BLACK, (self.width/2, 0), (self.width/2, self.height), width = 3)


width = 1000
height = 500

pg.init()
screen = pg.display.set_mode((width,height), pg.DOUBLEBUF | pg.HWACCEL )
screen.set_alpha(None)

rCaster = Raycaster(screen)
rCaster.load_map("map.txt")

clock = pg.time.Clock()
font = pg.font.SysFont("Arial", 25)

def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, WHITE)
    return fps

isRunning = True
while isRunning:

    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            isRunning = False

        elif ev.type == pg.KEYDOWN:
            newX = rCaster.player['x']
            newY = rCaster.player['y']
            forward = rCaster.player['angle'] * pi / 180
            right = (rCaster.player['angle'] + 90) * pi / 180

            if ev.key == pg.K_ESCAPE:
                isRunning = False
            elif ev.key == pg.K_w:
                newX += cos(forward) * rCaster.stepSize
                newY += sin(forward) * rCaster.stepSize
            elif ev.key == pg.K_s:
                newX -= cos(forward) * rCaster.stepSize
                newY -= sin(forward) * rCaster.stepSize
            elif ev.key == pg.K_a:
                newX -= cos(right) * rCaster.stepSize
                newY -= sin(right) * rCaster.stepSize
            elif ev.key == pg.K_d:
                newX += cos(right) * rCaster.stepSize
                newY += sin(right) * rCaster.stepSize
            elif ev.key == pg.K_q:
                rCaster.player['angle'] -= rCaster.turnSize
            elif ev.key == pg.K_e:
                rCaster.player['angle'] += rCaster.turnSize

            i = int(newX/rCaster.blocksize)
            j = int(newY/rCaster.blocksize)

            if rCaster.map[j][i] == ' ':
                rCaster.player['x'] = newX
                rCaster.player['y'] = newY


    screen.fill(GRAY)

    # Techo
    screen.fill(SADDLEBROWN, (int(width / 2), 0,  int(width / 2), int(height / 2)))

    # Piso
    screen.fill(DIMGRAY, (int(width / 2), int(height / 2),  int(width / 2), int(height / 2)))


    rCaster.render()

    #FPS
    screen.fill(BLACK, (0,0,30,30) )
    screen.blit(updateFPS(), (0,0))
    clock.tick(60)


    pg.display.flip()

pg.quit()
