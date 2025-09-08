# utils.py
# Utility functions and data for Nano Banana CFD

# Prepare all three input/output image pairs as a single list alternating input/output
def get_image_pairs():
    return [
        ("examples/airfoil 0 input.png", "examples/airfoil 0 output.png"),
        ("examples/airfoil 10 input.png", "examples/airfoil 10 output.png"),
        ("examples/airfoil 20 input.png", "examples/airfoil 20 output.png"),
    ]
