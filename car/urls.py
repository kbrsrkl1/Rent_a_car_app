from django.urls import path,include
from rest_framework import routers
from .views import CarView, ReservationView

router = routers.DefaultRouter()
router.register('car', CarView)



urlpatterns = [
    path('reservation/', ReservationView.as_view())
]


urlpatterns += router.urls