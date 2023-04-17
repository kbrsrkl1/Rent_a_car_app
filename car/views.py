from rest_framework.viewsets import ModelViewSet
from .models import Car,Reservation
from .serializers import CarSerializer, CarStaffSerializer, ResevationSeializers
from .permissions import IsStaffOrReadOnly
from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class CarView(ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = (IsStaffOrReadOnly,)  # [IsStaffOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = super().get_queryset()
        else:
            queryset = super().get_queryset().filter(availability=True)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if start is not None or end is not None:

                not_available = Reservation.objects.filter(
                    start_date__lt=end, end_date__gt=start
                ).values_list('car_id', flat=True)  # [1, 2]      
                not_available = Reservation.objects.filter(
                    Q(start_date__lt=end) & Q(end_date__gt=start)
                ).values_list('car_id', flat=True)  # [1, 2]      
                queryset = queryset.exclude(id__in=not_available)

                #queryset = queryset.annotate(
                #    is_available=~lexists(Reservation.objects.filter(
                #        Q(car=OuterRef('pk')) & Q(
                #            start_date__lt=end) & Q(end_date__gt=start)
                #    ))
                #)

        return queryset

    def get_serializer(self, *args, **kwargs):
        if self.request.user.is_staff:
            return CarStaffSerializer(*args, **kwargs)
        else:
            return CarSerializer(*args, **kwargs)
    
    #def get_serializer(self):
    #        if self.request.user.is_staff:
    #            return CarStaffSerializer
    #        else:
    #            CarSerializer


class ReservationView(ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ResevationSeializers
    permission_classes = (IsAuthenticated,)


    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(customer=self.request.user)
    
class ReservationDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ResevationSeializers

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        end = serializer.validated_data.get('end_date')
        car = serializer.validated_data.get('car')
        

        if Reservation.objects.filter(car=car).exists():
            for res in Reservation.objects.filter(car=car):
                if res.start_date < end < res.end_date:
                    return Response({'message': 'Car is not available...'})


        return super().update(request, *args, **kwargs)
