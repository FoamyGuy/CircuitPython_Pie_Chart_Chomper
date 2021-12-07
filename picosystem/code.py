import board
import digitalio
import displayio
from pi_chart_chompers_lib import PieChartChompersGame
from entity import Entity
import time

TICK_SPEED = 1 / 60
PREV_TICK = 0

PLAYER_SPRITE_CHANGE_SPEED = 1 / 3
PREV_PLAYER_SPRITE_CHANGE = 0

SCORE = 0

btn_down = digitalio.DigitalInOut(board.SW_DOWN)
btn_down.switch_to_input(pull=digitalio.Pull.UP)
btn_down.pull = digitalio.Pull.UP

btn_right = digitalio.DigitalInOut(board.SW_RIGHT)
btn_right.switch_to_input(pull=digitalio.Pull.UP)
btn_right.pull = digitalio.Pull.UP

btn_left = digitalio.DigitalInOut(board.SW_LEFT)
btn_left.switch_to_input(pull=digitalio.Pull.UP)
btn_left.pull = digitalio.Pull.UP

btn_up = digitalio.DigitalInOut(board.SW_UP)
btn_up.switch_to_input(pull=digitalio.Pull.UP)
btn_up.pull = digitalio.Pull.UP


display = board.DISPLAY

# Make the display context
main_group = displayio.Group()
display.show(main_group)

my_game = PieChartChompersGame(
    "pacman_map_2.json",
    camera_width=16,
    camera_height=16,
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


def _lose_level():
    global my_game
    print("Player colliding with ghost")
    main_group.remove(my_game)
    my_game = PieChartChompersGame(
        "pacman_map_0.json",
        camera_width=16,
        camera_height=9,
        entity_default_tile=4
    )
    main_group.append(my_game)
    my_game.lose_level = _lose_level


my_game.lose_level = _lose_level
while True:

    print(btn_right.value)
    #print("{} pressed".format(lcd.KEY_DICT[event.key_number]))
    if not btn_right.value:
        my_game.player_entity.direction = Entity.DIRECTION_RIGHT
    if not btn_left.value:
        my_game.player_entity.direction = Entity.DIRECTION_LEFT
    if not btn_up.value:
        my_game.player_entity.direction = Entity.DIRECTION_UP
    if not btn_down.value:
        my_game.player_entity.direction = Entity.DIRECTION_DOWN



    now = time.monotonic()

    if PREV_TICK + TICK_SPEED < now:
        PREV_TICK = now

        my_game.game_tick()

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
