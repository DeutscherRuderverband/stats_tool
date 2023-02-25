ALLOWED_COMPETITION_TYPES_MAPPING = {
    'ID_NF': 'ID',
    'CONT NF': 'CONT',
    'WCp 1': 'WCh 1',
    'WCp 2': 'WCh 2',
    'WCp 3': 'WCh 3',
    'WCH': 'WCh',
    'JWCH': 'JWCh',
    'MASTER_NF': 'MASTER',
    'YOG': 'YOG',
    'OG': 'OG',
    'PG': 'PG',
    'ERCC': 'ERCC',
    'ECH': 'ECh',
    'EJCH': 'EJCh',
    'WCH IE': 'WCh IE',
}

RELEVANT_CMP_TYPE_ABBREVATIONS = [
    "EJCH", 
    "ECH", 
    "WCp 1", 
    "WCp 2", 
    "WCp 3", 
    "WCH", 
    "U23WCH", 
    "OG", 
    "YOG", 
    "WCH IE", 
    "WCH IE JWCH", 
]

BOATCLASSES_BY_GENDER_AGE_WEIGHT = {
    'm': {
        'u19': {
            'single': ("JM1x", "Junior Men's Single Sculls", "079e71bb-98cd-47f4-8ca4-e3fd0cdbc538"),
            'double': ("JM2x", "Junior Men's Double Sculls", "78f004f6-cadd-4d0f-804b-21cf26458355"),
            'quad': ("JM4x", "Junior Men's Quadruple Sculls", "dc9439cd-36d9-47fd-a205-bc2612f4f83b"),
            'pair': ("JM2-", "Junior Men's Pair", "5851b9f9-5240-4fea-a19e-43b24eb99a10"),
            'coxed_four': ("JM4+", "Junior Men's Coxed Four", "1797cb82-0ced-4fb3-9acd-4a6646f824cb"),
            'four': ("JM4-", "Junior Men's Four", "8661c474-9506-473a-9784-d00ecfa2167f"),
            'eight': ("JM8+", "Junior Men's Eight", "bed56642-164b-4ea5-93ce-1fcadd0ef017")
        },
        'u23': {
            'single': ("BM1x", "U23 Men's Single Sculls", "6b7c0445-c065-49cd-90b3-4c56317e4346"),
            'double': ("BM2x", "U23 Men's Double Sculls", "74864b35-be40-431a-a48c-f1b605a6759e"),
            'quad': ("BM4x", "U23 Men's Quadruple Sculls", "be5a6d89-d55b-4316-9366-7ed1ef0f307b"),
            'pair': ("BM2-", "U23 Men's Pair", "3830f652-0963-4d75-a081-a4ef4553a10c"),
            'coxed_four': ("BM4+", "U23 Men's Coxed Four", "e784fbb3-b45f-45d5-be67-0699cdba4553"),
            'four': ("BM4-", "U23 Men's Four", "2fc7bcd7-3ccc-49eb-ab18-50ab09ae501d"),
            'eight': ("BM8+", "U23 Men's Eight", "2a2a5aa7-8592-4684-99ce-4f02679061e6"),
            'lw_single': ("BLM1x", "U23 Lightweight Men's Single Sculls", "2a2a5aa7-8592-4684-99ce-4f02679061e6"),
            'lw_double': ("BLM2x", "U23 Lightweight Men's Double Sculls", "cc8022e2-3ee1-463a-bddf-aa115d68e704"),
            'lw_quad': ("BLM4x", "U23 Lightweight Men's Quadruple Sculls", "8df04fba-76af-40c4-ac38-73f377bfb258"),
            'lw_pair': ("BLM2-", "U23 Lightweight Men's Pair", "3830f652-0963-4d75-a081-a4ef4553a10c"),
        },
        'elite': {
            'single': ("M1x", "Men's Single Sculls", "3f0d0a7d-92a6-4c53-90f5-7c8f01972964"),
            'double': ("M2x", "Men's Double Sculls", "9cb5d841-32a6-4388-8a30-6d7f51bdfdbc"),
            'quad': ("M4x", "Men's Quadruple Sculls", "d4140064-67dc-47d0-957a-a42e90bf8433"),
            'pair': ("M2-", "Men's Pair", "02316e75-fdf2-4660-af40-48dda1867e1f"),
            'four': ("M4-", "Men's Four", "27d5614e-6530-49d1-acf5-da132b71a45d"),
            'eight': ("M8+", "Men's Eight", "532b264c-47e1-4d35-928a-85d9733928d0"),
            'lw_single': ("LM1x", "Lightweight Men's Single Sculls", "182d0aae-7e73-4900-ae8e-f1aafbe5c48a"),
            'lw_double': ("LM2x", "Lightweight Men's Double Sculls", "4458faa3-d55b-495f-8018-51250f82e5ba"),
            'lw_quad': ("LM4x", "Lightweight Men's Quadruple Sculls", "ba397032-a5c6-466a-ba1b-23e521237048"),
            'lw_pair': ("LM2-", "Lightweight Men's Pair", "46564a8c-b4b3-4bb3-bbf4-cd96bb4ee4f5"),
        },
        'para': {
            '1': ("PR1 M1x", "PR1 Men's Single Sculls", "d7365b40-b544-480b-aa99-b0ffad7a13e9"),
            '2': ("PR2 M1x", "PR2 Men's Single Sculls", "731e3206-45c5-4596-b48e-5a21b1675918"),
            '3': ("PR3 M2-", "PR3 Men's Pair", "15e1ef74-79c6-4227-96f1-86d793efbf5b"),
        }
    },
    'w': {
        'u19': {
            'single': ("JW1x", "Junior Women's Single Sculls", "683b227a-51fd-4c09-a6a0-460ca3711b08"),
            'double': ("JW2x", "Junior Women's Double Sculls", "26af8860-5146-422d-bb10-3eef8b28d883"),
            'quad': ("JW4x", "Junior Women's Quadruple Sculls", "6edc9d42-edda-4f32-9469-91d54e0eaeb1"),
            'pair': ("JW2-", "Junior Women's Pair", "4bbcf35e-b424-4000-9f4f-048f2edce263"),
            'coxed_four': ("JW4+", "Junior Women's Coxed Four", "5911da97-fe4a-42ce-8431-7f3aa9cdfb20"),
            'four': ("JW4-", "Junior Women's Four", "ff2aa19c-db81-4c8e-a523-b7a3ef50ce31"),
            'eight': ("JW8+", "Junior Women's Eight", "d97e6295-e55a-4235-abc3-e986dead5137"),
        },
        'u23': {
            'single': ("BW1x", "U23 Women's Single Sculls", "e22e0fe4-66bc-42f1-82f4-162bb1cc384b"),
            'double': ("BW2x", "U23 Women's Double Sculls", "5a308214-114a-4b49-b985-fdc6e0b7b319"),
            'quad': ("BW4x", "U23 Women's Quadruple Sculls", "ba9814b9-0243-445c-979d-189da9ad8407"),
            'pair': ("BW2-", "U23 Women's Pair", "3304a580-b3b1-4b4e-b51f-e4f63d2e5853"),
            'coxed_four': ("BW4+", "U23 Women's Coxed Four", "e972ad8f-b73e-41ef-a30b-dee4a391a734"),
            'four': ("BW4-", "U23 Women's Four", "c5810370-41ac-45c2-aeff-01dcb1d6d078"),
            'eight': ("BW8+", "U23 Women's Eight", "871abbbb-2413-45b5-b83c-03619c6f0ee5"),
            'lw_single': ("BLW1x", "U23 Lightweight Women's Single Sculls", "60cecbef-919c-47c0-9f16-0a8edd105d82"),
            'lw_double': ("BLW2x", "U23 Lightweight Women's Double Sculls", "aee5f04d-6939-4173-a829-999dfb77f159"),
            'lw_quad': ("BLW4x", "U23 Lightweight Women's Quadruple Sculls", "c18403e0-53cf-4b6b-a1f1-60ad2b220c5a"),
            'lw_pair': ("BLW2-", "U23 Lightweight Women's Pair", "0f218eeb-6f65-48c7-941c-97f0901cb8cd"),
        },
        'elite': {
            'single': ("W1x", "Women's Single Sculls", "8a078108-6741-4ad1-ab5a-704194538227"),
            'double': ("W2x", "Women's Double Sculls", "16946db9-72f2-4375-a797-a26fd485dd26"),
            'quad': ("W4x", "Women's Quadruple Sculls", "7249e207-5c76-4c58-9c7c-b7e2a4c74b50"),
            'pair': ("W2-", "Women's Pair", "5e834702-14c3-4a85-b38d-9afb419f5294"),
            'four': ("W4-", "Women's Four", "2b2bfa01-a902-4ad8-be87-4527c9ba7e6d"),
            'eight': ("W8+", "Women's Eight", "b834436f-4378-4825-aaa0-f9905959abdb"),
            'lw_single': ("LW1x", "Lightweight Women's Single Sculls", "43b5679c-8f9e-45f9-8111-fca22bdc02cc"),
            'lw_double': ("LW2x", "Lightweight Women's Double Sculls", "61be8c32-b56d-4cac-bf56-46246fb1c349"),
            'lw_quad': ("LW4x", "Lightweight Women's Quadruple Sculls", "c47c6b93-dd0d-4645-9545-2ee853db284c"),
            'lw_pair': ("LW2-", "Lightweight Women's Pair", "7b8c2fd0-0286-4bd3-a5c3-0f17a4bc3bd0"),
        },
        'para': {
            '1': ("PR1 W1x", "PR1 Women's Single Sculls", "b61f430f-d4ee-48e0-a632-95b9194ccb16"),
            '2': ("PR2 W1x", "PR2 Women's Single Sculls", "dd434535-b9eb-4b38-9ecf-f3fd6dc9cadf"),
            '3': ("PR3 W2-", "PR3 Women's Pair", "15e1ef74-79c6-4227-96f1-86d793efbf5b"),
        }
    },
    'mixed': {
        'double_2': ("PR2 Mix2x", "PR2 Mixed Double Sculls", "843310e2-f28c-41a7-90e9-b6f8c289b154"),
        'double_3': ("PR3 Mix2x", "PR3 Mixed Double Sculls", "e23cc24f-4a62-4de3-ab99-50a40c8416f0"),
        'four': ("PR3 Mix4+", "PR3 Mixed Coxed Four", "b6bcf280-a57c-4a6a-96fb-91e6a1355002"),
    },
    "all": {
        "all": ("Alle", "Alle")
    }
}

