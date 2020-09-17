#!/usr/bin/env python3
import pyglet
from pyglet.window import key
import random
from neat.network import Network
from neat.genome import Genome

class BallBalanceBase(pyglet.window.Window):
    """A little game meant as a fitness function for NEAT"""

    def __init__(self):
        super().__init__(800, 600, resizable=False)
        self.bar = pyglet.shapes.Rectangle(50, 50, 500, 50)

        self.half_width = self.bar.width/2
        self.bar_center_x = self.half_width+self.bar.x
        self.bar_center_y = (self.bar.height/2)+self.bar.y

        self.ball = pyglet.shapes.Circle(self.bar_center_x,
                                    self.bar_center_y,
                                    50)
        self.score_label = pyglet.text.Label('0', x=0, y=0)
        self.time_label = pyglet.text.Label('0', x=50, y=0)
        self.input_label = pyglet.text.Label('', x=self.half_width+50, y=0)

        self.left_pressed = False
        self.right_pressed = False

        self.accel = 2.0
        self.ball.x += random.random()*2-1
        self.remaining_time = 20
        self.score = 0

    def on_draw(self):
        self.clear()
        self.bar.draw()
        self.ball.draw()
        self.score_label.draw()
        self.time_label.draw()
        self.input_label.draw()

    def get_center_dist(self):
        return float(self.bar_center_x - self.ball.x)

    def update(self, dt):
        self.remaining_time -= dt
        dist = self.get_center_dist()
        edge_dist = self.half_width - abs(dist)
        bg = (edge_dist / self.half_width)*255

        if abs(dist) > self.half_width or self.remaining_time <= 0:
            if self.remaining_time > 0:
                self.score -= self.remaining_time
            self.close()
            return

        if self.left_pressed:
            self.ball.x -= dt*(150.0+self.accel*abs(dist))
            self.input_label.text = '<-'
        if self.right_pressed:
            self.ball.x += dt*(150.0+self.accel*abs(dist))
            self.input_label.text = '->'
        if not (self.right_pressed or self.left_pressed):
            self.input_label.text = ''


        self.ball.color = (255, bg, bg)
        xplus = dist*self.accel*dt*-1
        self.ball.x += xplus
        self.score += (edge_dist**2.5)*0.00001*dt
        self.score_label.text = str(int(self.score))
        self.time_label.text = str(int(self.remaining_time))


class BallBalanceManual(BallBalanceBase):
    """
    For manually playing the ball balance game. used to debug and possibly to
    compare personal score to AI
    """
    def on_key_press(self, sym, mod):
        if sym == key.H:
            self.left_pressed = True
        if sym == key.L:
            self.right_pressed = True

    def on_key_release(self, sym, mod):
        if sym == key.H:
            self.left_pressed = False
        if sym == key.L:
            self.right_pressed = False


class BallBalanceNetwork(BallBalanceBase):
    """Ball balancing game run by a neural network"""
    def __init__(self, genome):
        super().__init__()
        self.network = Network(genome)

    def update(self, dt, *args, **kwargs):
        dist = self.get_center_dist()
        left_dist = self.half_width + dist
        right_dist = self.half_width - dist
        abs_dist = abs(dist)
        output = self.network.evaluate([left_dist, abs_dist, right_dist])
        self.left_pressed, self.right_pressed = output

        super().update(dt)


def evaluate_network(genome):
    instance = BallBalanceNetwork(genome)
    pyglet.clock.schedule(instance.update, 1/60)
    pyglet.app.run()
    return instance.score

def evaluate_multiple(genomes):
    windows = [BallBalanceNetwork(gen) for gen in genomes]
    def update_all(dt):
        for w in windows:
            w.update(dt)
    pyglet.clock.schedule_interval(update_all, 1/60)
    pyglet.app.run()
    scores = [win.score for win in windows]
    return scores




if __name__ == '__main__':
    windows = [BallBalanceManual() for _ in range(1)]
    def update_all(dt):
        for w in windows:
            w.update(dt)
    pyglet.clock.schedule_interval(update_all, 1/60)
    pyglet.app.run()
    print('you scored:', windows[0].score)
