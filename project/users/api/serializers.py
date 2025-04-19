from rest_framework import serializers

from project.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'patronymic', 'email', 'public_key']


class UserCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'patronymic', 'email', 'password1', 'password2']

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords must match.'})
        return attrs

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            patronymic=validated_data['patronymic'],
            email=validated_data['email'],
        )
        password = validated_data['password1']
        user.set_password(password)
        user.save()
        return user
