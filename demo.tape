# VHS Demo Recording for Demyst
# Records a demo of Computational Mirage detection

Output demo.gif

Set FontSize 16
Set Width 900
Set Height 500
Set Theme "Dracula"
Set Padding 20

# Show the title
Type "# Demyst - Scientific Integrity Linter" Sleep 500ms Enter
Sleep 1s

# Show the problem file
Type "# Let's check this AI safety code for hidden issues..." Sleep 500ms Enter
Sleep 500ms
Type "cat examples/swarm_collapse.py | head -25" Sleep 300ms Enter
Sleep 3s

# Clear and run demyst
Type "clear" Enter
Sleep 500ms

# Run demyst mirage detection
Type "# Running Demyst to detect Computational Mirages..." Sleep 500ms Enter
Sleep 500ms
Type "demyst mirage examples/swarm_collapse.py" Sleep 300ms Enter
Sleep 4s

# Explain the finding
Type "" Enter
Type "# Found! np.mean() hides the rogue agent (0.0 alignment)" Sleep 500ms Enter
Type "# Average = 0.999 looks safe, but 1 agent will cause cascade failure" Sleep 500ms Enter
Sleep 3s
