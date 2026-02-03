"""
User Model Unit Tests

Tests for User model methods and properties.
"""

from app.models.user import CareerStage, SubscriptionTier, User


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, app, db_session):
        """Test creating a new user."""
        with app.app_context():
            user = User(email="model_test@example.com", first_name="Model", last_name="Test")
            user.set_password("TestPassword123")
            db_session.add(user)
            db_session.commit()

            assert user.id is not None
            assert user.email == "model_test@example.com"
            assert user.subscription_tier == SubscriptionTier.BASIC.value

    def test_password_hashing(self, app, db_session):
        """Test password is properly hashed."""
        with app.app_context():
            user = User(email="hash_test@example.com")
            user.set_password("MySecurePassword123")

            assert user.password_hash is not None
            assert user.password_hash != "MySecurePassword123"
            assert user.check_password("MySecurePassword123") is True
            assert user.check_password("WrongPassword") is False

    def test_full_name_property(self, app, db_session):
        """Test full_name property."""
        with app.app_context():
            # Both names
            user1 = User(email="name1@example.com", first_name="John", last_name="Doe")
            assert user1.full_name == "John Doe"

            # First name only
            user2 = User(email="name2@example.com", first_name="Jane")
            assert user2.full_name == "Jane"

            # Last name only
            user3 = User(email="name3@example.com", last_name="Smith")
            assert user3.full_name == "Smith"

            # No name
            user4 = User(email="name4@example.com")
            assert user4.full_name == "Anonymous"

    def test_tier_limits_basic(self, app, db_session):
        """Test tier limits for basic subscription."""
        with app.app_context():
            user = User(
                email="basic@example.com",
                subscription_tier=SubscriptionTier.BASIC.value,
            )
            limits = user.tier_limits

            assert limits["recruiters"] == 5
            assert limits["tailored_resumes"] == 2
            assert limits["ai_messages"] == 10
            assert limits["interview_prep"] == 0

    def test_tier_limits_pro(self, app, db_session):
        """Test tier limits for pro subscription."""
        with app.app_context():
            user = User(email="pro@example.com", subscription_tier=SubscriptionTier.PRO.value)
            limits = user.tier_limits

            assert limits["recruiters"] == 50
            assert limits["tailored_resumes"] == 10
            assert limits["ai_messages"] == 100
            assert limits["interview_prep"] == 3

    def test_tier_limits_expert(self, app, db_session):
        """Test tier limits for expert subscription (unlimited)."""
        with app.app_context():
            user = User(
                email="expert@example.com",
                subscription_tier=SubscriptionTier.EXPERT.value,
            )
            limits = user.tier_limits

            # -1 means unlimited
            assert limits["recruiters"] == -1
            assert limits["tailored_resumes"] == -1
            assert limits["ai_messages"] == -1

    def test_can_use_feature_within_limit(self, app, db_session):
        """Test can_use_feature returns True within limits."""
        with app.app_context():
            user = User(
                email="feature_test@example.com",
                subscription_tier=SubscriptionTier.BASIC.value,
                monthly_message_count=5,
            )

            assert user.can_use_feature("ai_messages") is True
            assert user.can_use_feature("ai_messages", 4) is True

    def test_can_use_feature_at_limit(self, app, db_session):
        """Test can_use_feature returns False at limit."""
        with app.app_context():
            user = User(
                email="limit_test@example.com",
                subscription_tier=SubscriptionTier.BASIC.value,
                monthly_message_count=10,  # Basic limit is 10
            )

            assert user.can_use_feature("ai_messages") is False

    def test_can_use_feature_unlimited(self, app, db_session):
        """Test can_use_feature always returns True for unlimited tier."""
        with app.app_context():
            user = User(
                email="unlimited@example.com",
                subscription_tier=SubscriptionTier.EXPERT.value,
                monthly_message_count=1000000,
            )

            assert user.can_use_feature("ai_messages") is True

    def test_to_dict_basic(self, app, db_session):
        """Test to_dict returns expected fields."""
        with app.app_context():
            user = User(email="dict_test@example.com", first_name="Dict", last_name="Test")
            user.set_password("TestPassword123")
            db_session.add(user)
            db_session.commit()

            data = user.to_dict()

            assert "id" in data
            assert data["email"] == "dict_test@example.com"
            assert data["first_name"] == "Dict"
            assert data["last_name"] == "Test"
            assert "password_hash" not in data
            # Private fields should not be included by default
            assert "stripe_customer_id" not in data

    def test_to_dict_with_private(self, app, db_session):
        """Test to_dict with private fields included."""
        with app.app_context():
            user = User(
                email="private@example.com",
                first_name="Private",
                salary_expectation=100000,
            )
            user.set_password("TestPassword123")
            db_session.add(user)
            db_session.commit()

            data = user.to_dict(include_private=True)

            assert "salary_expectation" in data
            assert data["salary_expectation"] == 100000
            assert "tier_limits" in data
            assert "usage" in data


class TestCareerStageDetection:
    """Tests for career stage detection algorithm."""

    def test_entry_level_detection(self):
        """Test entry level detection (0-2 years)."""
        assert User.detect_career_stage(0) == CareerStage.ENTRY_LEVEL.value
        assert User.detect_career_stage(1) == CareerStage.ENTRY_LEVEL.value
        assert User.detect_career_stage(2) == CareerStage.ENTRY_LEVEL.value

    def test_early_career_detection(self):
        """Test early career detection (2-5 years)."""
        assert User.detect_career_stage(3) == CareerStage.EARLY_CAREER.value
        assert User.detect_career_stage(4) == CareerStage.EARLY_CAREER.value
        assert User.detect_career_stage(5) == CareerStage.EARLY_CAREER.value

    def test_mid_level_detection(self):
        """Test mid level detection (5-10 years)."""
        assert User.detect_career_stage(6) == CareerStage.MID_LEVEL.value
        assert User.detect_career_stage(8) == CareerStage.MID_LEVEL.value
        assert User.detect_career_stage(10) == CareerStage.MID_LEVEL.value

    def test_senior_detection(self):
        """Test senior detection (10-15 years)."""
        assert User.detect_career_stage(11) == CareerStage.SENIOR.value
        assert User.detect_career_stage(13) == CareerStage.SENIOR.value
        assert User.detect_career_stage(15) == CareerStage.SENIOR.value

    def test_executive_detection(self):
        """Test executive detection (15+ years)."""
        assert User.detect_career_stage(16) == CareerStage.EXECUTIVE.value
        assert User.detect_career_stage(20) == CareerStage.EXECUTIVE.value
        assert User.detect_career_stage(30) == CareerStage.EXECUTIVE.value

    def test_none_experience(self):
        """Test None years defaults to entry level."""
        assert User.detect_career_stage(None) == CareerStage.ENTRY_LEVEL.value
