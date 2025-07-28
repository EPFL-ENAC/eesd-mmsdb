#!/usr/bin/env python3
"""
line_minimum_trace.py

This script calculates the Line of Minimum Trace for:
- Vertical joints staggering properties
- Horizontal bed joint characteristics  
- Wall leaf connections of a masonry wall

Requirements:
- Binary format image (stones labeled as black pixels, mortar as white)
- Wall dimensions (ensure consistent units)

Authors: Mati Ullah Shah, Savvas Saloustros, and Katrin Beyer
Contact: mati.shah@epfl.ch
Last modified: 13 March 2025

Python translation by: GitHub Copilot
Translation date: July 2025

Note: 
- The shortest path calculation uses the `bwgraph` function, originally published by 
  George Abrahams under the MIT License.
- A slight modification has been made to include the alpha weighing factor,
  which accounts for the ratio of fracture energies of the stone-mortar interface to mortar.
- For further details on the `bwgraph` function, visit:
  https://github.com/WD40andTape/
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import networkx as nx
import os
from pathlib import Path
import scipy.io as sio
from bwgraph import bwgraph


def main():
    """Main function to execute the Line of Minimum Trace calculation."""
    
    # ################## USER INPUT REQUIRED BELOW ########################################
    
    # Specify the folder path containing the binary image
    image_file_path = '/mnt/c/Users/eschmann/Downloads/test_eesd.png'  # Update this path
    
    # Specify the folder path where to store the results
    output_folder_path = '.'  # Update this path
    
    # Enter the 2D panel dimensions
    real_length = 149
    real_height = 140
    
    # Enter number of line of minimum trace (LMT)
    number_LMT = 1
    
    # interface weight is the alpha value (choose between 0.1 and 1)
    interface_weight = 1.0
    
    # For Line of minimum trace:
    # - Vertical joints staggering properties, set calculate_LMT = 0
    # - Horizontal bed joint characteristics, set calculate_LMT = 1
    # - Wall leaf connections of a masonry wall, set calculate_LMT = 2
    calculate_LMT = 1
    
    # Adjust image boundaries to avoid LMT detection near edges,
    # boundary_margin is number of pixels. default value set to 5
    boundary_margin = 5
    
    # For manually selecting points to draw line of minimum trace, set draw_LMT = False
    # For automatic drawing of line of minimum trace, set draw_LMT = True
    draw_LMT = True
    
    # Only required for drawing automatic line of minimum trace
    # Specify exact coordinates for start and end points [row, col]
    # Set coordinates to None to use the offset-based method below
    start_coords = [5, 100]        # [row, col] - e.g., [0, 0] for top-left corner
    end_coords = [780 ,400]           # [row, col] - e.g., [399, 599] for specific point, or None for auto-calculate
    
    # Alternative: offset-based positioning (used when start_coords/end_coords are None)
    start_node_x = 80           # Distance from left edge 
    start_node_y = 80           # Distance from top edge
    
    # Specify the distance(in pixels) between two points on panel between two
    # line of minimum trace
    next_node_x = 100
    next_node_y = 100
    
    # ################## USER INPUT REQUIRED ABOVE ##########################################
    
    # Read the binary image
    if not os.path.exists(image_file_path):
        print(f"Error: Image file not found at {image_file_path}")
        print("Please update the image_file_path variable with the correct path.")
        return
    
    image = np.array(Image.open(image_file_path).convert('L'))
    # Convert to binary (assuming white=255 is mortar, black=0 is stone)
    image = (image > 128).astype(np.uint8)
    
    # Apply boundary conditions based on LMT type
    if calculate_LMT == 1:  # Horizontal bed joint
        image[:, :boundary_margin] = 1
        image[:, -boundary_margin:] = 1
        image[:boundary_margin, :] = 0
        image[-boundary_margin:, :] = 0
    else:  # Vertical joints or wall leaf connections
        image[:, :boundary_margin] = 0
        image[:, -boundary_margin:] = 0
        image[:boundary_margin, :] = 1
        image[-boundary_margin:, :] = 1
    
    # Create the graph
    print("Creating graph from binary image...")
    G = bwgraph(image.astype(bool), interface_weight=interface_weight)
    sz = image.shape
    
    pixel_length = sz[1]  # corresponding length in pixels
    pixel_height = sz[0]  # corresponding height in pixels
    
    # Calculate the scale factors for length and height
    length_scale_factor = real_length / pixel_length
    height_scale_factor = real_height / pixel_height
    
    # Initialize results storage
    total_length = []
    
    # Setup plotting
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image, cmap='gray')
    ax.set_title('Click on the image to select two points' if not draw_LMT 
                else 'Automatic Line of Minimum Trace')
    
    print(f"Calculating {number_LMT} line(s) of minimum trace...")
    
    # Main loop for calculating LMT
    for i in range(number_LMT):
        print(f"Processing line {i+1}/{number_LMT}")
        
        if not draw_LMT:
            # Manual point selection
            print("Click on two points in the image window...")
            points = plt.ginput(2, timeout=0)
            if len(points) != 2:
                print("Error: Need exactly 2 points. Skipping this line.")
                continue
                
            start_point = [int(round(points[0][1])), int(round(points[0][0]))]
            end_point = [int(round(points[1][1])), int(round(points[1][0]))]
        else:
            # Automatic point selection
            if start_coords is not None:
                # Use exact coordinates specified by user
                start_point = [start_coords[0], start_coords[1]]
                
                if end_coords is not None:
                    # Use exact end coordinates
                    end_point = [end_coords[0], end_coords[1]]
                else:
                    # Auto-calculate end point as opposite corner
                    end_point = [pixel_height - 1 - start_coords[0], pixel_length - 1 - start_coords[1]]
            else:
                # Use offset-based method (original behavior)
                start_point = [start_node_y, start_node_x]
                end_point = [pixel_height - 1 - start_node_y, pixel_length - 1 - start_node_x]

        # Ensure points are within image bounds
        start_point[0] = max(0, min(start_point[0], pixel_height - 1))
        start_point[1] = max(0, min(start_point[1], pixel_length - 1))
        end_point[0] = max(0, min(end_point[0], pixel_height - 1))
        end_point[1] = max(0, min(end_point[1], pixel_length - 1))
        
        # Check if points are on valid mortar (white) regions
        start_is_mortar = image[start_point[0], start_point[1]] == 1
        end_is_mortar = image[end_point[0], end_point[1]] == 1
        
        if not start_is_mortar:
            print(f"Warning: Start point {start_point} is on stone (black). Trying to find nearest mortar pixel...")
            # Find nearest mortar pixel within a small radius
            found_mortar = False
            for radius in range(1, 10):
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        new_y = start_point[0] + dy
                        new_x = start_point[1] + dx
                        if (0 <= new_y < pixel_height and 0 <= new_x < pixel_length and 
                            image[new_y, new_x] == 1):
                            start_point = [new_y, new_x]
                            print(f"  Found mortar at {start_point}")
                            found_mortar = True
                            break
                    if found_mortar:
                        break
                if found_mortar:
                    break
            
            if not found_mortar:
                print(f"Error: No mortar found near start point. Skipping line {i+1}")
                continue
        
        if not end_is_mortar:
            print(f"Warning: End point {end_point} is on stone (black). Trying to find nearest mortar pixel...")
            # Find nearest mortar pixel within a small radius
            found_mortar = False
            for radius in range(1, 10):
                for dy in range(-radius, radius + 1):
                    for dx in range(-radius, radius + 1):
                        new_y = end_point[0] + dy
                        new_x = end_point[1] + dx
                        if (0 <= new_y < pixel_height and 0 <= new_x < pixel_length and 
                            image[new_y, new_x] == 1):
                            end_point = [new_y, new_x]
                            print(f"  Found mortar at {end_point}")
                            found_mortar = True
                            break
                    if found_mortar:
                        break
                if found_mortar:
                    break
            
            if not found_mortar:
                print(f"Error: No mortar found near end point. Skipping line {i+1}")
                continue
        
        print(f"Using points: Start {start_point}, End {end_point}")
        
        # Convert to linear indices
        source = np.ravel_multi_index((start_point[0], start_point[1]), sz)
        target = np.ravel_multi_index((end_point[0], end_point[1]), sz)
        
        # Check if nodes exist in graph
        if source not in G.nodes or target not in G.nodes:
            print(f"Warning: Start or end point not in mortar (white) region. "
                  f"Skipping line {i+1}")
            continue
        
        try:
            # Calculate shortest path between start and end points
            path_nodes = nx.shortest_path(G, source=source, target=target, weight='weight')
            
            # Convert linear indices back to 2D coordinates
            path_coords = [np.unravel_index(node, sz) for node in path_nodes]
            pi = [coord[0] for coord in path_coords]
            pj = [coord[1] for coord in path_coords]
            
            # Plot the shortest path
            ax.plot(pj, pi, 'r-', linewidth=4, label=f'LMT {i+1}')
            ax.plot(start_point[1], start_point[0], 'go', markersize=10, linewidth=2)
            ax.plot(end_point[1], end_point[0], 'go', markersize=10, linewidth=2)
            
            # Update the starting points for the next line
            start_node_x += next_node_x
            start_node_y += next_node_y
            
            # Scale the path coordinates to real-world units
            pi_scaled = np.array(pi) * height_scale_factor
            pj_scaled = np.array(pj) * length_scale_factor
            
            # Combine x and y coordinates into a matrix
            zigzag_coordinates = np.column_stack((pj_scaled, pi_scaled))
            
            # Calculate the Euclidean distances between consecutive points
            distances = np.sqrt(np.sum(np.diff(zigzag_coordinates, axis=0)**2, axis=1))
            
            # Sum up the distances to get the total length
            total_length.append(np.sum(distances))
            
            print(f"Line {i+1} total length: {total_length[-1]:.2f} units")
            
        except nx.NetworkXNoPath:
            print(f"No path found between selected points for line {i+1}. "
                  f"Points may be in disconnected regions.")
            continue
        except Exception as e:
            print(f"Error calculating path for line {i+1}: {str(e)}")
            continue
    
    if not total_length:
        print("No valid paths were calculated. Exiting.")
        return
    
    # LMT calculation and results saving
    total_length = np.array(total_length)
    
    # Compute LMT based on the selected option
    if calculate_LMT == 0:
        LMT_type = 'vertical'
        LMT_result = total_length / real_height
    elif calculate_LMT == 1:
        LMT_type = 'horizontal'
        LMT_result = total_length / real_length
    else:
        LMT_type = 'wall_leaf_connection'
        LMT_result = total_length / real_height
        
    # Ensure LMT values are not less than 1
    LMT_result = np.maximum(LMT_result, 1.0)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder_path, exist_ok=True)
    
    # Generate file names
    base_name = Path(image_file_path).stem
    output_image_name = f"{base_name}_{LMT_type}_LMT.png"
    output_data_file_name = f"{base_name}_{LMT_type}_LMT.mat"
    
    # Save results
    ax.legend()
    ax.set_title(f'{LMT_type.title()} Line of Minimum Trace')
    
    image_path = os.path.join(output_folder_path, output_image_name)
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    print(f"Image saved to: {image_path}")
    
    data_path = os.path.join(output_folder_path, output_data_file_name)
    sio.savemat(data_path, {'LMT_result': LMT_result})
    print(f"Data saved to: {data_path}")
    
    # Print results summary
    print("\n" + "="*50)
    print("RESULTS SUMMARY")
    print("="*50)
    print(f"LMT Type: {LMT_type}")
    print(f"Number of lines calculated: {len(LMT_result)}")
    print(f"LMT Results: {LMT_result}")
    print(f"Mean LMT: {np.mean(LMT_result):.3f}")
    if len(LMT_result) > 1:
        print(f"Standard deviation: {np.std(LMT_result):.3f}")
    print("="*50)
    
    plt.show()


def interactive_point_selection(image, num_points=2):
    """
    Interactive point selection with visual feedback.
    
    Parameters
    ----------
    image : np.ndarray
        Binary image for point selection
    num_points : int
        Number of points to select
        
    Returns
    -------
    list
        List of selected points as [row, col] coordinates
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(image, cmap='gray')
    ax.set_title(f'Select {num_points} points by clicking on the image')
    
    points = []
    
    def onclick(event):
        if event.inaxes != ax:
            return
        if len(points) < num_points:
            points.append([int(round(event.ydata)), int(round(event.xdata))])
            ax.plot(event.xdata, event.ydata, 'ro', markersize=8)
            ax.text(event.xdata, event.ydata, f'  Point {len(points)}', 
                   fontsize=12, color='red')
            plt.draw()
            
            if len(points) == num_points:
                ax.set_title('Point selection complete. Close window to continue.')
    
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    
    return points


if __name__ == "__main__":
    main()
