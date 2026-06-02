#!/usr/bin/env python3
"""
LBot Dataset Generator V7 - Clean Dataset with Expanded Ranges
================================================================

Generates a comprehensive dataset (~235k examples) for training the V7
encoder-decoder (Seq2Seq) model with data augmentation for robustness.

Key Design Decision:
- Dataset uses ONLY centímetros — no multi-unit in training data
- Distance range: 1-999 cm (covers up to ~10 meters after preprocessing conversion)
- Angle range: ALL integers 1-360 (full circle coverage)
- Unit conversion (m, mm, km, yd, passos) happens in preprocessing BEFORE the model
- Augmentations: missing accents, abbreviations (cm/°), missing punctuation,
  typos, numbers as words, informal language

Distribution:
- ~95,000  Clean examples (standard + informal, cm-only)
- ~50,000  Single perturbation (1 augmentation applied)
- ~40,000  Multi perturbation (2+ augmentations combined)
- ~25,000  Typos
- ~15,000  Numbers as words
- ~10,000  Informal/colloquial augmentations
Total: ~235,000 examples

LBML V4 Format (unchanged):
- Displacement: D<value_cm><direction>; (ex: D40F;, D350F;, D999F;)
- Rotation: R<angle><direction>; (ex: R90R;, R270L;, R360R;)
- Compound: D40F;R90R;D200L;
"""

import random
import re
import unicodedata


# ============================================================================
# VOCABULARY DEFINITIONS
# ============================================================================

# Standard displacement verbs
DISPLACEMENT_VERBS = [
    "vá",
    "ande",
    "mova-se",
    "desloque-se",
    "se mova",
    "caminhe",
    "avance",
    "percorra",
    "se desloque",
    "siga",
]

# Informal displacement verbs
DISPLACEMENT_VERBS_INFORMAL = [
    "vai",
    "segue",
    "mexe",
    "se mexe",
    "bota pra andar",
]

# Standard rotation verbs
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

# Informal rotation verbs
ROTATION_VERBS_INFORMAL = [
    "roda",
    "dobra",
    "faz uma curva de",
    "muda de direção em",
]

# Standard direction phrases for displacement
DIRECTION_PHRASES = {
    'F': ['para frente', 'para a frente', 'à frente', 'adiante', 'pra frente'],
    'B': ['para trás', 'para atrás', 'atrás', 'pra trás'],
    'L': ['para esquerda', 'para a esquerda', 'à esquerda', 'pra esquerda'],
    'R': ['para direita', 'para a direita', 'à direita', 'pra direita'],
}

# Informal direction phrases
DIRECTION_PHRASES_INFORMAL = {
    'F': ['reto', 'em frente', 'pra frente'],
    'B': ['de ré', 'de costas', 'pra trás'],
    'L': ['pra esquerda', 'pro lado esquerdo'],
    'R': ['pra direita', 'pro lado direito'],
}

# Standard rotation direction phrases
ROTATION_DIRECTION_PHRASES = {
    'L': ['para esquerda', 'para a esquerda', 'à esquerda', 'sentido anti-horário', 'no sentido anti-horário'],
    'R': ['para direita', 'para a direita', 'à direita', 'sentido horário', 'no sentido horário'],
}

# Informal rotation direction phrases
ROTATION_DIRECTION_PHRASES_INFORMAL = {
    'L': ['pra esquerda', 'pro lado esquerdo'],
    'R': ['pra direita', 'pro lado direito'],
}

# Distance: ALL integers 1-999 cm
DISTANCE_VALUES_CM = list(range(1, 1000))

# Angles: ALL integers 1-360
ANGLE_VALUES = list(range(1, 361))

# Standard connectors
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

# Informal connectors
CONNECTORS_INFORMAL = [
    ", aí depois ",
    " e aí ",
    ", daí ",
    " e daí ",
    " aí ",
]


# ============================================================================
# NUMBER WORDS (Portuguese) for augmentation
# ============================================================================

