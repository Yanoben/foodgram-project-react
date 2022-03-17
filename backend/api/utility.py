from collections import defaultdict

from django.http import HttpResponse

from recipes.models import IngredientRecipe


def create_txt(request):
    """Скачать список покупок в txt."""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=ingredients.txt'
    user = request.user
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_cart__user=user
    )
    if not ingredients:
        response.writelines('Ваш список покупок пуст.')
        return response
    listing = defaultdict(int)
    for i in ingredients:
        listing[i.ingredient] += i.amount
    listing = [f'{k} - {v}' + '\n' for k, v in listing.items()]
    listing = ['Ваш список покупок: \n'] + listing
    response.writelines(listing)
    return response
