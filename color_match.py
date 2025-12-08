import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
from matplotlib.backend_bases import MouseEvent
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from cie2000 import CIEDE2000

import tkinter as tk
from tkinter.filedialog import askopenfilename



def load_palette(namefile):
    if is_loreal:
        palette_df = pd.read_csv(namefile, header=None, names=["color","R","G","B"])

    else: 
        palette_df = pd.read_csv(namefile, header=None, names=["color","R","G","B"])
        # palette_df = pd.read_csv("fitzpatrick_gpt.csv", header=None, names=["color","R","G","B"])
        # palette_df = pd.read_csv("fit2.csv", header=None, names=["color","R","G","B"])

    palette_df["RGB"] = list(zip(palette_df["R"], palette_df["G"], palette_df["B"]))
    colors = palette_df["RGB"].tolist()
    
    names = palette_df["color"].tolist()
    return colors, names    

def distance_lab(lab1, lab2):
    return CIEDE2000(lab1.get_value_tuple(), lab2.get_value_tuple())

def rgb_to_lab(rgb):
    srgb = sRGBColor(*[x / 255.0 for x in rgb], is_upscaled=False)
    return convert_color(srgb, LabColor)

def closest_color_in_palette(input_rgb, colors, names):
    input_lab = rgb_to_lab(input_rgb)
    
    closest_tone = None
    smallest_distance = float('inf')
    
    distances = []

    for color, name in zip(colors, names):
        color_lab = rgb_to_lab(color)
        distance = distance_lab(input_lab, color_lab)
        # print(name,color_lab,input_lab, distance)
        distances.append((distance, name))  
        
        if distance < smallest_distance:
            smallest_distance = distance
            closest_tone = name
    
    return closest_tone, distances

def plot_comparison(input_rgb, namefile):
    is_loreal = (namefile == "assets/skin_chart_loreal.csv")
    is_fitzpatrick = (namefile == "assets/skin_chart_fitzpatrick.csv")
    colors, names = load_palette(namefile)
    closest_tone, distances = closest_color_in_palette(input_rgb, colors, names)

    if (is_loreal):
        print("Closest L'Oréal tone:", closest_tone)
    elif (is_fitzpatrick):
        print("Closest Fitzpatrick tone:", closest_tone)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    ax1 = axes[0]
    if (is_loreal):
        ax1.set_xlim(0, 6)
        ax1.set_ylim(0, 11)
    else:
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 6)
    for i, (color, name) in enumerate(zip(colors, names)):
        if (is_loreal):
            row = i // 6
            col = i % 6
        else :
            row = i
            col = 0

        normalized_color = [c / 255 for c in color]
        if (is_loreal):
            rect = plt.Rectangle((col, 10 - row), 1, 1, color=normalized_color)
        else:
            rect = plt.Rectangle((col, 5 - row), 1, 1, color=normalized_color)
        ax1.add_patch(rect)
        if is_loreal:
            ax1.text(col + 0.5, 10 - row + 0.5, name, ha="center", va="center", fontsize=8, color="white" if sum(color) < 400 else "black")
        else:
            ax1.text(col + 0.5, 5 - row + 0.5, name, ha="center", va="center", fontsize=8, color="white" if sum(color) < 400 else "black")
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("Color Palette")

    ax2 = axes[1]
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.add_patch(plt.Rectangle((0, 0), 1, 1, color=[x / 255 for x in input_rgb]))
    ax2.text(0.5, 0.5, f"Test Color\n{input_rgb}", ha="center", va="center", fontsize=12, color="white")
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title(f"Test Color (Closest: {closest_tone})")

    ax3 = axes[2]
    if (is_loreal):
        ax3.set_xlim(-1, 6)
        ax3.set_ylim(-1, 11)
    else:
        ax3.set_xlim(-1, 1)
        ax3.set_ylim(-1, 6)

    distance_values = [d[0] for d in distances]
    
    if is_loreal:
        difference_grid = np.array(distance_values).reshape(11, 6)
    else:
        difference_grid = np.array(distance_values).reshape(6, 1)

    difference_grid = np.flipud(difference_grid)

    cax = ax3.imshow(difference_grid, cmap='viridis', interpolation='nearest')

    for i, (distance, name) in enumerate(distances):
        if (is_loreal):
            row = i // 6
            col = i % 6
            max_row=10
        else:
            row = i
            col = 0
            max_row = 5

        ax3.text(col, max_row - row, name, ha="center", va="center", fontsize=8, color="red" if name == closest_tone else "white", fontweight="bold" if name == closest_tone else "normal")
    
    ax3.set_aspect("equal")
    ax3.axis("off")
    ax3.set_title("Color Differences (Delta E)")
    fig.colorbar(cax, ax=ax3)

    plt.tight_layout()
    plt.show()

