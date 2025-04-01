import pygame
from pygame.locals import *
import os
from OpenGL.GL import *
from OpenGL.GLU import *
from src.game import Game
from src.menu import MainMenu

def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("The Worst - FPS Game")
    
    # Set up OpenGL perspective
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, (display[0] / display[1]), 0.1, 100.0)  # Wider FOV and farther view distance
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)
    
    # Enable point and line smoothing
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    # Enable alpha blending for transparency
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Initialize music system
    try:
        pygame.mixer.init()
        music_path = os.path.join('src', 'assets', 'sound', 'music.mp3')
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.3)  # 50% volume
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print("Background music started")
    except Exception as e:
        print(f"Could not initialize music: {e}")
    
    # Create game instance but don't start yet
    game = Game(display)
    
    # Create main menu
    def start_game_callback():
        # This will be called when Start Game is clicked
        # Lock and hide the mouse cursor for game mode
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    
    main_menu = MainMenu(display, start_game_callback)
    
    # Main game loop
    clock = pygame.time.Clock()
    last_time = pygame.time.get_ticks() / 1000.0
    
    try:
        while True:
            current_time = pygame.time.get_ticks() / 1000.0
            delta_time = current_time - last_time
            last_time = current_time
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    # Clean up and exit
                    if hasattr(game, 'cleanup'):
                        game.cleanup()
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not main_menu.active:
                            # Return to menu if in game
                            main_menu.active = True
                            pygame.mouse.set_visible(True)
                            pygame.event.set_grab(False)
                        else:
                            # Quit if in menu
                            if hasattr(game, 'cleanup'):
                                game.cleanup()
                            pygame.quit()
                            return
            
            # Pass all events to the game if in game mode
            if not main_menu.active:
                # This ensures all events are sent to the game
                game.handle_events(events)
                game.update()
                
                # Clear the screen and depth buffer
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                game.render()
            else:
                main_menu.handle_input(events)
                main_menu.update(delta_time)
                main_menu.render()
            
            pygame.display.flip()
            clock.tick(60)  # Cap at 60 FPS
    except Exception as e:
        print(f"Game crashed: {e}")
    finally:
        # Make sure to stop the music and clean up
        try:
            pygame.mixer.music.stop()
            if hasattr(game, 'cleanup'):
                game.cleanup()
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    main()