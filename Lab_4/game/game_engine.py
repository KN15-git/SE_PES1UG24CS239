import pygame
import random
import time
import math
import struct
import wave
import io
from game.beat import Note, LANES, LANE_KEYS, LANE_LABELS, LANE_COLORS

# Screen and display constants
WIDTH, HEIGHT = 480, 640
FPS = 60
HIT_Y = HEIGHT - 80
HIT_WINDOW = 30
SPAWN_Y = -30
BG = (15, 10, 25)
LANE_W = WIDTH // LANES

# Rhythm and BPM constants
BPM = 120
BEAT_INTERVAL = 60.0 / BPM  # 0.5s per beat at 120 BPM

# Hold note constants
HOLD_DURATION = 1.0       # Hold duration in seconds
HOLD_PROBABILITY = 0.2    # ~1 in 5 notes is a hold note
HOLD_GAP = 60             # Minimum pixel gap behind a hold note tail before spawning in the same lane

# Difficulty constants
INITIAL_SPEED = 5.0
MAX_SPEED = 10.0
SPEED_INCREMENT = 0.5
DIFFICULTY_RAMP_INTERVAL = 10.0  # Steady difficulty ramp every 10 seconds of play
MAX_MISSES = 15

# Audio constants
PERFECT_FREQ = 880   # A5
GREAT_FREQ = 660     # E5
OK_FREQ = 520        # C5
BEEP_DURATION = 0.08 # seconds
BEEP_VOLUME = 0.3


