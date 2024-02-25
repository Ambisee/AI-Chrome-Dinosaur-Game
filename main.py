import os
import io
import sys
import random
import argparse
import logging
import pickle

import pygame
import neat

from config import WIDTH, HEIGHT, TERMINATION_SCORE
from objects import Dinosaur, Cactus, Ground

pygame.init()
gen = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT))


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

    cactus1_pos = random.randrange(0, 250)
    cactus2_pos = cactus1_pos + WIDTH // 2 + random.randrange(0, 250)
    cactus3_pos = cactus2_pos + WIDTH // 2 + random.randrange(0, 250)
    current_cactus_index = 0
    last_cactus_index = 2

    cacti = [
        Cactus(WIDTH + cactus1_pos, 350),
        Cactus(WIDTH + cactus2_pos, 350),
        Cactus(WIDTH + cactus3_pos, 350),
    ]

    score = 0

    run = True
    FPS = 60
    clock = pygame.time.Clock()

    MOVE_EVENT = pygame.USEREVENT + 1
    frames_per_update = 1.25
    move_interval = int(1000 / (FPS * 1 / frames_per_update))

    pygame.time.set_timer(MOVE_EVENT, move_interval)

    font = pygame.font.SysFont('comicsans', 25, False)
    gen_display = font.render(f'Generation : {gen}', False, (0, 0, 0))

    while run:
        move = False
        clock.tick(FPS)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

            if event.type == MOVE_EVENT:
                move = True
        
        if not move:
            continue

        fps_display = font.render(f'FPS : {int(clock.get_fps())}', False, (0, 0, 0))
        score_display = font.render(f'Score : {score}', False, (0, 0, 0))
        population_display = font.render(f'Population : {len(ge)}', False, (0, 0, 0))

        if len(dinosaurs) < 1:
            run = False
            break

        timer = pygame.time.get_ticks()
        for index, dino in enumerate(dinosaurs):
            dino.move()
            ge[index].fitness += 0.1

            output = nets[index].activate((dino.x + dino.width, cacti[current_cactus_index].x))
            if output[0] > 0.5:
                dino.jump()
                ge[index].fitness -= 1
            else:
                ge[index].fitness += 3

        for i, cactus in enumerate(cacti):
            cactus.move()
    
            if cactus.x + cactus.width < 0:
                cactus.x = WIDTH + cacti[last_cactus_index].x + random.randrange(0, 250)
                last_cactus_index = i
                continue
            
        for index, dino in enumerate(dinosaurs):
            if cacti[current_cactus_index].check_collision(dino):
                ge[index].fitness -= 5
                dinosaurs.pop(index)
                nets.pop(index)
                ge.pop(index)
                
        if len(dinosaurs) > 0 and cacti[current_cactus_index].x < dinosaurs[0].x + dinosaurs[0].width:
            score += 1
            current_cactus_index = (current_cactus_index + 1) % len(cacti)
            for genome in ge:
                genome.fitness += 5

        if score >= TERMINATION_SCORE:
            run = False
            break

        screen.fill(pygame.Color(255, 255, 255))

        ground.draw(screen)
        for dino in dinosaurs:
            dino.draw(screen, lambda: (timer % 1 == 0))
        for cactus in cacti:
            cactus.draw(screen)
        
        # Top left displays
        screen.blit(fps_display, (0, 0))
        screen.blit(score_display, (0, fps_display.get_height()))
        screen.blit(population_display, (0, fps_display.get_height() + score_display.get_height()))

        # Top right displays
        screen.blit(gen_display, (WIDTH - gen_display.get_width(), 0))

        pygame.display.update()
    
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

    winner = p.run(evaluate_genomes, 30)
    return winner


