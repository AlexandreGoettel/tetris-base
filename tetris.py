import random
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT


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
        self.rect.x, self.rect.y = screen.get_coords(self.i, self.j)
        if update_grid:
            screen.checksum[self.j][self.i] = 1
        # if self.i < 0 or self.i >= len(screen.checksum[0])\
        #         or self.j < 0 or self.j >= len(screen.checksum):
        #     return
        # if self.i > 0:
        #     screen.checksum[self.j][self.i - 1] = 0
        # screen.checksum[self.j][self.i] = 1

    def check_move_down(self, screen):
        """Check if increasing j by 1 is possible."""
        if (not self.j + 1 == len(screen.checksum))\
                and (not screen.checksum[self.j + 1][self.i]):
            return True
        return False

    def move_down(self):
        """Move the block coord down by 1."""
        self.j += 1


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
        block_type = random.choice(colour_table.keys()) if block_type == "random" else block_type
        self.block_type = block_type
        self.colour = colour_table[block_type]
        self.blocks = self.assemble(screen)

    def assemble(self, screen):
        assert self.block_type == "O"  # TODO
        x, y = [0, 1, 0, 1], [0, 0, 1, 1]
        blocks = []
        for xi, yi in zip(x, y):
            blocks.append(Block(screen, colour=self.colour, i=xi, j=yi))
        return blocks

    def rotate(self, direction):
        if self.block_type == "O":
            return

    def move_down(self, screen):
        for block in self.blocks:
            if not block.check_move_down(screen):
                break
        else:
            for block in self.blocks:
                block.move_down()
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


def main(tickrate=30):
    # Define game variables
    clock = pygame.time.Clock()
    move_down_timer, move_down_interval = 0, 100

    # Process
    screen = Screen(400, epsilon=0.05, left_space=3, right_space=3)
    borders, surf = screen.setup_screen()
    surf.fill((0, 80, 102))
    borders.update(screen)
    borders.draw(surf)

    # Start with falling piece and get new one on stop condition
    active_blocks = pygame.sprite.Group()
    inactive_blocks = pygame.sprite.Group()

    active_piece = Tetris(screen, "O")  # TODO: random
    active_blocks.add(*active_piece.blocks)
    active_blocks.update(screen)
    active_blocks.draw(surf)
    pygame.display.flip()

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == QUIT:
                return

        current_time = pygame.time.get_ticks()
        if current_time - move_down_timer > move_down_interval:
            has_moved_down = active_piece.move_down(screen)
            if not has_moved_down:
                # Spawn new piece
                active_blocks.update(screen, update_grid=True)
                inactive_blocks.add(*active_piece.blocks)
                active_blocks.remove(*active_piece.blocks)
                active_piece = Tetris(screen, "O")  # TODO: random
                active_blocks.add(*active_piece.blocks)

            active_blocks.update(screen)
            surf.fill((0, 80, 102))
            for group in borders, active_blocks, inactive_blocks:
                group.draw(surf)
            pygame.display.flip()

            # Update time tracking
            move_down_timer = current_time

        clock.tick(tickrate)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
