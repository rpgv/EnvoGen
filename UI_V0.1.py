from numpy.random.mtrand import random
import pygame
from numpy.random import choice
import random

# Initiate PyGame and set up the clock
pygame.init()
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
# Define the maximum number of sprites (cells) in the simulation
MAX_SPRITES = 500

# Maps attraction code to a movement vector (direction in screen)
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

def color_generator(genes):
    """Genes are mapped to RGB values
        Parameters:
            genes (list): List of genes
        Returns:
            tuple: RGB values
    """
    r = (((sum([i for i in genes[:2]]) - 0) * 255) / 24) 
    g = (((sum([i for i in genes[2:5]]) - 0) * 255) / 24) 
    b = (((sum([i for i in genes[5:]]) - 0) * 255) / 24) 
    return r,g,b

def enforce_limit(int, limit):
    """Enforces limits on gene values
        Parameters:
            int (int): Integer to be limited
            limit (int): Limit to be enforced
        Returns:
            int: Limited integer
    """
    if int > limit:
        return limit
    elif int < 1:
        return 1
    else:
        return int

def clone_cells(sprite_g):
    """
    Clones cells
        Parameters:
            sprite_g (pygame.sprite.Group): Group of cells to clone
        Returns:
            None
    """
    for i in sprite_g.sprites():
        mutations = i.mutate()
        # print(f"Mutations: {mutations}")
        if i.reprod == 1:
            sprite_g.add(Cell(pos=(i.pos.x-10, i.pos.y-10), genes=mutations),
            Cell(pos=(i.pos.x, i.pos.y), genes=mutations))


def danger_zone(pos, size):
    """ 
    Parameters:
        pos (tuple): Position of the sprite
        size (tuple): Size of the sprite
    Returns:
        tuple: Collision zone of the sprite
    """
    return pos[0]-10,pos[0]+size[0]+10,pos[1]-10,pos[1]+size[1]+10


def collider(pos, s_group):
    """
    Checks if a position is within the collision zone of any sprite in a group
        Parameters:
            pos (tuple): Position of the sprite
            s_group (pygame.sprite.Group): Group of sprites to check for collision
        Returns:
            bool: True if the position is within the collision zone of any sprite in the group, False otherwise
    """
    collides = False
    for i in s_group:
        x1,x2,y1,y2 = danger_zone(i.pos, i.size)
        if pos[0] >= x1 and pos[0] <= x2 and pos[1] >= y1 and pos[1] <= y2:
            collides = True
    return collides

def mutation(genes):
    """
    Generates mutations for a cell based on their own mutation factor (genes[4])
        Parameters:
            genes (list): List of genes
        Returns:
            list: List of mutated genes
    """
    factor = genes[4]*0.10
    n_genes = []
    for g in genes[:-1]: 
        n_genes.append(enforce_limit(int(g+(choice([-1,0,1], p=[(1-factor)/2,factor,(1-factor)/2]))), 8))
    n_genes.append(enforce_limit(int(genes[-1]+(choice([0,1], p=[1-factor,factor]))), 8))
    return n_genes

def staying_factor(genes):
    """
    Calculates the staying factor of a cell based on its staying gene (genes[-2])
    Staying factor determines cell tendency to "stick" to a surface
        Parameters:
            genes (list): List of genes
        Returns:
            tuple: Staying factor
    """
    return ((genes[-2]/10)/2, (genes[-2]/10)/2, 1-(genes[-2]/10))

def add_env_object(buttons):
    """
    Defines interface buttons behavior when clicked
        Parameters:
            buttons (pygame.sprite.Group): Group of buttons
        Returns:
            None
    """
    if buttons.sprites()[0].edit:
        buttons.sprites()[1].edit = False
        buttons.sprites()[2].edit = False
        buttons.sprites()[3].edit = False
        cells.add(Cell(pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]), genes=[random.randint(1,5) for i in range(8)]))
    elif buttons.sprites()[1].edit:
        buttons.sprites()[0].edit = False
        buttons.sprites()[2].edit = False
        buttons.sprites()[3].edit = False
        threats.add(Threat(pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])))
    elif buttons.sprites()[2].edit:
        buttons.sprites()[0].edit = False
        buttons.sprites()[1].edit = False
        buttons.sprites()[3].edit = False
        nests.add(Nests(pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])))
    elif buttons.sprites()[3].edit:
        buttons.sprites()[0].edit = False
        buttons.sprites()[1].edit = False
        buttons.sprites()[2].edit = False
        walls.add(Walls(pos=(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])))

def base_button_border(screen, buttons):
    """
    Draws the border of the buttons - highlight they were clicked or not
        Parameters:
            screen (pygame.Surface): Screen to draw on
            buttons (pygame.sprite.Group): Group of buttons
        Returns:
            None
    """
    for i in buttons:
        if i.edit == False:
            pygame.draw.rect(screen, (0, 0, 0), i.rect,2)
        else:
            pygame.draw.rect(screen, (0, 0, 0), i.rect,4)

