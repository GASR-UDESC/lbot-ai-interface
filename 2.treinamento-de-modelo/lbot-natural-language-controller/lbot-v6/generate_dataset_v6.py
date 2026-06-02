#!/usr/bin/env python3
"""
LBot Dataset Generator V6 - High-Accuracy Seq2Seq Edition
==========================================================

Generates a comprehensive dataset (~80k examples) for training the V6
encoder-decoder (Seq2Seq) model.

Key Improvements from V5:
- ALL integers 1-100 for distance values (vs only 20 in V5)
- Fixed connector-space bug (trailing space added)
- Expanded vocabulary: 10 displacement verbs, 8 rotation verbs
- More connectors with proper spacing (8 vs 5)
- Compound commands up to 4 actions (vs 3 in V5)
- Larger compound proportion (37.5% vs 25%)
- Better distribution balance

Distribution:
- 25,000 Simple Displacement (D) commands  (31.25%)
- 25,000 Simple Rotation (R) commands      (31.25%)
- 30,000 Compound commands (2-4 actions)   (37.50%)
Total: 80,000 examples

LBML V4 Format:
- Displacement: D<value><direction>; (ex: D40F;)
- Rotation: R<value><direction>; (ex: R90R;)
- Compound: D40F;R90R;D20L;
"""

import random
import re


# ============================================================================
# VOCABULARY DEFINITIONS (Expanded from V5)
# ============================================================================

# Expanded displacement verbs (10, up from 4 in V5)
DISPLACEMENT_VERBS = [
    "vá",
    "ande",
    "mova-se",
    "desloque-se",
    "se mova",
    "caminhe",
    "avance",          # only forward, but we use generically
    "percorra",
    "se desloque",
    "siga",
]

# Expanded rotation verbs (8, up from 4 in V5)
ROTATION_VERBS = [
    "gire",
    "vire",
    "rotacione",
    "faça uma rotação de",
    "rode",
    "faça um giro de",
    "faça uma curva de",
    "mude a direção em",
]

# Standardized direction phrases for displacement
DIRECTION_PHRASES = {
    'F': ['para frente', 'para a frente', 'à frente', 'adiante', 'pra frente'],
    'B': ['para trás', 'para atrás', 'atrás', 'pra trás'],
    'L': ['para esquerda', 'para a esquerda', 'à esquerda', 'pra esquerda'],
    'R': ['para direita', 'para a direita', 'à direita', 'pra direita'],
}

# Standardized rotation direction phrases
ROTATION_DIRECTION_PHRASES = {
    'L': ['para esquerda', 'para a esquerda', 'à esquerda', 'sentido anti-horário', 'no sentido anti-horário'],
    'R': ['para direita', 'para a direita', 'à direita', 'sentido horário', 'no sentido horário'],
}

# ALL integers 1-100 for distance values (was only 20 in V5!)
DISTANCE_VALUES_CM = list(range(1, 101))

# Standard angles only
ANGLE_VALUES = [30, 45, 60, 90, 120, 135, 150, 180]

# Expanded connectors WITH TRAILING SPACE (fixed V5 bug!)
CONNECTORS = [
    ", depois ",
    ", em seguida ",
    " e depois ",
    "; depois ",
    ", então ",
    ". Depois ",
    " e então ",
    ", por fim ",
]


# ============================================================================
# DATASET GENERATION FUNCTIONS
# ============================================================================

def generate_simple_displacement(count=25000):
    """
    Generate simple displacement commands.
    Format: D<value><direction>;

    Example: "ande 40 centímetros para frente" -> "D40F;"
    """
    examples = []
    directions = ['F', 'B', 'L', 'R']

    for _ in range(count):
        verb = random.choice(DISPLACEMENT_VERBS)
        value = random.choice(DISTANCE_VALUES_CM)
        direction_code = random.choice(directions)
        direction_phrase = random.choice(DIRECTION_PHRASES[direction_code])

        # Unit text: "centímetro" for 1, "centímetros" for others
        unit = "centímetro" if value == 1 else "centímetros"

        # Build natural language command
        entrada = f"{verb} {value} {unit} {direction_phrase}"

        # Build LBML code
        saida = f"D{value}{direction_code};"

        examples.append((entrada, saida))

    return examples


def generate_simple_rotation(count=25000):
    """
    Generate simple rotation commands.
    Format: R<angle><direction>;

    Example: "gire 90 graus para direita" -> "R90R;"
    """
    examples = []
    directions = ['L', 'R']

    for _ in range(count):
        verb = random.choice(ROTATION_VERBS)
        angle = random.choice(ANGLE_VALUES)
        direction_code = random.choice(directions)
        direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES[direction_code])

        # Build natural language command
        entrada = f"{verb} {angle} graus {direction_phrase}"

        # Build LBML code
        saida = f"R{angle}{direction_code};"

        examples.append((entrada, saida))

    return examples


def generate_single_action():
    """Generate a single displacement or rotation action (text + LBML)."""
    if random.random() < 0.5:
        # Displacement
        verb = random.choice(DISPLACEMENT_VERBS)
        value = random.choice(DISTANCE_VALUES_CM)
        direction_code = random.choice(['F', 'B', 'L', 'R'])
        direction_phrase = random.choice(DIRECTION_PHRASES[direction_code])
        unit = "centímetro" if value == 1 else "centímetros"
        action_pt = f"{verb} {value} {unit} {direction_phrase}"
        action_lbml = f"D{value}{direction_code};"
    else:
        # Rotation
        verb = random.choice(ROTATION_VERBS)
        angle = random.choice(ANGLE_VALUES)
        direction_code = random.choice(['L', 'R'])
        direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES[direction_code])
        action_pt = f"{verb} {angle} graus {direction_phrase}"
        action_lbml = f"R{angle}{direction_code};"

    return action_pt, action_lbml


