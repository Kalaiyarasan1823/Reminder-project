from rest_framework import serializers
from .models import Reminder, Category
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['created_at']

class ReminderSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Reminder
        fields = [
            'id', 'title', 'description', 'date', 'time', 'priority', 
            'completed', 'created_at', 'category', 'category_id', 
            'repeat_type', 'is_recurring', 'next_due_date', 'user'
        ]
        read_only_fields = ['created_at', 'user', 'is_recurring', 'next_due_date']
    
    def create(self, validated_data):
        category_id = validated_data.pop('category_id', None)
        validated_data['user'] = self.context['request'].user
        
        # Set recurring logic
        if validated_data.get('repeat_type') != 'none':
            validated_data['is_recurring'] = True
            if not validated_data.get('next_due_date'):
                validated_data['next_due_date'] = validated_data['date']
        
        reminder = Reminder.objects.create(**validated_data)
        
        # Set category if provided
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=validated_data['user'])
                reminder.category = category
                reminder.save()
            except Category.DoesNotExist:
                pass
        
        return reminder
    
    def update(self, instance, validated_data):
        category_id = validated_data.pop('category_id', None)
        
        # Update recurring logic
        if validated_data.get('repeat_type') != 'none':
            validated_data['is_recurring'] = True
            if not validated_data.get('next_due_date'):
                validated_data['next_due_date'] = validated_data.get('date', instance.date)
        else:
            validated_data['is_recurring'] = False
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Set category if provided
        if category_id is not None:
            if category_id:
                try:
                    category = Category.objects.get(id=category_id, user=instance.user)
                    instance.category = category
                except Category.DoesNotExist:
                    instance.category = None
            else:
                instance.category = None
        
        instance.save()
        return instance 