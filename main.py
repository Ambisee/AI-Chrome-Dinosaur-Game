import os
import sys
import time
import random
import argparse

import pygame
import neat

from config import WIDTH, HEIGHT, TERMINATION_SCORE
from objects import Dinosaur, Cactus, Ground

pygame.init()
gen = 0

def evaluate_genomes(genomes, config):
    global gen

    nets = []
    ge = []
    dinosaurs = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinosaurs.append(Dinosaur())
        g.fitness = 0
        ge.append(g)
    
    ground = Ground()
    cacti = [Cactus(WIDTH + random.randrange(0, 150), 350)]
    score = 0

    run = True
    FPS = 60
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    font = pygame.font.SysFont('comicsans', 25, False)
    gen_display = font.render(f'Generation : {gen}', False, (0, 0, 0))
    c_time = time.time()
    timer = 0

    def is_timer_even():
        return timer % 2 == 0

    while run:
        clock.tick(FPS)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        cactus_index = 0
        if len(dinosaurs) > 0:
            if len(cacti) > 1 and dinosaurs[0].x > cacti[0].x + cacti[0].width:
                cactus_index = 1
        else:
            run = False
            break

        
        fps_display = font.render(f'FPS : {int(clock.get_fps())}', False, (0, 0, 0))
        score_display = font.render(f'Score : {score}', False, (0, 0, 0))
        
        add_cactus = False
        for index, dino in enumerate(dinosaurs):
            if is_timer_even():
                dino.move()
                ge[index].fitness += 0.1

                output = nets[index].activate((dino.x + dino.width, cacti[cactus_index].x))
                if output[0] > 0.5:
                    dino.jump()

        for cactus in cacti:
            if is_timer_even():
                cactus.move()
            
            if cactus.x + cactus.width < 0:
                cacti.remove(cactus)
                continue
                
            for index, dino in enumerate(dinosaurs):
                if dino.x > cactus.x + cactus.width:
                    add_cactus |= True

                if cactus.check_collision(dino):
                    ge[index].fitness -= 1
                    dinosaurs.pop(index)
                    nets.pop(index)
                    ge.pop(index)
                
        if add_cactus and len(cacti) < 2:
            score += 1
            cacti.append(Cactus(WIDTH + random.randrange(0, 300), 350))
            for genome in ge:
                genome.fitness += 5

        if score >= TERMINATION_SCORE:
            run = False
            break

        screen.fill(pygame.Color(255, 255, 255))

        ground.draw(screen)
        for dino in dinosaurs:
            dino.draw(screen, is_timer_even)
        for cactus in cacti:
            cactus.draw(screen)
        
        screen.blit(fps_display, (0, 0))
        screen.blit(score_display, (0, fps_display.get_height()))
        screen.blit(gen_display, (WIDTH - gen_display.get_width(), 0))

        pygame.display.update()

        timer += 1
        c_time = time.time()
    
    gen += 1

def run(config_path):
    configuration = neat.config.Config(
        neat.genome.DefaultGenome, 
        neat.reproduction.DefaultReproduction,
        neat.species.DefaultSpeciesSet,
        neat.stagnation.DefaultStagnation,
        config_path
    )

    p = neat.population.Population(configuration)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.statistics.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(evaluate_genomes ,30)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the AI Chrome Dinosaur Simulator.', prog='main')
    parser.add_argument('-f', '--filename', action='store', metavar='file', 
        type=str, help='use the file that contains a pickled NEAT object')

    object_file = parser.parse_args().filename

    if object_file is not None:
        pass

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.ini')
    run(config_path)
    
    sys.exit()
