import random
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE
from utils import Timer
from screen import Screen
from blocks import BlockManager


def run_random_ai(mngr, screen):
    """Temporary AI that returns random actions."""
    return random.choice(["right", "clockwise", "down", "left"])


def run_game_loop(action, score, mngr, screen, borders, surf):
    """
    Run game logic given AI inputs.

    Instead of presses, 7 possible actions:
     - move: {left, right, down} (down lets the game wait for soft-down)
     - rotate: {clockwise, counterclockwise}
     - hold piece
     - hard drop
    """
    #FIXME
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return "STOP", score, mngr, screen

    if action in ["left", "right", "down"]:
        mngr.active_piece.move(screen, action)

    elif action in ["clockwise", "counterclockwise"]:
        mngr.active_piece.rotate(screen, {"clockwise": "w", "counterclockwise": "e"}[action])

    elif action == "hard":
        while mngr.active_piece.move(screen, "down"):
            pass

    elif action == "hold":
        if mngr.can_hold and not (mngr.held_piece is not None\
                and mngr.held_piece.block_type == mngr.active_piece.block_type):
            mngr.hold_piece(screen)

            # Check

    # Now update pieces and score
    has_moved_down = mngr.active_piece.move(screen, "down")
    if not has_moved_down:
        if any([block.j <= 0 for block in mngr.active_piece.blocks]):
            return "STOP", score, mngr, screen
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

    # Draw updates
    mngr.active_blocks.update(screen)
    surf.fill((0, 0, 0))
    for group in borders, mngr.active_blocks, mngr.inactive_blocks:
        group.draw(surf)
    screen.draw_queue(surf, mngr.queue)
    screen.draw_held(surf, mngr.held_piece)

    return "RUNNING", score, mngr, screen


def main():
    # Define game variables
    n_blocks_in_queue = 3
    clock = pygame.time.Clock()
    # timer = Timer(interval=200, delta=150, soft_delay=100)
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

    # Game loop
    while True:
        key_presses = run_random_ai(mngr, screen)
        state, score, mngr, screen = run_game_loop(
            key_presses, score, mngr, screen, borders, surf)
        screen.set_score(score)

        if state == "STOP":
            break

        screen.draw_score(surf)
        pygame.display.flip()
        clock.tick(10)


pygame.init()
main()
pygame.quit()