_UNITS_WORDS = {
    0: 'zero', 1: 'um', 2: 'dois', 3: 'três', 4: 'quatro', 5: 'cinco',
    6: 'seis', 7: 'sete', 8: 'oito', 9: 'nove', 10: 'dez',
    11: 'onze', 12: 'doze', 13: 'treze', 14: 'quatorze', 15: 'quinze',
    16: 'dezesseis', 17: 'dezessete', 18: 'dezoito', 19: 'dezenove',
}

_TENS_WORDS = {
    20: 'vinte', 30: 'trinta', 40: 'quarenta', 50: 'cinquenta',
    60: 'sessenta', 70: 'setenta', 80: 'oitenta', 90: 'noventa',
}

_HUNDREDS_WORDS = {
    100: 'cem', 200: 'duzentos', 300: 'trezentos', 400: 'quatrocentos',
    500: 'quinhentos', 600: 'seiscentos', 700: 'setecentos', 800: 'oitocentos',
    900: 'novecentos',
}


def number_to_words(n: int) -> str:
    """Convert integer (0-999) to Portuguese words.

    Examples:
        40 -> 'quarenta'
        25 -> 'vinte e cinco'
        100 -> 'cem'
        142 -> 'cento e quarenta e dois'
        350 -> 'trezentos e cinquenta'
        999 -> 'novecentos e noventa e nove'
    """
    if n < 0 or n > 999:
        return str(n)

    if n <= 19:
        return _UNITS_WORDS[n]

    if n < 100:
        tens = (n // 10) * 10
        units = n % 10
        if units == 0:
            return _TENS_WORDS[tens]
        return f"{_TENS_WORDS[tens]} e {_UNITS_WORDS[units]}"

    if n == 100:
        return 'cem'

    hundreds = (n // 100) * 100
    remainder = n % 100

    if hundreds == 100:
        hundreds_word = 'cento'
    else:
        hundreds_word = _HUNDREDS_WORDS[hundreds]

    if remainder == 0:
        return hundreds_word

    remainder_words = number_to_words(remainder)
    return f"{hundreds_word} e {remainder_words}"


# ============================================================================
# AUGMENTATION FUNCTIONS
# ============================================================================

def remove_accents(text: str) -> str:
    """Remove all accents from text using unicode decomposition.

    Examples:
        'centímetros' -> 'centimetros'
        'à frente' -> 'a frente'
    """
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def abbreviate_units(text: str) -> str:
    """Replace full unit names with abbreviations.

    Examples:
        '40 centímetros' -> '40cm'
        '90 graus' -> '90°'
    """
    text = re.sub(r'(\d+)\s+cent[ií]metros?\b', r'\1cm', text)
    text = re.sub(r'(\d+)\s+graus\b', r'\1°', text)
    return text


def remove_punctuation(text: str) -> str:
    """Remove commas and semicolons before connectors.

    Examples:
        ', depois ' -> ' depois '
        '; depois ' -> ' depois '
    """
    text = re.sub(r'[,;.]\s*(depois|em seguida|então|entao|por fim|aí|ai|daí|dai)\b',
                  r' \1', text, flags=re.IGNORECASE)
    return text


def inject_typos(text: str, max_typos: int = 2) -> str:
    """Inject random typos into text.

    Types: character swap, deletion, duplication.
    Only applies to words with 4+ characters.
    """
    words = text.split()
    result = []

    eligible_indices = [
        i for i, w in enumerate(words)
        if len(w) >= 4 and not w.isdigit() and not re.match(r'^\d+$', w)
    ]

    if not eligible_indices:
        return text

    n_typos = min(max_typos, len(eligible_indices))
    typo_indices = set(random.sample(eligible_indices, n_typos))

    for i, word in enumerate(words):
        if i in typo_indices:
            word = _apply_single_typo(word)
        result.append(word)

    return ' '.join(result)


def _apply_single_typo(word: str) -> str:
    """Apply a single typo to a word."""
    if len(word) < 3:
        return word

    typo_type = random.choice(['swap', 'delete', 'duplicate'])
    chars = list(word)

    if typo_type == 'swap' and len(chars) >= 3:
        pos = random.randint(1, len(chars) - 2)
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    elif typo_type == 'delete' and len(chars) >= 4:
        pos = random.randint(1, len(chars) - 2)
        chars.pop(pos)
    elif typo_type == 'duplicate' and len(chars) >= 3:
        pos = random.randint(1, len(chars) - 2)
        chars.insert(pos, chars[pos])

    return ''.join(chars)


def convert_numbers_to_words(text: str) -> str:
    """Convert numeric digits to Portuguese words in text.

    Only converts numbers 0-999 before unit words.

    Examples:
        '40 centímetros' -> 'quarenta centímetros'
        '350 centímetros' -> 'trezentos e cinquenta centímetros'
        '90 graus' -> 'noventa graus'
    """
    def _replace_number(match):
        num = int(match.group(1))
        rest = match.group(2)
        if 0 <= num <= 999:
            return f"{number_to_words(num)} {rest}"
        return match.group(0)

    # Match number followed by unit word (only centímetros and graus in clean dataset)
    text = re.sub(
        r'\b(\d+)\s+(cent[ií]metros?|graus|cm\b)',
        _replace_number, text, flags=re.IGNORECASE
    )
    return text


def informalize(text: str) -> str:
    """Make text more informal/colloquial.

    Examples:
        'vá 40 centímetros para frente' -> 'vai uns 40 centímetros pra frente'
    """
    replacements = [
        (r'\bvá\b', 'vai'),
        (r'\bande\b', random.choice(['vai', 'anda'])),
        (r'\bsiga\b', 'segue'),
        (r'\bgire\b', 'gira'),
        (r'\bvire\b', 'vira'),
        (r'\brode\b', 'roda'),
        (r'\bpara frente\b', 'pra frente'),
        (r'\bpara trás\b', 'pra trás'),
        (r'\bpara atrás\b', 'pra trás'),
        (r'\bpara esquerda\b', 'pra esquerda'),
        (r'\bpara a esquerda\b', 'pra esquerda'),
        (r'\bpara direita\b', 'pra direita'),
        (r'\bpara a direita\b', 'pra direita'),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Optionally add "uns" before number (30% chance)
    if random.random() < 0.3:
        text = re.sub(r'(\b(?:vai|anda|segue|gira|roda|vira)\s+)(\d)', r'\1uns \2', text)

    return text


# ============================================================================
# DATASET GENERATION FUNCTIONS (Clean, cm-only)
# ============================================================================

def generate_simple_displacement(count=35000):
    """
    Generate simple displacement commands using only centímetros (1-999).

    Example: "ande 350 centímetros para frente" -> "D350F;"
    """
    examples = []
    directions = ['F', 'B', 'L', 'R']

    for _ in range(count):
        verb = random.choice(DISPLACEMENT_VERBS)
        direction_code = random.choice(directions)
        direction_phrase = random.choice(DIRECTION_PHRASES[direction_code])

        value = random.choice(DISTANCE_VALUES_CM)
        unit_text = "centímetro" if value == 1 else "centímetros"

        entrada = f"{verb} {value} {unit_text} {direction_phrase}"
        saida = f"D{value}{direction_code};"

        examples.append((entrada, saida))

    return examples


def generate_simple_rotation(count=30000):
    """
    Generate simple rotation commands with angles 1-360.

    Example: "gire 270 graus para direita" -> "R270R;"
    """
    examples = []
    directions = ['L', 'R']

    for _ in range(count):
        verb = random.choice(ROTATION_VERBS)
        angle = random.choice(ANGLE_VALUES)
        direction_code = random.choice(directions)
        direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES[direction_code])

        entrada = f"{verb} {angle} graus {direction_phrase}"
        saida = f"R{angle}{direction_code};"

        examples.append((entrada, saida))

    return examples


def generate_single_action():
    """Generate a single displacement or rotation action (text + LBML)."""
    if random.random() < 0.5:
        # Displacement (cm-only, 1-999)
        verb = random.choice(DISPLACEMENT_VERBS)
        direction_code = random.choice(['F', 'B', 'L', 'R'])
        direction_phrase = random.choice(DIRECTION_PHRASES[direction_code])

        value = random.choice(DISTANCE_VALUES_CM)
        unit_text = "centímetro" if value == 1 else "centímetros"

        action_pt = f"{verb} {value} {unit_text} {direction_phrase}"
        action_lbml = f"D{value}{direction_code};"
    else:
        # Rotation (1-360)
        verb = random.choice(ROTATION_VERBS)
        angle = random.choice(ANGLE_VALUES)
        direction_code = random.choice(['L', 'R'])
        direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES[direction_code])
        action_pt = f"{verb} {angle} graus {direction_phrase}"
        action_lbml = f"R{angle}{direction_code};"

    return action_pt, action_lbml


def generate_compound_command(num_actions):
    """Generate a compound command with 2, 3, or 4 actions."""
    actions_pt = []
    actions_lbml = []

    for _ in range(num_actions):
        action_pt, action_lbml = generate_single_action()
        actions_pt.append(action_pt)
        actions_lbml.append(action_lbml)

    connector = random.choice(CONNECTORS)
    entrada = connector.join(actions_pt)
    saida = ''.join(actions_lbml)

    return (entrada, saida)


def generate_compound_commands(count=20000):
    """
    Generate compound commands with 2-4 actions.

    Distribution: 50% 2-action, 33% 3-action, 17% 4-action
    """
    examples = []

    two_action_count = int(count * 0.5)
    for _ in range(two_action_count):
        examples.append(generate_compound_command(2))

    three_action_count = int(count * 0.33)
    for _ in range(three_action_count):
        examples.append(generate_compound_command(3))

    four_action_count = count - two_action_count - three_action_count
    for _ in range(four_action_count):
        examples.append(generate_compound_command(4))

    return examples


# ============================================================================
# INFORMAL EXAMPLE GENERATION
# ============================================================================

def generate_informal_displacement(count=3000):
    """Generate informal displacement commands (cm-only, 1-999)."""
    examples = []
    directions = ['F', 'B', 'L', 'R']

    for _ in range(count):
        verb = random.choice(DISPLACEMENT_VERBS_INFORMAL)
        value = random.choice(DISTANCE_VALUES_CM)
        direction_code = random.choice(directions)
        direction_phrase = random.choice(DIRECTION_PHRASES_INFORMAL[direction_code])

        unit_text = "centímetro" if value == 1 else "centímetros"
        prefix = "uns " if random.random() < 0.3 else ""

        entrada = f"{verb} {prefix}{value} {unit_text} {direction_phrase}"
        saida = f"D{value}{direction_code};"

        examples.append((entrada, saida))

    return examples


def generate_informal_rotation(count=2000):
    """Generate informal rotation commands (angles 1-360)."""
    examples = []
    directions = ['L', 'R']

    for _ in range(count):
        verb = random.choice(ROTATION_VERBS_INFORMAL)
        angle = random.choice(ANGLE_VALUES)
        direction_code = random.choice(directions)
        direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES_INFORMAL[direction_code])

        entrada = f"{verb} {angle} graus {direction_phrase}"
        saida = f"R{angle}{direction_code};"

        examples.append((entrada, saida))

    return examples


