"""Corporate colour palette and global matplotlib / seaborn style configuration.

Colours inspired by Butterfield branding:
• Off-white background – `#F8F9FA`
• Dark navy – `#1A2A4B`
• Muted orange – `#C46A2B`
• Complementary teal – `#3E6C72`
• Light blue accent – `#7FA6D6`
"""

from __future__ import annotations

import matplotlib as mpl
import seaborn as sns

# Palette definition
OFF_WHITE = "#F8F9FA"
NAVY = "#1A2A4B"
ORANGE = "#C46A2B"
TEAL = "#3E6C72"
LIGHT_BLUE = "#7FA6D6"

PALETTE = [NAVY, ORANGE, TEAL, LIGHT_BLUE]


def set_theme():
    """Apply global matplotlib & seaborn theme."""

    sns.set_theme(style="white", palette=PALETTE, rc={
        "axes.facecolor": OFF_WHITE,
        "figure.facecolor": OFF_WHITE,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": NAVY,
        "text.color": NAVY,
        "xtick.color": NAVY,
        "ytick.color": NAVY,
        "grid.color": "#D9DCDD",
    })

    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=PALETTE)


# Automatically apply when module imported
set_theme() 