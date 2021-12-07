from entity import Entity
from tiled_game_map import TiledGameMap

class Ghost(Entity):
    def game_tick(self, game_obj):

        if self.direction != Entity.DIRECTION_NONE:
            next_pixel_loc = self.next_pixel_current_direction
            next_tile_coords = {
                "x": next_pixel_loc[0] // game_obj._tile_width,
                "y": next_pixel_loc[1] // game_obj._tile_height
            }
            # print(next_tile_coords)
            # print(next_pixel_loc)
            if game_obj.is_tile_moveable(
                    next_tile_coords
            ):
                if self.direction == Entity.DIRECTION_RIGHT:
                    self.x += 1
                if self.direction == Entity.DIRECTION_LEFT:
                    self.x -= 1
                if self.direction == Entity.DIRECTION_UP:
                    self.y -= 1
                if self.direction == Entity.DIRECTION_DOWN:
                    self.y += 1
            else:
                if self.direction == Entity.DIRECTION_RIGHT:
                    print("turning to face up")
                    self.direction = Entity.DIRECTION_UP
                elif self.direction == Entity.DIRECTION_LEFT:
                    print("turning to face down")
                    self.direction = Entity.DIRECTION_DOWN
                elif self.direction == Entity.DIRECTION_UP:
                    print("turning to face left")
                    self.direction = Entity.DIRECTION_LEFT
                elif self.direction == Entity.DIRECTION_DOWN:
                    print("turning to face right")
                    self.direction = Entity.DIRECTION_RIGHT


class Player(Entity):
    def game_tick(self, game_obj):
        if game_obj.player_entity.direction != Entity.DIRECTION_NONE:
            next_pixel_loc = game_obj.player_entity.next_pixel_current_direction
            next_tile_coords = {
                "x": next_pixel_loc[0] // game_obj._tile_width,
                "y": next_pixel_loc[1] // game_obj._tile_height
            }
            #print(next_tile_coords)
            #print(next_pixel_loc)
            if game_obj.is_tile_moveable(
                    next_tile_coords
            ):
                #print(my_game.get_tile_name(next_tile_coords))
                if game_obj.get_tile_name(next_tile_coords) == "pellet":
                    game_obj.SCORE += 1
                    print("score +1")
                    game_obj.REMAINING_PELLETES -= 1
                    #my_game.map_obj['layers'][1]["data"][my_game.get_index_from_coords(next_tile_coords)] = 24
                    game_obj.change_map_tile(next_tile_coords, 24)
                    if game_obj.REMAINING_PELLETES == 0:
                        print("YOU WIN!!")

                next_tile_origin = game_obj.get_tile_origin(next_tile_coords)

                #print("can walk on next tile")
                if game_obj.player_entity.direction == Entity.DIRECTION_RIGHT:
                    game_obj.player_entity.x += 1
                    if game_obj.player_entity.y != next_tile_origin[1]:
                        game_obj.player_entity.y = next_tile_origin[1]
                if game_obj.player_entity.direction == Entity.DIRECTION_LEFT:
                    game_obj.player_entity.x -= 1
                    if game_obj.player_entity.y != next_tile_origin[1]:
                        game_obj.player_entity.y = next_tile_origin[1]
                if game_obj.player_entity.direction == Entity.DIRECTION_UP:
                    game_obj.player_entity.y -= 1
                    if game_obj.player_entity.x != next_tile_origin[0]:
                        game_obj.player_entity.x = next_tile_origin[0]
                if game_obj.player_entity.direction == Entity.DIRECTION_DOWN:
                    game_obj.player_entity.y += 1
                    if game_obj.player_entity.x != next_tile_origin[0]:
                        game_obj.player_entity.x = next_tile_origin[0]
            else:
                game_obj.player_entity.direction = Entity.DIRECTION_NONE


class PieChartChompersGame(TiledGameMap):
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
        self.SCORE = 0
        self.player_property = "player"
        self.player_entity_class = Player
        self.npc_entity_map = {
            "ghost": Ghost
        }
        super().__init__(
            map_json_file,
            camera_width,
            camera_height,
            background_default_tile,
            entity_default_tile,
            player_default_tile,
            cursor_default_tile,
            empty_map_tile,
            use_cursor
        )
        self.REMAINING_PELLETES = self.map_obj["tilesets"][0]["tiles"][4]["count"]
        self.entities[0].direction = Entity.DIRECTION_LEFT

    def game_tick(self):
        super().game_tick()
        for enemy in self.entities:
            # print("player loc: ({}, {})".format(my_game.player_entity.x, my_game.player_entity.y))
            # print("enemy loc: ({}, {})".format(my_game.player_entity.x, my_game.player_entity.y))
            if self.player_entity.is_colliding(enemy):
                self.lose_level()