def generate_compound_command(num_actions):
    """
    Generate a compound command with 2, 3, or 4 actions.

    Args:
        num_actions: 2, 3, or 4

    Returns:
        (entrada, saida) tuple
    """
    actions_pt = []
    actions_lbml = []

    for _ in range(num_actions):
        action_pt, action_lbml = generate_single_action()
        actions_pt.append(action_pt)
        actions_lbml.append(action_lbml)

    # Join with connector (WITH proper spacing — V5 bug fixed)
    connector = random.choice(CONNECTORS)
    entrada = connector.join(actions_pt)

    # LBML just concatenates
    saida = ''.join(actions_lbml)

    return (entrada, saida)


def generate_compound_commands(count=30000):
    """
    Generate compound commands with 2-4 actions.

    Distribution:
    - 50% with 2 actions (15,000)
    - 33% with 3 actions (10,000)
    - 17% with 4 actions (5,000)
    """
    examples = []

    # 50% with 2 actions
    two_action_count = int(count * 0.5)
    for _ in range(two_action_count):
        examples.append(generate_compound_command(2))

    # 33% with 3 actions
    three_action_count = int(count * 0.33)
    for _ in range(three_action_count):
        examples.append(generate_compound_command(3))

    # 17% with 4 actions (remaining)
    four_action_count = count - two_action_count - three_action_count
    for _ in range(four_action_count):
        examples.append(generate_compound_command(4))

    return examples


def validate_lbml(lbml_code):
    """
    Validate LBML V4 format.

    Format: (D<num><FBLR>;|R<num><LR>;)+
    """
    pattern = r'^(D\d+[FBLR];|R\d+[LR];)+$'
    return re.match(pattern, lbml_code) is not None


def save_dataset(examples, filename='lbot_dataset_v6.txt'):
    """
    Save dataset in the standard format:
    Entrada: <command> | Saída: <lbml>
    """
    valid_count = 0
    invalid_count = 0

    with open(filename, 'w', encoding='utf-8') as f:
        for entrada, saida in examples:
            # Validate LBML before saving
            if not validate_lbml(saida):
                print(f"⚠️  Invalid LBML: {saida} for '{entrada}'")
                invalid_count += 1
                continue

            f.write(f"Entrada: {entrada}\n")
            f.write(f"Saída: {saida}\n")
            f.write("\n")
            valid_count += 1

    print(f"✅ Dataset saved to {filename}")
    print(f"   Valid: {valid_count:,} | Invalid: {invalid_count:,}")
    return valid_count


def generate_full_dataset():
    """
    Generate complete LBot V6 dataset.

    Total: ~80,000 examples
    - 25,000 simple displacement
    - 25,000 simple rotation
    - 30,000 compound (2-4 actions)
    """
    print("🤖 LBot Dataset Generator V6")
    print("=" * 50)
    print()

    all_examples = []

    # 1. Simple Displacement (25k)
    print("📝 Generating 25,000 simple displacement commands...")
    displacement = generate_simple_displacement(25000)
    all_examples.extend(displacement)
    print(f"   ✅ Generated {len(displacement):,} displacement examples")

    # 2. Simple Rotation (25k)
    print("📝 Generating 25,000 simple rotation commands...")
    rotation = generate_simple_rotation(25000)
    all_examples.extend(rotation)
    print(f"   ✅ Generated {len(rotation):,} rotation examples")

    # 3. Compound Commands (30k)
    print("📝 Generating 30,000 compound commands (2-4 actions)...")
    compound = generate_compound_commands(30000)
    all_examples.extend(compound)
    print(f"   ✅ Generated {len(compound):,} compound examples")

    # Shuffle all examples
    print("\n🔀 Shuffling dataset...")
    random.shuffle(all_examples)

    # Save to file
    print("💾 Saving dataset...")
    valid = save_dataset(all_examples, 'lbot_dataset_v6.txt')

    # Statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"   • Total examples: {valid:,}")
    print(f"   • Simple displacement: 25,000 (31.25%)")
    print(f"   • Simple rotation: 25,000 (31.25%)")
    print(f"   • Compound 2-action: ~15,000 (18.75%)")
    print(f"   • Compound 3-action: ~10,000 (12.50%)")
    print(f"   • Compound 4-action: ~5,000 (6.25%)")
    print(f"   • Distance values: ALL integers 1-100 (was only 20 in V5!)")
    print(f"   • Displacement verbs: {len(DISPLACEMENT_VERBS)} (was 4 in V5)")
    print(f"   • Rotation verbs: {len(ROTATION_VERBS)} (was 4 in V5)")
    print(f"   • Connectors: {len(CONNECTORS)} (was 5 in V5, now with spaces)")
    print()

    # Show sample examples
    print("📋 Sample Examples:")
    for i in range(8):
        entrada, saida = all_examples[i]
        print(f"   {i+1}. '{entrada}'")
        print(f"      → {saida}")

    print()
    print("✅ Dataset generation complete!")
    print(f"📁 File: lbot_dataset_v6.txt")
    print(f"📊 Size increase: 40k → 80k examples (2× V5)")
    print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)

    # Generate dataset
    generate_full_dataset()