# Genetic code reference: [size, life_span, reprod_rate, predator, mutation_factor, speed, staying_factor, attraction]
class Cell(pygame.sprite.Sprite):
    """
    Represents a single cell instance in the simulation
        Parameters:
            pos (tuple): Position of the cell
            genes (list): List of genes
        Returns:
            None
    """
    def __init__(self, pos, genes=[1,1,1,0,1,1,1,1]):
        super(Cell, self).__init__()
        image = pygame.Surface((5+genes[0], 5+genes[0]))
        r,g,b = color_generator(genes)
        print(f"Genes: [{genes}] to RGB: [{r},{g},{b}]")
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
        self.internal_clock = pygame.time.get_ticks()/1000
        self.reprod = 0
        self.genes = genes
        self.reprod_season = (genes[2]*self.genes[1])-1

    def mutate(self):
        # [size (0), life_span (1), reprod_rate (2), predator (3), mutation_factor (4), speed (5), staying_factor (6), attraction (7)]
        return mutation(self.genes)

    def update(self, dt, sim_time):
        """
        Update cell position and check for collisions
            Parameters:
                dt (float): Delta time
                sim_time (float): Simulation time
            Returns:
                None
        """
        self.pos.x += self.dir.x * attraction_map[self.genes[7]][0]* 0.1 * dt + ((self.genes[5]+0.1)/100)
        self.pos.y += self.dir.y * attraction_map[self.genes[7]][1]* 0.1 * dt + ((self.genes[5]+0.1)/100)
        self.rect.topleft = self.pos
        
        if collider(self.pos, threats):
            print("Collision")
            self.kill()
        elif collider(self.pos, nests):
            n_genes = [i for i in self.genes]
            n_genes[2] = self.genes[2]*0.9
            n_genes[4] = self.genes[4]*0.9

            if len(cells.sprites()) < (MAX_SPRITES/10):
                self.kill()
                cells.add(Cell(pos=(self.pos.x-10, self.pos.y-10), genes=n_genes), Cell(pos=(self.pos.x, self.pos.y), genes=n_genes))
        
        elif collider(self.pos, walls):
            self.dir.x *= -1 * choice([-1,0,1],p=staying_factor(self.genes))
            self.dir.y *= -1 * choice([-1,0,1],p=staying_factor(self.genes))
        
        if self.rect.left <= 0:
            self.rect.left = 0
            self.pos.x = 0
            self.dir.x *= -1 * choice([-1,0,1],p=staying_factor(self.genes))
        elif self.rect.right >= 720:
            self.rect.right = 720
            self.pos.x = 720 - self.rect.width
            self.dir.x *= -1 * choice([-1,0,1],p=staying_factor(self.genes))
        if self.rect.top <= 0:
            self.rect.top = 0
            self.pos.y = 0
            self.dir.y *= -1 * choice([-1,0,1],p=staying_factor(self.genes))
        elif self.rect.bottom >= 520:
            self.rect.bottom = 520
            self.pos.y = 520 - self.rect.height
            self.dir.y *= -1 * choice([-1,0,1],p=staying_factor(self.genes))
        

        if self.genes[1]*10 <= sim_time-(self.internal_clock-0.05) and len(cells.sprites()) < MAX_SPRITES:
            self.reprod += 1 

        if self.genes[1]*10 <= sim_time-self.internal_clock:
            self.kill()

class Button(pygame.sprite.Sprite):
    """
    Represents a single button instance in the simulation
        Parameters:
            pos (tuple): Position of the button
            size (tuple): Size of the button
            image (pygame.Surface): Image of the button
            bid (int): Button ID
        Returns:
            None
    """
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
        if self.rect.collidepoint(mouse_pos) and mouse_clicked and not self.pressed and not self.edit:
            for i in buttons.sprites():
                if i.bid != self.bid:
                    i.edit = False
            self.pressed = True
            self.edit = True
            print(self.pressed, self.edit)
        elif self.rect.collidepoint(mouse_pos) and mouse_clicked and not self.pressed and self.edit:
            self.pressed = True
            self.edit = False
            print(self.pressed, self.edit)
        if not mouse_clicked:
            self.pressed = False
            

class Threat(pygame.sprite.Sprite):
    """
    Represents a single threat instance in the simulation - threats kill cells on contact
        Parameters:
            pos (tuple): Position of the threat
            size (tuple): Size of the threat
            bid (int): Threat ID
        Returns:
            None
    """
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
        if self.rect.collidepoint(*mouse_pos) and mouse_clicked and buttons.sprites()[4].edit:
            self.kill()

