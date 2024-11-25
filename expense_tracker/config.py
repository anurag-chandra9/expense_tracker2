import os
from dotenv import load_dotenv

load_dotenv()

# Edge Config settings
EDGE_CONFIG = {
    'ID': os.getenv('EDGE_CONFIG_ID', 'ecfg_mxz8vua8xfihbqwo0qja3dxtdrlh'),
    'DIGEST': '5bf6b008a9ec05f6870c476d10b53211797aa000f95aae344ae60f9b422286da',
}

# Application settings that can be overridden by Edge Config
DEFAULT_SETTINGS = {
    'EXPENSE_CATEGORIES': [
        'Food',
        'Transportation',
        'Entertainment',
        'Shopping',
        'Bills',
        'Others'
    ],
    'MAX_EXPENSES_PER_PAGE': 10,
    'ENABLE_ANALYTICS': True,
    'DEFAULT_CURRENCY': 'USD'
}
