"""
ulam3d.py

Interactive 3-D visualization of prime numbers on a cubic-shell analogue
of the Ulam spiral.

Implementation written by ChatGPT (OpenAI) from prompts by Lev Yampolsky,
with iterative testing and debugging feedback from Lev Yampolsky.
"""

import numpy as np
import plotly.graph_objects as go


# ============================================================
# PRIME SIEVE
# ============================================================

def prime_sieve(n):
    is_prime = np.ones(n + 1, dtype=bool)
    is_prime[:2] = False

    for p in range(2, int(np.sqrt(n)) + 1):
        if is_prime[p]:
            is_prime[p * p:n + 1:p] = False

    return is_prime


# ============================================================
# PRIME POWERS
# ============================================================

def prime_powers_mask(n, is_prime):
    """Return mask for p^k with prime p and k >= 2."""
    mask = np.zeros(n + 1, dtype=bool)

    for p in np.where(is_prime)[0]:
        if p < 2:
            continue

        value = p * p

        while value <= n:
            mask[value] = True

            if value > n // p:
                break

            value *= p

    return mask


# ============================================================
# SQUARE RING
# ============================================================

def square_ring(r, z):
    """
    One square ring of Chebyshev radius r in the xy-plane at fixed z.
    r = 0 gives the center point.
    """
    if r == 0:
        return [(0, 0, z)]

    pts = []
    x, y = r, 0
    dx, dy = 0, 1

    for _ in range(8 * r):
        pts.append((x, y, z))
        x += dx
        y += dy

        if abs(x) == abs(y):
            dx, dy = -dy, dx

    return pts


# ============================================================
# CUBIC SHELL
# ============================================================

def cubic_shell(r):
    """
    Generate one cubic shell:
        max(|x|, |y|, |z|) = r
    """
    if r == 0:
        return [(0, 0, 0)]

    pts = []
    s = (-1) ** r

    # First face: center outward
    z0 = -s * r
    for d in range(r + 1):
        pts.extend(square_ring(d, z0))

    # Side walls
    for zz in range(1 - r, r):
        pts.extend(square_ring(r, s * zz))

    # Opposite face: outside inward
    z1 = s * r
    for d in range(r, -1, -1):
        pts.extend(square_ring(d, z1))

    return pts


# ============================================================
# BUILD SPIRAL
# ============================================================

def cubic_spiral(n):
    coords = []
    r = 0

    while len(coords) < n:
        coords.extend(cubic_shell(r))
        r += 1

    return np.array(coords[:n])


# ============================================================
# PARAMETERS
# ============================================================

N = 100_000


# ============================================================
# GENERATE DATA
# ============================================================

print("Building spiral...")

coords = cubic_spiral(N)
numbers = np.arange(1, N + 1)
max_shell = int(np.max(np.abs(coords)))

print("Maximum shell:", max_shell)

is_prime_full = prime_sieve(N)
prime_mask = is_prime_full[1:]

prime_power_full = prime_powers_mask(N, is_prime_full)
prime_power_mask = prime_power_full[1:]

other_composite_mask = np.ones(N, dtype=bool)
other_composite_mask[0] = False  # 1 is neither prime nor composite
other_composite_mask[prime_mask] = False
other_composite_mask[prime_power_mask] = False

prime_numbers = numbers[prime_mask]
prime_coords = coords[prime_mask]

prime_power_numbers = numbers[prime_power_mask]
prime_power_coords = coords[prime_power_mask]

other_coords = coords[other_composite_mask]

prime_mod6 = prime_numbers % 6
prime_mod30 = prime_numbers % 30


# ============================================================
# FIGURE
# ============================================================

fig = go.Figure()


# TRACE 0 — primes colored by value
fig.add_trace(
    go.Scatter3d(
        x=prime_coords[:, 0],
        y=prime_coords[:, 1],
        z=prime_coords[:, 2],
        mode="markers",
        name="Primes",
        visible=True,
        marker=dict(
            size=2.4,
            opacity=0.80,
            color=prime_numbers,
            colorscale="Viridis",
            colorbar=dict(title="prime"),
        ),
        text=[f"{p:,}" for p in prime_numbers],
        hovertemplate=(
            "prime = %{text}<br>"
            "x = %{x}<br>"
            "y = %{y}<br>"
            "z = %{z}"
            "<extra></extra>"
        ),
    )
)


