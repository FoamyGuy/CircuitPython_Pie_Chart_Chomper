import time

import displayio
from foamyguy_waveshare_pico_lcd_1_14 import WavesharePicoLCD114
from TiledGameMap import TiledGameMap
from entity import Entity
import time

TICK_SPEED = 1 / 60
PREV_TICK = 0

PLAYER_SPRITE_CHANGE_SPEED = 1 / 3
PREV_PLAYER_SPRITE_CHANGE = 0

SCORE = 0

lcd = WavesharePicoLCD114()

display = lcd.display

# Make the display context
main_group = displayio.Group()
display.show(main_group)

my_game = TiledGameMap(
    "pacman_map_0.json",
    camera_width=16,
    camera_height=9,
    entity_default_tile=4
)
#print("entity tilegrid (0,0) = {}".format(my_game._map_tilegrid[0, 0]))

main_group.append(my_game)

# Variable to old previous button state
#prev_btn_vals = ugame.buttons.get_pressed()
_new_loc = {"x": my_game.player_loc["x"], "y": my_game.player_loc["y"]}
_moved = False

#print(my_game.tile_properties)
#print("player property {}".format(my_game.get_tile_property(0, "player")))

print(my_game.map_obj["tilesets"][0]["tiles"][4]["count"])
REMAINING_PELLETES = my_game.map_obj["tilesets"][0]["tiles"][4]["count"]

