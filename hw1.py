import cv2
import numpy as np

def main():

    image_path = 'box.jpeg'
    image = cv2.imread(image_path)

    """
    points = []

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (255, 0, 0), -1) # Mark the selected point
            cv2.imshow('Image', image)

    cv2.imshow('Image', image)
    cv2.setMouseCallback('Image', click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print("Selected points:", points)
    # Choose corner points (and maybe middle for left side)
    # Assign 3D coordinates as in the picture
    """
    
    # Solving for camera matrix:

    # 3D points
    points_3D = np.array([
        [0, 2, 1],
        [1, 2, 1],
        [0, 1, 1],
        [1, 1, 1],
        [0, 0, 1],
        [1, 0, 1],
        [0, 2, 0],
        [0, 1, 0],
        [0, 0, 0],
        [1, 0, 0]
    ])

    # 2D points
    points_2D = np.array([
        [48, 201],
        [426, 103],
        [273, 346],
        [619, 177],
        [501, 501],
        [908, 284],
        [153, 531],
        [284, 649],
        [503, 851],
        [811, 623]
    ])

    # Forming the Q matrix
    Q = []
    for i in range(len(points_3D)):
        X, Y, Z = points_3D[i]
        x, y = points_2D[i]
        Q.append([-X, -Y, -Z, -1, 0, 0, 0, 0, x*X, x*Y, x*Z, x])
        Q.append([0, 0, 0, 0, -X, -Y, -Z, -1, y*X, y*Y, y*Z, y])

    Q = np.array(Q)

    # Solve for m using SVD
    U, S, Vt = np.linalg.svd(Q)
    m = Vt[-1]  # The last row of V^T

    # Reshape m to form the camera matrix M
    M = m.reshape(3, 4)

    print("Camera Matrix M:")
    print(M)

    #######################################################################

    
    # Placing cube
    cube_vertices = np.array([
    [0, 0, 0, 1],  # Vertex 0
    [0, 0, 1, 1],  # Vertex 1
    [0, 1, 0, 1],  # Vertex 2
    [0, 1, 1, 1],  # Vertex 3
    [1, 0, 0, 1],  # Vertex 4
    [1, 0, 1, 1],  # Vertex 5
    [1, 1, 0, 1],  # Vertex 6
    [1, 1, 1, 1]   # Vertex 7
    ])

    projected_vertices = cube_vertices @ M.T  # Transpose M to align dimensions for multiplication
    projected_vertices = projected_vertices[:, :2] / projected_vertices[:, [2]]

    # Define the cube edges
    edges = [
        (0, 1), (1, 3), (3, 2), (2, 0),  # Top face
        (4, 5), (5, 7), (7, 6), (6, 4),  # Bottom face
        (0, 4), (1, 5), (3, 7), (2, 6)   # Side edges connecting top and bottom faces
    ]

    # Draw the edges
    for start, end in edges:
        start_point = tuple(projected_vertices[start].astype(int))
        end_point = tuple(projected_vertices[end].astype(int))
        cv2.line(image, start_point, end_point, (0, 255, 0), 3)

    cv2.imshow('Image with Cube', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    
    #######################################################################


    """
    # Try to draw a sphere
    num_points = 30

    def generate_sphere_points(center, radius, num_points=num_points):
        points = []
        for phi in np.linspace(0, np.pi, num_points):
            for theta in np.linspace(0, 2 * np.pi, num_points):
                x = center[0] + radius * np.cos(theta) * np.sin(phi)
                y = center[1] + radius * np.sin(theta) * np.sin(phi)
                z = center[2] + radius * np.cos(phi)
                points.append([x, y, z, 1])  # Homogeneous coordinates
        return np.array(points)

    center = [0.5, 0.5, 0.5]  # Assuming the sphere is centered at this point in the box's coordinate system
    radius = 0.5  # Assuming a radius that fits within the unit box
    sphere_points = generate_sphere_points(center, radius)


    # Project the sphere's points using the camera matrix M
    projected_sphere_points = sphere_points @ M.T  # Assuming M is your camera matrix
    projected_sphere_points = projected_sphere_points[:, :2] / projected_sphere_points[:, [2]]

  # This should match the number used in generate_sphere_points
    points_per_line = num_points

    # Reshape the projected points for easier handling
    reshaped_points = projected_sphere_points.reshape(num_points, num_points, 2)

    # Draw longitude lines (connect points vertically)
    for i in range(num_points):
        for j in range(1, num_points):
            start_point = tuple(reshaped_points[j - 1, i].astype(int))
            end_point = tuple(reshaped_points[j, i].astype(int))
            cv2.line(image, start_point, end_point, (0, 255, 0), 1)

    # Draw latitude lines (connect points within each 'phi' slice)
    for i in range(num_points):
        for j in range(1, num_points):
            start_point = tuple(reshaped_points[i, j - 1].astype(int))
            end_point = tuple(reshaped_points[i, j].astype(int))
            cv2.line(image, start_point, end_point, (0, 255, 0), 1)

    # Close the loops for the last points
    for i in range(num_points - 1):
        # Close the latitude loop
        start_point = tuple(reshaped_points[i, 0].astype(int))
        end_point = tuple(reshaped_points[i, -1].astype(int))
        cv2.line(image, start_point, end_point, (0, 255, 0), 1)

    if not np.allclose(reshaped_points[0, 0], reshaped_points[-1, 0]):
        for i in range(num_points):
            start_point = tuple(reshaped_points[0, i].astype(int))
            end_point = tuple(reshaped_points[-1, i].astype(int))
            cv2.line(image, start_point, end_point, (0, 255, 0), 1)

    # Show the image with the sphere
    cv2.imshow('Image with Sphere', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    """

if __name__ == '__main__':
    main()