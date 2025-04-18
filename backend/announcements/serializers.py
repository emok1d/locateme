from rest_framework import serializers
from .models import Announcements
from buildings.models import Buildings

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buildings
        fields = [
            'building_id',
            'address_text',
            'district',
            'coordinates',
            'house_type',
            'year_of_construction',
            'number_of_floors',
            'ceiling_height',
            'passenger_elevator',
            'service_elevator',
            'courtyard',
            'parking'
        ]

class AnnouncementSerializer(serializers.ModelSerializer):
    building = BuildingSerializer(read_only=True)
    walk_score = serializers.SerializerMethodField()
    personal_score = serializers.SerializerMethodField()

    class Meta:
        model = Announcements
        fields = "__all__"
        depth = 1
        
    def get_walk_score(self, obj):
        # Если walk_score не установлен, попробуем вычислить его
        if obj.walk_score is None and obj.coordinates:
            return obj.calculate_walk_score()
        return obj.walk_score or 0  # Возвращаем 0 вместо None
    
    def get_personal_score(self, obj):
        request = self.context.get('request')
        if not request:
            return None
            
        # Собираем фильтры удобств из query-параметров
        amenities_filters = {
            key.split('amenities_')[1]: value
            for key, value in request.GET.items()
            if key.startswith('amenities_') and 
               value in ["any", "nearby", "far", "close"]
        }
        
        # Преобразуем "close" в "nearby" для бэкенда
        #print("Фильтры из запроса:", amenities_filters)
        translated_filters = {
            k: "nearby" if v == "close" else v
            for k, v in amenities_filters.items()
        }
        
        return obj.calculate_personal_score(translated_filters, verbose=True)