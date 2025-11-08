import os
# run headless
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import time
import threading
import pygame
import sys
sys.path.insert(0, r"c:\Dev\snake_game")
import main

# helper to post key presses
def post_events():
    # wait for initialization
    time.sleep(1.0)
    try:
        # simulate: right x10, down x5, left x10, up x5
        for _ in range(10):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}))
            time.sleep(0.05)
        for _ in range(5):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
            time.sleep(0.05)
        for _ in range(10):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}))
            time.sleep(0.05)
        for _ in range(5):
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}))
            time.sleep(0.05)
        # toggle god mode on/off
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_9}))
        time.sleep(0.5)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_9}))
        # toggle music (if available)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_m}))
        time.sleep(1.0)
        # pause and resume
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
        time.sleep(0.5)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE}))
        time.sleep(1.0)
        # quit by posting QUIT
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    except Exception as e:
        print('Error posting events:', e)

threading.Thread(target=post_events, daemon=True).start()

# run the game (this will use the dummy video driver)
try:
    main.run_game()
except SystemExit:
    pass
except Exception as e:
    print('Error during automated run:', e)
    raise
