from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # Проверяем лимит открытых объявлений только при создании или смене статуса на OPEN
        if data.get('status') == 'OPEN':
            user = self.context['request'].user
            open_ads_count = Advertisement.objects.filter(
                creator=user, 
                status='OPEN'
            ).count()
            
            # При обновлении не считаем текущее объявление
            if self.instance and self.instance.status != 'OPEN':
                if open_ads_count >= 10:
                    raise serializers.ValidationError('Нельзя иметь более 10 открытых объявлений')
            elif not self.instance and open_ads_count >= 10:
                raise serializers.ValidationError('Нельзя иметь более 10 открытых объявлений')

        return data