def play(model=None):
    ground = Ground()

    cactus1_pos = random.randrange(0, 250)
    cactus2_pos = cactus1_pos + WIDTH // 2 + random.randrange(0, 250)
    cactus3_pos = cactus2_pos + WIDTH // 2 + random.randrange(0, 250)
    current_cactus_index = 0
    last_cactus_index = 2

    dinosaur = Dinosaur()
    cacti = [
        Cactus(WIDTH + cactus1_pos, 350),
        Cactus(WIDTH + cactus2_pos, 350),
        Cactus(WIDTH + cactus3_pos, 350),
    ]

    score = 0

    run = True
    FPS = 60
    clock = pygame.time.Clock()

    # Fires an event signaling a frame to move all game objects
    MOVE_EVENT = pygame.USEREVENT + 1
    frames_per_update = 1.25
    move_interval = int(1000 / (FPS * 1 / frames_per_update))

    pygame.time.set_timer(MOVE_EVENT, move_interval)

    font = pygame.font.SysFont('comicsans', 25, False)
    gen_display = font.render(f'Generation : {gen}', False, (0, 0, 0))

    while run:
        move = False
        clock.tick(FPS)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and model is None:
                dinosaur.jump()

            if event.type == MOVE_EVENT:
                move = True
        
        if not move:
            continue

        fps_display = font.render(f'FPS : {int(clock.get_fps())}', False, (0, 0, 0))
        score_display = font.render(f'Score : {score}', False, (0, 0, 0))

        dinosaur.move()
        for i, cactus in enumerate(cacti):
            cactus.move()
    
            if cactus.x + cactus.width < 0:
                cactus.x = WIDTH // 2 + cacti[last_cactus_index].x + random.randrange(0, WIDTH)
                last_cactus_index = i
                continue
        
        if cacti[current_cactus_index].check_collision(dinosaur):
            run = False

        if model.activate((dinosaur.x + dinosaur.width, cacti[current_cactus_index].x))[0] > 0.5:
            dinosaur.jump()

        if cacti[current_cactus_index].x < dinosaur.x + dinosaur.width:
            score += 1
            current_cactus_index = (current_cactus_index + 1) % len(cacti)
        screen.fill(pygame.Color(255, 255, 255))

        ground.draw(screen)

        dinosaur.draw(screen, lambda: True)
        for cactus in cacti:
            if cactus.x < WIDTH:
                cactus.draw(screen)
        
        screen.blit(fps_display, (0, 0))
        screen.blit(score_display, (0, fps_display.get_height()))
        screen.blit(gen_display, (WIDTH - gen_display.get_width(), 0))

        pygame.display.update()


def main():
    parser = argparse.ArgumentParser(prog='main',
                                     description='Run the AI Chrome Dinosaur Simulator.'
                                     'Note: Only one flag can be specified when executing the program.')
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-P', '--play',
                       action='store_true',
                       help='run the program as a game')
    group.add_argument('-I', '--input',
                       action='store',
                       metavar='FILE',
                       type=argparse.FileType('rb'),
                       help='a Pickle object file as input that represents a DefaultGenome object to run the game')
    group.add_argument('-O', '--output',
                       action='store',
                       metavar='FILE',
                       type=str,
                       help='a path to where a winning NEAT genome will be saved to as a Pickle object file')

    args = parser.parse_args()
    
    play_mode: bool = args.play
    input_file: io.TextIOWrapper = args.input
    output_file: str = args.output

    # Get the path for a NEAT configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat_config.ini')

    logger = logging.Logger('AI Dinosaur Logger')
    logging.basicConfig(format='[%(levelname)s]: %(message)s')

    if play_mode:
        play()
        return
    
    if input_file:
        try:
            genome = pickle.load(input_file)
            configuration = neat.config.Config(
                neat.genome.DefaultGenome,
                neat.reproduction.DefaultReproduction,
                neat.species.DefaultSpeciesSet,
                neat.stagnation.DefaultStagnation,
                config_path
            )

            model = neat.nn.FeedForwardNetwork.create(genome, configuration)
            play(model)
        except FileNotFoundError as file_e:
            logger.error(str(file_e))
        finally:
            input_file.close()
        return

    output_model = run(config_path)
    
    try:
        output = open(output_file, 'wb')
        pickle.dump(output_model, output)
    except FileNotFoundError as file_e:
        logger.error(str(file_e))
    finally:
        output.close()

    return


if __name__ == '__main__':
    main()
