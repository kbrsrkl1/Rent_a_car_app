from posixpath import lexists
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Car,Reservation
from .serializers import CarSerializer
from .permissions import IsStaffOrReadOnly
from django.db.models import Q, Exists, OuterRef


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

    # def get_serializer_class(self):
    #     if self.request.user.is_staff:
    #         return CarStaffSerializer
    #     else:
    #         CarSerizlizer