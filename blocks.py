import random
import pygame


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

    def __repr__(self):
        return f"Block({self.i}, {self.j})"


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
        self.coord_table = {
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
        # Random with SNES-bias against getting same twice in a row
        if block_type == "random":
            block_type = random.choice(list(colour_table.keys()) + ["random"])
            if block_type == "random" or\
                    (previous is not None and previous.block_type == block_type):
                block_type = random.choice(list(colour_table.keys()))

        self.block_type = block_type
        self.colour = colour_table[block_type]
        self.blocks = self.assemble(screen, *self.coord_table[block_type])
        self.orientation = "N"

    def reset(self):
        """Reset a piece's position and orientation to just-spawned."""
        for idx, (i, j) in enumerate(zip(*self.coord_table[self.block_type])):
            self.blocks[idx].i, self.blocks[idx].j = i, j
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

        self.held_piece = None
        self.can_hold = True

    @property
    def active_piece(self):
        """Getter for the current active piece in the queue."""
        return self.queue[0]

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
        self.can_hold = True

    def hold_piece(self, screen):
        """Hold current piece and, if existing, place held piece back in play."""
        previously_held = self.held_piece
        self.held_piece = self.queue.pop(0)
        self.active_blocks.remove(*self.held_piece.blocks)
        if previously_held is not None:
            self.queue = [previously_held] + self.queue
            self.can_hold = False
        else:
            self.queue.append(Tetris(screen, "random", previous=self.queue[-1]))
        self.active_piece.reset()
        self.active_blocks.add(*self.active_piece.blocks)
