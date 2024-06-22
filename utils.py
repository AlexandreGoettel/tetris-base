import pygame


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

    def set_on(self):
        """Make sure the timer triggers."""
        self.move_down_timer -= self.move_down_interval

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
