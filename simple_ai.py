import random
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE
from utils import Timer
from screen import Screen
from blocks import BlockManager


def run_random_ai(mngr, screen):
    """Temporary AI that returns random actions."""
    yield random.choice(["right", "clockwise", "left"])


def run_simple_ai(mngr, screen):
    """Simple AI, each action followed by hard drop."""
    best_score, best_moves = None, None

    orientation_value = {"N": 0, "E": 1, "S": 2, "W": 3}
    rotation_reference = [(block.i, block.j) for block in mngr.active_piece.blocks]
    for orientation in ["N", "W", "E", "S"]:
        # Rotate piece to desired orientation
        n_clockwise_rotations = orientation_value[orientation]\
            - orientation_value[mngr.active_piece.orientation]
        rotations = ["w"]*n_clockwise_rotations if n_clockwise_rotations < 3 else ["e"]
        for rotation in rotations:
            mngr.active_piece.rotate(screen, rotation)

        left_most = min([block.i for block in mngr.active_piece.blocks])
        translation_reference = [(block.i, block.j) for block in mngr.active_piece.blocks]
        for target_position in range(10):
            # TODO: This could all be made faster if moves were just mathematical
            # Move piece to desired i-position
            n_right_moves = target_position - left_most
            moves = ["right"]*n_right_moves if n_right_moves >= 0 else ["left"]*-n_right_moves
            if any([not mngr.active_piece.can_move(screen, move) for move in moves]):
                continue  # Move not possible
            for move in moves:
                mngr.active_piece.move(screen, move)

            # Simulate hard drop
            moves_down = 0
            while mngr.active_piece.move(screen, "down"):
                moves_down += 1

            # Check if any line was cleared
            new_screen = screen.copy()
            mngr.active_blocks.update(new_screen, update_grid=True)
            n_cleared = sum([line.checksum == 1023 for line in new_screen.checksum])
            # Check if any "gap" exists
            n_gaps = 0
            for i in range(len(new_screen.checksum[0])):
                ref = new_screen.checksum[0][i]
                for j in range(len(new_screen.checksum)-2, -1, -1):
                    if not new_screen.checksum[j][i]:
                        continue
                    if not ref:
                        n_gaps += 1
                    else:
                        ref = 1

            # Book-keep
            score = n_cleared * len(screen.checksum) * len(screen.checksum[0]) - n_gaps
            if best_score is None or best_score < score:
                best_score = score
                best_moves = rotations + moves + ["down"]*moves_down

            # Reset for next round
            for block, (i, j) in zip(mngr.active_piece.blocks, translation_reference):
                    block.i, block.j = i, j
        for block, (i, j) in zip(mngr.active_piece.blocks, rotation_reference):
                block.i, block.j = i, j

    print(best_score, best_moves)
    mngr.active_blocks.update(screen)
    for move in best_moves:
        yield move


def run_game_loop(action, score, mngr, screen, borders, surf):
    """
    Run game logic given AI inputs.

    Instead of presses, 7 possible actions:
     - move: {left, right, down} (down lets the game wait for soft-down)
     - rotate: {clockwise, counterclockwise}
     - hold piece
     - hard drop
    """
    for event in pygame.event.get():
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            return "STOP", score, mngr, screen, False

    if action in ["left", "right"]:  # down?
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

    # Now update pieces and score
    # print(action)
    has_spawned = False
    # print([(block.i, block.j) for block in mngr.active_piece.blocks])
    if not mngr.active_piece.move(screen, "down"):
        print("SPAWNING NEW PIECE")
        has_spawned = True
        if any([block.j <= 0 for block in mngr.active_piece.blocks]):
            return "STOP", score, mngr, screen, has_spawned
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

    return "RUNNING", score, mngr, screen, has_spawned


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
    ai = run_simple_ai
    # ai = run_random_ai

    # Game loop
    while True:
        actions = ai(mngr, screen)
        for action in actions:
            state, score, mngr, screen, has_spawned = run_game_loop(
                action, score, mngr, screen, borders, surf)
            screen.set_score(score)

            if state == "STOP":
                return

            screen.draw_score(surf)
            pygame.display.flip()
            clock.tick(10)

            if has_spawned:
                break


pygame.init()
main()
pygame.quit()