class Nests(pygame.sprite.Sprite):
    """
    Represents a single nest instance in the simulation - nests are resets cell lifecycle and triggers reproduction (if less than 10% of max sprites)
        Parameters:
            pos (tuple): Position of the nest
            size (tuple): Size of the nest
            bid (int): Nest ID
        Returns:
            None
    """
    def __init__(self, pos, size=(32, 32),bid=0):
        super(Nests, self).__init__()
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
        if self.rect.collidepoint(*mouse_pos) and mouse_clicked and buttons.sprites()[4].edit:
            self.kill()

class Walls(pygame.sprite.Sprite):
    """
    Represents a single wall instance in the simulation - walls are obstacles for cells
        Parameters:
            pos (tuple): Position of the wall
            size (tuple): Size of the wall
            bid (int): Wall ID
        Returns:
            None
    """
    def __init__(self, pos, size=(32, 32),bid=0):
        super(Walls, self).__init__()
        image = pygame.Surface(size)
        image.fill((0, 0, 0))
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
        if self.rect.collidepoint(*mouse_pos) and mouse_clicked and buttons.sprites()[4].edit:
            self.kill()

# --- Sprite Groups ---
cells = pygame.sprite.Group()

# --- Button Images ---
image = pygame.Surface((100, 40))
image.fill((0, 173, 76))
image2 = pygame.Surface((100, 40))
image2.fill((200,20,20))
image3 = pygame.Surface((100, 40))
image3.fill((20,20,200))
image4 = pygame.Surface((100, 40))
image4.fill((105,105,105))
image5 = pygame.Surface((100, 40))
image5.fill((200,70,70))
buttons = pygame.sprite.Group()
buttons.add(
    Button(pos=(20, 535), image=image,bid=0), 
    Button(pos=(20, 580), image=image2,bid=1),
    Button(pos=(20, 625), image=image3,bid=2),
    Button(pos=(20, 670), image=image4,bid=3),
    Button(pos=(125, 535), image=image5,bid=4)
)        

# --- Threat Group ---
threats = pygame.sprite.Group()
threats.add(
    Threat(pos=(0, 0), size=(40,40)),
    Threat(pos=(680, 0), size=(40,40)),
    Threat(pos=(0, 480), size=(40,40)),
    Threat(pos=(680, 480), size=(40,40)),
)

# --- Nest Group ---
nests = pygame.sprite.Group()
nests.add(
    Nests(pos= (680, 260), size=(40,40)),
    Nests(pos=(0, 260), size=(40,40)),
)

# --- Wall Group ---
walls = pygame.sprite.Group()
walls.add(
    Walls(pos=(360, 260), size=(40,40))
)

# --- Text Rendering ---
smallfont = pygame.font.SysFont('Corbel',25)

# --- Main simulation loop ---
while True:
    dt = clock.tick(60)
    sim_time = pygame.time.get_ticks()/1000
    
    # Define Metrics Text
    text1 = smallfont.render(f'Cells in   SIM: {len(cells.sprites())}' , True , 'green')
    text2 = smallfont.render(f'Total SIM time: {sim_time}' , True , 'green')
    text3 = smallfont.render(f'Threats in SIM: {len(threats.sprites())}' , True , 'green')
    text4 = smallfont.render(f'Nests   in SIM: {len(nests.sprites())}' , True , 'green')
    edit_ = smallfont.render(f'' , True , 'green')
    cell_ = smallfont.render(f'+ Cells' , True , 'green')
    threats_ = smallfont.render(f'+ Threats' , True , 'green')
    nests_ = smallfont.render(f'+ Nests' , True , 'green')
    walls_ = smallfont.render(f'+ Walls' , True , 'green')
    to_rmv = smallfont.render(f'Edit' , True , 'green')



    if len(cells.sprites()) < 1:
        g = [random.randint(1,4) for i in range(8)]
        cells.add(
            Cell(pos=(random.randint(0,720), random.randint(0,520)), genes=g)
        )
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
                add_env_object(buttons)
    if buttons.sprites()[-1].edit:
        edit_ = smallfont.render(f'Editing: right-click on object to remove' , True , 'green')
        

    cells.update(dt, sim_time) 
    buttons.update()
    threats.update()
    nests.update()
    walls.update()
    screen.fill((255, 255, 255))
    cells.draw(screen)  # Draws all sprites to the given Surface.
    buttons.draw(screen)
    base_button_border(screen, buttons)
    threats.draw(screen)
    nests.draw(screen)
    walls.draw(screen)
    screen.blit(cell_ ,   (25, 545))
    screen.blit(threats_ ,(25, 590))
    screen.blit(nests_ ,  (25, 635))
    screen.blit(walls_ ,  (25, 680))
    screen.blit(to_rmv ,  (130, 545))
    screen.blit(text1 ,   (135,595))
    screen.blit(text2 ,   (135,645))
    screen.blit(text3 ,   (300,545))
    screen.blit(text4 ,   (300,595))
    screen.blit(edit_ ,   (30,500))
    pygame.draw.rect(screen, (0, 0, 0), (0, 520, 720, 2))
    pygame.display.update()
