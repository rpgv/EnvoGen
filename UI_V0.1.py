# Source - https://stackoverflow.com/a
# Posted by Ted Klein Bergman, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-16, License - CC BY-SA 3.0
import pygame
from numpy.random import choice
import random
pygame.init()

screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
MAX_SPRITES = 500

attraction_map = {
    1:[1,1],
    2:[-1,1],
    3:[1,-1],
    4:[-1,-1],
    5:[0,1],
    6:[0,-1],
    7:[1,0],
    8:[-1,0],
}

stay_fact_map = {
    1:[0.05,0.95],
    2:[0.25,0.75],
    3:[0.50,0.50],
    4:[0.75,0.25],
    5:[0.99,0.01],
}

def color_generator(genes):
    r = abs(sum([i for i in genes[:2]])*19)+1
    g = abs(sum([i for i in genes[2:5]])*5)+1
    b = abs(sum([i for i in genes[5:]])*11)+1
    return r,g,b

def enforce_limit(int, limit):
    if int > limit:
        return limit
    elif int < 1:
        return 1
    else:
        return int

def clone_cells(sprite_g):
    for i in sprite_g.sprites():
        mutations = i.mutate()
        # print(f"Mutations: {mutations}")
        if i.reprod == 1:
            sprite_g.add(Cell(pos=(i.pos.x-10, i.pos.y-10), genes=mutations),
            Cell(pos=(i.pos.x, i.pos.y), genes=mutations))

def danger_zone(pos, size):
    return pos[0]-10,pos[0]+size[0]+10,pos[1]-10,pos[1]+size[1]+10

def collider(pos, s_group):
    collides = False
    for i in s_group:
        x1,x2,y1,y2 = danger_zone(i.pos, i.size)
        if pos[0] >= x1 and pos[0] <= x2 and pos[1] >= y1 and pos[1] <= y2:
            collides = True
    return collides
        

