
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from account.models import UserAccount


""" Registers a user after some validations:
	1. Email must be unique
	2. Username must be unique
	3. Two passwords must match 
"""

OPTIONS = (
    ('admin', 'Admin'),
    ('organization', 'Organization'),
    ('database-admin', 'Database Admin'),
    # ('hr-admin', 'HR Admin'),
    # ('CSR', 'CSR'),
    # ('registration-admin', 'Registration Admin'),
    # ('labowner', 'Lab'),
    # ('finance-officer', 'Finance Officer'),
    # ('organization', 'Organization'),
    # ('superadmin', 'Superadmin'),

)


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255,required=False)
    username = serializers.CharField(
        required=True, min_length=5, max_length=50,
        validators=[UniqueValidator(queryset=UserAccount.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password], style={'input_type': 'password'})

    password2 = serializers.CharField(write_only=True, required=True, style={
                                      'input_type': 'password'})

    account_type = serializers.ChoiceField(required=True, choices=OPTIONS)

    class Meta:
        model = UserAccount
        fields = ('id', 'username', 'email', 'password', 'last_login',
                  'password2', 'account_type', 'password_foradmins')

    # Validate passwords and throw error if two passwords didn't match

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    # Create user if all data is valid
    def create(self, validated_data):
        user = UserAccount.objects.create(
            username=validated_data['username'],
            account_type=validated_data['account_type']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    model = UserAccount

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
