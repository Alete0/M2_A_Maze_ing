#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   config.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: czuluaga <czuluaga@student.42malaga.com>     +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/06/11 10:09:18 by czuluaga            #+#    #+#            #
#   Updated: 2026/06/11 10:09:19 by czuluaga           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import sys
from dataclasses import dataclass
from typing import Tuple, Optional

Coord = Tuple[int, int]


@dataclass(frozen=True)
class MazeConfig:
    width: int
    height: int
    entry: Coord
    exit: Coord
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def load_config(file_path: str) -> MazeConfig:
    """Load and validate maze configuration from a KEY=VALUE file.

    Args:
        file_path: Path to the configuration file.

    Returns:
        A validated MazeConfig instance.

    Raises:
        SystemExit: If the file is missing, malformed, or contains
        invalid values.
    """
    config_data = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                clean_line = line.split('#', 1)[0].strip()
                if not clean_line:
                    continue

                if '=' not in clean_line:
                    raise ValueError(f"Line {line_num}: Format invalid. "
                                     "Missing '='.")

                key, val = clean_line.split('=', 1)
                config_data[key.strip().upper()] = val.strip()

    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.",
              file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Critical error reading the file: {e}", file=sys.stderr)
        sys.exit(1)

    mandatory_keys = {'WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE',
                      'PERFECT'}
    missing = mandatory_keys - config_data.keys()
    if missing:
        print(f"Error: Mandatory keys are missing: {', '.join(missing)}",
              file=sys.stderr)
        sys.exit(1)

    try:
        width = int(config_data['WIDTH'])
        height = int(config_data['HEIGHT'])
        if width <= 0 or height <= 0:
            raise ValueError("WIDTH and HEIGHT must be positive"
                             "integer number (>0).")

        def parse_coord(
                coord_str: str, w: int, h: int, key_name: str
                ) -> Coord:
            parts = coord_str.split(',')
            if len(parts) != 2:
                raise ValueError(f"Format {key_name} invalid."
                                 "Must be 'x,y'.")
            x, y = int(parts[0].strip()), int(parts[1].strip())
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(f"{key_name} ({x},{y}) out of the boundaries."
                                 f"X: 0-{w-1}, Y: 0-{h-1}.")
            return (x, y)

        entry_coord = parse_coord(config_data['ENTRY'], width, height, 'ENTRY')
        exit_coord = parse_coord(config_data['EXIT'], width, height, 'EXIT')

        if entry_coord == exit_coord:
            raise ValueError("ENTRY and EXIT can't be identical. They must be "
                             "different cells.")

        perfect_str = config_data['PERFECT'].lower()
        if perfect_str in ('true', '1', 'yes'):
            perfect = True
        elif perfect_str in ('false', '0', 'no'):
            perfect = False
        else:
            raise ValueError("PERFECT must be a boolean value "
                             "('True' or 'False').")

        output_file = config_data['OUTPUT_FILE']
        if not output_file:
            raise ValueError("OUTPUT_FILE can not be empty.")

        seed = None
        if 'SEED' in config_data:
            seed = int(config_data['SEED'])

        return MazeConfig(
            width=width,
            height=height,
            entry=entry_coord,
            exit=exit_coord,
            output_file=output_file,
            perfect=perfect,
            seed=seed,
        )

    except ValueError as ve:
        print(f"Validation error on the cofiguration values: {ve}",
              file=sys.stderr)
        sys.exit(1)