class GameEngine:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except Exception:
            pass
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rhythm Tap")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22, bold=True)
        self.hud_font = pygame.font.SysFont("monospace", 24, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.stat_font = pygame.font.SysFont("monospace", 20, bold=True)
        self.init_sounds()
        self.reset()

    def init_sounds(self):
        self.sounds = {}
        try:
            if pygame.mixer.get_init():
                self.sounds["PERFECT"] = self._generate_beep(PERFECT_FREQ, BEEP_DURATION, BEEP_VOLUME)
                self.sounds["GREAT"] = self._generate_beep(GREAT_FREQ, BEEP_DURATION, BEEP_VOLUME)
                self.sounds["OK"] = self._generate_beep(OK_FREQ, BEEP_DURATION, BEEP_VOLUME)
        except Exception:
            self.sounds = {}

    @staticmethod
    def _generate_beep(frequency, duration, volume):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            for i in range(n_samples):
                decay = 1.0 - (i / n_samples)
                val = int(32767 * volume * decay * math.sin(2.0 * math.pi * frequency * (i / sample_rate)))
                wav_file.writeframes(struct.pack('<h', val))
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def play_sound(self, grade):
        sound = self.sounds.get(grade)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def reset(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.misses = 0
        self.stats = {"PERFECT": 0, "GREAT": 0, "OK": 0, "MISS": 0}
        self.speed = INITIAL_SPEED
        self.start_time = time.time()
        self.next_beat = 0
        self.feedback = []  # (text, color, ttl, x, y)
        self.game_over = False

    def get_free_lanes(self):
        # A lane is blocked if occupied by an active hold note (or within HOLD_GAP of its tail)
        # or if a note was just spawned there.
        hold_blocked = set()
        spawn_blocked = set()
        for note in self.notes:
            if note.is_hold and not note.completed:
                tail_y = note.y - note.length
                if tail_y < SPAWN_Y + HOLD_GAP:
                    hold_blocked.add(note.lane)
            elif not note.hit and not note.missed:
                if note.y < SPAWN_Y + Note.HEIGHT + 10:
                    spawn_blocked.add(note.lane)

        # Lanes with neither hold notes nor notes sitting at spawn line
        completely_free = [l for l in range(LANES) if l not in hold_blocked and l not in spawn_blocked]
        if completely_free:
            return completely_free

        # Fallback: prefer any lane that is not occupied by a hold note
        non_hold_lanes = [l for l in range(LANES) if l not in hold_blocked]
        if non_hold_lanes:
            return non_hold_lanes

        return list(range(LANES))

    def spawn_note(self):
        chosen_lane = random.randint(0, LANES - 1)
        free_lanes = self.get_free_lanes()
        if free_lanes:
            if chosen_lane not in free_lanes:
                chosen_lane = random.choice(free_lanes)

        is_hold = random.random() < HOLD_PROBABILITY
        self.notes.append(Note(chosen_lane, y=SPAWN_Y, speed=self.speed, is_hold=is_hold, hold_duration=HOLD_DURATION, fps=FPS))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif not self.game_over:
                    for i, key in enumerate(LANE_KEYS):
                        if event.key == key:
                            self.process_tap(i)
            elif event.type == pygame.KEYUP:
                if not self.game_over:
                    for i, key in enumerate(LANE_KEYS):
                        if event.key == key:
                            self.process_release(i)
        return True

    def process_tap(self, lane):
        # Find closest unhit note in this lane near the hit line
        best = None
        best_dist = 9999
        for note in self.notes:
            if note.lane == lane and not note.hit and not note.missed and not note.holding:
                dist = abs(note.y + Note.HEIGHT // 2 - HIT_Y)
                if dist < best_dist:
                    best_dist = dist
                    best = note
        lane_x = lane * LANE_W + LANE_W // 2
        if best and best_dist <= HIT_WINDOW:
            if best_dist < 8:
                grade, pts = "PERFECT", 300
                col = (255, 220, 0)
            elif best_dist < 18:
                grade, pts = "GREAT", 200
                col = (100, 220, 100)
            else:
                grade, pts = "OK", 100
                col = (180, 180, 255)
            self.play_sound(grade)

            if best.is_hold:
                # Start holding; grade and score finalized when held to completion
                best.holding = True
                best.head_grade = grade
                best.head_pts = pts
                best.head_col = col
            else:
                best.hit = True
                self.stats[grade] += 1
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self.score += pts * max(1, self.combo // 5)
                self.feedback.append([grade, col, 40, lane_x, HIT_Y - 30])
        else:
            # Badly timed press resets combo without a MISS popup
            self.combo = 0

    def process_release(self, lane):
        # Releasing an active hold note early counts as a MISS
        for note in self.notes:
            if note.lane == lane and note.is_hold and note.holding and not note.completed:
                note.holding = False
                note.missed = True
                self.misses += 1
                self.stats["MISS"] += 1
                self.combo = 0
                lane_x = lane * LANE_W + LANE_W // 2
                self.feedback.append(["MISS", (220, 60, 60), 40, lane_x, HIT_Y - 30])

    def update(self):
        if self.game_over:
            return

        elapsed = time.time() - self.start_time

        # Steady difficulty ramp based on elapsed play time
        ramp_level = int(elapsed // DIFFICULTY_RAMP_INTERVAL)
        self.speed = min(MAX_SPEED, INITIAL_SPEED + ramp_level * SPEED_INCREMENT)

        # BPM-synced spawning: calculate fall time and spawn ahead of beat
        fall_dist = (HIT_Y - Note.HEIGHT // 2) - SPAWN_Y
        t_fall = fall_dist / (self.speed * FPS)
        base_delay = fall_dist / (INITIAL_SPEED * FPS)

        while True:
            target_hit_time = base_delay + self.next_beat * BEAT_INTERVAL
            spawn_time = target_hit_time - t_fall
            if elapsed >= spawn_time:
                self.spawn_note()
                self.next_beat += 1
            else:
                break

        for note in self.notes:
            note.update()
            if note.is_hold and note.holding and not note.hit and not note.missed:
                # Tail reaches hit line: hold completed successfully
                if (note.y - note.length + Note.HEIGHT // 2) >= HIT_Y:
                    note.hit = True
                    note.holding = False
                    note.completed = True
                    self.stats[note.head_grade] += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    self.score += note.head_pts * max(1, self.combo // 5)
                    lane_x = note.lane * LANE_W + LANE_W // 2
                    self.feedback.append([note.head_grade, note.head_col, 40, lane_x, HIT_Y - 30])
            # Mark missed when head leaves hit window without being pressed
            elif not note.hit and not note.missed and not note.holding and (note.y + Note.HEIGHT // 2) > (HIT_Y + HIT_WINDOW):
                note.missed = True
                self.misses += 1
                self.stats["MISS"] += 1
                self.combo = 0
                lane_x = note.lane * LANE_W + LANE_W // 2
                self.feedback.append(["MISS", (220, 60, 60), 40, lane_x, HIT_Y - 30])

        self.notes = [n for n in self.notes if not (n.hit or (n.missed and (n.y - (n.length if n.is_hold else 0)) > HEIGHT + 10))]
        self.feedback = [[t, c, ttl - 1, x, y] for t, c, ttl, x, y in self.feedback if ttl > 1]

        if self.misses >= MAX_MISSES:
            self.game_over = True

    def draw(self):
        self.screen.fill(BG)

        # Lane dividers
        for i in range(LANES + 1):
            pygame.draw.line(self.screen, (40, 40, 60), (i * LANE_W, 0), (i * LANE_W, HEIGHT), 1)

        # Hit line
        pygame.draw.line(self.screen, (80, 80, 100), (0, HIT_Y), (WIDTH, HIT_Y), 2)
        for i in range(LANES):
            lx = i * LANE_W + LANE_W // 2
            pygame.draw.rect(
                self.screen,
                LANE_COLORS[i],
                pygame.Rect(lx - Note.WIDTH // 2, HIT_Y - 12, Note.WIDTH, 24),
                border_radius=6
            )
            lbl = self.font.render(LANE_LABELS[i], True, (20, 20, 20))
            self.screen.blit(lbl, (lx - lbl.get_width() // 2, HIT_Y - 10))

        # Notes
        for note in self.notes:
            if note.hit:
                continue
            lx = note.lane * LANE_W + LANE_W // 2
            base_col = LANE_COLORS[note.lane]
            # Show brighter color when note is actively being held
            col = tuple(min(255, c + 70) for c in base_col) if note.holding else base_col

            if note.is_hold:
                # Body bar
                body_rect = note.get_body_rect(lx)
                pygame.draw.rect(self.screen, col, body_rect, border_radius=4)
                # Tail cap
                tail_rect = note.get_tail_rect(lx)
                pygame.draw.rect(self.screen, col, tail_rect, border_radius=5)
                # Head cap
                head_rect = note.get_rect(lx)
                pygame.draw.rect(self.screen, col, head_rect, border_radius=5)
            else:
                rect = note.get_rect(lx)
                pygame.draw.rect(self.screen, col, rect, border_radius=5)

        # Hit feedback popups
        for text, color, ttl, x, y in self.feedback:
            surf = self.font.render(text, True, color)
            alpha = min(255, ttl * 7)
            surf.set_alpha(alpha)
            self.screen.blit(surf, (x - surf.get_width() // 2, y))

        # HUD
        sc = self.hud_font.render(f"Score: {self.score}", True, (220, 220, 220))
        co = self.hud_font.render(f"Combo: {self.combo}x", True, (255, 220, 80))
        mi = self.hud_font.render(f"Misses: {self.misses}/{MAX_MISSES}", True, (220, 100, 100))
        self.screen.blit(sc, (10, 10))
        self.screen.blit(co, (10, 38))
        self.screen.blit(mi, (WIDTH - 180, 10))

        # Grade Summary Screen on Game Over
        if self.game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 200))
            self.screen.blit(ov, (0, 0))

            msg = self.big_font.render("GAME OVER", True, (220, 60, 60))
            self.screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 70))

            sc_msg = self.hud_font.render(f"Final Score: {self.score}", True, (240, 240, 240))
            self.screen.blit(sc_msg, (WIDTH // 2 - sc_msg.get_width() // 2, 130))

            cb_msg = self.hud_font.render(f"Max Combo: {self.max_combo}x", True, (255, 220, 80))
            self.screen.blit(cb_msg, (WIDTH // 2 - cb_msg.get_width() // 2, 165))

            # Breakdown counts
            p_msg = self.stat_font.render(f"PERFECT: {self.stats['PERFECT']}", True, (255, 220, 0))
            g_msg = self.stat_font.render(f"GREAT:   {self.stats['GREAT']}", True, (100, 220, 100))
            o_msg = self.stat_font.render(f"OK:      {self.stats['OK']}", True, (180, 180, 255))
            m_msg = self.stat_font.render(f"MISS:    {self.stats['MISS']}", True, (220, 60, 60))

            self.screen.blit(p_msg, (WIDTH // 2 - 80, 220))
            self.screen.blit(g_msg, (WIDTH // 2 - 80, 255))
            self.screen.blit(o_msg, (WIDTH // 2 - 80, 290))
            self.screen.blit(m_msg, (WIDTH // 2 - 80, 325))

            # Accuracy calculation
            total_hits = self.stats["PERFECT"] + self.stats["GREAT"] + self.stats["OK"]
            total_judged = total_hits + self.stats["MISS"]
            accuracy = (total_hits / total_judged * 100.0) if total_judged > 0 else 0.0
            acc_msg = self.hud_font.render(f"Accuracy: {accuracy:.1f}%", True, (100, 230, 255))
            self.screen.blit(acc_msg, (WIDTH // 2 - acc_msg.get_width() // 2, 385))

            restart = self.font.render("Press R to Restart", True, (170, 170, 170))
            self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 460))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
