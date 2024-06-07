import random
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_w, K_a, K_SPACE, K_d, K_s


class Bit10:
    """Use a efficient checksum logic to encode tetris grids."""

    def __init__(self):
        self.checksum = 0

    def set_bit(self, i):
        """Set bit i to be 1."""
        self.checksum |= (1 << i)

    def clear_bit(self, i):
        """Set bit i to be 0."""
        self.checksum &= ~(1 << i)

    def get_bit(self, i):
        """Get bit value at position i."""
        return (self.checksum >> i) & 1

    def __getitem__(self, i):
        return self.get_bit(i)

    def __setitem__(self, k, v):
        if v:
            self.set_bit(k)
        else:
            self.clear_bit(k)

    def __repr__(self):
        bit_str = ''.join([str(self.get_bit(10 - 1 - i)) for i in range(10)])
        return f"Bit10({bit_str}) -> {self.checksum}"

    def __len__(self):
        return 10


class Block(pygame.sprite.Sprite):

    def __init__(self, screen, colour=(165, 169, 180), i=None, j=None):
        super().__init__()
        # Create an image of the block, and fill it with a color.
        block_width_in_pixel = screen.scale // 10 * (1 - screen.epsilon)
        self.image = pygame.Surface([block_width_in_pixel, block_width_in_pixel])
        self.image.fill(colour)

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
        self.i, self.j = i, j  # Grid coordinates, not screen position

    def update(self, screen, update_grid=False):
        """Convert grid position to pixel locations and update screen if neccessary."""
        self.rect.x, self.rect.y = screen.get_coords(self.i, self.j)
        if update_grid:
            screen.checksum[self.j][self.i] = 1

    def check_move(self, screen, direction):
        """Check if movement by 1 is possible."""
        if direction == "down":
            if self.j < -1:
                return True
            if (not self.j + 1 == len(screen.checksum))\
                    and (not screen.checksum[self.j + 1][self.i]):
                return True
        elif direction == "left":
            if (not self.i - 1 == -1)\
                    and (not screen.checksum[self.j][self.i - 1]):
                return True
        elif direction == "right":
            if (not self.i + 1 == len(screen.checksum[0]))\
                    and (not screen.checksum[self.j][self.i + 1]):
                return True
        return False

    def move(self, direction):
        """Move the block coord down by 1."""
        if direction == "down":
            self.j += 1
        elif direction == "left":
            self.i -= 1
        elif direction == "right":
            self.i += 1