def generate_informal_compound(count=5000):
    """Generate informal compound commands (cm-only 1-999, angles 1-360)."""
    examples = []

    for _ in range(count):
        num_actions = random.choices([2, 3, 4], weights=[0.5, 0.33, 0.17])[0]

        actions_pt = []
        actions_lbml = []

        for _ in range(num_actions):
            if random.random() < 0.5:
                # Informal displacement
                verb = random.choice(DISPLACEMENT_VERBS_INFORMAL + DISPLACEMENT_VERBS[:3])
                value = random.choice(DISTANCE_VALUES_CM)
                direction_code = random.choice(['F', 'B', 'L', 'R'])

                if random.random() < 0.5:
                    direction_phrase = random.choice(DIRECTION_PHRASES_INFORMAL[direction_code])
                else:
                    direction_phrase = random.choice(DIRECTION_PHRASES[direction_code])

                unit_text = "centímetro" if value == 1 else "centímetros"
                action_pt = f"{verb} {value} {unit_text} {direction_phrase}"
                action_lbml = f"D{value}{direction_code};"
            else:
                # Informal rotation
                verb = random.choice(ROTATION_VERBS_INFORMAL + ROTATION_VERBS[:3])
                angle = random.choice(ANGLE_VALUES)
                direction_code = random.choice(['L', 'R'])

                if random.random() < 0.5:
                    direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES_INFORMAL[direction_code])
                else:
                    direction_phrase = random.choice(ROTATION_DIRECTION_PHRASES[direction_code])

                action_pt = f"{verb} {angle} graus {direction_phrase}"
                action_lbml = f"R{angle}{direction_code};"

            actions_pt.append(action_pt)
            actions_lbml.append(action_lbml)

        if random.random() < 0.6:
            connector = random.choice(CONNECTORS_INFORMAL)
        else:
            connector = random.choice(CONNECTORS)

        entrada = connector.join(actions_pt)
        saida = ''.join(actions_lbml)

        examples.append((entrada, saida))

    return examples


