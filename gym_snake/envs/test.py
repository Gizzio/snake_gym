from snake import Game, Renderer, KeyboardInput

H = 30
W = 30

game = Game(H, W)
renderer = Renderer(game)
input = KeyboardInput(renderer.window)

while True:
    renderer.render_frame()
    action = input.get_input()
    if action:
        game.input(action)
    game.update()

    if game.has_ended():
        renderer.close_window()
        print('THE END')
        
        break
    '''   
    try:
        change = game.changed_tiles
        renderer.render_frame(change)
        action = input.get_input()
        if action:
            game.input(action)
        game.update()

        if game.has_ended():
            print('THE END')
            break
    except:
        print('THE END')
        break
    '''