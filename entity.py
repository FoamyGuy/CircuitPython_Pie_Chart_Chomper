import displayio


class Entity:
    DIRECTION_UP = 0
    DIRECTION_RIGHT = 1
    DIRECTION_LEFT = 2
    DIRECTION_DOWN = 3
    DIRECTION_NONE = 4

    RIGHT_SPRITES = (0,5)
    LEFT_SPRITES = (2,7)
    UP_SPRITES = (1,6)
    DOWN_SPRITES = (3,8)

    def __init__(
        self,
        bitmap: displayio.Bitmap,
        pixel_shader: displayio.Palette,
        width: int = 1,
        height: int = 1,
        tile_width: int = 16,
        tile_height: int = 16,
        default_tile: int = 0
    ):
        self._direction = self.DIRECTION_NONE
        self._tilegrid = displayio.TileGrid(
            bitmap,
            pixel_shader=pixel_shader,
            width=width,
            height=height,
            tile_width=tile_width,
            tile_height=tile_height,
            default_tile=default_tile,
        )
        self.width = tile_width * width
        self.height = tile_height * height

        self.current_sprites = self.LEFT_SPRITES
        self.sprite_index = 0

    def next_sprite(self):
        self.sprite_index += 1
        if self.sprite_index >= len(self.current_sprites):
            self.sprite_index = 0
        self._tilegrid[0,0] = self.current_sprites[self.sprite_index]


    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        print("inside direction setter")
        if new_direction == self.DIRECTION_UP:
            self.current_sprites = self.UP_SPRITES
        if new_direction == self.DIRECTION_DOWN:
            self.current_sprites = self.DOWN_SPRITES
        if new_direction == self.DIRECTION_RIGHT:
            self.current_sprites = self.RIGHT_SPRITES
        if new_direction == self.DIRECTION_LEFT:
            self.current_sprites = self.LEFT_SPRITES
        self._direction = new_direction
    @property
    def top_front_pixel(self):
        return (self.x + self.width // 2, self.y - 1)

    @property
    def right_front_pixel(self):
        return (self.x + self.width, self.y + self.height // 2)

    @property
    def left_front_pixel(self):
        return (self.x - 1, self.y + self.height // 2)

    @property
    def bottom_front_pixel(self):
        return (self.x + self.width // 2, self.y + self.height)

    @property
    def next_pixel_current_direction(self):
        if self.direction == Entity.DIRECTION_UP:
            return self.top_front_pixel
        if self.direction == Entity.DIRECTION_DOWN:
            return self.bottom_front_pixel
        if self.direction == Entity.DIRECTION_LEFT:
            return self.left_front_pixel
        if self.direction == Entity.DIRECTION_RIGHT:
            return self.right_front_pixel

    @property
    def x(self):
        return self._tilegrid.x

    @property
    def y(self):
        return self._tilegrid.y

    @x.setter
    def x(self, new_x):
        self._tilegrid.x = new_x

    @y.setter
    def y(self, new_y):
        #print("y setter")
        self._tilegrid.y = new_y

    @property
    def tilegrid(self):
        return self._tilegrid

    def is_colliding(self, _other_entity):
        """
        :param _other_entity: another entity to check ourself against
        :return: True if this instance is colidding with the _other_entity
        """
        _colliding_x = False
        _colliding_y = False
        length_x = abs(self.x - _other_entity.x)
        half_width_self = self.width / 2
        half_width_other = _other_entity.width / 2

        gap_between = length_x - half_width_self - half_width_other
        if (gap_between > 0):
            pass
        elif(gap_between == 0):
            pass
        elif(gap_between < 0):
            _colliding_x = True

        length_y = abs(self.y - _other_entity.y)
        half_height_self = self.height / 2
        half_height_other = _other_entity.height / 2

        gap_between = length_y - half_height_self - half_height_other
        if (gap_between > 0):
            pass
        elif (gap_between == 0):
            pass
        elif (gap_between < 0):
            _colliding_y = True

        #print("colliding x: {} - y: {}".format(_colliding_x, _colliding_y))

        return _colliding_x and _colliding_y

    def game_tick(self, game_obj):
        """
        Subclasses override this to add behavior to the entity.
        :return:
        """