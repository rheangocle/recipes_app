from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from ..models import Recipe, Feedback, RecipePreference


class UserStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user's recipe statistics"""
        user = request.user

        total_favorites = RecipePreference.objects.filter(
            user=user, preference="favorite"
        ).count()

        total_rated = Feedback.objects.filter(user=user).count()

        avg_rating = (
            Feedback.objects.filter(user=user).aggregate(avg=Avg("rating"))["avg"] or 0
        )

        fodmap_recipes_tried = Feedback.objects.filter(
            user=user, recipe__fodmap_friendly=True
        ).count()

        cuisine_stats = (
            Recipe.objects.filter(
                Q(user_preferences__user=user, user_preferences__preference="favorite")
                | Q(feedback__user=user)
            )
            .values("cuisine")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        return Response(
            {
                "total_favorites": total_favorites,
                "total_rated": total_rated,
                "average_rating": avg_rating,
                "fodmap_recipes_tried": fodmap_recipes_tried,
                "top_cuisines": cuisine_stats,
            }
        )
