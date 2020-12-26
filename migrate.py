"""
Exported method which are supposed to be run once per deployment
"""
from src.users import table_creation, create_default_users


if __name__ == "__main__":
    table_creation()
    create_default_users()
