from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .models import Resource, Booking, TimeSlot
from .serializers import ResourceSerializer, BookingSerializer, TimeSlotSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        time_slot_id = request.data.get('time_slot')
        date = request.data.get('date')

        # Получаем временной слот
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id, date=date)
        except TimeSlot.DoesNotExist:
            return Response({
                'error': 'The selected time slot does not exist for the specified date.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Проверка: есть ли уже бронирование этого пользователя для данного слота
        existing_booking = Booking.objects.filter(
            user=request.user, time_slot=time_slot, date=date
        ).exists()

        if existing_booking:
            return Response({
                'error': 'You have already booked this time slot for the specified date.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Проверяем, заполнены ли слоты
        active_bookings = Booking.objects.filter(
            time_slot=time_slot, date=date, status='active'
        )

        if active_bookings.count() >= time_slot.max_people:
            # Все слоты заняты, добавляем пользователя в очередь
            queue_position = Booking.objects.filter(time_slot=time_slot, date=date, status='queued').count() + 1
            booking = Booking.objects.create(
                user=request.user,
                time_slot=time_slot,
                date=date,
                status='queued',
                queue_position=queue_position
            )
            print(f'User {request.user.username} has been added to the queue.')
            return Response({
                'message': 'All slots are full. You have been added to the queue.'
            }, status=status.HTTP_201_CREATED)

        # Если есть свободные слоты, создаем активное бронирование
        booking = Booking.objects.create(
            user=request.user,
            time_slot=time_slot,
            date=date,
            status='active'
        )
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        booking = self.get_object()

        # Удаляем бронирование
        self.perform_destroy(booking)

        # Проверяем наличие пользователей в очереди для этого слота
        queued_booking = Booking.objects.filter(
            time_slot=booking.time_slot, date=booking.date, status='queued'
        ).order_by('queue_position').first()

        if queued_booking:
            # Переводим первого в очереди в статус активного
            queued_booking.status = 'active'
            queued_booking.queue_position = None
            queued_booking.save()

            # Уведомляем в консоль
            print(f'User {queued_booking.user.username} has been moved from queue to active booking.')

        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        # Получение всех бронирований текущего пользователя
        bookings = Booking.objects.filter(user=request.user).order_by('date', 'time_slot__start_time')
        return Response(BookingSerializer(bookings, many=True).data)
