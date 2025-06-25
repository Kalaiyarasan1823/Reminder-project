from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Reminder, Category
from .serializers import ReminderSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Reminder.objects.filter(user=self.request.user)
        
        # Filter by priority
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by completion status
        completed = self.request.query_params.get('completed', None)
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            queryset = queryset.filter(completed=completed_bool)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Search by title or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(title__icontains=search) |
                models.Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_completion(self, request, pk=None):
        reminder = self.get_object()
        reminder.completed = not reminder.completed
        reminder.save()
        return Response({
            'id': reminder.id,
            'completed': reminder.completed
        })
    
    @action(detail=True, methods=['post'])
    def advance_recurring(self, request, pk=None):
        reminder = self.get_object()
        if reminder.is_recurring:
            reminder.advance_to_next()
            return Response({
                'id': reminder.id,
                'next_due_date': reminder.next_due_date,
                'message': f"Reminder '{reminder.title}' advanced to next occurrence."
            })
        return Response({
            'error': 'This reminder is not recurring.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get reminders due in the next 7 days"""
        from datetime import date, timedelta
        today = date.today()
        next_week = today + timedelta(days=7)
        
        queryset = self.get_queryset().filter(
            date__range=[today, next_week],
            completed=False
        ).order_by('date', 'time')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue reminders"""
        from datetime import date
        
        queryset = self.get_queryset().filter(
            date__lt=date.today(),
            completed=False
        ).order_by('date', 'time')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 