class Tetris:
    """Hold four blocks in given Tetris shape."""

    def __init__(self, screen, block_type, previous=None):
        colour_table = {
            "O": (255, 255, 0),
            "I": (0, 255, 255),
            "S": (0, 255, 0),
            "Z": (255, 0, 0),
            "J": (0, 0, 255),
            "T": (128, 0, 128),
            "L": (255, 127, 0),
        }
        coord_table = {
            "O": ((4, 5, 4, 5), (0, 0, 1, 1)),
            "I": ((3, 4, 5, 6), (0, 0, 0, 0)),
            "S": ((3, 4, 4, 5), (0, 0, -1, -1)),
            "Z": ((3, 4, 4, 5), (-1, -1, 0, 0)),
            "J": ((3, 3, 4, 5), (-1, 0, 0, 0)),
            "T": ((3, 4, 5, 4), (0, 0, 0, -1)),
            "L": ((5, 5, 4, 3), (-1, 0, 0, 0)),
        }
        self.clockwise_rotation_table = {
            "I":
            {
                "N": ((2, 1, 0, -1), (-1, 0, 1, 2)),
                "E": ((1, 0, -1, -2), (2, 1, 0, -1)),
                "S": ((-2, -1, 0, 1), (1, 0, -1, -2)),
                "W": ((-1, 0, 1, 2), (-2, -1, 0, 1))
            },
            "L":
            {
                "E": ((-2, -1, 0, 1), (0, -1, 0, 1)),
                "S": ((0, 1, 0, -1), (-2, -1, 0, 1)),
                "W": ((2, 1, 0, -1), (0, 1, 0, -1)),
                "N": ((0, -1, 0, 1), (2, 1, 0, -1))
            },
            "J":
            {
                "W": ((0, -1, 0, 1), (-2, -1, 0, 1)),
                "N": ((2, 1, 0, -1), (0, -1, 0, 1)),
                "E": ((0, 1, 0, -1), (2, 1, 0, -1)),
                "S": ((-2, -1, 0, 1), (0, 1, 0, -1))
            },
            "S":
            {
                "N": ((1, 0, 1, 0), (-1, 0, 1, 2)),
                "E": ((1, 0, -1, -2), (1, 0, 1, 0)),
                "S": ((-1, 0, -1, 0), (1, 0, -1, -2)),
                "W": ((-1, 0, 1, 2), (-1, 0, -1, 0))
            },
            "Z":
            {
                "N": ((2, 1, 0, -1), (0, 1, 0, 1)),
                "E": ((0, -1, 0, -1), (2, 1, 0, -1)),
                "S": ((-2, -1, 0, 1), (0, -1, 0, -1)),
                "W": ((0, 1, 0, 1), (-2, -1, 0, 1))
            },
            "T":
            {
                "N": ((1, 0, 0, 0), (1, 0, 0, 0)),
                "E": ((0, 0, 0, -1), (0, 0, 0, 1)),
                "S": ((0, 0, -1, 0), (0, 0, -1, 0)),
                "W": ((-1, 0, 1, 1), (-1, 0, 1, -1))
            }
        }
        self.kick_table = {
            "I": {
                "N-E": ((0, 0), (-2, 0), (1, 0), (-2, 1), (1, -2)),  # 0->R
                "E-S": ((0, 0), (-1, 0), (2, 0), (-1, -2), (2, 1)),  # R->2
                "S-W": ((0, 0), (2, 0), (-1, 0), (2, -1), (-1, 2)),  # 2->L
                "W-N": ((0, 0), (1, 0), (-2, 0), (1, 2), (-2, 1))  # L->0
            },
            "else": {
                "N-E": ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),  # 0->R
                "E-S": ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),  # R->2
                "S-W": ((0, 0), (1, 0), (1, 1), (0, 2), (1, 2)),  # 2->L
                "W-N": ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2))  # L->0
            }
        }
        # Random with bias against getting same twice in a row
        if block_type == "random":
            block_type = random.choice(list(colour_table.keys()) + ["random"])
            if block_type == "random" or\
                    (previous is not None and previous.block_type == block_type):
                block_type = random.choice(list(colour_table.keys()))

        self.block_type = block_type
        self.colour = colour_table[block_type]
        self.blocks = self.assemble(screen, *coord_table[block_type])
        self.orientation = "N"

    def assemble(self, screen, x, y):
        """Transform assortment of coords to a tetromino made of blocks."""
        blocks = []
        for xi, yi in zip(x, y):
            blocks.append(Block(screen, colour=self.colour, i=xi, j=yi))
        return blocks

    def rotate(self, screen, direction):
        """Implement gameboy-style rotation system."""
        # TODO: implement counter-clockwise rotation
        orientation_table = {"N": "E", "E": "S", "S": "W", "W": "N"}

        if self.block_type == "O" or direction != "w":
            return

        # Check if a rotation is possible and if yes, do it
        dx, dy = self.clockwise_rotation_table[self.block_type][self.orientation]
        kick_type = "I" if self.block_type == "I" else "else"
        kick_key = f"{self.orientation}-{orientation_table[self.orientation]}"
        for kickx, kicky in self.kick_table[kick_type][kick_key]:
            for block, dxi, dyi in zip(self.blocks, dx, dy):
                i, j = block.i + dxi + kickx, block.j + dyi + kicky
                if j >= len(screen.checksum) or i < 0 or i >= len(screen.checksum[0]):
                    break
                if screen.checksum[j][i]:
                    break
            else:
                # If all yes, rotate
                self.orientation = orientation_table[self.orientation]
                for block, dxi, dyi in zip(self.blocks, dx, dy):
                    block.i += dxi + kickx
                    block.j += dyi + kicky
                return

    def move(self, screen, direction):
        """Move either "down", "left", or "right"."""
        for block in self.blocks:
            if not block.check_move(screen, direction):
                break
        else:
            for block in self.blocks:
                block.move(direction)
            return True
        return False

    def __repr__(self):
        return f"{self.block_type}-piece"


class BlockManager:
    """Manage tetrominos."""
    def __init__(self, screen, surf, n_blocks_in_queue=3):
        """Initialise first piece and queue, update screen."""
        self.active_blocks = pygame.sprite.Group()
        self.inactive_blocks = pygame.sprite.Group()

        self.queue = [Tetris(screen, "random")]
        self.active_blocks.add(*self.active_piece.blocks)
        self.active_blocks.update(screen)
        self.active_blocks.draw(surf)
        for _ in range(n_blocks_in_queue - 1):
            self.queue.append(Tetris(screen, "random", previous=self.queue[-1]))

    @property
    def active_piece(self):
        """Getter for the current active piece in the queue."""
        return self.queue[0]

    # def next(self, screen):
    #     """Get next piece in the queue and re-fill with new random piece"""
    #     piece = self.queue.pop(0)
    #     self.queue.append(Tetris(screen, "random"))
    #     return piece

    def remove_active(self, screen):
        """Transition current piece blocks from active to inactive."""
        self.active_blocks.update(screen, update_grid=True)
        self.inactive_blocks.add(*self.active_piece.blocks)
        self.active_blocks.remove(*self.active_piece.blocks)

    def spawn_new_piece(self, screen):
        """Delete first queue entry, replace with new at end of queue, update vars."""
        _ = self.queue.pop(0)
        self.queue.append(Tetris(screen, "random", previous=self.queue[-1]))
        self.active_blocks.add(*self.active_piece.blocks)


