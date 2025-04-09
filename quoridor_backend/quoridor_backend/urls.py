"""
URL configuration for quoridor_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from game.views import game_view, get_game_state, move_pawn, place_fence

urlpatterns = [
    path("admin/", admin.site.urls),
    path('game/<int:game_id>/', game_view, name='game'),
    path('api/game/<int:game_id>/', get_game_state, name='api-game-state'),
    path('api/game/<int:game_id>/move/', move_pawn, name='api-move-pawn'),
    path('api/game/<int:game_id>/fence/', place_fence, name='api-place-fence'),
]
