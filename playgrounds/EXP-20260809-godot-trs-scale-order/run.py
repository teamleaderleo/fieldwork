#!/usr/bin/env python3
import json
import math


def rotation_matrix(axis, angle):
    norm = math.sqrt(sum(v * v for v in axis))
    x, y, z = [v / norm for v in axis]
    c = math.cos(angle)
    s = math.sin(angle)
    one_minus_c = 1.0 - c
    return [
        [c + x * x * one_minus_c, x * y * one_minus_c - z * s, x * z * one_minus_c + y * s],
        [y * x * one_minus_c + z * s, c + y * y * one_minus_c, y * z * one_minus_c - x * s],
        [z * x * one_minus_c - y * s, z * y * one_minus_c + x * s, c + z * z * one_minus_c],
    ]


def left_scale(matrix, scale):
    return [[scale[i] * matrix[i][j] for j in range(3)] for i in range(3)]


def right_scale(matrix, scale):
    return [[matrix[i][j] * scale[j] for j in range(3)] for i in range(3)]


def compare_case(name, axis, angle, scale):
    rotation = rotation_matrix(axis, angle)
    left = left_scale(rotation, scale)
    right = right_scale(rotation, scale)
    differences = [abs(left[i][j] - right[i][j]) for i in range(3) for j in range(3)]
    return {
        "name": name,
        "axis": axis,
        "angle": angle,
        "scale": scale,
        "max_abs_element_diff": max(differences),
        "frobenius_diff": math.sqrt(sum(value * value for value in differences)),
        "left_scaled_S_times_R": left,
        "right_scaled_R_times_S": right,
    }


axis = (1.0, 2.0, 3.0)
cases = [
    ("nonuniform_positive", axis, 0.7, (2.0, 1.0, 3.0)),
    ("uniform_positive", axis, 0.7, (2.0, 2.0, 2.0)),
    ("identity_rotation", axis, 0.0, (2.0, 1.0, 3.0)),
    ("nonuniform_negative_x", axis, 0.7, (-2.0, 1.0, 3.0)),
    ("mixed_negative", axis, 0.7, (-2.0, -1.0, 3.0)),
    ("uniform_negative", axis, 0.7, (-2.0, -2.0, -2.0)),
]

print(json.dumps({"cases": [compare_case(*case) for case in cases]}, indent=2))