def compute_ita_from_lab(lab):
    L = lab.lab_l
    b = lab.lab_b
    return math.degrees(math.atan2(L - 50, b))

def compute_ita_from_rgb(rgb):
    lab = rgb_to_lab(tuple([int(x) for x in rgb]))  # ensure ints 0–255
    return compute_ita_from_lab(lab)


def plot_ita_palette(colors, names, palette_title):
    ita_values = [compute_ita_from_rgb(c) for c in colors]

    x = np.arange(len(colors))

    fig, ax = plt.subplots(figsize=(10, 6))

    for xi, ita, rgb, name in zip(x, ita_values, colors, names):
        ax.scatter(
            xi, ita,
            s=200,
            color=[c/255 for c in rgb],
            edgecolor="black",
            linewidth=0.8
        )
        ax.text(xi, ita + 1, name, ha="center", fontsize=8)

    ax.set_title(f"ITA Curve — {palette_title}")
    ax.set_xlabel("Color index")
    ax.set_ylabel("ITA (°)")
    ax.grid(True)

    return fig, ax, ita_values

def add_input_rgb_to_ita_plot(ax, input_rgb):
    ita_input = compute_ita_from_rgb(input_rgb)
    ax.scatter(
        [-1], [ita_input],  # place slightly to the left
        s=300,
        marker="X",
        color=[c/255 for c in input_rgb],
        edgecolor="black",
        linewidth=1.5,
        zorder=5,
    )
    ax.text(-1, ita_input, f"input {input_rgb}\nITA={ita_input:.1f}°",
            ha="right", va="center", fontsize=10)

