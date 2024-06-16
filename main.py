import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_w, K_a, K_SPACE, K_d, K_s, K_LSHIFT, K_q
# Project imports
from utils import Timer
from screen import Screen
from blocks import BlockManager


def run_game_loop(score, mngr, screen, timer, borders, surf):
    """Run one game loop logic."""
    state = "RUNNING"
    # Check for key presses
    for event in pygame.event.get():
        if event.type == QUIT:
            state = "SCORESCREEN"
            continue
        elif event.type != KEYDOWN:
            continue

        if event.key == K_ESCAPE:
            state = "SCORESCREEN"
            continue
        elif event.key == K_LSHIFT:
            if mngr.can_hold and not (mngr.held_piece is not None\
                    and mngr.held_piece.block_type == mngr.active_piece.block_type):
                mngr.hold_piece(screen)
        elif event.key == K_SPACE:
            timer.set_on()
            while mngr.active_piece.move(screen, "down"):
                pass
        elif event.key == K_w:
            mngr.active_piece.rotate(screen, "w")
        elif event.key == K_q:
            mngr.active_piece.rotate(screen, "e")
        elif event.key == K_a:
            mngr.active_piece.move(screen, "left")
        elif event.key == K_d:
            mngr.active_piece.move(screen, "right")

        if event.key in [K_w, K_a, K_d]:
            timer.delta()

    # Check for continuous movement
    keys = pygame.key.get_pressed()
    if (keys[K_a] and keys[K_d]) or not timer.can_soft_move:
        pass

    elif keys[K_a]:
        if mngr.active_piece.move(screen, "left"):
            timer.delta()

    elif keys[K_d]:
        if mngr.active_piece.move(screen, "right"):
            timer.delta()

    elif keys[K_s]:
        if mngr.active_piece.move(screen, "down"):
            timer.delta()

    # Natural move down
    if state == "RUNNING":
        if timer.can_move_down:
            has_moved_down = mngr.active_piece.move(screen, "down")
            if not has_moved_down:
                if any([block.j <= 0 for block in mngr.active_piece.blocks]):
                    return "SCORESCREEN", score, mngr, screen, timer
                mngr.remove_active(screen)

                # Check for line clear
                indices_to_clear, to_remove = [], []
                for j, line in enumerate(screen.checksum):
                    if line.checksum != 1023:
                        continue

                    indices_to_clear.append(j)
                    for block in mngr.inactive_blocks:
                        if block.j == j:
                            to_remove.append(block)

                # Update score
                score_table = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
                score += score_table[len(indices_to_clear)]

                # Clear lines
                for block in to_remove:
                    screen.checksum[block.j][block.i] = 0
                    mngr.inactive_blocks.remove(block)

                # Update blocks above cleared lines
                for j in indices_to_clear:
                    blocks_to_move = [block for block in mngr.inactive_blocks if block.j < j]
                    for block in blocks_to_move:
                        screen.checksum[block.j][block.i] = 0

                    for block in blocks_to_move:
                        block.move("down")
                        block.update(screen, update_grid=True)

                mngr.spawn_new_piece(screen)

            timer.update()

        mngr.active_blocks.update(screen)
        surf.fill((0, 0, 0))
        for group in borders, mngr.active_blocks, mngr.inactive_blocks:
            group.draw(surf)
        screen.draw_queue(surf, mngr.queue)
        screen.draw_held(surf, mngr.held_piece)

    return state, score, mngr, screen, timer


def run(tickrate=30, n_blocks_in_queue=3):
    # Define game variables
    clock = pygame.time.Clock()
    timer = Timer(interval=200, delta=150, soft_delay=100)
    score = 0

    # Process
    screen = Screen(400, epsilon=0.05, left_space=4, right_space=4)
    borders, surf = screen.setup_screen()
    surf.fill((0, 0, 0))
    borders.update(screen)
    borders.draw(surf)

    # Init blocks and screen
    mngr = BlockManager(screen, surf, n_blocks_in_queue)
    pygame.display.flip()
    state = "RUNNING"

    # Game loop
    while True:
        if state == "RUNNING":
            state, score, mngr, screen, timer = run_game_loop(
                score, mngr, screen, timer, borders, surf)
            # Print score
            screen.set_score(score)
            screen.draw_score(surf)
        else:
            # TODO: Score screen
            return

        pygame.display.flip()
        clock.tick(tickrate)


if __name__ == '__main__':
    pygame.init()
    run()
    pygame.quit()
