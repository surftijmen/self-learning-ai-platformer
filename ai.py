import pygame
import os
import neat
import time
import pickle
from threading import Timer
pygame.font.init()

# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 150, 150)
DARK_GREEN = (255,10,0)
YELLOW = (200, 200, 0, 50)
GRAY = (35, 35, 35)
STAT_FONT = pygame.font.SysFont("comicsans", 50)
GEN = 0
# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
done = False

SPEED = 1


class Player(pygame.sprite.Sprite):
    """ This class represents the bar at the bottom that the player
        controls. """

    # -- Methods
    def __init__(self, position, level):
        """ Constructor function """

        # Call the parent's constructor
        super(Player, self).__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        width = 50
        height = 50
        self.image = pygame.Surface([width, height])
        self.image.fill(DARK_GREEN)

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()
        # Set speed vector of player
        self.position = position
        self.change_x = 0
        self.change_y = 0
        self.closest_block = [9990,99990]
        self.block_tops = []
        self.closest_block_distance = 1500
        self.listMade = False


        # List of sprites we can bump against
        self.level = level

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x
        if not self.listMade:
            for i in range(len(self.level.platform_list)):
                self.block_tops.append(0)
            self.listMade = True

        if (self.change_x != 0 or self.change_y != 0):
            for i, block in enumerate(self.level.platform_list):
                if block.rect.x > self.rect.x:
                    self.block_tops[i] = block.rect.top
                    self.closest_block_distance = min(self.block_tops, key=lambda x: abs(x - self.rect.bottom))

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)

        '''  for block in self.level.platform_list:
                    list.append((block.rect.top + block.rect.bottom) / 2)

                 list[min(range(len(list)), key = lambda i: abs(list[i]-self.rect.bottom)'''

        self.closest_block = [1500, 0]
        for block in self.level.platform_list:
            if (block.rect.x > self.rect.x):
                if (block.rect.x - self.rect.x) < self.closest_block[0]:
                    self.closest_block[0] = block.rect.x
        for block in block_hit_list:

            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = .4 * SPEED
        else:
            self.change_y += .4  * SPEED

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down
        # 1 when working with a platform moving down.
        self.rect.y += 2 * SPEED
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2 * SPEED

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10 * SPEED

    # Player-controlled movement:
    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0 * SPEED

    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = 5 * SPEED

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 10 * SPEED

class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, width, height):
        """ Platform constructor . Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this
            code. """
        super(Platform, self).__init__()

        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()


class Level(object):
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        # Background image
        self.background = None

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen, gen, times, FPS, players):
        """ Draw everything on this level. """

        # Draw the background
        screen.fill(GRAY)

        score_label = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
        screen.blit(score_label, (10, 10))

        score_label = STAT_FONT.render("Time: " + str(times), 1, (255, 255, 255))
        screen.blit(score_label, (10, 50))

        score_label = STAT_FONT.render("FPS: " + str(FPS), 1, (255, 255, 255))
        screen.blit(score_label, (10, 90))

        # draw line to last touched block
        for x, player in enumerate(players):
            if (player.closest_block != [0,0]):
                pass

            pygame.draw.line(screen, (180, 130, 200),
                             (player.rect.x + player.image.get_width() / 2,
                              player.rect.y + player.image.get_height() / 2),
                             (player.closest_block[0], player.rect.y + player.rect.height / 2), 3)
       #         pygame.draw.circle(screen, (255, 255, 0), (player.rect.x, player.rect.y), player.closest_block_distance)

            #draw line to finish
            pygame.draw.line(screen, (10, 10, 200),
                             (player.rect.x + player.image.get_width() / 2,
                              player.rect.y + player.image.get_height() / 2),
                             (1500, player.rect.y + player.rect.height / 2), 2)

            # draw line to bottom
            pygame.draw.line(screen, (10, 100, 20),
                             (player.rect.x + player.image.get_width() / 2,
                              player.rect.y + player.image.get_height() / 2),
                             (player.rect.x + player.rect.width / 2, 600), 2)

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)


# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        # Array with width, height, x, and y of platform
        level = [[50, 100, 200, 500],

                 [50, 150, 700, 450],
                 [50, 150, 1100, 450]
                 ]



        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

def main(genomes, config):
    timer = 8
    global GEN
    global done
    GEN += 1


    nets = []
    ge = []
    players = []
    current_level = Level_01(Player)

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(340, current_level))
        g.fitness = 0
        ge.append(g)

    pygame.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("pws ai-1 Tijmen & Floris")

    # Create the player
    # player = Player(340,current_level)

    # Create all the levels
    # level_list.append( Level_01(player) )

    # Set the current level

    active_sprite_list = pygame.sprite.Group()

    for player in players:
        player.rect.y = SCREEN_HEIGHT - player.rect.height
        active_sprite_list.add(player)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    clock.tick(60)
    # -------- Main Program Loop -----------
    while not done:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                done = True
                replay_genome(os.path.join(local_dir, "config-feedforward.txt"))
                pygame.quit()
                quit()

            for x, player in enumerate(players):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        player.go_left()
                    if event.key == pygame.K_d:
                        player.go_right()
                    if event.key == pygame.K_SPACE:
                        player.jump()


                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a and player.change_x < 0:
                        player.stop()
                    if event.key == pygame.K_d and player.change_x > 0:
                        player.stop()

        #make a timer
        if (int(clock.get_fps()) != 0):
            timer -= 1 /int(clock.get_fps())

           # for x, player in enumerate(players):

                #if (player.rect.y > 200 + 50 * timer):
                 #   ge[x].fitness -= 1
                  #  nets.pop(players.index(player))
                  #  ge.pop(players.index(player))
                  # players.pop(players.index(player))


            if (timer <= 0):

                Done = True
                break

        #set player fitness
        for x, player in enumerate(players):
            xtra = 0
            if x > 1100 and timer > 8:
                xtra = 5
            ge[x].fitness = (player.rect.x / 100)

            output = nets[x].activate((player.rect.y/ 600, player.rect.x/1500, player.closest_block[0]/300))

            if (ge[x].fitness > 1):
                player.image.fill((255 - (255 / (1 + ge[x].fitness * 5)),10 * ge[x].fitness, ge[x].fitness))

            if (output[0] > 0):
                player.stop()
            if output[1] > 0.5:
                player.jump()
            if output[0] <= 0:
                player.go_right()


        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # If the player gets near the right side, shift the world left (-x)
        for player in players:
            if player.rect.right > SCREEN_WIDTH:
                player.rect.right = SCREEN_WIDTH

            # If the player gets near the left side, shift the world right (+x)
            if player.rect.left < 0:
                player.rect.left = 0

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen, GEN, int(timer * 100) / 100, int(clock.get_fps()),players)
        active_sprite_list.draw(screen)

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
def replay_genome(config_path, genome_path="winner.pkl"):
    # Load requried NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    main(genomes, config)

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 150)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()
    replay_genome(config_path)



if __name__ == "__main__":
    # main()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