# ============================================================================
# AUGMENTATION PIPELINE
# ============================================================================

def apply_single_augmentation(entrada: str) -> str:
    """Apply one random augmentation to an example."""
    aug = random.choice(['no_accents', 'abbreviate', 'no_punctuation'])

    if aug == 'no_accents':
        return remove_accents(entrada)
    elif aug == 'abbreviate':
        return abbreviate_units(entrada)
    elif aug == 'no_punctuation':
        return remove_punctuation(entrada)

    return entrada


def apply_multi_augmentation(entrada: str) -> str:
    """Apply 2-3 random augmentations to an example."""
    augmentations = ['no_accents', 'abbreviate', 'no_punctuation']
    n = random.randint(2, min(3, len(augmentations)))
    selected = random.sample(augmentations, n)

    for aug in selected:
        if aug == 'no_accents':
            entrada = remove_accents(entrada)
        elif aug == 'abbreviate':
            entrada = abbreviate_units(entrada)
        elif aug == 'no_punctuation':
            entrada = remove_punctuation(entrada)

    return entrada


def augment_with_typos(examples: list, count: int) -> list:
    """Create augmented versions with typos."""
    augmented = []
    for _ in range(count):
        entrada, saida = random.choice(examples)
        typo_entrada = inject_typos(entrada, max_typos=random.randint(1, 2))
        augmented.append((typo_entrada, saida))
    return augmented


