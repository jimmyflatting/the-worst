class InputHandler:
    def __init__(self):
        self.keys = {}
        self.mouse_buttons = {}
        self.mouse_position = (0, 0)

    def update(self):
        self.keys = pygame.key.get_pressed()
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_position = pygame.mouse.get_pos()

    def is_key_pressed(self, key):
        return self.keys.get(key, False)

    def is_mouse_button_pressed(self, button):
        return self.mouse_buttons.get(button, False)

    def get_mouse_position(self):
        return self.mouse_position

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()