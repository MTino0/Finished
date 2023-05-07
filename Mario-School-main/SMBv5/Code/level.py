import pygame
from support import import_csv_layout, import_cut_graphics
from settings import tile_size, screen_width, screen_height
from tiles import Tile, StaticTile, AnimatedTile, Coin
from player import Player
from enemy import Enemy
from particles import ParticleEffect

class Level:
    def __init__(self,level_data,surface):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # player
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)
        
        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        
        # water setup
        water_layout = import_csv_layout(level_data['water'])
        self.water_sprites = self.create_tile_group(water_layout, 'water')
        
        # blocks setup
        blocks_layout = import_csv_layout(level_data['blocks'])
        self.blocks_sprites = self.create_tile_group(blocks_layout, 'blocks')
        
        # background
        background_layout = import_csv_layout(level_data['background'])
        self.background_sprites = self.create_tile_group(background_layout, 'background')
        
        # house
        house_layout = import_csv_layout(level_data['house'])
        self.house_sprites = self.create_tile_group(house_layout, 'house')
        
        # flag
        flag_layout = import_csv_layout(level_data['flag'])
        self.flag_sprites = self.create_tile_group(flag_layout, 'flag')
        
        # flag_pole
        flag_pole_layout = import_csv_layout(level_data['flag_pole'])
        self.flag_pole_sprites = self.create_tile_group(flag_pole_layout, 'flag_pole')
        
        # money
        money_layout = import_csv_layout(level_data['money'])
        self.coin_sprites = self.create_tile_group(money_layout, 'money')
        
        # enemies
        enemies_layout = import_csv_layout(level_data['enemies'])
        self.enemies_sprites = self.create_tile_group(enemies_layout, 'enemies')
               
        # constraints
        constraints_layout = import_csv_layout(level_data['constraints'])
        self.constraints_sprites = self.create_tile_group(constraints_layout, 'constraints')
        
    def create_tile_group(self,layout,type):
        sprite_group = pygame.sprite.Group()
        
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size
                    
                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'blocks':
                        question_block_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/terrain/terrain_tiles.png')
                        tile_surface = question_block_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                        
                    if type == 'house':
                        house_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/house/House.png')
                        tile_surface = house_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'background':
                        background_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/background/background.png')
                        tile_surface = background_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'flag':
                        flag_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/flag/Flag.png')
                        tile_surface = flag_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'flag_pole':
                        flag_pole_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/flag/flag.png')
                        tile_surface = flag_pole_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'money':
                        money_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/coin/coin.png')
                        tile_surface = money_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'water':
                        water_tile_list = import_cut_graphics('Mario-School-main/SMBv5/Graphics/water/water.png')
                        tile_surface = water_tile_list[int(val)]
                        sprite = StaticTile(tile_size,x,y,tile_surface)
                        
                    if type == 'enemies':
                        sprite = Enemy(tile_size,x,y)
                        
                    if type == 'constraints':
                        sprite = Tile(tile_size,x,y)
                        
                    sprite_group.add(sprite)
                    
        return sprite_group
    
    def player_setup(self,layout): # Player image
        for row_index, row in enumerate(layout):
            for col_index,val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player((x,y))
                    self.player.add(sprite)
                if val == '1':
                    spawn_surface = pygame.image.load('Mario-School-main/SMBv5/Graphics/player/player.png').convert_alpha()
                    sprite = StaticTile(tile_size,x,y,spawn_surface)
                    self.goal.add(sprite)
                    
    def enemy_collision_reverse(self):
        for enemy in self.enemies_sprites.sprites():
            if pygame.sprite.spritecollide(enemy,self.constraints_sprites,False):
                enemy.reverse()   
                
    def horizontal_movement_collision(self): # Collision with side of sprites
        player = self.player.sprite    
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites() + self.blocks_sprites.sprites()
        
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right
                    
    def vertical_movement_collision(self): # Collision with top and bottom of sprites
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites() + self.blocks_sprites.sprites()
        
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0  
                    player.on_ground = True   
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0  
                    player.on_ceiling = True
                    
            if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
                player.on_ground = False
       
    def scroll_x(self): # Camera movement
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        
        if player_x < screen_width/4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width/2) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed= 8
            
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False    
            
    def check_coin_collisions(self):
        coin_collisions = pygame.sprite.spritecollide(self.player.sprite,self.coin_sprites,False)
        
        if coin_collisions:
            for coin in coin_collisions:
                coin_centre = coin.rect.centery
                coin_top = coin.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if coin_top < player_bottom < coin_centre and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -15
                    coin.kill()
                    

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite,self.enemies_sprites,False)
        
        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_centre = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if enemy_top < player_bottom < enemy_centre and self.player.sprite.direction.y >= 0:
                    self.player.sprite.direction.y = -15
                    enemy.kill()
                else:
                    self.player.sprite.get.damage()
                    
    def check_water_collisions(self):
        water_collisions = pygame.sprite.spritecollide(self.player.sprite,self.water_sprites,False)
        
        if water_collisions:
            for water in water_collisions:
                water_centre = water.rect.centery
                water_top = water.rect.top
                player_bottom = self.player.rect.bottom
                if water_top < player_bottom < water_centre and self.player.sprite.direction.y >= 0:
                    water.kill()
    
    def run(self):
        # Run the entire game / level

        # Update and draw terrain sprites
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        
        # Update and draw water sprites
        self.water_sprites.update(self.world_shift)
        self.water_sprites.draw(self.display_surface)
        self.water_sprites.draw(self.display_surface)

        # Update and draw block sprites
        self.blocks_sprites.update(self.world_shift)
        self.blocks_sprites.draw(self.display_surface)
        
        # Update and draw background sprites
        self.background_sprites.update(self.world_shift)
        self.background_sprites.draw(self.display_surface)

        # Update and draw house sprites
        self.house_sprites.update(self.world_shift)
        self.house_sprites.draw(self.display_surface)

        # Update and draw flag_pole sprites
        self.flag_pole_sprites.update(self.world_shift)
        self.flag_pole_sprites.draw(self.display_surface)

        # Update and draw flag sprites
        self.flag_sprites.update(self.world_shift)
        self.flag_sprites.draw(self.display_surface)
        
        # Update and draw money
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)
        
        # Update and draw enemies
        self.enemies_sprites.update(self.world_shift)
        self.constraints_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemies_sprites.draw(self.display_surface)

        # player sprites
        self.player.update()
        self.horizontal_movement_collision()
        
        self.get_player_on_ground()
        self.vertical_movement_collision()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        self.check_coin_collisions()
        self.check_enemy_collisions()
        self.check_water_collisions()