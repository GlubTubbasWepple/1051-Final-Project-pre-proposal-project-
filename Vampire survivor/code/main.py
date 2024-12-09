from settings import *
from player import Player
from sprites import *
from random import uniform, choice, randint
from pytmx.util_pygame import load_pygame
from groups import AllSprites
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
class Game:
    def __init__(self):
        #setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('monkey')
        self.clock = pygame.time.Clock()
        self.running = True
 
        #groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.font = pygame.font.Font(join('images', 'Oxanium-bold.ttf'), 40)
        
        #gun timer
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100

        #hp
        self.current_health = 100
        self.maximum_health = 500
        self.health_bar_len = 200
        self.health_ratio = self.maximum_health / self.health_bar_len

        #enemy timers
        self.enemy_evnt = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_evnt, 300)
        self.spawn_positions = []

        #audio
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        #self.shoot_sound.set_volume(uniform(0.1,0.8))
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.impact_sound.set_volume(0.2)
        self.music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music.set_volume(0.2)
        self.music.play(loops = -1)

       
        #setup
        self.setup()
        self.load_images()
    def update(self):
        self.basic_health()
    def get_dmg(self, amount):
        if self.current_health > 0:
            self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
    def get_health(self, amount):
        if self.current_health < self.maximum_health:
            self.current_health += amount
        if self.current_health >= self.maximum_health:
            self.current_health = self.maximum_health

    def basic_health(self):
        pygame.draw.rect(self.display_surface , (255, 0 ,0 ), (10,10, self.current_health/self.health_ratio, 25))

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()

        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            self.shoot_sound.set_volume(uniform(0.232,0.5))
            
            pos = self.gun.rect.center + self.gun.player_direction * 48
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
    
    def gun_timer(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.shoot_time >= self.gun_cooldown:
            self.can_shoot = True
    
    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))
        
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x *TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites) 
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collisions(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprite = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprite:
                    for sprite in collision_sprite:
                        self.impact_sound.play()
                        sprite.destroy()
                                          
    def player_collisions(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False
    def display_score(self):
        current_time = pygame.time.get_ticks() //1000
        text_surf = self.font.render(str(current_time), True, (200, 200, 240))
        text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT -50))
        screen.blit(text_surf, text_rect)
        pygame.draw.rect(screen,(200, 200, 240), text_rect.inflate(20,10).move(0,-6), 5, 10)
    def run(self):
        while self.running:
            #delta time

            dt = self.clock.tick(144) / 1000

            #event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_evnt:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)

            # update
            self.basic_health()
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collisions()
            self.player_collisions()

            #draw
            self.display_surface.fill("black")
            self.all_sprites.draw(self.player.rect.center)
            self.display_score()
            pygame.display.update()
            

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()