# TRACE 1 — primes mod 6
fig.add_trace(
    go.Scatter3d(
        x=prime_coords[:, 0],
        y=prime_coords[:, 1],
        z=prime_coords[:, 2],
        mode="markers",
        name="Primes mod 6",
        visible=False,
        marker=dict(
            size=2.4,
            opacity=0.80,
            color=prime_mod6,
            colorscale="Turbo",
            cmin=0,
            cmax=5,
            colorbar=dict(title="mod 6"),
        ),
        text=[
            f"{p:,}<br>mod 6 = {r}"
            for p, r in zip(prime_numbers, prime_mod6)
        ],
        hovertemplate=(
            "%{text}<br>"
            "x = %{x}<br>"
            "y = %{y}<br>"
            "z = %{z}"
            "<extra></extra>"
        ),
    )
)


# TRACE 2 — primes mod 30
fig.add_trace(
    go.Scatter3d(
        x=prime_coords[:, 0],
        y=prime_coords[:, 1],
        z=prime_coords[:, 2],
        mode="markers",
        name="Primes mod 30",
        visible=False,
        marker=dict(
            size=2.4,
            opacity=0.80,
            color=prime_mod30,
            colorscale="Rainbow",
            cmin=0,
            cmax=29,
            colorbar=dict(title="mod 30"),
        ),
        text=[
            f"{p:,}<br>mod 30 = {r}"
            for p, r in zip(prime_numbers, prime_mod30)
        ],
        hovertemplate=(
            "%{text}<br>"
            "x = %{x}<br>"
            "y = %{y}<br>"
            "z = %{z}"
            "<extra></extra>"
        ),
    )
)


# TRACE 3 — ordinary composites
fig.add_trace(
    go.Scatter3d(
        x=other_coords[:, 0],
        y=other_coords[:, 1],
        z=other_coords[:, 2],
        mode="markers",
        name="Other composites",
        visible="legendonly",
        marker=dict(
            size=1.0,
            opacity=0.035,
            color="gray",
        ),
        hoverinfo="skip",
    )
)


# TRACE 4 — prime powers
fig.add_trace(
    go.Scatter3d(
        x=prime_power_coords[:, 0],
        y=prime_power_coords[:, 1],
        z=prime_power_coords[:, 2],
        mode="markers",
        name="Prime powers",
        visible="legendonly",
        marker=dict(
            size=3.0,
            opacity=0.95,
            color="orange",
        ),
        text=[f"{n:,}" for n in prime_power_numbers],
        hovertemplate=(
            "prime power = %{text}<br>"
            "x = %{x}<br>"
            "y = %{y}<br>"
            "z = %{z}"
            "<extra></extra>"
        ),
    )
)


# ============================================================
# ROTATION ANIMATION
# ============================================================
#
# IMPORTANT:
# For a 3-D Plotly scene, redraw=True is needed for camera-only
# animation frames. With redraw=False, the Rotate button may appear
# to run while the camera does not actually move.
# ============================================================

rotation_frames = []
number_of_frames = 120
camera_radius = 2.2
camera_height = 0.9

for i in range(number_of_frames):
    theta = 2 * np.pi * i / number_of_frames

    rotation_frames.append(
        go.Frame(
            name=f"rotation_{i}",
            layout=go.Layout(
                scene_camera=dict(
                    eye=dict(
                        x=camera_radius * np.cos(theta),
                        y=camera_radius * np.sin(theta),
                        z=camera_height,
                    ),
                    up=dict(x=0, y=0, z=1),
                )
            ),
        )
    )

fig.frames = rotation_frames


# ============================================================
# SHELL SLIDER
# ============================================================

shell_steps = []

for r in range(1, max_shell + 1):
    lim = r + 0.5

    shell_steps.append(
        dict(
            method="relayout",
            label=str(r),
            args=[
                {
                    "scene.xaxis.range": [-lim, lim],
                    "scene.yaxis.range": [-lim, lim],
                    "scene.zaxis.range": [-lim, lim],
                }
            ],
        )
    )

shell_slider = dict(
    active=max_shell - 1,
    x=0.10,
    y=0.02,
    len=0.80,
    xanchor="left",
    yanchor="bottom",
    currentvalue=dict(
        prefix="Shell radius: ",
        visible=True,
        xanchor="center",
        font=dict(size=16),
    ),
    pad=dict(t=25, b=5),
    steps=shell_steps,
)