RACE_PHASE_SUBTYPE_BY_RACE_PHASE = {
    "final": {
        "fa": 1,
        "fb": 2,
        "fc": 3,
        "fd": 4
    },
    "semifinal": {
        "sa/b": 1,
        "sc/d": 2
    },
    "quarterfinal": {
        "q1-4": [1, 2, 3, 4]
    },
    "repechage": None,
    "preliminary": None,
}

RACE_PHASE_MAPPING = {
    "final1": "FA",
    "final2": "FB",
    "final3": "FC",
    "final4": "FD",
    "final5": "FE",
    "semifinalA/B1": "S A/B 1",
    "semifinalA/B2": "S A/B 2",
    "semifinalC/D1": "S C/D 1",
    "semifinalC/D2": "S C/D 2",
    "quarterfinal1": "Q1",
    "quarterfinal2": "Q2",
    "quarterfinal3": "Q3",
    "quarterfinal4": "Q4",
    "repechage1": "R1",
    "repechage2": "R2",
    "repechage3": "R3",
    "repechage4": "R4",
    "repechage5": "R5",
    "repechage6": "R6",
    "heat1": "H1",
    "heat2": "H2",
    "heat3": "H3",
    "heat4": "H4",
    "heat5": "H5",
    "heat6": "H6",
    "heat7": "H7",
    "heat8": "H8",
    "preliminary1": "P1",
    "preliminary2": "P2",
    "exhibition": "X"  # TODO: Check if this is relevant
}
