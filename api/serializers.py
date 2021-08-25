from rest_framework import serializers
from predictor.models import Prediction, Banker, LiveGame
from accounts.models import User

class LiveGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveGame
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    FavouriteTeam = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='Nickname'
    )
    class Meta:
        model = User
        fields = ('id','Full_Name', 'FavouriteTeam')

class PredictionSerializer(serializers.ModelSerializer):
    Game = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='TeamsName'
    )
    User = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='Full_Name'
    )
    class Meta:
        model = Prediction
        fields = ('User','Game','PredWeek','Winner', 'Banker', 'Points', 'Joker')

class BankerSerializer(serializers.ModelSerializer):
    User = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='Full_Name'
    )
    BankerTeam = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='Nickname'
    )
    class Meta:
        model = Banker
        fields = ('User','BankWeek', 'BankSeason', 'BankerTeam')