# ============================================================
# LAYOUT
# ============================================================

lim = max_shell + 0.5

fig.update_layout(
    title=f"3-D cubic Ulam spiral — integers ≤ {N:,}",

    scene=dict(
        domain=dict(x=[0, 1], y=[0.15, 1]),
        aspectmode="cube",
        bgcolor="black",

        camera=dict(
            eye=dict(x=2.2, y=2.2, z=0.9)
        ),

        xaxis=dict(
            title="x",
            range=[-lim, lim],
            color="white",
            backgroundcolor="black",
            gridcolor="#444444",
        ),

        yaxis=dict(
            title="y",
            range=[-lim, lim],
            color="white",
            backgroundcolor="black",
            gridcolor="#444444",
        ),

        zaxis=dict(
            title="z",
            range=[-lim, lim],
            color="white",
            backgroundcolor="black",
            gridcolor="#444444",
        ),
    ),

    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="white"),

    width=1150,
    height=1000,

    margin=dict(
        l=0,
        r=0,
        b=160,
        t=120,
    ),

    sliders=[shell_slider],

    updatemenus=[
        # Prime coloring mode
        dict(
            type="buttons",
            direction="right",
            x=0.01,
            y=1.10,
            showactive=True,
            buttons=[
                dict(
                    label="Prime value",
                    method="restyle",
                    args=[
                        {"visible": [True, False, False]},
                        [0, 1, 2],
                    ],
                ),
                dict(
                    label="mod 6",
                    method="restyle",
                    args=[
                        {"visible": [False, True, False]},
                        [0, 1, 2],
                    ],
                ),
                dict(
                    label="mod 30",
                    method="restyle",
                    args=[
                        {"visible": [False, False, True]},
                        [0, 1, 2],
                    ],
                ),
            ],
        ),

        # Background mode
        dict(
            type="buttons",
            direction="right",
            x=0.01,
            y=1.04,
            showactive=True,
            buttons=[
                dict(
                    label="Black",
                    method="relayout",
                    args=[
                        {
                            "paper_bgcolor": "black",
                            "plot_bgcolor": "black",
                            "scene.bgcolor": "black",
                            "font.color": "white",
                            "scene.xaxis.color": "white",
                            "scene.yaxis.color": "white",
                            "scene.zaxis.color": "white",
                            "scene.xaxis.backgroundcolor": "black",
                            "scene.yaxis.backgroundcolor": "black",
                            "scene.zaxis.backgroundcolor": "black",
                            "scene.xaxis.gridcolor": "#444444",
                            "scene.yaxis.gridcolor": "#444444",
                            "scene.zaxis.gridcolor": "#444444",
                        }
                    ],
                ),
                dict(
                    label="White",
                    method="relayout",
                    args=[
                        {
                            "paper_bgcolor": "white",
                            "plot_bgcolor": "white",
                            "scene.bgcolor": "white",
                            "font.color": "black",
                            "scene.xaxis.color": "black",
                            "scene.yaxis.color": "black",
                            "scene.zaxis.color": "black",
                            "scene.xaxis.backgroundcolor": "white",
                            "scene.yaxis.backgroundcolor": "white",
                            "scene.zaxis.backgroundcolor": "white",
                            "scene.xaxis.gridcolor": "#CCCCCC",
                            "scene.yaxis.gridcolor": "#CCCCCC",
                            "scene.zaxis.gridcolor": "#CCCCCC",
                        }
                    ],
                ),
            ],
        ),

        # Rotation controls
        dict(
            type="buttons",
            direction="right",
            x=0.67,
            y=1.10,
            showactive=False,
            buttons=[
                dict(
                    label="▶ Rotate",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(
                                duration=60,
                                redraw=True,
                            ),
                            transition=dict(duration=0),
                            fromcurrent=True,
                            mode="immediate",
                        ),
                    ],
                ),
                dict(
                    label="⏸ Pause",
                    method="animate",
                    args=[
                        [None],
                        dict(
                            frame=dict(
                                duration=0,
                                redraw=True,
                            ),
                            transition=dict(duration=0),
                            mode="immediate",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# ============================================================
# DISPLAY
# ============================================================

print("Displaying figure...")
fig.show()
