#Космические захватчики программа основана на базе другой игры из книги Майкла Доусона

from livewires import games, color

#Создание графического экрана
games.init(screen_width = 640, screen_height = 480, fps = 50)

class Wrapper(games.Sprite):
    """Класс, который отвечает за функции передвижения спрайта в рамках границ графического экрана"""
    def update(self):    
        if self.left > games.screen.width:
            self.right = 0   
        if self.right < 0:
            self.left = games.screen.width
    def die(self):
        """Destroy метод класс Sprite"""
        self.destroy()


class Collider(Wrapper):
    """Класс отвечающий за взаимодействие сталкивающихся объектов"""
    def update(self):
        """Проверка сталкивающихся спрайтов"""
        super(Collider, self).update()
        #overlapping_sprites свойства класс Спрайт; это списко всех объектов, которые перекрываются с другими спрайтами
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
            self.die() 

class Ship(Collider):
    """Корабль игрока"""
    image = games.load_image("ship.bmp")
    sound = games.load_sound("thrust.wav")
    MISSILE_DELAY = 40

    def __init__(self, game):
        """Создание спрайта короабля"""
        super(Ship, self).__init__(image = Ship.image, x = games.mouse.x, y = games.screen.height)
        self.missile_wait = 0
        self.game = game

    def update(self):
        """Движение корабля производится с помощью мышки"""
        self.x = games.mouse.x
        super(Ship, self).update()
            
        #Условие ожидания следующего выстрела
        if self.missile_wait > 0:
            self.missile_wait -= 1
            
        #Запуск ракеты с помощью пробела  
        if games.keyboard.is_pressed(games.K_SPACE) and self.missile_wait == 0:
            new_missile = Missile(self.x, self.y)
            games.screen.add(new_missile)        
            self.missile_wait = Ship.MISSILE_DELAY

    def die(self):
        """Уничтожает корабль и заканчивает игру"""
        self.game.end()
        super(Ship, self).die()


class Missile(Collider):
    """Запуск ракеты с помощью корабля игрока"""
    image = games.load_image("missile.bmp")
    sound = games.load_sound("missile.wav")
    LIFETIME = 75

    def __init__(self, ship_x, ship_y):
        """Создания спрайта ракеты"""
        Missile.sound.play()
        #Вычисление стартовой позиции ракеты
        x = ship_x 
        y = ship_y - 50

        #Вычесление скорости ракеты
        dx = 0
        dy = -5

        # create the missile
        super(Missile, self).__init__(image = Missile.image,
                                      x = x, y = y,
                                      dx = dx, dy = dy)
        self.lifetime = Missile.LIFETIME

    def update(self):
        """Движение ракеты"""
        super(Missile, self).update()

        #Если время закончилось ракета уничтожается
        self.lifetime -= 1
        if self.lifetime == 0:
            self.destroy()


class Asteroid(Collider):
    "Класс Спрайта Астеройда, обьект который необходимо уничтожить"
    image = games.load_image("asteroid_small.bmp")
    total = 0 
    POINTS = 5  

    def __init__(self,x,y,game,dx ,dy):     
        #total позволяет определить количество созданных обьектов
        Asteroid.total += 1
        """Создание астеройда"""
        super(Asteroid, self).__init__(image = Asteroid.image,
                                      dx = dx,
                                      dy = dy, x = x,y = y
                                      )
        self.game = game
        
    def update(self):
        """Передвижение спрайта"""
        if self.right > games.screen.width:
            self.right = 0             


    def die(self):
        """Удаление спрайта, уменьшение общего количества"""
        Asteroid.total -= 1  

        self.game.score.value += int(Asteroid.POINTS)
        self.game.score.right = games.screen.width - 10   
        

        #Если все астеройды уничтожены, переход на следующий уровень    
        if Asteroid.total == 0:
            self.game.advance()

        if self.bottom > games.screen.height:
            self.game.end()


        super(Asteroid, self).die()

class Game(object):
    """Класс игры создание обьектов, уровней, концовка игры"""
    def __init__(self):
        #Параметры уровня
        self.level = 0
        self.dx = 1.5
        self.dy = 0.07
        self.sound = games.load_sound("level.wav")
        #Вывод на экран очков, свойство is_collideable определяет будет ли обьект иметь свойство "сталкиваться"
        self.score = games.Text(value = 0,
                                size = 30,
                                color = color.white,
                                top = 5,
                                right = games.screen.width - 10,
                                is_collideable = False)
        games.screen.add(self.score)
        #Создание корабля игрока
        self.ship = Ship(game = self)
        games.screen.add(self.ship)

    def play(self):
        games.music.load("theme.mid")
        games.music.play(-1)

        #Загрузка изображения заднего фона
        nebula_image = games.load_image("nebula.jpg")
        games.screen.background = nebula_image

        #Загрузка уровня
        self.advance()

        # start play
        games.screen.mainloop()

    def advance(self):
        """Функция уровня, с каждым уровнем скорость передвижения астеройдов увеличиваются"""
        self.level += 1
        self.dx += 0.5
        self.dy += 0.05

        # Создает серию астеройдов
        for i in range(self.level):
            len_y = 50
            len_x = 50
            y = games.screen.height / 2
            for i in range (3):
                x = games.screen.width 
                y -= len_y
                for j in range (4):
                    x -= len_x
                    new_asteroid = Asteroid(game = self,
                                            x = x,
                                            y = y,
                                            dx = self.dx,
                                            dy = self.dy
                                            )

                    games.screen.add(new_asteroid)

        #Отображение уровня
        level_message = games.Message(value = "Level " + str(self.level),
                                      size = 40,
                                      color = color.yellow,
                                      x = games.screen.width/2,
                                      y = games.screen.width/10,
                                      is_collideable = False)
        games.screen.add(level_message)

        #Звуки нового уровня
        if self.level > 1:
            self.sound.play()
            
    def end(self):
        end_message = games.Message(value = "Game Over",
                                    size = 90,
                                    color = color.red,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 5 * games.screen.fps,
                                    after_death = games.screen.quit,
                                    is_collideable = False)
        games.screen.add(end_message)

def main():
    astrocrash = Game()
    astrocrash.play()

main()