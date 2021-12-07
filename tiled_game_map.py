from displayio import Group, TileGrid, Bitmap, Palette
import json
import adafruit_imageload

from entity import Entity


class TiledGameMap(Group):

    def __init__(
            self,
            map_json_file,
            camera_width=10,
            camera_height=8,
            background_default_tile=15,
            entity_default_tile=15,
            player_default_tile=0,
            cursor_default_tile=17,
            empty_map_tile=15,
            use_cursor=False
    ):
        super().__init__()

        f = open(map_json_file, "r")
        self._map_obj = json.loads(f.read())
        f.close()

        self.empty_map_tile = empty_map_tile
        self.cursor_default_tile = cursor_default_tile
        self.player_default_tile = player_default_tile
        self.entity_default_tile = entity_default_tile
        self.background_default_tile = background_default_tile

        self.player_loc = {"x": 1, "y": 1}
        self.cursor_loc = {"x": 1, "y": 1}

        self.camera_loc = {"x": 0, "y": 0}
        self._tile_properties = {0: {"can_walk": True}}
        self.entities = []

        if "tiles" in self.map_obj['tilesets'][0]:
            print("has tiles")
            for _tile in self.map_obj['tilesets'][0]['tiles']:
                _tile_id = _tile["id"]
                if _tile_id not in self.tile_properties:
                    self.tile_properties[_tile_id] = {}
                for _property in _tile["properties"]:
                    self.tile_properties[_tile_id][_property["name"]] = _property["value"]

        _sprite_sheet_image = self.map_obj["tilesets"][0]["image"]
        # Load the sprite sheet (bitmap)
        self._sprite_sheet, self._palette = adafruit_imageload.load(_sprite_sheet_image,
                                                                    bitmap=Bitmap,
                                                                    palette=Palette)

        self._palette.make_transparent(0)

        self._tile_width = self.map_obj["tilewidth"]
        self._tile_height = self.map_obj["tileheight"]

        # Create the background TileGrid
        self._background_tilegrid = TileGrid(self._sprite_sheet, pixel_shader=self._palette,
                                             width=camera_width,
                                             height=camera_height,
                                             tile_width=self._tile_width,
                                             tile_height=self._tile_height,
                                             default_tile=background_default_tile)

        # Create the castle TileGrid
        self._map_tilegrid = TileGrid(self._sprite_sheet, pixel_shader=self._palette,
                                      width=camera_width,
                                      height=camera_height,
                                      tile_width=self._tile_width,
                                      tile_height=self._tile_height,
                                      default_tile=entity_default_tile)

        # Create the player sprite TileGrid
        # self._sprite_tilegrid = TileGrid(self._sprite_sheet, pixel_shader=self._palette,
        #                                  width=1,
        #                                  height=1,
        #                                  tile_width=self._tile_width,
        #                                  tile_height=self._tile_height,
        #                                  default_tile=player_default_tile)

        if self.player_entity_class:
            _player_entity_class = self.player_entity_class
            print("have custom Player entity class")
        else:
            _player_entity_class = Entity

        self._player_entity = _player_entity_class(
            self._sprite_sheet, pixel_shader=self._palette,
            width=1,
            height=1,
            tile_width=self._tile_width,
            tile_height=self._tile_height,
            default_tile=player_default_tile
        )

        self.append(self._background_tilegrid)
        self.append(self._map_tilegrid)
        # self.append(self._sprite_tilegrid)
        self.append(self._player_entity.tilegrid)

        self.camera_width = camera_width
        self.camera_height = camera_height
        if self.npc_entity_map:
            entity_map = self.npc_entity_map
        else:
            entity_map = None
        if self.player_property:
            player_property = self.player_property
        else:
            player_property = None

        self._load_tilegrids(
            width=camera_width,
            height=camera_height,
            player_property=player_property,
            npc_entity_map=entity_map
        )

        # set the initial player location
        self.update_player_location()

        self.use_cursor = use_cursor
        if use_cursor:
            self._cursor_tilegrid = TileGrid(self._sprite_sheet, pixel_shader=self._palette,
                                             width=1,
                                             height=1,
                                             tile_width=self._tile_width,
                                             tile_height=self._tile_height,
                                             default_tile=cursor_default_tile)

            self.append(self._cursor_tilegrid)
            self.update_cursor_location(self.cursor_loc)

    def update_tilegrids(self):
        self._load_tilegrids(x=self.camera_loc["x"], y=self.camera_loc["y"],
                             width=self.camera_width, height=self.camera_height)

    def change_map_tile(self, tile_coords, new_tile_index):
        self.map_obj['layers'][1]["data"][self.get_index_from_coords(tile_coords)] = new_tile_index
        self._map_tilegrid[tile_coords['x'], tile_coords['y']] = new_tile_index

    def _load_tilegrids(self, x=0, y=0, width=10, height=8, player_property="player", npc_entity_map=None):
        self.camera_loc["x"] = x
        self.camera_loc["y"] = y

        def _build_tiles_list(layer_index):
            print("building tile list for {}".format(layer_index))
            _tiles_to_load = []
            for _y in range(height):
                for _x in range(width):
                    _extra_offset = (self.map_obj["width"] - width) * _y
                    _tiles_to_load.append(
                        self.map_obj['layers'][layer_index]['data'][_x + _y * width + start_index + _extra_offset])
            print(_tiles_to_load)
            return _tiles_to_load

        _extra_offset = (self.map_obj["width"] - width) * y
        print("extra_offset: {}".format(_extra_offset))
        start_index = y * width + x + _extra_offset
        print("start index {}".format(start_index))

        # _tiles_to_load = self.map_obj['layers'][0]['data'][start_index:start_index+count]

        _background_tiles = _build_tiles_list(0)
        for index, tile_index in enumerate(_background_tiles):
            _y = index // width
            _x = index % width
            # print("{}, {} = {}".format(_x, _y, tile_index - 1))
            self._background_tilegrid[_x, _y] = tile_index - 1

        _map_tiles = _build_tiles_list(1)
        print("map tiles:")
        print(_map_tiles)

        _player_tiles = _build_tiles_list(2)
        print("player tiles:")
        print(_player_tiles)
        for index, tile_index in enumerate(_map_tiles):
            _y = index // width
            _x = index % width
            # print("({}, {}) = {}".format(_x, _y, tile_index))

            if tile_index != 0:
                # print("{}, {} = {}".format(_x, _y, tile_index - 1))
                _player_layer_index = _player_tiles[index]
                # print("player layer index: ({},{})={}".format(_x, _y, _player_layer_index))
                if self.get_tile_property(_player_layer_index - 1, player_property):
                    print("found player ({}, {})".format(_x, _y))
                    # place player
                    self.player_loc["x"] = _x + x
                    self.player_loc["y"] = _y + y

                for entity_type in npc_entity_map.keys():
                    if self.get_tile_property(_player_layer_index - 1, entity_type):
                        # create a entity obj
                        _new_entity = npc_entity_map[entity_type](
                            self._sprite_sheet, pixel_shader=self._palette,
                            width=1,
                            height=1,
                            tile_width=self._tile_width,
                            tile_height=self._tile_height,
                            default_tile=_player_layer_index - 1
                        )
                        _new_entity.x = (_x + x) * self._tile_width
                        _new_entity.y = (_y + y) * self._tile_height
                        print("enemy loc: ({}, {})".format(_new_entity.x, _new_entity.y))
                        self.entities.append(_new_entity)

                # place non-player entity
                if "count" not in self.map_obj["tilesets"][0]["tiles"][tile_index - 1].keys():
                    self.map_obj["tilesets"][0]["tiles"][tile_index - 1]["count"] = 1
                else:
                    self.map_obj["tilesets"][0]["tiles"][tile_index - 1]["count"] += 1

                self._map_tilegrid[_x, _y] = tile_index - 1
            else:
                # put empty space for tile id 0
                # print("{}, {} = {}".format(_x, _y, 15))

                # must be set to an index for empty spot in the spritesheet
                self._map_tilegrid[_x, _y] = self.empty_map_tile
        print("entity tilegrid (0,0) = {}".format(self._map_tilegrid[0, 0]))

        for _enemy in self.entities:
            self.append(_enemy.tilegrid)

    @property
    def map_obj(self):
        return self._map_obj

    @property
    def tile_properties(self):
        return self._tile_properties

    def get_tile_property(self, tile_id, property_name):
        if tile_id >= 0:
            if property_name in self.tile_properties[tile_id]:
                return self.tile_properties[tile_id][property_name]
        return None

    def update_player_location(self):
        # self._sprite_tilegrid.x = self._tile_width * (self.player_loc["x"] - self.camera_loc["x"])
        # self._sprite_tilegrid.y = self._tile_height * (self.player_loc["y"] - self.camera_loc["y"])
        self._player_entity.x = self._tile_width * (self.player_loc["x"] - self.camera_loc["x"])
        self._player_entity.y = self._tile_height * (self.player_loc["y"] - self.camera_loc["y"])

    def update_cursor_location(self, tile_coords):
        """
        :param tile_coords: dictionary with x and y entries
        :return: None
        """
        self.cursor_loc["x"] = tile_coords["x"]
        self.cursor_loc["y"] = tile_coords["y"]
        self._cursor_tilegrid.x = self._tile_width * (self.cursor_loc["x"] - self.camera_loc["x"])
        self._cursor_tilegrid.y = self._tile_height * (self.cursor_loc["y"] - self.camera_loc["y"])

    def is_tile_moveable(self, tile_coords):
        """
        Check the can_walk property of the tile at the given coordinates
        :param tile_coords: dictionary with x and y entries
        :return: True if the player can walk on this tile. False otherwise.
        """

        _layer_can_walks = []

        _index = (tile_coords['y'] * self.map_obj["width"]) + tile_coords['x']
        # print("index {}".format(_index))
        for layer in self.map_obj['layers']:
            tile_type = layer['data'][_index]
            tile_type = max(tile_type - 1, 0)

            if "can_walk" in self.tile_properties[tile_type]:
                # print("can_walk {}".format(tile_properties[tile_type]["can_walk"]))
                _layer_can_walks.append(self.tile_properties[tile_type]["can_walk"])
            else:
                _layer_can_walks.append(False)

        if False in _layer_can_walks:
            return False

        return True

    def get_tile_origin(self, tile_coords):
        if "x" not in tile_coords or "y" not in tile_coords:
            print("invalid location")
            return None
        return (tile_coords['x'] * self._tile_width, tile_coords['y'] * self._tile_height)

    def get_index_from_coords(self, tile_coords):
        return (tile_coords['y'] * self.map_obj["width"]) + tile_coords['x']

    def get_tile(self, tile_coords):
        """

        :param tile_coords: dictionary with x and y entries
        :return: Tiled index for the entity at the location given, or
                 if no entity is present, returns Tiled index for the
                 background tile at the location given. Tiled indexes are
                 1 based.
        """

        if "x" not in tile_coords or "y" not in tile_coords:
            print("invalid location")
            return None

        _index = self.get_index_from_coords(tile_coords)
        # print("index {}".format(_index))

        map_tile = self.map_obj['layers'][1]["data"][_index]
        if map_tile:
            return map_tile

        background_tile = self.map_obj['layers'][0]["data"][_index]
        return background_tile

    def get_tile_name(self, tile_coords):
        tile_id = self.get_tile(tile_coords)
        return self.get_tile_property(tile_id - 1, "name")

    def set_camera_loc(self, tile_coords):
        self._load_tilegrids(x=tile_coords["x"], y=tile_coords["y"])
        self.update_cursor_location(self.cursor_loc)
        self.update_player_location()

    @property
    def player_entity(self):
        return self._player_entity

    def game_tick(self):
        self.player_entity.game_tick(self)
        for entity in self.entities:
            entity.game_tick(self)