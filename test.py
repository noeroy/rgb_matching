import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.backend_bases import MouseEvent
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color

palette_df = pd.read_csv("skin_chart_loreal.csv", header=None, names=["color","R","G","B"])
palette_df["RGB"] = list(zip(palette_df["R"], palette_df["G"], palette_df["B"]))
colors = palette_df["RGB"].tolist()
names = palette_df["color"].tolist()

def distance_lab(lab1, lab2):
    return np.sqrt(pow(lab1.lab_l - lab2.lab_l,2)+pow(lab1.lab_a - lab2.lab_a,2)+pow(lab1.lab_b - lab2.lab_b,2))


# Assuming 'colors' and 'names' are defined already as in previous code

# Step 1: Function to convert RGB to Lab
def rgb_to_lab(rgb):
    srgb = sRGBColor(*[x / 255.0 for x in rgb], is_upscaled=False)
    return convert_color(srgb, LabColor)

# Step 2: Function to find the closest color in the palette
def closest_color_in_palette(input_rgb):
    input_lab = rgb_to_lab(input_rgb)
    
    closest_tone = None
    smallest_distance = float('inf')
    
    distances = []
    
    # Loop through the palette and calculate the Euclidean distance in Lab space
    for color, name in zip(colors, names):
        color_lab = rgb_to_lab(color)
        distance = distance_lab(input_lab, color_lab)
        distances.append((distance, name))  # Store the distance and name as a tuple
        
        if distance < smallest_distance:
            smallest_distance = distance
            closest_tone = name
    
    return closest_tone, distances

# Step 3: Function to plot the three panels
def plot_comparison(input_rgb):
    # Step 3.1: Get the closest color and the distances
    closest_tone, distances = closest_color_in_palette(input_rgb)

    # Step 3.2: Set up the figure with 3 panels
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Panel 1: Color Palette
    ax1 = axes[0]
    ax1.set_xlim(0, 6)
    ax1.set_ylim(0, 11)
    for i, (color, name) in enumerate(zip(colors, names)):
        row = i // 6
        col = i % 6
        normalized_color = [c / 255 for c in color]
        rect = plt.Rectangle((col, 10 - row), 1, 1, color=normalized_color)
        ax1.add_patch(rect)
        ax1.text(col + 0.5, 10 - row + 0.5, name, ha="center", va="center", fontsize=8, color="white" if sum(color) < 400 else "black")
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("Color Palette")

    # Panel 2: Test Color
    ax2 = axes[1]
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.add_patch(plt.Rectangle((0, 0), 1, 1, color=[x / 255 for x in input_rgb]))
    ax2.text(0.5, 0.5, f"Test Color\n{input_rgb}", ha="center", va="center", fontsize=12, color="white")
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title(f"Test Color (Closest: {closest_tone})")

    # Panel 3: Difference Heatmap
    ax3 = axes[2]
    ax3.set_xlim(-1, 6)
    ax3.set_ylim(-1, 11)

    # Extract only the distance values for the heatmap
    distance_values = [d[0] for d in distances]
    
    # Reshape to match the palette grid size (11 rows, 6 columns)
    difference_grid = np.array(distance_values).reshape(11, 6)

    # Flip the grid vertically so that the top is at the top and the bottom at the bottom
    difference_grid = np.flipud(difference_grid)

    # Create the heatmap
    cax = ax3.imshow(difference_grid, cmap='viridis', interpolation='nearest')

    # Annotate with color names and highlight the closest color
    for i, (distance, name) in enumerate(distances):
        row = i // 6
        col = i % 6
        # Adjusting the text position to be centered in the cells
        ax3.text(col, 10 - row, name, ha="center", va="center", fontsize=8, color="red" if name == closest_tone else "white", fontweight="bold" if name == closest_tone else "normal")
    
    ax3.set_aspect("equal")
    ax3.axis("off")
    ax3.set_title("Color Differences (Delta E)")
    fig.colorbar(cax, ax=ax3)

    # Show the plot
    plt.tight_layout()
    plt.show()

# Step 4: Function to load and display the image, and capture clicks
def load_image_and_click(image_path):
    img = plt.imread(image_path)
    
    fig, ax = plt.subplots()
    ax.imshow(img)
    ax.axis('off')  # Hide axes
    
    def on_click(event: MouseEvent):
        if event.inaxes != ax:
            return  # Click was outside the image
        # Get the RGB value at the click position
        x, y = int(event.xdata), int(event.ydata)
        rgb = img[y, x]  # img[y, x] gives the (R, G, B) value
        print(f"Clicked at: {x}, {y}, RGB: {rgb}")
        
        # Call the comparison plot function
        plot_comparison(rgb)

    # Connect the click event to the handler
    fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.show()

# Example usage: Replace with your image path
image_path = 'hand.jpg'  # Replace with your image path
load_image_and_click(image_path)