def augment_with_number_words(examples: list, count: int) -> list:
    """Create augmented versions with numbers written as words."""
    augmented = []
    for _ in range(count):
        entrada, saida = random.choice(examples)
        word_entrada = convert_numbers_to_words(entrada)
        if word_entrada != entrada:
            augmented.append((word_entrada, saida))
        else:
            for backup_entrada, backup_saida in random.sample(examples, min(10, len(examples))):
                word_backup = convert_numbers_to_words(backup_entrada)
                if word_backup != backup_entrada:
                    augmented.append((word_backup, backup_saida))
                    break
            else:
                augmented.append((word_entrada, saida))
    return augmented


def augment_with_informalization(examples: list, count: int) -> list:
    """Create augmented versions with informal language."""
    augmented = []
    for _ in range(count):
        entrada, saida = random.choice(examples)
        informal_entrada = informalize(entrada)
        augmented.append((informal_entrada, saida))
    return augmented


# ============================================================================
# VALIDATION
# ============================================================================

def validate_lbml(lbml_code):
    """Validate LBML V4 format."""
    pattern = r'^(D\d+[FBLR];|R\d+[LR];)+$'
    return re.match(pattern, lbml_code) is not None


def save_dataset(examples, filename='lbot_dataset_v7.txt'):
    """Save dataset in standard format."""
    valid_count = 0
    invalid_count = 0

    with open(filename, 'w', encoding='utf-8') as f:
        for entrada, saida in examples:
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


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_full_dataset():
    """
    Generate complete LBot V7 dataset.

    Total: ~235,000 examples
    - ~95k clean (base cm-only + informal)
    - ~50k single augmentation
    - ~40k multi augmentation
    - ~25k typos
    - ~15k numbers as words
    - ~10k informal augmentations
    """
    print("🤖 LBot Dataset Generator V7 — Clean Dataset + Expanded Ranges")
    print("=" * 60)
    print()
    print("📐 Design: cm-only training (1-999), angles 1-360")
    print("   Unit conversion (m, mm, km, yd, passos) happens in preprocessing")
    print()

    all_examples = []

    # ── Phase 1: Clean examples (~95k) ───────────────────────────
    print("📝 Phase 1: Generating clean examples (cm-only, 1-999)...")

    # 1a. Simple Displacement — cm only, 1-999 (35k)
    print("   📝 Generating 35,000 simple displacement commands...")
    displacement = generate_simple_displacement(35000)
    all_examples.extend(displacement)
    print(f"   ✅ Generated {len(displacement):,}")

    # 1b. Simple Rotation — angles 1-360 (30k)
    print("   📝 Generating 30,000 simple rotation commands (1-360°)...")
    rotation = generate_simple_rotation(30000)
    all_examples.extend(rotation)
    print(f"   ✅ Generated {len(rotation):,}")

    # 1c. Compound Commands — cm only (20k)
    print("   📝 Generating 20,000 compound commands...")
    compound = generate_compound_commands(20000)
    all_examples.extend(compound)
    print(f"   ✅ Generated {len(compound):,}")

    # 1d. Informal examples (10k)
    print("   📝 Generating 10,000 informal examples (1-999 cm, 1-360°)...")
    informal_disp = generate_informal_displacement(3000)
    informal_rot = generate_informal_rotation(2000)
    informal_comp = generate_informal_compound(5000)
    informal_all = informal_disp + informal_rot + informal_comp
    all_examples.extend(informal_all)
    print(f"   ✅ Generated {len(informal_all):,}")

    clean_count = len(all_examples)
    print(f"\n   📊 Total clean examples: {clean_count:,}")

    # ── Phase 2: Augmented examples (~140k) ──────────────────────
    print("\n📝 Phase 2: Generating augmented examples...")

    # 2a. Single augmentation (50k)
    print("   📝 Generating 50,000 single-augmentation examples...")
    single_aug = []
    for _ in range(50000):
        entrada, saida = random.choice(all_examples[:clean_count])
        aug_entrada = apply_single_augmentation(entrada)
        single_aug.append((aug_entrada, saida))
    all_examples.extend(single_aug)
    print(f"   ✅ Generated {len(single_aug):,}")

    # 2b. Multi augmentation (40k)
    print("   📝 Generating 40,000 multi-augmentation examples...")
    multi_aug = []
    for _ in range(40000):
        entrada, saida = random.choice(all_examples[:clean_count])
        aug_entrada = apply_multi_augmentation(entrada)
        multi_aug.append((aug_entrada, saida))
    all_examples.extend(multi_aug)
    print(f"   ✅ Generated {len(multi_aug):,}")

    # 2c. Typos (25k)
    print("   📝 Generating 25,000 typo examples...")
    typo_examples = augment_with_typos(all_examples[:clean_count], 25000)
    all_examples.extend(typo_examples)
    print(f"   ✅ Generated {len(typo_examples):,}")

    # 2d. Number words (15k)
    print("   📝 Generating 15,000 number-as-words examples...")
    number_word_examples = augment_with_number_words(all_examples[:clean_count], 15000)
    all_examples.extend(number_word_examples)
    print(f"   ✅ Generated {len(number_word_examples):,}")

    # 2e. Informal augmentation on clean examples (10k)
    print("   📝 Generating 10,000 informal augmentation examples...")
    informal_aug = augment_with_informalization(all_examples[:clean_count], 10000)
    all_examples.extend(informal_aug)
    print(f"   ✅ Generated {len(informal_aug):,}")

    # ── Phase 3: Shuffle and save ────────────────────────────────
    print(f"\n📊 Total examples before shuffle: {len(all_examples):,}")
    print("🔀 Shuffling dataset...")
    random.shuffle(all_examples)

    # Save to file
    print("💾 Saving dataset...")
    valid = save_dataset(all_examples, 'lbot_dataset_v7.txt')

    # ── Statistics ───────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"📊 Dataset Statistics — LBot V7 (Clean, Expanded Ranges)")
    print(f"{'=' * 60}")
    print(f"   • Total examples: {valid:,}")
    print(f"   • Clean examples: ~{clean_count:,}")
    print(f"   • Single augmentation: ~{len(single_aug):,}")
    print(f"   • Multi augmentation: ~{len(multi_aug):,}")
    print(f"   • Typo examples: ~{len(typo_examples):,}")
    print(f"   • Number-as-words: ~{len(number_word_examples):,}")
    print(f"   • Informal augmentation: ~{len(informal_aug):,}")
    print(f"\n   📐 Coverage:")
    print(f"   • Units in training: ONLY centímetros (other units handled in preprocessing)")
    print(f"   • Distance values: 1-999 cm")
    print(f"   • Angles: 1-360°")
    print(f"   • Displacement verbs: {len(DISPLACEMENT_VERBS)} standard + {len(DISPLACEMENT_VERBS_INFORMAL)} informal")
    print(f"   • Rotation verbs: {len(ROTATION_VERBS)} standard + {len(ROTATION_VERBS_INFORMAL)} informal")
    print(f"   • Connectors: {len(CONNECTORS)} standard + {len(CONNECTORS_INFORMAL)} informal")
    print(f"   • Augmentations: accents, abbreviations, punctuation, typos, number words, informal")
    print()

    # Show sample examples
    print("📋 Sample Examples:")
    print("   ── Clean (small values 1-100) ──")
    small = [(e, s) for e, s in displacement if any(f" {v} " in e for v in range(1, 101))]
    for i in range(min(3, len(small))):
        e, s = small[i]
        print(f"   {i+1}. '{e}' → {s}")

    print("   ── Clean (3-digit values 100-999) ──")
    big = [(e, s) for e, s in displacement if any(f" {v} " in e for v in range(100, 1000))]
    for i in range(min(3, len(big))):
        e, s = big[i]
        print(f"   {i+4}. '{e}' → {s}")

    print("   ── Informal ──")
    for i in range(3):
        e, s = informal_all[i]
        print(f"   {i+7}. '{e}' → {s}")

    print("   ── Augmented (single) ──")
    for i in range(3):
        e, s = single_aug[i]
        print(f"   {i+10}. '{e}' → {s}")

    print("   ── Typos ──")
    for i in range(3):
        e, s = typo_examples[i]
        print(f"   {i+13}. '{e}' → {s}")

    print("   ── Number Words ──")
    for i in range(3):
        e, s = number_word_examples[i]
        print(f"   {i+16}. '{e}' → {s}")

    print()
    print("✅ Dataset generation complete!")
    print(f"📁 File: lbot_dataset_v7.txt")
    print(f"📊 Size: {clean_count:,} clean + ~{valid - clean_count:,} augmented = {valid:,} total")
    print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    random.seed(42)
    generate_full_dataset()