class Screen:
    """Hold methods and information related to screen placement and drawing."""

    def __init__(self, scale, epsilon=0.05, left_space=3, right_space=3, font=None, ft=32):
        self.scale = scale
        self.epsilon = epsilon
        self.left = left_space
        self.right = right_space
        self.checksum = [Bit10() for _ in range(20)]
        self.score = 0
        self.font = pygame.font.SysFont(font, ft)

    def setup_screen(self):
        """Create tetris-ready screen based on scaling factor."""
        # Define screen & game borders
        block = self.scale / 10
        screen_width = self.scale*1.2 + (self.left + self.right) * block
        screen_height = self.scale*2.1
        screen = pygame.display.set_mode([screen_width, screen_height])

        # Layer outside edges with grey blocks
        borders = pygame.sprite.Group()
        for i in range(12):
            borders.add(Block(self, i=i - 1, j=20))
        for j in range(20):
            for delta in [-1, 10]:
                borders.add(Block(self, i=delta, j=j))

        # Add score box
        delta = 0.1
        box_under = pygame.sprite.Sprite()
        box_under.image = pygame.Surface([block*(self.right - 2*delta), block*2*(1 - delta)])
        box_under.image.fill((0, 120, 80))
        box_under.rect = box_under.image.get_rect()
        box_under.rect.x, box_under.rect.y = block*(self.left + 12 + delta), block*(3 + delta)
        borders.add(box_under)

        # Could be replaced by font bkg?
        box_over = pygame.sprite.Sprite()
        box_over.image = pygame.Surface([block*(self.right - 4*delta), block*(2 - 4*delta)])
        box_over.image.fill((255, 255, 255))
        box_over.rect = box_over.image.get_rect()
        box_over.rect.x, box_over.rect.y = block*(self.left + 12 + 2*delta), block*(3 + 2*delta)
        borders.add(box_over)

        self.draw_score(screen, delta=delta)
        return borders, screen

    def get_coords(self, i, j):
        """Convert i, j to screen coords."""
        x_coord = self.scale / 10 * (i + self.left + 1 + self.epsilon / 2)
        y_coord = self.scale / 10 * (j + self.epsilon / 2)
        return x_coord, y_coord

    def set_score(self, score):
        """Setter for score value."""
        self.score = score

    def draw_score(self, screen, delta=0.1):
        """Draw score as text."""
        score_text = self.font.render(str(self.score), True, (0, 0, 0))
        screen.blit(score_text, (self.scale/10*(self.left + 12 + 2*delta),
                                 self.scale/10*(3 + 2*delta)))


class Timer:

    def __init__(self, interval=100, delta=150, soft_delay=100):
        """Set time between block updates and action delta."""
        self.move_down_interval = interval
        self.action_delta = delta
        self.soft_delay = soft_delay
        self.move_down_timer = 0
        self.last_action_time = 0

    def delta(self):
        """Adjust timer to allow for action delay - spam proof."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_action_time >= self.action_delta:
            self.move_down_timer += self.action_delta
        self.last_action_time = current_time

    def update(self):
        """Update main timer."""
        self.move_down_timer = pygame.time.get_ticks()

    @property
    def can_move_down(self):
        """Check if time has elapsed move down interval"""
        current_time = pygame.time.get_ticks()
        return current_time - self.move_down_timer > self.move_down_interval

    @property
    def can_soft_move(self):
        """Alternative timer rule for soft movement."""
        current_time = pygame.time.get_ticks()
        return current_time > self.last_action_time + self.soft_delay


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

        elif event.key == K_SPACE:
            while mngr.active_piece.move(screen, "down"):
                pass
        elif event.key == K_w:
            mngr.active_piece.rotate(screen, "w")
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

    return state, score, mngr, screen, timer


def main(tickrate=30, n_blocks_in_queue=3):
    # Define game variables
    clock = pygame.time.Clock()
    timer = Timer(interval=200, delta=150, soft_delay=100)
    score = 0

    # Process
    screen = Screen(400, epsilon=0.05, left_space=3, right_space=3)
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
    main()
    pygame.quit()