my_game.enemies[0].direction = Entity.DIRECTION_LEFT
while True:
    event = lcd.key_events()
    if event:
        if event.pressed:
            print("{} pressed".format(lcd.KEY_DICT[event.key_number]))
            if event.key_number == lcd.RIGHT:
                my_game.player_entity.direction = Entity.DIRECTION_RIGHT
            if event.key_number == lcd.LEFT:
                my_game.player_entity.direction = Entity.DIRECTION_LEFT
            if event.key_number == lcd.UP:
                my_game.player_entity.direction = Entity.DIRECTION_UP
            if event.key_number == lcd.DOWN:
                my_game.player_entity.direction = Entity.DIRECTION_DOWN

        if event.released:
            print("{} released".format(lcd.KEY_DICT[event.key_number]))

    now = time.monotonic()

    if PREV_TICK + TICK_SPEED < now:
        PREV_TICK = now

        if my_game.player_entity.direction != Entity.DIRECTION_NONE:
            next_pixel_loc = my_game.player_entity.next_pixel_current_direction
            next_tile_coords = {
                "x": next_pixel_loc[0] // my_game._tile_width,
                "y": next_pixel_loc[1] // my_game._tile_height
            }
            #print(next_tile_coords)
            #print(next_pixel_loc)
            if my_game.is_tile_moveable(
                    next_tile_coords
            ):
                #print(my_game.get_tile_name(next_tile_coords))
                if my_game.get_tile_name(next_tile_coords) == "pellet":
                    SCORE += 1
                    print("score +1")
                    REMAINING_PELLETES -= 1
                    #my_game.map_obj['layers'][1]["data"][my_game.get_index_from_coords(next_tile_coords)] = 24
                    my_game.change_map_tile(next_tile_coords, 24)
                    if REMAINING_PELLETES == 0:
                        print("YOU WIN!!")

                for enemy in my_game.enemies:
                    #print("player loc: ({}, {})".format(my_game.player_entity.x, my_game.player_entity.y))
                    #print("enemy loc: ({}, {})".format(my_game.player_entity.x, my_game.player_entity.y))
                    if my_game.player_entity.is_colliding(enemy):
                        print("Player colliding with ghost")
                        main_group.remove(my_game)
                        my_game = TiledGameMap(
                            "pacman_map_0.json",
                            camera_width=16,
                            camera_height=9,
                            entity_default_tile=4
                        )
                        main_group.append(my_game)

                next_tile_origin = my_game.get_tile_origin(next_tile_coords)

                #print("can walk on next tile")
                if my_game.player_entity.direction == Entity.DIRECTION_RIGHT:
                    my_game.player_entity.x += 1
                    if my_game.player_entity.y != next_tile_origin[1]:
                        my_game.player_entity.y = next_tile_origin[1]
                if my_game.player_entity.direction == Entity.DIRECTION_LEFT:
                    my_game.player_entity.x -= 1
                    if my_game.player_entity.y != next_tile_origin[1]:
                        my_game.player_entity.y = next_tile_origin[1]
                if my_game.player_entity.direction == Entity.DIRECTION_UP:
                    my_game.player_entity.y -= 1
                    if my_game.player_entity.x != next_tile_origin[0]:
                        my_game.player_entity.x = next_tile_origin[0]
                if my_game.player_entity.direction == Entity.DIRECTION_DOWN:
                    my_game.player_entity.y += 1
                    if my_game.player_entity.x != next_tile_origin[0]:
                        my_game.player_entity.x = next_tile_origin[0]
            else:
                my_game.player_entity.direction = Entity.DIRECTION_NONE

        # Enemy movement
        for enemy in my_game.enemies:
            if enemy.direction != Entity.DIRECTION_NONE:
                next_pixel_loc = enemy.next_pixel_current_direction
                next_tile_coords = {
                    "x": next_pixel_loc[0] // my_game._tile_width,
                    "y": next_pixel_loc[1] // my_game._tile_height
                }
                # print(next_tile_coords)
                # print(next_pixel_loc)
                if my_game.is_tile_moveable(
                        next_tile_coords
                ):
                    if enemy.direction == Entity.DIRECTION_RIGHT:
                        enemy.x += 1
                    if enemy.direction == Entity.DIRECTION_LEFT:
                        enemy.x -= 1
                    if enemy.direction == Entity.DIRECTION_UP:
                        enemy.y -= 1
                    if enemy.direction == Entity.DIRECTION_DOWN:
                        enemy.y += 1
                else:
                    if enemy.direction == Entity.DIRECTION_RIGHT:
                        print("turning to face up")
                        enemy.direction = Entity.DIRECTION_UP
                    elif enemy.direction == Entity.DIRECTION_LEFT:
                        print("turning to face down")
                        enemy.direction = Entity.DIRECTION_DOWN
                    elif enemy.direction == Entity.DIRECTION_UP:
                        print("turning to face left")
                        enemy.direction = Entity.DIRECTION_LEFT
                    elif enemy.direction == Entity.DIRECTION_DOWN:
                        print("turning to face right")
                        enemy.direction = Entity.DIRECTION_RIGHT

    if my_game.player_entity.direction != Entity.DIRECTION_NONE:
        if PREV_PLAYER_SPRITE_CHANGE + PLAYER_SPRITE_CHANGE_SPEED < now:
            PREV_PLAYER_SPRITE_CHANGE = now
            my_game.player_entity.next_sprite()

    """
    cur_btn_vals = ugame.buttons.get_pressed()  # update button sate

    _new_loc = {"x": my_game.player_loc["x"], "y": my_game.player_loc["y"]}
    # if up button was pressed
    if not prev_btn_vals & ugame.K_UP and cur_btn_vals & ugame.K_UP:
        _new_loc["y"] = _new_loc["y"] - 1
        _moved = True
    # if down button was pressed
    if not prev_btn_vals & ugame.K_DOWN and cur_btn_vals & ugame.K_DOWN:
        _new_loc["y"] = _new_loc["y"] + 1
        _moved = True
    # if right button was pressed
    if not prev_btn_vals & ugame.K_RIGHT and cur_btn_vals & ugame.K_RIGHT:
        _new_loc["x"] = _new_loc["x"] + 1
        _moved = True
    # if left button was pressed
    if not prev_btn_vals & ugame.K_LEFT and cur_btn_vals & ugame.K_LEFT:
        _new_loc["x"] = _new_loc["x"] - 1
        _moved = True

    if _moved:
        print(_new_loc)
        print(my_game.player_loc)
        _moved = False
        print("loc changed")
        _tile_is_movable = my_game.is_tile_moveable(_new_loc)
        print("tile is moveable {}".format(_tile_is_movable))
        if _tile_is_movable:
            my_game.player_loc["x"] = _new_loc["x"]
            my_game.player_loc["y"] = _new_loc["y"]

        # update the the player sprite position
        my_game.update_player_location()

    # update the previous values
    prev_btn_vals = cur_btn_vals
    """
