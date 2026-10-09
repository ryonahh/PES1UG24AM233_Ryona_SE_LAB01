import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35  
                # --- AI surge cycle (Task 2) ---
        self.build_ms = 4000
        self.surge_ms = 1500
        self.cooldown_ms = 2000
        self.phase_multipliers = {"BUILDING": 1.0, "SURGE": 3.5, "COOLDOWN": 0.3}
        self.ai_phase = "BUILDING"
        self.phase_start = pygame.time.get_ticks()
        self.exhausted = False
        self.exhaust_below = 10
        self.recover_at = 30
        self.counter_window_ms = 1200
        self.counter_bonus_ms = 3000
        self.counter_active = False
        self.counter_used = False
        self.counter_start = 0
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.exhausted or self.stamina <= self.exhaust_below:
                return
                
            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT: 
                    self.arm_position -= self.push_strength()
                    self.stamina = max(0.0, self.stamina - 5.0)
                    self.last_key = pygame.K_LEFT
            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT: 
                    self.arm_position -= self.push_strength()
                    self.stamina = max(0.0, self.stamina - 5.0)
                    self.last_key = pygame.K_RIGHT

    def set_ai_phase(self, phase):
        self.ai_phase = phase
        self.counter_used = False
        self.phase_start = pygame.time.get_ticks()

    def update_ai_phase(self):
        elapsed = pygame.time.get_ticks() - self.phase_start
        if self.ai_phase == "BUILDING" and elapsed >= self.build_ms:
            self.set_ai_phase("SURGE")
        elif self.ai_phase == "SURGE" and elapsed >= self.surge_ms:
            self.set_ai_phase("COOLDOWN")
        elif self.ai_phase == "COOLDOWN" and elapsed >= self.cooldown_ms:
            self.set_ai_phase("BUILDING")
    
    def push_strength(self):
        now = pygame.time.get_ticks()
        if (not self.counter_active and not self.counter_used
                and self.ai_phase == "COOLDOWN"
                and now - self.phase_start <= self.counter_window_ms):
            self.counter_active = True
            self.counter_used = True
            self.counter_start = now
            self.stamina = min(self.max_stamina, self.stamina + 30.0)
        return 8.4 if self.counter_active else 4.2

    def update(self):
        if self.game_state != "PLAYING":
            return

        self.update_ai_phase()
        if self.counter_active and pygame.time.get_ticks() - self.counter_start > self.counter_bonus_ms:
            self.counter_active = False
        ai_variance = random.uniform(0.3, 1.0)
        force = self.ai_strength * ai_variance * self.phase_multipliers[self.ai_phase]
        self.arm_position += force

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + (0.8 if self.counter_active else 0.2))

        if self.stamina <= self.exhaust_below:
            self.exhausted = True
        elif self.exhausted and self.stamina >= self.recover_at:
            self.exhausted = False
        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"
        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.counter_active = False
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.set_ai_phase("BUILDING")
        self.exhausted = False

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render("ARM WRESTLE SHOWDOWN", True, (240, 240, 240))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 12))

        player_header = self.font_med.render("PLAYER", True, (80, 160, 255))
        computer_header = self.font_med.render("COMPUTER", True, (255, 100, 80))
        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))

        table_rect = pygame.Rect(40, 100, self.width - 80, 310)
        pygame.draw.rect(screen, (110, 50, 15), table_rect, border_radius=14)
        pygame.draw.rect(screen, (70, 30, 8), table_rect, width=5, border_radius=14)

        pygame.draw.line(screen, (45, 18, 4), (self.width // 2, 100), (self.width // 2, 410), 4)

        offset_x = (self.arm_position / self.target_limit) * 95
        hand_x = (self.width // 2) + int(offset_x)
        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)
        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(screen, (200, 145, 110), p_shoulder, p_elbow, 32)
        pygame.draw.line(screen, (215, 160, 125), p_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (185, 130, 95), p_elbow, 18)

        pygame.draw.line(screen, (170, 110, 85), c_shoulder, c_elbow, 32)
        pygame.draw.line(screen, (185, 125, 95), c_elbow, (hand_x, hand_y), 26)
        pygame.draw.circle(screen, (150, 95, 70), c_elbow, 18)

        pygame.draw.circle(screen, (225, 175, 140), (hand_x, hand_y), 24)
        pygame.draw.circle(screen, (160, 115, 85), (hand_x, hand_y), 24, width=3)

        stamina_label = self.font_med.render("STAMINA", True, (220, 220, 220))
        screen.blit(stamina_label, (40, 445))

        stamina_bg = pygame.Rect(140, 448, 240, 22)
        stamina_fill = pygame.Rect(140, 448, int(240 * (self.stamina / self.max_stamina)), 22)
        pygame.draw.rect(screen, (45, 50, 60), stamina_bg, border_radius=6)
        blink = (pygame.time.get_ticks() // 200) % 2 == 0
        if self.exhausted:
            bar_color = (255, 40, 40) if blink else (120, 20, 20)
        else:
            bar_color = (60, 210, 100) if self.stamina > 25 else (220, 60, 60)        
        pygame.draw.rect(screen, bar_color, stamina_fill, border_radius=6)
        if self.exhausted:
            ex_surf = self.font_med.render("EXHAUSTED!", True, (255, 80, 80))
            screen.blit(ex_surf, (400, 450))

        if self.ai_phase == "SURGE" and self.game_state == "PLAYING" and blink:
            warn = self.font_big.render("!! AI SURGE !!", True, (255, 170, 40))
            screen.blit(warn, (self.width // 2 - warn.get_width() // 2, 60))
            pygame.draw.rect(screen, (255, 120, 40), pygame.Rect(0, 0, self.width, self.height), width=6)
        if self.counter_active and self.game_state == "PLAYING":
            cs = self.font_big.render("COUNTER-SURGE! x2", True, (80, 240, 120))
            screen.blit(cs, (self.width // 2 - cs.get_width() // 2, 510))
            pygame.draw.rect(screen, (80, 240, 120), pygame.Rect(0, 0, self.width, self.height), width=6)

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            win_text = "PLAYER WINS THE MATCH!" if self.winner == "PLAYER" else "COMPUTER WINS!"
            color = (80, 240, 100) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 45)
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
