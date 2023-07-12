import pygame, random, time

#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

class Text:
    def __init__(self, x, y, text: str, visible = True) -> None:
        self.x = x
        self.y = y
        self.text = text
        self.font = pygame.font.SysFont("Calibri", 36)
        self.visible = visible

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        if self.visible:
            self.rendered = self.font.render(self.text, True, "white")
            screen.blit(self.rendered, (self.x, self.y))

#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

class Explosion:
    def __init__(self, x, y, sprite: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.sprite = sprite

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

class Collectible:
    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.sprite = sprite
        self.angle = 0

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface, dt) -> None:
        self.angle = self.angle + 5 * dt
        screen.blit(pygame.transform.rotate(self.sprite, self.angle), (self.x, self.y))

    def randomise_position(self) -> None:
        self.x = random.randint(50,1250)
        self.y = random.randint(50,670)
        self.rect = self.sprite.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.angle = random.randint(0, 360)

#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

class Player:
    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        self.x = x
        self.y = y
        self.sprite = sprite
        self.velocity = 200
        self.direction = "up"
        self.angle = 0
        self.moving = False
        self.rect = self.sprite.get_rect()

    def update(self, dt) -> None:
        if self.moving:
            self.move(dt)
        self.rect.x = self.x
        self.rect.y = self.y

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, (self.x, self.y))

    def set_angle(self, new_angle: int) -> None:
        rotation = self.angle - new_angle
        self.angle = new_angle
        self.sprite = pygame.transform.rotate(self.sprite, rotation)

    def move(self, dt) -> None:
        match self.direction:
            case "up":
                self.y -= self.velocity * dt
            case "down":
                self.y += self.velocity * dt
            case "left":
                self.x -= self.velocity * dt
            case "right":
                self.x += self.velocity * dt
        pass

        self.x = min(1280 - self.sprite.get_width(), self.x) 
        self.x = max(0, self.x)
        self.y = min(720 - self.sprite.get_height(), self.y) 
        self.y = max(0, self.y)

#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------

class Game:
    def __init__(self) -> None: #"self" refers to class 'Game'
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((1280, 720))

        self.score = 0

        self.sprites = self.load_sprites()

        self.player = Player(640,360, self.sprites["spaceship"])

        self.collectible = Collectible(100,100, self.sprites["astronaut"])
        self.collectible.randomise_position()

        self.explosion = Explosion(-50, -50, self.sprites["explosion"])

        self.text = Text(10, 10, "", True)
        self.text.visible = True
        self.death_text = Text(600, 350, "You died!", False)

        self.inBounds = True

        self.keybinds = {
            pygame.K_UP: ("up", 0),
            pygame.K_DOWN: ("down", 180),
            pygame.K_LEFT: ("left", 270),
            pygame.K_RIGHT: ("right", 90),
        }

        self.dt = time.time()

        pygame.mixer_music.load("./sfx/background.wav")
        pygame.mixer_music.set_volume(0.3)
        pygame.mixer_music.play(-1)

        self.ship_engine = pygame.mixer.Sound("./sfx/ship.wav")
        self.ship_engine.set_volume(0.10)
        self.ship_engine.play(-1)

        self.collect_sound = pygame.mixer.Sound("./sfx/collect.mp3")
        self.collect_sound.set_volume(0.07)

        self.ship_change_direction = pygame.mixer.Sound("./sfx/ship_change-direction.mp3")
        self.ship_change_direction.set_volume(0.03)

        self.explosion_sound = pygame.mixer.Sound("./sfx/explosion.mp3")
        self.explosion_sound.set_volume(0.1)

    def poll_events(self) -> None: 
        if self.inBounds:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN and event.key in self.keybinds:
                    self.player.direction = self.keybinds[event.key][0]
                    self.player.set_angle(self.keybinds[event.key][1])
                    self.player.moving = True
                    self.ship_change_direction.play(0)

    def update(self) -> None:
        now = time.time()
        self.dt = now - self.previous_time
        self.previous_time = now

        if self.death_text.visible:
            time.sleep(2)
            self.__init__()

        self.inBounds = self.player.x > 1 and self.player.y > 1 and self.player.x < 1279 - self.player.sprite.get_width() and self.player.y < 719 - self.player.sprite.get_height()
        if self.inBounds:
            self.player.update(self.dt)
            self.collectible.update()

            if self.player.rect.colliderect(self.collectible.rect):
                self.collectible.randomise_position()
                self.player.velocity += 30
                self.score += 100
                self.collect_sound.play(0)

        self.text.text = "Score: " + str(self.score)
        self.text.update()

        if not self.inBounds:
            self.explosion.x = self.player.x
            self.explosion.y = self.player.y
            self.death_text.visible = True
            self.explosion_sound.play(0)
            self.player.moving = False

        

    def render(self) -> None:
        self.screen.fill("black")
        self.screen.blit(self.sprites["background"], (0,0))

        self.collectible.render(self.screen, self.dt)
        self.player.render(self.screen)

        self.text.render(self.screen)

        self.death_text.render(self.screen)

        self.explosion.render(self.screen)

        pygame.display.update()

    def run(self) -> None:
        self.previous_time = time.time()
        while self.running:
            self.poll_events()
            self.update()
            self.render()
        pygame.quit()

    def load_sprites(self) -> dict:
        sprites = {}

        sprites["spaceship"] = pygame.transform.scale(pygame.image.load("gfx/ship.png").convert_alpha(), (50, 50)) #convert_alpha necessary for any images with transparency
        sprites["astronaut"] = pygame.transform.scale(pygame.image.load("gfx/astronaut.png").convert_alpha(), (25, 25))
        sprites["background"] = pygame.image.load("gfx/background.png")
        sprites["explosion"] = pygame.image.load("gfx/explosion.png").convert_alpha()

        # Downscale
        # sprites["spaceship"] = pygame.transform.scale(sprites["spaceship"], (100,100)) #part of tutorial to demonstrate downsizing graphics- my png is much smaller than his

        return sprites
        


        
game = Game()
game.run()