cells = pygame.sprite.Group()
# CheckPoint (For ME)
# Genetic code reference: [size, life_span, reprod_rate, predator, mutation_factor, speed, attraction, staying_factor]
class Cell(pygame.sprite.Sprite):
    def __init__(self, pos, genes=[1,1,1,0,1,1,1,1]):
        super(Cell, self).__init__()
        image = pygame.Surface((5+genes[0], 5+genes[0]))
        r,g,b = color_generator(genes)
        image.fill((r,g,b))
        if image is None:
            self.rect = pygame.Rect(pos, (5+genes[0], 5+genes[0]))
            self.image = pygame.Surface((5+genes[0], 5+genes[0]))
        else:
            self.image = image
            self.rect = image.get_rect(topleft=pos)
        self.pressed = False
        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(-1, -1)
        self.size_gene = genes[0]
        self.life_span = 10*genes[1]
        self.reprod_season = (genes[2]*self.life_span)-1
        self.reprod = 0
        self.internal_clock = pygame.time.get_ticks()/1000
        self.predator = genes[3]
        self.mutation_factor = genes[4]
        self.speed = genes[5]
        self.attraction = genes[6]
        self.staying_factor = genes[7]
        self.genes = genes

    def mutate(self):
        # [size, life_span, reprod_rate, predator, mutation_factor, speed, attraction, staying_factor]
        factor = self.mutation_factor*0.15
        # print(f"Mutation factor: {factor}")
        resize_gene = enforce_limit(int(self.size_gene+(choice([0,1], p=[1-factor, factor]))), 4)
        life_gene = enforce_limit(int(self.genes[1]+(choice([-1,0,1], p=[factor*0.25,1-factor ,factor*0.75]))), 4)
        reprod_gene = enforce_limit(int(self.genes[2]+(choice([-1,0,1], p=[factor*0.25,1-factor,factor*0.75]))), 4)
        pred_gene = enforce_limit(int(self.predator), 4)
        speed_gene = self.speed+(choice([-1,0,1], p=[factor/2,1-factor,factor/2]))
        mutation_gene = enforce_limit(int(choice([self.mutation_factor,self.mutation_factor+1], p=[1-factor,factor])), 4)
        attract_gene = enforce_limit(int(self.attraction+(choice([0,1], p=[1-factor,factor]))), 8)
        staying_gene = enforce_limit(int(self.staying_factor+(choice([0,1], p=[1-factor,factor]))), 5)
        return [resize_gene,life_gene,reprod_gene,pred_gene,speed_gene,mutation_gene,attract_gene,staying_gene]

    def update(self, dt, sim_time):
        self.pos.x += self.dir.x * attraction_map[self.attraction][0]* 0.1 * dt + ((self.speed+0.1)/100)
        self.pos.y += self.dir.y * attraction_map[self.attraction][1]* 0.1 * dt + ((self.speed+0.1)/100)
        self.rect.topleft = self.pos
        
        if collider(self.pos, threats):
            print("Collision")
            self.kill()
        elif collider(self.pos, homes):
            n_genes = [self.genes[0], self.genes[1], self.genes[2], 0, 0.9*self.genes[4], self.genes[5], self.genes[6], 5]

            if len(cells.sprites()) < (MAX_SPRITES/10):
                self.kill()
                cells.add(Cell(pos=(self.pos.x-10, self.pos.y-10), genes=n_genes), Cell(pos=(self.pos.x, self.pos.y), genes=n_genes))
        
        if self.rect.left <= 0:
            self.rect.left = 0
            self.pos.x = 0
            self.dir.x *= -1 * choice([-1,1],p=stay_fact_map[self.staying_factor])
        elif self.rect.right >= 720:
            self.rect.right = 720
            self.pos.x = 720 - self.rect.width
            self.dir.x *= -1 * choice([-1,1],p=stay_fact_map[self.staying_factor])
        if self.rect.top <= 0:
            self.rect.top = 0
            self.pos.y = 0
            self.dir.y *= -1 * choice([-1,1],p=stay_fact_map[self.staying_factor])
        elif self.rect.bottom >= 520:
            self.rect.bottom = 520
            self.pos.y = 520 - self.rect.height
            self.dir.y *= -1 * choice([-1,1],p=stay_fact_map[self.staying_factor])
        

        if self.life_span <= sim_time-(self.internal_clock-0.05) and len(cells.sprites()) < MAX_SPRITES:
            self.reprod += 1 

        if self.life_span <= sim_time-self.internal_clock:
            self.kill()

class Button(pygame.sprite.Sprite):
    def __init__(self, pos, size=(32, 32), image=None,bid=0):
        super(Button, self).__init__()
        if image is None:
            self.rect = pygame.Rect(pos, size)
            self.image = pygame.Surface(size)
        else:
            self.image = image
            self.rect = image.get_rect(topleft=pos)
        self.pressed = False
        self.bid = bid
        self.edit = False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(mouse_pos) and mouse_clicked and not self.pressed:
            self.pressed = True
            if self.bid==0:
                g = [random.randint(1,4) for i in range(8)]
                cells.add(Cell(pos=(random.randint(0,700), random.randint(0,520)), genes=g))
            elif self.bid==1:
                threats.add(Threat(pos=(random.randint(0,720), random.randint(0,480)), size=(40,40)))
            elif self.bid==2:
                homes.add(Home(pos=(random.randint(0,720), random.randint(0,480)), size=(40,40)))
            elif self.bid==3 and self.edit == False:
                self.edit = True
            elif self.bid==3 and self.edit == True:
                self.edit = False
                
        
        if not mouse_clicked:
            self.pressed = False
            

class Threat(pygame.sprite.Sprite):
    def __init__(self, pos, size=(32, 32),bid=0):
        super(Threat, self).__init__()
        image = pygame.Surface(size)
        image.fill((255, 0, 0))
        self.pos = pos
        if image is None:
            self.rect = pygame.Rect(pos, size)
            self.image = pygame.Surface(size)
        else:
            self.image = image
            self.rect = image.get_rect(topleft=pos)
            self.size = size
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(*mouse_pos) and mouse_clicked and buttons.sprites()[3].edit:
            self.kill()

