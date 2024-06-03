import random
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT, K_w, K_a, K_s, K_d


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

    def __init__(self, screen, block_type):
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
        block_type = random.choice(list(colour_table.keys()))\
            if block_type == "random" else block_type
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
        # TODO: implement wall-kicks and counter-clockwise rotation
        orientation_table = {"N": "E", "E": "S", "S": "W", "W": "N"}

        if self.block_type == "O":
            return

        # This could all be made easier by using a big table?
        elif self.block_type == "I" and direction == "w":
            dx, dy = {
                "N": ((2, 1, 0, -1), (-1, 0, 1, 2)),
                "E": ((1, 0, -1, -2), (2, 1, 0, -1)),
                "S": ((-2, -1, 0, 1), (1, 0, -1, -2)),
                "W": ((-1, 0, 1, 2), (-2, -1, 0, 1))
            }[self.orientation]

        elif self.block_type == "L" and direction == "w":
            dx, dy = {
                "E": ((-2, -1, 0, 1), (0, -1, 0, 1)),
                "S": ((0, 1, 0, -1), (-2, -1, 0, 1)),
                "W": ((2, 1, 0, -1), (0, 1, 0, -1)),
                "N": ((0, -1, 0, 1), (2, 1, 0, -1))
            }[self.orientation]

        elif self.block_type == "J" and direction == "w":
            dx, dy = {
                "W": ((0, -1, 0, 1), (-2, -1, 0, 1)),
                "N": ((2, 1, 0, -1), (0, -1, 0, 1)),
                "E": ((0, 1, 0, -1), (2, 1, 0, -1)),
                "S": ((-2, -1, 0, 1), (0, 1, 0, -1))
            }[self.orientation]

        elif self.block_type == "S" and direction == "w":
            dx, dy = {
                "N": ((1, 0, 1, 0), (-1, 0, 1, 2)),
                "E": ((1, 0, -1, -2), (1, 0, 1, 0)),
                "S": ((-1, 0, -1, 0), (1, 0, -1, -2)),
                "W": ((-1, 0, 1, 2), (-1, 0, -1, 0))
            }[self.orientation]

        elif self.block_type == "Z" and direction == "w":
            dx, dy = {
                "N": ((2, 1, 0, -1), (0, 1, 0, 1)),
                "E": ((0, -1, 0, -1), (2, 1, 0, -1)),
                "S": ((-2, -1, 0, 1), (0, -1, 0, -1)),
                "W": ((0, 1, 0, 1), (-2, -1, 0, 1))
            }[self.orientation]

        elif self.block_type == "T":
            dx, dy = {
                "N": ((1, 0, 0, 0), (1, 0, 0, 0)),
                "E": ((0, 0, 0, -1), (0, 0, 0, 1)),
                "S": ((0, 0, -1, 0), (0, 0, -1, 0)),
                "W": ((-1, 0, 1, 1), (-1, 0, 1, -1))
            }[self.orientation]

        else:  # Temporary catch-all
            return

        # Check if a rotation is possible and if yes, do it
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


class Screen:
    """Hold methods and information related to screen placement and drawing."""

    def __init__(self, scale, epsilon=0.05, left_space=3, right_space=3):
        self.scale = scale
        self.epsilon = epsilon
        self.left = left_space
        self.right = right_space
        self.checksum = [Bit10() for _ in range(20)]

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
        return borders, screen

    def get_coords(self, i, j):
        """Convert i, j to screen coords."""
        x_coord = self.scale / 10 * (i + self.left + 1 + self.epsilon / 2)
        y_coord = self.scale / 10 * (j + self.epsilon / 2)
        return x_coord, y_coord


def run_game_loop(active_blocks, inactive_blocks, screen, surf,
                  active_piece, move_down_interval, move_down_timer, borders):
    """Run one game loop logic."""
    state = "RUNNING"
    for event in pygame.event.get():
        if event.type == QUIT:
            state = "SCORESCREEN"
            continue

        elif event.type != KEYDOWN:
            continue

        if event.key == K_ESCAPE:
            state = "SCORESCREEN"
            continue

        elif event.key == K_w:
            active_piece.rotate(screen, "w")
        elif event.key == K_a:
            active_piece.move(screen, "left")
        elif event.key == K_d:
            active_piece.move(screen, "right")

    if state == "RUNNING":
        current_time = pygame.time.get_ticks()
        if current_time - move_down_timer > move_down_interval:
            has_moved_down = active_piece.move(screen, "down")
            if not has_moved_down:
                # Update board
                active_blocks.update(screen, update_grid=True)
                inactive_blocks.add(*active_piece.blocks)
                active_blocks.remove(*active_piece.blocks)

                # Check for line clear
                indices_to_clear, to_remove = [], []
                for j, line in enumerate(screen.checksum):
                    if line.checksum != 1023:
                        continue

                    indices_to_clear.append(j)
                    for block in inactive_blocks:
                        if block.j == j:
                            to_remove.append(block)

                # Clear lines
                for block in to_remove:
                    screen.checksum[block.j][block.i] = 0
                    inactive_blocks.remove(block)

                # Update blocks above cleared lines
                for j in indices_to_clear:
                    blocks_to_move = [block for block in inactive_blocks if block.j < j]
                    for block in blocks_to_move:
                        screen.checksum[block.j][block.i] = 0

                    for block in blocks_to_move:
                        block.move("down")
                        block.update(screen, update_grid=True)

                # Spawn new piece
                active_piece = Tetris(screen, "random")
                active_blocks.add(*active_piece.blocks)

            # Update time tracking
            move_down_timer = current_time

        active_blocks.update(screen)
        surf.fill((0, 80, 102))
        for group in borders, active_blocks, inactive_blocks:
            group.draw(surf)
        pygame.display.flip()

    return state, active_blocks, inactive_blocks, screen, active_piece, move_down_timer


def main(tickrate=30):
    # Define game variables
    clock = pygame.time.Clock()
    move_down_timer, move_down_interval = 0, 100

    # Process
    screen = Screen(400, epsilon=0.05, left_space=3, right_space=3)
    borders, surf = screen.setup_screen()
    surf.fill((0, 0, 0))
    borders.update(screen)
    borders.draw(surf)

    # Start with falling piece and get new one on stop condition
    active_blocks = pygame.sprite.Group()
    inactive_blocks = pygame.sprite.Group()

    active_piece = Tetris(screen, "random")
    active_blocks.add(*active_piece.blocks)
    active_blocks.update(screen)
    active_blocks.draw(surf)
    pygame.display.flip()
    state = "RUNNING"

    # Game loop
    while True:
        if state == "RUNNING":
            state, active_blocks, inactive_blocks, screen, active_piece, move_down_timer =\
                run_game_loop(
                    active_blocks, inactive_blocks, screen, surf, active_piece,
                    move_down_interval, move_down_timer, borders)
        else:
            # TODO: Score screen
            return

        clock.tick(tickrate)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