def plot_ita_map_with_palette(colors, names, input_rgb, title="ITA Skin Map"):
    """
    Plot a 2D ITA map (L* vs b*) with:
    - ITA heatmap
    - ITA contour lines for standard skin tone bands
    - palette colors as points
    - input_rgb as a big X
    """
    # Define L* and b* grid
    L_grid = np.linspace(10, 100, 200)
    b_grid = np.linspace(0, 50, 200)
    L, b = np.meshgrid(L_grid, b_grid)
    
    ITA = np.degrees(np.arctan2(L - 50, b))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ita_levels = [-30, 10, 28, 41, 55]
    contour_labels = ["Dark", "Brown", "Tan", "Intermediate", "Light", "Very Light"]
    CS = ax.contour(b, L, ITA, levels=ita_levels, colors='black', linewidths=1.2,linestyles='dashed')
    ax.clabel(CS, inline=True, fontsize=8, fmt='%1.0f°')
    
    for rgb, name in zip(colors, names):
        lab = rgb_to_lab(rgb)
        ax.scatter(lab.lab_b, lab.lab_l, color=[c/255 for c in rgb], edgecolor='black', s=100)
        ax.text(lab.lab_b, lab.lab_l + 1, name, ha='center', va='bottom', fontsize=8)
    
    lab_input = rgb_to_lab(input_rgb)
    ax.scatter(lab_input.lab_b, lab_input.lab_l, marker='X', s=300,
               color=[c/255 for c in input_rgb], edgecolor='black', linewidth=1.5, zorder=5)
    ax.text(lab_input.lab_b, lab_input.lab_l + 2, f"Input\nITA={compute_ita_from_lab(lab_input):.1f}°",
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel("b* (yellow–blue)")
    ax.set_ylabel("L* (lightness)")
    ax.set_title(title)
    ax.set_xlim(0, 50)
    ax.set_ylim(10, 100)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def plot_L_vs_a(colors, names, input_rgb, title="L* vs a* Skin Plot"):
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot palette points
    for rgb, name in zip(colors, names):
        lab = rgb_to_lab(rgb)
        ax.scatter(lab.lab_a, lab.lab_l, color=[c/255 for c in rgb], edgecolor='black', s=100)
        ax.text(lab.lab_a, lab.lab_l + 1, name, ha='center', va='bottom', fontsize=8)

    # Plot input RGB
    lab_input = rgb_to_lab(input_rgb)
    ax.scatter(lab_input.lab_a, lab_input.lab_l, marker='X', s=300,
               color=[c/255 for c in input_rgb], edgecolor='black', linewidth=1.5, zorder=5)
    ax.text(lab_input.lab_a, lab_input.lab_l + 2,
            f"Input\nL*={lab_input.lab_l:.1f}, a*={lab_input.lab_a:.1f}",
            ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xlabel("a* (green–red)")
    ax.set_ylabel("L* (lightness)")
    ax.set_title(title)
    ax.set_xlim(-10, 30)  # typical skin a* range
    ax.set_ylim(10, 100)   # typical skin L* range
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def plot_L_vs_a_b(colors, names, input_rgb, title_prefix="Skin Tone Analysis"):
    """
    Plot L* vs a* and L* vs b* side by side for palette colors and input RGB.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Prepare input Lab
    lab_input = rgb_to_lab(input_rgb)
    
    # Plot L* vs a*
    ax = axes[0]
    for rgb, name in zip(colors, names):
        lab = rgb_to_lab(rgb)
        ax.scatter(lab.lab_a, lab.lab_l, color=[c/255 for c in rgb], edgecolor='black', s=100)
        ax.text(lab.lab_a, lab.lab_l + 1, name, ha='center', va='bottom', fontsize=8)
    ax.scatter(lab_input.lab_a, lab_input.lab_l, marker='X', s=300,
               color=[c/255 for c in input_rgb], edgecolor='black', linewidth=1.5, zorder=5)
    # ax.text(lab_input.lab_a, lab_input.lab_l + 2,
    #         f"Input\nL*={lab_input.lab_l:.1f}, a*={lab_input.lab_a:.1f}",
    #         ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_xlabel("a* (green–red)")
    ax.set_ylabel("L* (lightness)")
    ax.set_title(f"{title_prefix} — L* vs a*")
    ax.set_xlim(-10, 30)
    ax.set_ylim(10, 100)
    ax.grid(True, alpha=0.3)
    
    # Plot L* vs b*
    ax = axes[1]
    for rgb, name in zip(colors, names):
        lab = rgb_to_lab(rgb)
        ax.scatter(lab.lab_b, lab.lab_l, color=[c/255 for c in rgb], edgecolor='black', s=100)
        ax.text(lab.lab_b, lab.lab_l + 1, name, ha='center', va='bottom', fontsize=8)
    ax.scatter(lab_input.lab_b, lab_input.lab_l, marker='X', s=300,
               color=[c/255 for c in input_rgb], edgecolor='black', linewidth=1.5, zorder=5)
    # ax.text(lab_input.lab_b, lab_input.lab_l + 2,
    #         f"Input\nL*={lab_input.lab_l:.1f}, b*={lab_input.lab_b:.1f}",
    #         ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_xlabel("b* (blue–yellow)")
    ax.set_ylabel("L* (lightness)")
    ax.set_title(f"{title_prefix} — L* vs b*")
    ax.set_xlim(0, 50)
    ax.set_ylim(10, 100)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# Step 4: Function to load and display the image, and capture clicks
def load_image_and_click(image_path, is_loreal=True):
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
        rgb_int = tuple(int(v) for v in rgb[:3])

        print(f"Clicked at: {x}, {y}, RGB: {rgb}")
        
        # Call the comparison plot function
        
       
        plot_comparison(rgb, "assets/skin_chart_loreal.csv")
        plot_comparison(rgb, "assets/skin_chart_fitzpatrick.csv")
        # reload_palette(False)
        # plot_comparison(rgb, False)

        colors_loreal, names_loreal = load_palette("assets/skin_chart_loreal.csv")
        colors_fitz, names_fitz = load_palette("assets/skin_chart_fitzpatrick.csv")

        plot_ita_map_with_palette(colors_loreal, names_loreal, rgb_int, "L'Oréal ITA Map")
        plot_ita_map_with_palette(colors_fitz, names_fitz, rgb_int, "Fitzpatrick ITA Map")

        # plot_L_vs_a(colors_loreal, names_loreal, rgb_int, "L* vs a* L'Oréal Skin Plot")
        # plot_L_vs_a(colors_fitz, names_fitz, rgb_int, "L* vs a* Fitzpatrick Skin Plot")

        # plot_L_vs_a_b(colors_loreal, names_loreal, rgb_int, "L'Oréal Skin Plot")
        # plot_L_vs_a_b(colors_fitz, names_fitz, rgb_int, "Fitzpatrick Skin Plot")

    # Connect the click event to the handler
    fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.show()

# Example usage: Replace with your image path
# image_path = 'hand_noe.jpg'  # Replace with your image path
# image_path = 'hand_kay.jpg'  # Replace with your image path
tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

fn = askopenfilename()
print("user chose", fn)

is_loreal=False
load_image_and_click(fn)
