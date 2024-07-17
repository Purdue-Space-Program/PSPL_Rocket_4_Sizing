# Rocket 4 Sizing

This repository contains the sizing code for Rocket 4. This is work in progress and is subject to change.

## Filesystem Hierarchy

```plaintext
└── PSPL_ROCKET_4_SIZING/
    ├── data/
    │   ├── inputs/
    │   │   └── rocket_defining_inputs.xlsx
    │   └── outputs/
    │       └── YYYY-MM-DD_HH-MM-SS/
    │           ├── possible_rockets.xlsx
    |           └── rocket_defining_inputs.xlsx
    ├── scripts/
    │   ├── combustion.py
    │   ├── propulsion.py
    │   ├── structural.py
    │   ├── tanks.py
    │   └── traj.py
    ├── tests/
    │   ├── test_combustion.py
    │   ├── test_propulsion.py
    │   ├── test_structural.py
    │   ├── test_tanks.py
    │   └── test_traj.py
    ├── utils/
    │   ├── clean_up.py
    │   └── rocket_defining_input_handler.py
    ├── main.py
    ├── .gitignore
    ├── README.md
    └── requirements.txt

```

## Installation

1. Clone the repository

```bash
git clone https://github.com/Purdue-Space-Program/PSPL_Rocket_4_Sizing.git
```

2. Navigate to the repository

```bash
cd PSPL_Rocket_4_Sizing
```

3. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
```

4. Install the required packages

```bash
pip3 install -r requirements.txt
```

## Usage

1. Edit the `rocket_defining_inputs.xlsx` file in the `data/inputs/` directory to define the rocket's parameters.
2. Run the main script

```bash
python3 main.py
```

## Additional Information

- **Data**: Input data should be placed in `data/inputs/`. Output data will be generated in `data/outputs/`.
- **Scripts**: Contains the core logic for different components of the sizing script.
- **Tests**: Unit tests for ensuring the correctness of the code.
- **Utils**: Utility functions for common tasks.