class Home(pygame.sprite.Sprite):
    def __init__(self, pos, size=(32, 32),bid=0):
        super(Home, self).__init__()
        image = pygame.Surface(size)
        image.fill((0, 0, 255))
        self.pos = pos
        if image is None:
            self.rect = pygame.Rect(pos, size)
            self.image = pygame.Surface(size)
        else:
            self.image = image
            self.rect = image.get_rect(topleft=pos)
            self.size = size
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(*mouse_pos) and mouse_clicked and buttons.sprites()[3].edit:
            self.kill()

image = pygame.Surface((100, 40))
image.fill((0, 173, 76))

image2 = pygame.Surface((100, 40))
image2.fill((200,0,0))

image3 = pygame.Surface((100, 40))
image3.fill((0,0,255))

image4 = pygame.Surface((100, 40))
image4.fill((200,70,70))

buttons = pygame.sprite.Group()

buttons.add(
    Button(pos=(20, 540), image=image,bid=0), 
    Button(pos=(20, 590), image=image2,bid=1),
    Button(pos=(20, 640), image=image3,bid=2),
    Button(pos=(130, 540), image=image4,bid=3),
)        


cells.add(
    Cell(pos=(200, 370), genes=[1,1,1,0,1,1,1,1])
)


threats = pygame.sprite.Group()
threats.add(
    Threat(pos=(20, 350), size=(40,40)),
)

homes = pygame.sprite.Group()
homes.add(
    Home(pos=(520, 350), size=(40,40)),
)

# Defining Button Text
smallfont = pygame.font.SysFont('Corbel',25)

text = smallfont.render('Add Cell' , True , 'white')
text2 = smallfont.render('Add Threat' , True , 'white')
text3 = smallfont.render('Add Home' , True , 'white')
text4 = smallfont.render('Edit Env' , True , 'white')


while True:
    dt = clock.tick(60)
    sim_time = pygame.time.get_ticks()/1000
    
    # Define Metrics Text
    text5 = smallfont.render(f'Cells in   SIM: {len(cells.sprites())}' , True , 'green')
    text6 = smallfont.render(f'Total SIM time: {sim_time}' , True , 'green')
    text7 = smallfont.render(f'Threats in SIM: {len(threats.sprites())}' , True , 'green')
    text8 = smallfont.render(f'Homes   in SIM: {len(homes.sprites())}' , True , 'green')
    edit_ = smallfont.render(f'' , True , 'green')

    clone_cells(cells)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if len(cells.sprites()) >= 1:
                print(f"Cells in SIM: {len(cells.sprites())}")
                print(f"Total SIM time in seconds:{sim_time}")
                print(f"Cell[0] genes:{[i.genes for i in cells.sprites()]}")
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                threats.add(Threat(pos=pygame.mouse.get_pos(), size=(40,40)))
                homes.add(Home(pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]+50), size=(40,40)))
    if buttons.sprites()[3].edit:
        edit_ = smallfont.render(f'Editing Env... left click to remove Home or Threat' , True , 'green')
        

    cells.update(dt, sim_time) 
    buttons.update()
    threats.update()
    homes.update()
    screen.fill((255, 255, 255))
    cells.draw(screen)  # Draws all sprites to the given Surface.
    buttons.draw(screen)
    pygame.draw.rect(screen, (0, 0, 0), (20, 540, 100, 40),2)
    pygame.draw.rect(screen, (0, 0, 0), (20, 590, 100, 40),2)
    pygame.draw.rect(screen, (0, 0, 0), (20, 640, 100, 40),2)
    pygame.draw.rect(screen, (0, 0, 0), (130, 540, 100, 40),2)
    threats.draw(screen)
    homes.draw(screen)
    screen.blit(text  , (25,545))
    screen.blit(text2 , (25,595))
    screen.blit(text3 , (25,645))
    screen.blit(text4 , (135,545))
    screen.blit(text5 , (135,595))
    screen.blit(text6 , (135,645))
    screen.blit(text7 , (300,545))
    screen.blit(text8 , (300,595))
    screen.blit(edit_ , (25,500))
    pygame.draw.rect(screen, (0, 0, 0), (0, 520, 720, 2))
    pygame.display.update()
