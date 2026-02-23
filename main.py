import pygame  # Import the pygame library togit  use its game development modules

pygame.init()  # Initialize all imported pygame modules (display, event, time, etc.)

screen = pygame.display.set_mode((800, 600))  # Create a window with width=800 and height=600 pixels
pygame.display.set_caption("StrongMemory")  # Set the window title

running = True  # Boolean variable to control the main game loop

while running:  # Start the main game loop (runs until running becomes False)
    
    for event in pygame.event.get():  # Get all events from the event queue
        
        if event.type == pygame.QUIT:  # Check if the user clicked the window close button
            running = False  # Stop the loop to exit the game

pygame.quit()  # Properly uninitialize pygame and close the window