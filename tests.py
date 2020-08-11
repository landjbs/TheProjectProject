from app import create_app
from app.config import test_config
from app.database import db
from app.user.models import User
from sqlalchemy.sql.expression import func
from faker import Faker
import unittest
