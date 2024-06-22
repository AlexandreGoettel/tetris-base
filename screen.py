import pygame
from blocks import Bit10, Block, Tetris


class Screen:
    """Hold methods and information related to screen placement and drawing."""

    def __init__(self, scale, epsilon=0.05, left_space=3, right_space=3, font=None, ft=32):
        self.scale = scale
        self.epsilon = epsilon
        self.left = left_space
        self.right = right_space
        self.checksum = [Bit10() for _ in range(20)]
        self.score = 0
        self.font = pygame.font.SysFont(font, ft) if font is None else font

    def copy(self):
        """Return a new Screen object with same coord info."""
        new_screen = Screen(self.scale, self.epsilon, self.left, self.right, self.font)
        for i, row in enumerate(self.checksum):
            for j, val in enumerate(row):
                new_screen.checksum[i][j] = val
        return new_screen

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

    def draw_queue(self, surf, queue):
        """Draw pieces in queue."""
        # TODO: Add checks to avoid screen overflow OR scale everything!
        draw_group = pygame.sprite.Group()
        for i, piece in enumerate(queue[1:]):
            draw_piece = Tetris(self, piece.block_type)
            # Align using top left corner
            left = min([block.i for block in draw_piece.blocks])
            top = min([block.j for block in draw_piece.blocks])
            for block in draw_piece.blocks:
                block.i += 10 - left + 1
                block.j += 6 - top + (i)*3
                draw_group.add(block)
        draw_group.update(self)
        draw_group.draw(surf)

    def draw_held(self, surf, piece):
        """Draw copy of held piece."""
        if piece is None:
            return
        group = pygame.sprite.Group()
        piece_copy = Tetris(self, piece.block_type)
        # Align using top left corner
        left = min([block.i for block in piece_copy.blocks])
        top = min([block.j for block in piece_copy.blocks])
        for block in piece_copy.blocks:
            block.i -= left + self.left + 1
            block.j += 6 - top
            group.add(block)

        group.update(self)
        group.draw(surf)
